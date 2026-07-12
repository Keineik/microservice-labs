"""Locust load test for the read/search endpoints (assignment BT1).

Run via `make load` then open http://localhost:8089, or headless:
    locust -f load/locustfile.py --host http://localhost:8000 \
           --users 50 --spawn-rate 10 --run-time 1m --headless
"""

import random

from locust import HttpUser, between, task

# Matches the seed volume (150 students / 100 courses).
MAX_STUDENT_ID = 150
MAX_COURSE_ID = 100


class EnrollmentApiUser(HttpUser):
    wait_time = between(0.5, 2.0)

    @task(3)
    def list_students(self) -> None:
        self.client.get("/api/v1/students?page=1&size=20", name="GET /students [list]")

    @task(2)
    def search_students(self) -> None:
        self.client.get("/api/v1/students?search=a", name="GET /students [search]")

    @task(3)
    def get_student(self) -> None:
        sid = random.randint(1, MAX_STUDENT_ID)
        self.client.get(f"/api/v1/students/{sid}", name="GET /students/{id}")

    @task(2)
    def list_courses(self) -> None:
        self.client.get("/api/v1/courses?page=1&size=20", name="GET /courses [list]")

    @task(1)
    def student_enrollments(self) -> None:
        sid = random.randint(1, MAX_STUDENT_ID)
        self.client.get(
            f"/api/v1/students/{sid}/enrollments", name="GET /students/{id}/enrollments"
        )
