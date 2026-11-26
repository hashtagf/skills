"""Pure scheduling/validation rules for the team queue (no I/O; unit-tested)."""
import hashlib, json, math, re, shlex, time, uuid

TERMINAL = {'passed', 'failed', 'cancelled', 'error'}
ACTIVE = {'queued', 'running'}
DEFAULTS = {'slots': 2, 'cpu_budget': 12, 'memory_gb_budget': 12}
HEARTBEAT_STALE = 600        # seconds without agent heartbeat => error, never replay
REPUBLISH_AFTER = 600        # queued this long with no claim => publish again (idempotent)
BOOT_CAP = 6900              # GCE max run duration is 7200; leave collection margin
SOURCE_FILES = ('source.bundle', 'worktree.tar.gz', 'snapshot.json')
NODE_RE = r'[a-z0-9][a-z0-9-]{0,62}'
UP = {'PROVISIONING', 'STAGING', 'RUNNING'}


class Invalid(ValueError):
    pass


def validate(p, cfg=DEFAULTS):
    """Normalize a submission. Mirrors the single-user queue's rules."""
    def need(cond, msg):
        if not cond: raise Invalid(msg)
    timeout, cpus, mem = p.get('timeout', 3600), p.get('cpus', 6), p.get('memory_gb', 6)
    for v in (timeout, cpus, mem):
        need(type(v) is int, 'timeout/cpus/memory_gb must be integers')
    need(1 <= timeout <= 6000 and cpus >= 1 and mem >= 1, 'timeout must be 1..6000; resources must be positive')
    exclusive = bool(p.get('exclusive'))
    reason = p.get('exclusive_reason')
    image = p.get('image')
    shell = p.get('shell') or 'bash'
    mongo = p.get('mongo')
    cache_go = bool(p.get('cache_go'))
    packages = p.get('go_packages')
    toolchain = p.get('go_toolchain')
    command = p.get('command')
    need(shell in ('bash', 'sh'), 'shell must be bash or sh')
    need(exclusive or (cpus <= cfg['cpu_budget'] and mem <= cfg['memory_gb_budget']),
         'Job exceeds configured budget; choose smaller limits or --exclusive')
    need(not exclusive or (isinstance(reason, str) and len(reason.strip()) >= 12),
         '--exclusive requires --exclusive-reason describing the host resource; use --mongo for MongoDB or --image for a compiler image')
    need(exclusive or not reason, '--exclusive-reason requires --exclusive')
    need(not image or (not exclusive and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_./:@-]*', image)),
         '--image requires container mode and a valid image reference')
    need(mongo in (None, '6', '7', '8'), 'mongo must be 6, 7 or 8')
    need(not toolchain or re.fullmatch(r'go1\.[0-9]+\.[0-9]+', toolchain), 'Use exact Go toolchain, e.g. go1.25.5')
    need(not toolchain or packages, '--go-toolchain requires --go-packages')
    need(not (exclusive and (mongo or cache_go or packages)), 'Managed integration/cache require container mode, not --exclusive')
    need(not mongo or (cpus >= 2 and mem >= 2), 'Mongo service requires at least 2 CPUs / 2 GiB total job budget')
    if packages:
        need(not command, 'Use --go-packages or --command, not both')
        need(isinstance(packages, list) and packages, 'go_packages must be a nonempty list')
        need(all(isinstance(x, str) and re.fullmatch(r'[A-Za-z0-9_./-]+', x) and not x.startswith('-') for x in packages), 'Invalid Go package path')
        quoted = ' '.join(shlex.quote(x) for x in packages)
        duration = p.get('test_timeout', 300)
        need(type(duration) is int and 1 <= duration <= timeout, 'Test timeout must fit job timeout')
        command = 'set -euo pipefail; ' + ('export GOTOOLCHAIN=' + toolchain + '; ' if toolchain else '') + '; '.join(
            'printf %s ' + stage + ' > .remote-test-stage; ' + c for stage, c in [
                ('build', 'go build ' + quoted), ('vet', 'go vet ' + quoted),
                ('test', 'go test -count=1 -timeout=' + str(duration) + 's -json ' + quoted)])
        cache_go = True
    need(isinstance(command, str) and command.strip(), 'Provide --command or --go-packages')
    need(len(command) <= 20000, 'Command too long')
    strict_requested = bool(p.get('strict'))
    return dict(command=command, timeout=timeout, cpus=cpus, memory_gb=mem, exclusive=exclusive,
                exclusive_reason=reason, container_image=image, shell=shell, mongo=mongo, cache_go=cache_go,
                go_toolchain=toolchain, strict=bool(packages or strict_requested), strict_requested=strict_requested)


