"""Seed the database with realistic synthetic data.

Generates 150 students, 100 courses and ~400 enrollments (>=100 rows per table,
as the assignment requires). Idempotent: re-running is a no-op once seeded.

Run:  python scripts/seed_data.py       (inside the api container: `make seed`)
"""

import asyncio
import random

from faker import Faker
from sqlalchemy import func, select

from app.db.session import SessionLocal, engine
from app.models import Course, Enrollment, Student

fake = Faker()

N_STUDENTS = 150
N_COURSES = 100
N_ENROLLMENTS = 400
SEMESTERS = ["2024-1", "2024-2", "2025-1"]
DEPARTMENTS = [
    "Computer Science",
    "Mathematics",
    "Physics",
    "Electrical Engineering",
    "Business",
]
MAJORS = ["Software Engineering", "Data Science", "Information Systems", "AI", "Networks"]


async def seed() -> None:
    async with SessionLocal() as db:
        existing = (await db.execute(select(func.count()).select_from(Student))).scalar_one()
        if existing:
            print(f"Database already seeded ({existing} students). Nothing to do.")
            return

        students = [
            Student(
                student_code=f"SV{i:05d}",
                full_name=fake.name(),
                email=f"sv{i:05d}@univ.edu",
                major=random.choice(MAJORS),
                enrollment_year=random.randint(2020, 2025),
            )
            for i in range(1, N_STUDENTS + 1)
        ]
        courses = [
            Course(
                course_code=f"C{i:04d}",
                title=fake.catch_phrase(),
                credits=random.choice([2, 3, 3, 4]),
                department=random.choice(DEPARTMENTS),
                capacity=random.choice([30, 50, 80, 120]),
            )
            for i in range(1, N_COURSES + 1)
        ]
        db.add_all(students)
        db.add_all(courses)
        await db.flush()  # assign primary keys

        seen: set[tuple[int, int, str]] = set()
        enrollments: list[Enrollment] = []
        while len(enrollments) < N_ENROLLMENTS:
            student = random.choice(students)
            course = random.choice(courses)
            semester = random.choice(SEMESTERS)
            key = (student.id, course.id, semester)
            if key in seen:
                continue
            seen.add(key)
            enrollments.append(
                Enrollment(
                    student_id=student.id,
                    course_id=course.id,
                    semester=semester,
                    status=random.choice(["ENROLLED", "ENROLLED", "COMPLETED"]),
                )
            )
        db.add_all(enrollments)
        await db.commit()

        print(
            f"Seeded {len(students)} students, {len(courses)} courses, "
            f"{len(enrollments)} enrollments."
        )
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
