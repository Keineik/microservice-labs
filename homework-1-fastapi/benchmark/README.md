# BT1 benchmark: sync (Flask) vs async (FastAPI)

Goal: show how the **concurrency model** affects performance on I/O-bound DB
reads. Same database, same queries, same serialization, same connection pool —
the only variable is sync (Flask/WSGI, blocks a worker per request) vs async
(FastAPI/ASGI, one event loop overlaps many in-flight I/O waits). Driven from
the **Locust web UI** so you can control the load and screenshot the charts.

## Files

- `bench_common.py` - shared SQLAlchemy statements + serialization (imports the
  real `app.models`). Both apps use these, so payloads are byte-identical.
- `bench_async.py` - FastAPI + async SQLAlchemy + asyncpg (uvicorn).
- `bench_sync.py` - Flask + sync SQLAlchemy + psycopg2 (gunicorn sync workers).
- `locustfile.py` - one load test for either app; tags pick the scenario.

Both apps expose the same paths: `/offerings`, `/offerings/{id}`,
`/students/{id}/enrollments`, `/courses`, and `/io?seconds=` (a `pg_sleep`
endpoint used to isolate the effect; default 100ms).

## Run it (Docker Compose + Locust UI)

```bash
make up && make seed     # builds the image (with bench deps) + seeds Postgres
make bench-up            # bench-async :9001, bench-sync :9002, Locust UI :8089
```

Then open the Locust UI at <http://localhost:8089> and, for each app:

1. Set **Host** to `http://bench-async:9001` (async) or `http://bench-sync:9002`
   (sync) — these are the compose service names, resolvable from the Locust
   container.
2. Set number of users (e.g. 200) and spawn rate (e.g. 20), start swarming.
3. Watch the **Charts** tab (RPS, response times, users). Screenshot it for the
   report (async run and sync run, same settings).

Scenario tag defaults to `io` (the clincher). Switch scenarios / sync workers by
recreating the stack:

```bash
BENCH_TAGS=read make bench-up        # realistic read scenario
WEB_CONCURRENCY=4 make bench-up      # 4 workers for BOTH async (uvicorn) and sync (gunicorn)
make bench-down                      # stop
```

## What is held constant (fairness)

- Same Postgres, same seed data, same SQL (shared statements), same indexes.
- **High pool, not a bottleneck** (`BENCH_POOL_SIZE`, default 100) and
  `max_overflow=0` on both, so the ceiling comes from the concurrency model + CPU,
  not an artificially small pool. Each worker process has its own pool, so total
  connections = workers x pool; Postgres `max_connections` is raised to 500 to fit.
- Same JSON payloads (shared serializer; dates/times to ISO strings).
- Same users/spawn-rate/scenario per compared pair.
- **Same CPU/memory cap on both containers** (`BENCH_CPUS` default 2, `BENCH_MEM`
  default 1g) so neither grabs more of the host. Locust is left unlimited (so the
  load generator is never the bottleneck); Postgres is shared (equal for both).
  Make sure the Colima VM has enough cores for the caps (e.g. `colima start --cpu 4`).

Only the concurrency model + worker count change.

## Suggested comparison

Four runs (async/sync x 1/4 workers), same users + scenario, screenshot each:

- `async` 1 worker (`make bench-up`, host `bench-async:9001`)
- `async` 4 workers (`WEB_CONCURRENCY=4 make bench-up`, host `bench-async:9001`)
- `sync` 1 worker (`make bench-up`, host `bench-sync:9002`)
- `sync` 4 workers (`WEB_CONCURRENCY=4 make bench-up`, host `bench-sync:9002`)

Run the `io` scenario (100ms sleep) for the headline gap, then optionally `read`
(fast queries) to show the gap shrinks when the DB/queries dominate.

## Interpreting the results

- Async wins most on **I/O-bound** work under **high concurrency**; for CPU-bound
  work or when the DB is the bottleneck, the gap shrinks (`io` vs `read` show
  both ends).
- `psycopg2` releases the GIL during network I/O, so multi-worker sync can also
  overlap I/O; async's edge is doing it in one process with far less memory.
