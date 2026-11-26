#!/usr/bin/env python3
"""remote-test team client: snapshot a Git repo, upload it, queue it on the
shared VM pool, and read status/results. Needs only python3, git and gcloud.
"""
import argparse, gzip, hashlib, json, os, pathlib, re, subprocess, sys, tarfile, tempfile, time, urllib.parse, uuid
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import core, gcp

CONFIG = pathlib.Path(os.environ.get('REMOTE_TEST_CONFIG', pathlib.Path.home() / '.config/remote-test/team.json'))
LOCAL = pathlib.Path(os.environ.get('REMOTE_TEST_HOME', pathlib.Path.home() / '.local/share/remote-test'))
SECRET_NAMES = {'.npmrc', '.pypirc', 'credentials.json', 'id_rsa', 'id_ed25519', '.netrc'}
SECRET_SUFFIXES = {'.pem', '.key', '.p12', '.pfx'}


def git(repo, *args, text=True):
    return subprocess.run(['git', *args], cwd=repo, check=True, capture_output=True, text=text).stdout


def snapshot(repo, dest):
    """Git bundle of HEAD+tags plus tracked/untracked-nonignored worktree files,
    minus common credential files, dependencies and generated state."""
    head = git(repo, 'rev-parse', 'HEAD').strip()
    if any(line.startswith('160000 ') for line in git(repo, 'ls-files', '--stage').splitlines()):
        raise RuntimeError('Submodules are not supported; refusing an incomplete source snapshot.')
    subprocess.run(['git', 'bundle', 'create', str(dest / 'source.bundle'), 'HEAD', '--tags'], cwd=repo, check=True, capture_output=True)
    names = git(repo, 'ls-files', '-z', '--cached', '--others', '--exclude-standard').split('\0')
    sent, excluded = [], []
    with tarfile.open(dest / 'worktree.tar.gz', 'w:gz') as archive:
        for name in sorted(set(filter(None, names))):
            path = pathlib.PurePosixPath(name)
            secret = path.name in SECRET_NAMES or path.suffix in SECRET_SUFFIXES or (
                path.name.startswith('.env') and not path.name.endswith(('.example', '.sample', '.template')))
            generated = '.foundation' in path.parts and name not in {'.foundation/.gitignore', '.foundation/README.md'}
            if secret or generated or any(part in {'.git', 'node_modules', '.venv', '.ssh'} for part in path.parts):
                excluded.append(name); continue
            source = repo / name
            if source.is_symlink() and not source.resolve().is_relative_to(repo):
                raise RuntimeError('Symlink outside repository: ' + name)
            if source.is_file() or source.is_symlink():
                archive.add(source, arcname=name, recursive=False); sent.append(name)
    sha = hashlib.sha256((dest / 'worktree.tar.gz').read_bytes()).hexdigest()
    (dest / 'snapshot.json').write_text(json.dumps(dict(head=head, included=sent, excluded=excluded, sha256=sha), indent=2))
    digest = hashlib.sha256()
    with gzip.open(dest / 'worktree.tar.gz', 'rb') as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b''): digest.update(chunk)
    with open(dest / 'source.bundle', 'rb') as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b''): digest.update(chunk)
    return head, digest.hexdigest(), len(excluded)


PROFILES = pathlib.Path(os.environ.get('REMOTE_TEST_PROFILES', pathlib.Path.home() / '.config/remote-test/projects'))
PARAM_ARGS = (('command', 'command'), ('timeout', 'timeout'), ('cpus', 'cpus'), ('memory_gb', 'memory_gb'),
              ('exclusive', 'exclusive'), ('exclusive_reason', 'exclusive_reason'), ('image', 'image'), ('shell', 'shell'),
              ('mongo', 'mongo'), ('cache_go', 'cache_go'), ('go_packages', 'go_packages'), ('go_toolchain', 'go_toolchain'),
              ('test_timeout', 'test_timeout'), ('strict', 'strict'))


def check_profile_name(name):
    if not re.fullmatch(r'[a-z0-9][a-z0-9_-]{0,31}', name or ''): raise ValueError('Profile name: lowercase letters, digits, - or _ (e.g. quick, full)')


