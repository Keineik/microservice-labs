# BT1 benchmark: sync (Flask) vs async (FastAPI)

Goal: show how the **concurrency model** affects performance on I/O-bound DB
reads. Same database, same queries, same serialization, same connection pool —
the only variable is sync (Flask/WSGI, blocks a worker per request) vs async
(FastAPI/ASGI, one event loop overlaps many in-flight I/O waits).

## Files

- `bench_common.py` - shared SQLAlchemy statements + serialization (imports the
  real `app.models`). Both apps use these, so payloads are byte-identical.
- `bench_async.py` - FastAPI + async SQLAlchemy + asyncpg (uvicorn).
- `bench_sync.py` - Flask + sync SQLAlchemy + psycopg2 (gunicorn sync workers).
- `locustfile.py` - one load test for either app; tags pick the scenario.
- `results/` - Locust CSV output + exported charts.

Both apps expose the same paths: `/offerings`, `/offerings/{id}`,
`/students/{id}/enrollments`, `/courses`, and `/io?seconds=` (a `pg_sleep`
endpoint used to isolate the effect).

## Prerequisites

```bash
make up && make seed          # Postgres (host :5432) up and seeded
uv sync --extra bench         # flask, gunicorn, psycopg2, locust
uv sync --extra analysis      # (optional) pandas, matplotlib, jupyterlab for the notebook
```

## What is held constant (fairness)

- Same Postgres, same seed data, same SQL (shared statements), same indexes.
- Same pool size (`BENCH_POOL_SIZE`, default 10) and `max_overflow=0` on both.
- Same JSON payloads (shared serializer; dates/times to ISO strings).
- Same machine; warm up before measuring; run each scenario a few times.

Only the concurrency model changes. Note: a sync app scaled to N gunicorn
workers holds N x pool_size DB connections total, while the async app holds
pool_size in one process - call that out when comparing.

## Scenarios

Start each app in its own terminal, then load-test it.

```bash
# ASYNC contender (one event loop)
make bench-async                        # FastAPI on :9001

# SYNC contender (start ONE of these)
make bench-sync                         # Flask, 1 sync worker  on :9002
WEB_CONCURRENCY=4 make bench-sync       # Flask, 4 sync workers on :9002
```

Realistic read load:

```bash
make bench-load HOST=http://localhost:9001 NAME=async-read   TAGS=read
make bench-load HOST=http://localhost:9002 NAME=sync-1w-read TAGS=read
```

I/O-isolation load (the clincher — each request waits in the DB; default 300 ms,
override with `BENCH_IO_SECONDS` or `?seconds=`):

```bash
make bench-load HOST=http://localhost:9001 NAME=async-io   TAGS=io
make bench-load HOST=http://localhost:9002 NAME=sync-1w-io TAGS=io
```

Suggested matrix: `async-1w` vs `sync-1w` (headline), plus `sync-4w` to show
sync catching up at the cost of more processes/connections. Optionally sweep
`-u` (users) to plot throughput vs concurrency.

Each run writes `results/<NAME>_stats.csv` (+ `_stats_history.csv`,
`_failures.csv`).

## Reading the results

`results/*_stats.csv` has per-endpoint and aggregated rows (request count,
failures, median/95%/99%, RPS). Compare the "Aggregated" row across runs, and
watch p95/p99 diverge as concurrency rises. Capture `docker stats` (or `top`)
during a run to record CPU/memory cost per configuration.

The `analysis.ipynb` notebook (see the project README / report §1) reads these
CSVs with pandas, plots RPS and p95 vs concurrency, exports the figures to
`../report/assets/`, and writes the analysis that feeds report section 1.

## Caveats to state in the report

- Async wins most on **I/O-bound** work under **high concurrency**; for CPU-bound
  work or when the DB is the bottleneck, the gap shrinks - the `read` vs `io`
  scenarios show both ends.
- `psycopg2` releases the GIL during network I/O, so threaded/multi-worker sync
  can also overlap I/O; async's edge is doing it in one thread with far less
  memory and context-switching.
