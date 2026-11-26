# Test strategy

## Go + MongoDB

From a trusted Git root, after selecting scope from project instructions:

```sh
remote-test submit --repo /absolute/project \
  --mongo 7 --go-packages ./controller/... --go-toolchain go1.25.5 \
  --test-timeout 300 --timeout 1200 --cpus 6 --memory-gb 6
```

Versions/package paths above are examples. The generated command runs build,
vet, then `go test -count=1 -timeout=300s -json`; a failed stage stops later stages
and preserves its exit code. Choose focused packages during edits, then submit
`--go-packages ./...` when the full gate is required and prerequisites pass.
Do not run focused and full suites simultaneously for the same unchanged source
merely to fill CPU. `--command` and `--go-packages` are mutually exclusive.

`--mongo` creates a unique service and network per job with no published host
port, a 60-second readiness deadline, a 1-CPU / 1-GiB cap and job-scoped cleanup.
The URI is `mongodb://127.0.0.1:27017` (the app shares only its own
Mongo sidecar network namespace, not the host or another job), exposed as MONGO_URI, MONGODB_ENDPOINT,
LOGIN_TEST_MONGO_URI, TEST_MONGO_URI and MONGO_TEST_URI. Verify the project's test
configuration actually reads one of these names. This is disposable test data.
Other services and commands that need Docker still require host-exclusive mode.
Do not merely remove `--exclusive` from commands that invoke Docker.

Custom container commands may combine `--mongo` and `--cache-go`. Go profiles use bash errexit/pipefail. Custom commands preserve their own shell
error handling; opt in with `--strict` when appropriate. Do not force errexit on
a command that captures PIPESTATUS after a filter: grep may return 1 for empty
output even when the test succeeded. Do not pipe test output through grep/head
for the test result; inspect the collected full log afterward. The Go profile
avoids these lossy pipelines.

## Cache and measurement

Go profiles automatically use a persistent module/compiler cache. Custom commands
opt in with `--cache-go`. The cache key includes repository path, execution image,
explicit toolchain and go.mod/go.sum bytes. Test results are not cached by the
profile (`-count=1`), and databases are always fresh. Do not put credentials in
cache paths or override GOCACHE/GOMODCACHE/GOPATH when expecting this cache.
Caches are per VM, not synchronized between nodes; cleanup is manual.

`status ID --live` reads progress stage, elapsed time and log silence; silence
alone does not prove a hang. Overall job timeout covers remote setup and test
execution; image preparation/upload remain separate. Go's timeout applies per
package, while the outer timeout bounds the entire job. Readiness and cancellation
also clean up the job's service.

Results include elapsed execution time, enqueue-to-executor delay, cache key,
cleanup errors and sampled peak CPU/memory for the test container plus services.
CPU percentage is per core (100% = one core); these are periodic samples, not
continuous peak guarantees. Short jobs can have no useful resource sample.

Start at 2 jobs/node and 6 CPU / 6 GiB total per job. Increase only after observing
representative runtime, memory, failures and queue wait; a brief CPU trough is
not evidence of spare sustained capacity. No CPU-based automatic overcommit.


## Avoid unnecessary exclusive jobs

For a legacy compiler image, use a normal capped container directly:

```sh
remote-test submit --repo /absolute/project \
  --image golang:1.19.2-alpine3.16 --shell sh --cache-go \
  --command 'export CGO_ENABLED=0; go build ./...; go test -count=1 -timeout=5m ./...'
```

Pin the actual required image/version and confirm its selected shell exists.
The cwd is /workspace. Compiler image selection is not a host-exclusive need.
Do not wrap this in another `docker run`. Keep test scope project-specific.

`--exclusive` requires `--exclusive-reason` describing concrete host integration,
hardware, or conflicting resources. A broad job or old habit is not a reason.
Exclusive jobs still run alone on their node; low sampled CPU cannot override
that promise. Use bounded readiness/test deadlines to avoid holding a node
indefinitely, and inspect progress before calling a quiet test hung.

To change an already-queued job, cancel it (your own) and submit the corrected
job; do not rewrite running jobs or reinterpret an existing receipt.