def repo_identity(repo):
    """Same repository across clones/worktrees: normalized origin URL, else its path."""
    try: url = git(repo, 'config', '--get', 'remote.origin.url').strip()
    except subprocess.CalledProcessError: url = ''
    if not url: return 'path:' + str(pathlib.Path(repo).resolve())
    url = re.sub(r'^[a-z+]+://', '', url)          # scheme
    url = re.sub(r'^[^@/]+@', '', url)              # user/credentials
    url = re.sub(r'^([^/:]+):(?!\d+/)', r'\1/', url)  # scp-style host:path
    url = re.sub(r':\d+/', '/', url)                # port
    return 'git:' + re.sub(r'\.git/?$', '', url).rstrip('/').lower()


class Profiles:
    """Per-user, per-repository saved run settings in ~/.config/remote-test/projects."""
    def __init__(self, repo):
        self.repo = pathlib.Path(repo).resolve()
        self.identity = repo_identity(self.repo)
        slug = re.sub(r'[^a-z0-9]+', '-', self.identity.split(':', 1)[1].lower()).strip('-')[-60:]
        self.path = PROFILES / (slug + '-' + hashlib.sha256(self.identity.encode()).hexdigest()[:8] + '.json')

    def load(self):
        return json.loads(self.path.read_text()) if self.path.exists() else dict(repo=self.identity, default=None, profiles={})

    def save(self, name, params, job_id, head, make_default=False):
        check_profile_name(name); core.validate(params)
        data = self.load()
        data['profiles'][name] = dict(params=params, verified_job=job_id, verified_head=head, saved_at=time.strftime('%Y-%m-%d %H:%M:%S'))
        if make_default or not data.get('default') or data['default'] not in data['profiles']: data['default'] = name
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix('.tmp'); tmp.write_text(json.dumps(data, indent=2)); tmp.replace(self.path)
        return dict(profile=name, default=data['default'], file=str(self.path))

    def pick(self, name=None):
        data = self.load()
        if not data['profiles']:
            raise ValueError('No saved profile for this repository. Run `remote-test setup` to see suggestions, then '
                             '`remote-test submit ... --save-profile quick` once.')
        name = name or data.get('default')
        if name not in data['profiles']: raise ValueError(f'Unknown profile {name}; have: ' + ', '.join(sorted(data['profiles'])))
        return name, data['profiles'][name]

    def delete(self, name):
        data = self.load()
        if name not in data['profiles']: raise ValueError('Unknown profile ' + name)
        del data['profiles'][name]
        if data.get('default') == name: data['default'] = next(iter(sorted(data['profiles'])), None)
        self.path.write_text(json.dumps(data, indent=2))
        return data


