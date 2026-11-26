---
name: remote-test
description: Submit project tests to the team's shared Google Cloud VM pool queue (Pub/Sub + Firestore), run isolated MongoDB integration and Go test profiles, check status, cancel, replay, and collect results. Use for remote tests, queue/job status, cancellation, replay or VM test performance comparisons across projects.
---

# Remote test (team queue)

`remote-test` sends a snapshot of a trusted Git repository to the team's shared
Linux VM pool. Everyone on the team uses the same queue and the same five VMs.
Nodes start automatically when work is queued and power themselves off when
drained. Your Mac only uploads and reads results; it can sleep after submitting.

## Select the operation

- **Run:** A request to run tests remotely authorizes one submission and result
  retrieval. Do not ask again for the same permission.
- **Status/results/plan:** Inspect only (`list`, `status`, `nodes`). Do not submit
  work just to answer a status, planning or pricing question.
- **Replay/compare:** `--replay-run JOB_ID` reruns the exact uploaded source.
- **Cancel:** Only your own jobs (admins may cancel any). Cancel only what the
  user asked for or what the current task owns.

Discovering this skill is not permission to move an otherwise local test task to
paid cloud compute. Follow the user's requested execution location.

## First-time install (once per Mac)

If `remote-test` is not on PATH (`command -v remote-test`), install the CLI
bundled with this skill. It needs the team's `team.json` from the queue admin
(API URL + bucket); never invent one.

```sh
gcloud auth login                                   # company account
bash <this skill>/scripts/install.sh /path/to/team.json
remote-test whoami                                  # 403 = not in the access group
```

The queue backend (Cloud Run API, Firestore, Pub/Sub, node agents) is deployed
separately by the admin; this skill only ships the client.

## Fast path: saved profiles (setup once per repo)

Profiles are per user and per repository (same origin URL = same repo across
clones/worktrees), stored in `~/.config/remote-test/projects/`, never in the repo.

1. `remote-test profile list --repo /abs/repo` — if a suitable profile exists,
   just run it: `remote-test run --repo /abs/repo [--profile full]`.
   Overrides allowed: `--timeout`, `--cpus`, `--memory-gb`.
2. **Setup mode** (user says "setup remote-test" / no profile yet):
   - `remote-test setup --repo /abs/repo` prints detected commands, hints
     (Mongo, Playwright, Go toolchain, CI files) and existing profiles. These are
     heuristics: confirm against README/agent instructions/CI before using.
   - Submit the chosen command once with `--save-profile quick` (and later a
     `full` gate if the project has one). Check `remote-test status JOB_ID` at
     checkpoints; the profile is saved automatically only when the job **passes**.
   - If it fails, read `test.log`, fix the command/flags (not the tests), and
     resubmit with `--save-profile` again. Never save a failing configuration.
   - A passed job submitted without the flag can be saved later:
     `remote-test profile save NAME --from-job JOB_ID --repo /abs/repo`.
   - `remote-test profile default NAME` / `profile delete NAME` manage them.
3. Report which profile ran. If the project's test setup changed (new service,
   new script), redo setup for that profile instead of patching around failures.

## Prepare a run

1. Resolve the Git root/worktree and read its agent instructions, test docs and
   CI commands. Preserve local changes. Use focused checks while editing and
   the full gate when required.
2. Choose a **non-interactive Linux** command. The container image has Node 24
   (Node 22 cached), Corepack/pnpm/Yarn, Bun, Go, Python 3/uv, Ruby, build tools,
   browser OS libraries and Xvfb. Install pinned project dependencies inside the
   command. Browser binaries must match the project's Playwright version.
   Do not claim support for macOS-only checks, production services or unknown
   dependencies.
3. State the command, scope and resources, then submit **once**. A busy pool is
   not a reason to resubmit; jobs wait in FIFO order (approximate across nodes).

## Submit

```sh
remote-test submit --repo /absolute/project/path \
  --timeout 3600 --cpus 6 --memory-gb 6 \
  --command 'npm ci && npm test'
```

The npm command is an example, not a default. Quote the whole command as one
argument; never interpolate untrusted text. `--repo` must be the Git root; for a
monorepo put `cd package &&` inside the command. Timeout is 1..6000 seconds.

Submission snapshots the repo **now** (HEAD bundle + tracked and untracked
non-ignored files), uploads it and returns a Job ID. An identical active
submission by you returns the existing ID. Default capacity: two 6-CPU / 6-GiB
container jobs per node, ten across the pool. Each job runs in its own Docker
container, workspace and network with CPU/memory caps and no host Docker socket.

- `--mongo 6|7|8`: private MongoDB sidecar at `mongodb://127.0.0.1:27017`
  (exported as MONGO_URI, MONGODB_ENDPOINT, TEST_MONGO_URI, MONGO_TEST_URI,
  LOGIN_TEST_MONGO_URI). Needs ≥2 CPU / 2 GiB; 1/1 goes to MongoDB.
- `--go-packages ./... [--go-toolchain go1.x.y] [--test-timeout 300]`: build → vet
  → test with preserved exit codes and a Go cache.
- `--image IMAGE --shell bash|sh`: run in a pinned toolchain image instead.
- `--exclusive --exclusive-reason "specific host resource"`: whole node on the
  first VM, for Docker Compose/host Docker. It waits until that node drains.
  Needing a database or compiler version is not a reason.

See [test strategy](references/testing.md) for profiles and caching.

## Status, results, cancel

```sh
remote-test list
remote-test status JOB_ID          # add --live for stage/elapsed/log silence
remote-test cancel JOB_ID
remote-test nodes                  # VM state and running jobs per node
```

Never write `while`/`until` polling loops or waiting shells. Report queued/running
as pending, never passed. If the task is only submission, return the Job ID.
If completion is requested, check status at reasonable checkpoints.

When finished, `status` downloads results to
`~/.local/share/remote-test/runs/JOB_ID/results/`. Read `result.json` **and**
`test.log`. Report command scope, snapshot commit (`head`), outcome, duration
and evidence paths. Nonzero exit is a failure; `error` status, exit 125 or a
missing receipt is an execution problem, not a pass. A heartbeat-lost job is
marked `error` and is never replayed automatically. Do not attach a pass from a
different commit or older snapshot to the current worktree.

Cancelling a queued job is immediate; cancelling a running job is a request
until its status becomes `cancelled`.

## Source and safety boundaries

- No commit or push is needed. The snapshot omits `.env*` (except
  example/sample/template), common key/credential files, `node_modules`, `.venv`
  and `.foundation` state, but it **includes Git history (HEAD and tags)**. It is
  not a secret scanner. Never submit a repository with committed secrets, and
  never upload credentials to make a test pass.
- Uploads and results live in a team bucket for 30 days and are readable by the
  whole team. Treat them as shared.
- Submodules and symlinks escaping the repository are refused. Git LFS content
  and extra artifacts (screenshots, coverage) are not collected automatically.
- The pool is a trusted-team host, not a security boundary between untrusted
  projects. Tests cannot reach the VM's cloud credentials.
- VM time costs money. Do not rerun full suites just to demonstrate the tool.

## Troubleshooting

- `gcloud authentication failed`: run `gcloud auth login` with your company account.
- `Queue API 403`: you are not in the team Google Group; ask the admin.
- `Missing configuration`: rerun the team installer.