def new_job_id(now=None):
    return time.strftime('%Y%m%d-%H%M%S', time.gmtime(now or time.time())) + '-' + uuid.uuid4().hex[:8]


def fingerprint(spec, source_sha, repo_key):
    keys = ('command', 'timeout', 'cpus', 'memory_gb', 'exclusive', 'mongo', 'cache_go', 'container_image', 'shell', 'strict', 'strict_requested')
    digest = hashlib.sha256(source_sha.encode())
    digest.update(json.dumps(dict({k: spec[k] for k in keys}, repo=repo_key), sort_keys=True).encode())
    return digest.hexdigest()


def safe_name(email):
    return re.sub(r'[^a-z0-9._-]', '_', email.lower())[:80] or 'unknown'


def source_prefix_ok(prefix, email):
    """Submitters may only reference uploads under their own prefix."""
    return isinstance(prefix, str) and re.fullmatch(r'uploads/' + re.escape(safe_name(email)) + r'/[0-9a-f]{32}', prefix) is not None


def eligible(job, active, cfg=DEFAULTS):
    """Whether a node with `active` specs may start `job` now."""
    if any(x['exclusive'] for x in active): return False
    if job['exclusive']: return not active
    if len(active) >= cfg['slots']: return False
    if sum(x['cpus'] for x in active) + job['cpus'] > cfg['cpu_budget']: return False
    return sum(x['memory_gb'] for x in active) + job['memory_gb'] <= cfg['memory_gb_budget']


def can_cancel(job, caller, admins):
    return caller == job.get('submitter') or caller in admins


def plan_starts(nodes, states, jobs, cfg=DEFAULTS):
    """Which stopped nodes to start. nodes: ordered list (first = exclusive host);
    states: node_id -> GCE status; jobs: job docs. Packs running nodes first."""
    queued = sorted((j for j in jobs if j['status'] == 'queued' and not j.get('cancel')), key=lambda j: j['created'])
    normal = [j for j in queued if not j['exclusive']]
    exclusive_waiting = any(j['exclusive'] for j in queued)
    running = [j for j in jobs if j['status'] == 'running']
    primary = nodes[0]['id']
    free = 0
    for n in nodes:
        if states.get(n['id']) not in UP: continue
        if n['id'] == primary and exclusive_waiting: continue  # drains for the exclusive job
        on_node = [j for j in running if j.get('node_id') == n['id']]
        if any(j['exclusive'] for j in on_node): continue
        free += max(0, cfg['slots'] - len(on_node))
    starts = []
    if exclusive_waiting and states.get(primary) == 'TERMINATED':
        starts.append(primary)
    need = math.ceil(max(0, len(normal) - free) / cfg['slots'])
    for n in nodes:
        if need <= 0: break
        if n['id'] in starts or states.get(n['id']) != 'TERMINATED': continue
        if n['id'] == primary and exclusive_waiting: continue
        starts.append(n['id']); need -= 1
    return starts


def stale_running(jobs, now):
    return [j for j in jobs if j['status'] == 'running' and now - (j.get('heartbeat') or j.get('started') or 0) > HEARTBEAT_STALE]


def republish(jobs, now):
    return [j for j in jobs if j['status'] == 'queued' and not j.get('cancel')
            and now - max(j.get('published') or 0, j['created']) > REPUBLISH_AFTER]


def boot_allows(uptime, timeout):
    return uptime + timeout + 600 < BOOT_CAP


def view(doc):
    """Client-facing job summary."""
    spec = json.loads(doc.get('data') or '{}')
    out = dict(job_id=doc['_id'], status=doc['status'], cancel_requested=bool(doc.get('cancel')),
               submitter=doc.get('submitter'), node_id=doc.get('node_id'), project=spec.get('project'),
               head=spec.get('head'), exclusive=spec.get('exclusive', False), exclusive_reason=spec.get('exclusive_reason'),
               command=spec.get('command'), error=doc.get('error'), created=doc.get('created'),
               submitted_seconds_ago=round(time.time() - doc.get('created', time.time()), 1))
    if doc.get('result'): out['result'] = json.loads(doc['result'])
    if doc.get('progress'): out['progress'] = json.loads(doc['progress'])
    return out