def detect(repo):
    """Heuristic suggestions only; the agent/user must confirm against project docs and CI."""
    repo = pathlib.Path(repo); hints, out = [], []
    files = set(git(repo, 'ls-files').splitlines())
    def has(name): return name in files
    if has('package.json'):
        pkg = json.loads((repo / 'package.json').read_text() or '{}')
        scripts = pkg.get('scripts', {})
        pm = 'pnpm' if has('pnpm-lock.yaml') else 'yarn' if has('yarn.lock') else 'bun' if (has('bun.lockb') or has('bun.lock')) else 'npm'
        install = {'pnpm': 'corepack enable && pnpm install --frozen-lockfile', 'yarn': 'corepack enable && yarn install --immutable',
                   'bun': 'bun install --frozen-lockfile', 'npm': 'npm ci'}[pm]
        run = (lambda s: f'{pm} run {s}') if pm != 'npm' else (lambda s: f'npm run {s}' if s != 'test' else 'npm test')
        if 'test' in scripts: out.append(dict(name='quick', command=f'{install} && {run("test")}'))
        for s in ('test:all', 'test:ci', 'ci', 'test:e2e', 'test:integration'):
            if s in scripts: out.append(dict(name='full' if s in ('test:all', 'test:ci', 'ci') else s.replace('test:', ''), command=f'{install} && {run(s)}'))
        if 'playwright' in json.dumps(pkg): hints.append('Playwright detected: add `npx playwright install chromium` (matching version) before e2e tests.')
        if pkg.get('engines', {}).get('node'): hints.append('package.json engines.node = ' + pkg['engines']['node'] + ' (image default Node 24, Node 22 cached).')
    if has('go.mod'):
        line = next((l for l in (repo / 'go.mod').read_text().splitlines() if l.startswith(('toolchain ', 'go '))), '')
        out.append(dict(name='full' if not out else 'go', go_packages=['./...']))
        if line: hints.append('go.mod: ' + line + ' (pin with --go-toolchain goX.Y.Z if required).')
    if (has('pyproject.toml') or has('requirements.txt')) and not out:
        out.append(dict(name='quick', command='uv sync && uv run pytest' if has('uv.lock') else 'python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt && pytest'))
    if has('Makefile') and re.search(r'^test:', (repo / 'Makefile').read_text(errors='ignore'), re.M) and not out:
        out.append(dict(name='quick', command='make test'))
    try:
        if subprocess.run(['git', 'grep', '-qil', '-e', 'MONGO_URI', '-e', 'mongodb://', '--', '*.go', '*.ts', '*.js', '*.py', '*.env.example'],
                          cwd=repo, capture_output=True).returncode == 0:
            hints.append('MongoDB referenced: consider --mongo 7 (check which env var the tests read).')
    except OSError: pass
    if any(f.startswith(('docker-compose', 'compose.')) for f in files): hints.append('Compose file present: only use --exclusive if tests really need host Docker.')
    for ci in sorted(f for f in files if f.startswith('.github/workflows/') or f in ('.gitlab-ci.yml', 'bitbucket-pipelines.yml'))[:5]:
        hints.append('Compare with CI: ' + ci)
    return out, hints


