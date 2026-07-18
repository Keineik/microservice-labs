"""Locust load test for the sync-vs-async comparison.

Runs in the `locust-bench` container (Locust web UI on :8089). In the UI, set
Host to http://bench-async:9001 (async) or http://bench-sync:9002 (sync), pick
users + spawn rate, start swarming, and watch the Charts tab.

Both apps expose the same paths, so one locustfile targets either. The scenario
is chosen by tag on the container command (`--tags io` by default, or
`BENCH_TAGS=read make bench-up`):

  - read: realistic DB reads (fast queries).
  - io:   each request waits on pg_sleep (default 100ms) to isolate the effect.

wait_time is 0 so each user pushes continuously -> we measure saturation
throughput/latency, not user think-time.
"""

import os
import random

from locust import HttpUser, constant, tag, task

MAX_STUDENT_ID = 150
MAX_OFFERING_ID = 150
CURRENT_TERM_ID = 3
# DB sleep for the /io scenario (seconds). Default 100 ms; override with env.
IO_SECONDS = float(os.getenv("BENCH_IO_SECONDS", "0.1"))


class BenchUser(HttpUser):
    wait_time = constant(0)

    @tag("read")
    @task(3)
    def browse_offerings(self) -> None:
        self.client.get(
            f"/offerings?term_id={CURRENT_TERM_ID}&page=1&size=20",
            name="GET /offerings [browse]",
        )

    @tag("read")
    @task(2)
    def search_offerings(self) -> None:
        self.client.get("/offerings?search=a", name="GET /offerings [search]")

    @tag("read")
    @task(2)
    def offering_detail(self) -> None:
        oid = random.randint(1, MAX_OFFERING_ID)
        self.client.get(f"/offerings/{oid}", name="GET /offerings/{id}")

    @tag("read")
    @task(3)
    def student_enrollments(self) -> None:
        sid = random.randint(1, MAX_STUDENT_ID)
        self.client.get(f"/students/{sid}/enrollments", name="GET /students/{id}/enrollments")

    @tag("read")
    @task(1)
    def list_courses(self) -> None:
        self.client.get("/courses?page=1&size=20", name="GET /courses")

    @tag("io")
    @task
    def io_wait(self) -> None:
        self.client.get(f"/io?seconds={IO_SECONDS}", name="GET /io [pg_sleep]")
