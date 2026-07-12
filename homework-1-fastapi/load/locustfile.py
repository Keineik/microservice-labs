"""Locust load test for the read/browse endpoints (assignment BT1).

Run via `make load` then open http://localhost:8089, or headless:
    locust -f load/locustfile.py --host http://localhost:8000 \
           --users 50 --spawn-rate 10 --run-time 1m --headless
"""

import random

from locust import HttpUser, between, task

# Matches the seed volume: 150 students, 150 offerings, current term id = 3.
MAX_STUDENT_ID = 150
MAX_OFFERING_ID = 150
CURRENT_TERM_ID = 3


class RegistrationApiUser(HttpUser):
    wait_time = between(0.5, 2.0)

    @task(3)
    def browse_offerings(self) -> None:
        self.client.get(
            f"/api/v1/offerings?term_id={CURRENT_TERM_ID}&page=1&size=20",
            name="GET /offerings [browse term]",
        )

    @task(2)
    def search_offerings(self) -> None:
        self.client.get("/api/v1/offerings?search=a", name="GET /offerings [search]")

    @task(2)
    def offering_detail(self) -> None:
        oid = random.randint(1, MAX_OFFERING_ID)
        self.client.get(f"/api/v1/offerings/{oid}", name="GET /offerings/{id}")

    @task(3)
    def student_enrollments(self) -> None:
        sid = random.randint(1, MAX_STUDENT_ID)
        self.client.get(
            f"/api/v1/students/{sid}/enrollments", name="GET /students/{id}/enrollments"
        )

    @task(1)
    def student_schedule(self) -> None:
        sid = random.randint(1, MAX_STUDENT_ID)
        self.client.get(
            f"/api/v1/students/{sid}/schedule?term_id={CURRENT_TERM_ID}",
            name="GET /students/{id}/schedule",
        )

    @task(1)
    def list_courses(self) -> None:
        self.client.get("/api/v1/courses?page=1&size=20", name="GET /courses [list]")