class Client:
    def __init__(self, config=None, tokens=None):
        self.cfg = config or json.loads(CONFIG.read_text())
        self.tokens = tokens or gcp.GcloudTokens()
        self.storage = gcp.Storage(self.cfg['bucket'], self.tokens)

    def api(self, method, path, body=None):
        try:
            return gcp.request(method, self.cfg['api_url'].rstrip('/') + path, body=body, token=self.tokens.identity(), timeout=120,
                               data=b'' if method == 'POST' and body is None else None)
        except gcp.ApiError as error:
            raise RuntimeError(f'Queue API {error.code}: {error.message}') from None

    def submit(self, args):
        params = {k: v for k, v in ((key, getattr(args, attr, None)) for attr, key in PARAM_ARGS) if v is not None}
        if args.replay_run:
            core.validate(params)
            if not re.fullmatch(r'[0-9]{8}-[0-9]{6}-[0-9a-f]{8}', args.replay_run): raise ValueError('Invalid replay job ID')
            return self.api('POST', '/submit', dict(params=params, replay_of=args.replay_run))
        return self.submit_params(params, args.repo, getattr(args, 'save_profile', None))

    def submit_params(self, params, repo_arg, save_profile=None, profile_used=None):
        core.validate(params)  # fail fast; the API re-validates
        if save_profile: check_profile_name(save_profile)
        repo = pathlib.Path(repo_arg).resolve()
        root = pathlib.Path(git(repo, 'rev-parse', '--show-toplevel').strip()).resolve()
        if root != repo: raise ValueError('--repo must be the Git root; use cd inside --command for packages')
        email = self.api('GET', '/whoami')['email']
        prefix = f'uploads/{core.safe_name(email)}/{uuid.uuid4().hex}'
        with tempfile.TemporaryDirectory(prefix='remote-test-') as tmp:
            folder = pathlib.Path(tmp)
            head, sha, excluded = snapshot(repo, folder)
            for name in core.SOURCE_FILES:
                self.storage.upload(prefix + '/' + name, folder / name)
        out = self.api('POST', '/submit', dict(params=params, source_prefix=prefix, source_sha256=sha, head=head,
                                               project=repo.name, repo_key=str(repo)))
        out['excluded_files'] = excluded
        record = LOCAL / 'runs' / out['job_id']; record.mkdir(parents=True, exist_ok=True)
        (record / 'submission.json').write_text(json.dumps(dict(out, repo=str(repo), repo_identity=repo_identity(repo),
                                                params=params, save_profile=save_profile, profile=profile_used), indent=2))
        out['results'] = str(record / 'results')
        if profile_used: out['profile'] = profile_used
        if save_profile: out['save_profile'] = f'{save_profile} (saved automatically when `remote-test status {out["job_id"]}` shows passed)'
        return out

    def run(self, args):
        repo = git_root(args.repo)
        name, profile = Profiles(repo).pick(args.profile)
        params = dict(profile['params'])
        for attr in ('timeout', 'cpus', 'memory_gb'):
            if getattr(args, attr) is not None: params[attr] = getattr(args, attr)
        return self.submit_params(params, str(repo), profile_used=name)

    def save_from_job(self, name, job_id, repo, make_default=False):
        """Save a passed job's exact parameters as a local profile for this repo."""
        check_profile_name(name)
        record = LOCAL / 'runs' / job_id / 'submission.json'
        if not record.exists(): raise ValueError('Job was not submitted from this Mac; no local parameters for ' + job_id)
        sub = json.loads(record.read_text())
        status = self.api('GET', '/jobs/' + job_id)['jobs'][0]['status']
        if status != 'passed': raise ValueError(f'Job {job_id} is {status}; only a passed job can become a profile')
        profiles = Profiles(pathlib.Path(repo).resolve())
        if sub.get('repo_identity', 'path:' + sub['repo']) != profiles.identity:
            raise ValueError('Job ' + job_id + ' was for a different repository: ' + sub['repo'])
        return profiles.save(name, sub['params'], job_id, sub.get('head'), make_default)

    def fetch_results(self, job):
        """Download a finished job's results into the local cache."""
        folder = LOCAL / 'runs' / job['job_id'] / 'results'
        folder.mkdir(parents=True, exist_ok=True)
        for name in self.storage.list(f"runs/{job['job_id']}/results/"):
            target = folder / name.rsplit('/', 1)[1]
            if not target.exists(): self.storage.download(name, target)
        return str(folder)

    def status(self, job_id, live=False):
        out = self.api('GET', '/jobs/' + job_id)
        for job in out['jobs']:
            if job['status'] in core.TERMINAL and job.get('result'):
                try: job['results'] = self.fetch_results(job)
                except Exception as error: job['results_unavailable'] = str(error)
            if not live: job.pop('progress', None)
            record = LOCAL / 'runs' / job['job_id'] / 'submission.json'
            if job['status'] == 'passed' and record.exists():
                sub = json.loads(record.read_text())
                if sub.get('save_profile') and not sub.get('profile_saved'):
                    try:
                        saved = Profiles(pathlib.Path(sub['repo'])).save(sub['save_profile'], sub['params'], job['job_id'], sub.get('head'))
                        job['profile_saved'] = saved
                        record.write_text(json.dumps(dict(sub, profile_saved=True), indent=2))
                    except Exception as error: job['profile_save_failed'] = str(error)
        return out


