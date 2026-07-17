"""Locust load test for the sync-vs-async comparison.

Both benchmark apps expose the same paths, so one locustfile targets either via
--host. Tags let you pick the scenario:

  read scenario (realistic DB reads):
    locust -f benchmark/locustfile.py --host http://localhost:9001 \
           --tags read --headless -u 100 -r 20 -t 60s --csv benchmark/results/async-read

  io scenario (isolates the async advantage: each request waits on pg_sleep):
    locust -f benchmark/locustfile.py --host http://localhost:9002 \
           --tags io --headless -u 100 -r 20 -t 60s --csv benchmark/results/sync-io

wait_time is 0 so each user pushes continuously -> we measure saturation
throughput/latency, not user think-time.
"""

import os
import random

from locust import HttpUser, constant, tag, task

MAX_STUDENT_ID = 150
MAX_OFFERING_ID = 150
CURRENT_TERM_ID = 3
# DB sleep for the /io scenario (seconds). Default 300 ms; override with env.
IO_SECONDS = float(os.getenv("BENCH_IO_SECONDS", "0.3"))


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