def parser():
    p = argparse.ArgumentParser(prog='remote-test', description=__doc__)
    subs = p.add_subparsers(dest='action', required=True)
    s = subs.add_parser('submit')
    s.add_argument('--repo', default='.'); s.add_argument('--command')
    s.add_argument('--strict', action='store_true', help='bash errexit/pipefail for custom commands')
    s.add_argument('--exclusive', action='store_true', help='Run alone on the host (Docker Compose / host access)')
    s.add_argument('--exclusive-reason')
    s.add_argument('--image', help='Container image for a pinned toolchain'); s.add_argument('--shell', choices=['bash', 'sh'], default='bash')
    s.add_argument('--mongo', choices=['6', '7', '8']); s.add_argument('--cache-go', action='store_true')
    s.add_argument('--go-packages', nargs='+'); s.add_argument('--go-toolchain')
    s.add_argument('--test-timeout', type=int, default=300)
    s.add_argument('--replay-run', help='Rerun the exact uploaded source of an earlier job ID')
    s.add_argument('--timeout', type=int, default=3600)
    s.add_argument('--cpus', type=int, default=6); s.add_argument('--memory-gb', type=int, default=6)
    s.add_argument('--save-profile', metavar='NAME', help='Save these settings as a local profile once this job passes')
    u = subs.add_parser('setup', help='One-time per repo: show detected test commands and saved profiles')
    u.add_argument('--repo', default='.')
    r = subs.add_parser('run', help='Submit using a saved profile for this repo')
    r.add_argument('--profile', help='Profile name (default: the repo default)'); r.add_argument('--repo', default='.')
    r.add_argument('--timeout', type=int); r.add_argument('--cpus', type=int); r.add_argument('--memory-gb', type=int)
    pr = subs.add_parser('profile', help='Manage saved profiles for this repo')
    pr.add_argument('op', choices=['list', 'save', 'default', 'delete']); pr.add_argument('name', nargs='?')
    pr.add_argument('--from-job', help='Passed job ID whose settings to save'); pr.add_argument('--repo', default='.')
    l = subs.add_parser('list'); l.add_argument('--limit', type=int, default=30)
    for name in ('status', 'cancel'):
        q = subs.add_parser(name); q.add_argument('job_id')
        if name == 'status': q.add_argument('--live', action='store_true', help='Include remote progress')
    subs.add_parser('nodes'); subs.add_parser('whoami'); subs.add_parser('tick')
    return p


def git_root(path):
    return pathlib.Path(git(pathlib.Path(path).resolve(), 'rev-parse', '--show-toplevel').strip()).resolve()


def main(argv=None):
    args = parser().parse_args(argv)
    if args.action == 'setup':
        repo = git_root(args.repo); profiles = Profiles(repo); suggestions, hints = detect(repo)
        data = profiles.load()
        out = dict(repo=str(repo), repository_identity=profiles.identity, saved_profiles=data['profiles'], default=data.get('default'),
                   profile_file=str(profiles.path), suggestions=suggestions, hints=hints,
                   next_steps=['Confirm the command against the project README/CI (suggestions are heuristics).',
                               'remote-test submit --repo ' + str(repo) + " --command '<cmd>' [--mongo 7] --save-profile quick",
                               'remote-test status JOB_ID   # profile is saved automatically when the job passes',
                               'Afterwards: remote-test run [--profile NAME]'])
        print(json.dumps(out, indent=2)); return
    if args.action == 'profile' and args.op in ('list', 'default', 'delete'):
        profiles = Profiles(git_root(args.repo)); data = profiles.load()
        if args.op != 'list' and not args.name: raise ValueError('Profile name required')
        if args.op == 'default':
            if args.name not in data['profiles']: raise ValueError('Unknown profile ' + args.name)
            data['default'] = args.name; profiles.path.write_text(json.dumps(data, indent=2))
        if args.op == 'delete': data = profiles.delete(args.name)
        print(json.dumps(dict(data, file=str(profiles.path)), indent=2)); return
    client = Client()
    if args.action == 'profile':
        if not (args.name and args.from_job): raise ValueError('Usage: remote-test profile save NAME --from-job JOB_ID')
        out = client.save_from_job(args.name, args.from_job, git_root(args.repo))
    elif args.action == 'run': out = client.run(args)
    elif args.action == 'submit': out = client.submit(args)
    elif args.action == 'list': out = client.api('GET', f'/jobs?limit={args.limit}')
    elif args.action == 'status': out = client.status(args.job_id, args.live)
    elif args.action == 'cancel': out = client.api('POST', f'/jobs/{urllib.parse.quote(args.job_id)}/cancel')
    elif args.action == 'nodes': out = client.api('GET', '/nodes')
    elif args.action == 'whoami': out = client.api('GET', '/whoami')
    else: out = client.api('POST', '/tick')
    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    try: main()
    except FileNotFoundError as error:
        print(f'Missing configuration {CONFIG}; run the team installer. ({error})', file=sys.stderr); sys.exit(125)
    except Exception as error:
        print(str(error), file=sys.stderr); sys.exit(125)
