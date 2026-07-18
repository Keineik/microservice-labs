"""Seed realistic synthetic data for the course-registration system.

Creates students, a catalog of courses, three terms (two past + one with
registration currently OPEN), course offerings (sections with schedules), and
enrollments split into COMPLETED (past, graded) and REGISTERED (current).
Idempotent: re-running is a no-op once seeded.

Run:  python scripts/seed_data.py   (inside the api container: `make seed`)
"""

import asyncio
import random
from datetime import UTC, datetime, time, timedelta

from faker import Faker
from sqlalchemy import func, select

from app.db.session import SessionLocal, engine
from app.models import Course, CourseOffering, Enrollment, Student, Term

fake = Faker()

N_STUDENTS = 150
N_COURSES = 100
OFFERINGS_PER_TERM = 50
DAYS = ["MON", "TUE", "WED", "THU", "FRI"]
SLOTS = [time(8, 0), time(9, 30), time(13, 0), time(14, 30), time(16, 0)]
DEPARTMENTS = ["Computer Science", "Mathematics", "Physics", "Electronics", "Business"]
MAJORS = ["Software Engineering", "Data Science", "Information Systems", "AI", "Networks"]


def _slot_end(start: time) -> time:
    minutes = start.hour * 60 + start.minute + 90
    return time(minutes // 60, minutes % 60)


async def seed() -> None:
    async with SessionLocal() as db:
        if (await db.execute(select(func.count()).select_from(Student))).scalar_one():
            print("Database already seeded. Nothing to do.")
            return

        # Deterministic data: a fresh reseed always yields the same rows, so the
        # demo/notebook can hardcode ids (e.g. student 1 registers for offering 101).
        random.seed(42)
        Faker.seed(42)

        now = datetime.now(UTC)
        today = now.date()

        terms = [
            Term(
                code="2024-2",
                name="Fall 2024 (past)",
                starts_on=today - timedelta(days=360),
                ends_on=today - timedelta(days=260),
                registration_starts_at=now - timedelta(days=380),
                registration_ends_at=now - timedelta(days=362),
            ),
            Term(
                code="2025-1",
                name="Spring 2025 (past)",
                starts_on=today - timedelta(days=180),
                ends_on=today - timedelta(days=80),
                registration_starts_at=now - timedelta(days=200),
                registration_ends_at=now - timedelta(days=182),
            ),
            Term(
                code="2025-2",
                name="Fall 2025 (current — registration open)",
                starts_on=today - timedelta(days=10),
                ends_on=today + timedelta(days=100),
                registration_starts_at=now - timedelta(days=14),
                registration_ends_at=now + timedelta(days=28),
            ),
        ]
        past_terms = terms[:-1]
        current_term = terms[-1]

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
                description=fake.sentence(),
            )
            for i in range(1, N_COURSES + 1)
        ]
        db.add_all(terms)
        db.add_all(students)
        db.add_all(courses)
        await db.flush()

        offerings: list[CourseOffering] = []
        for term in terms:
            for course in random.sample(courses, OFFERINGS_PER_TERM):
                start = random.choice(SLOTS)
                offerings.append(
                    CourseOffering(
                        course_id=course.id,
                        term_id=term.id,
                        section_no="01",
                        capacity=random.choice([30, 40, 50, 60]),
                        instructor=fake.name(),
                        status="CLOSED" if random.random() < 0.05 else "OPEN",
                        day_of_week=random.choice(DAYS),
                        start_time=start,
                        end_time=_slot_end(start),
                        room=f"R{random.randint(100, 499)}",
                    )
                )
        db.add_all(offerings)
        await db.flush()

        by_term: dict[int, list[CourseOffering]] = {
            t.id: [o for o in offerings if o.term_id == t.id] for t in terms
        }
        reg_count: dict[int, int] = {o.id: 0 for o in offerings}
        enrollments: list[Enrollment] = []

        for student in students:
            # Past terms -> COMPLETED with a grade (0-10 scale).
            for term in past_terms:
                for offering in random.sample(by_term[term.id], k=random.randint(3, 5)):
                    enrollments.append(
                        Enrollment(
                            student_id=student.id,
                            offering_id=offering.id,
                            status="COMPLETED",
                            grade=round(random.uniform(4.0, 10.0), 1),
                        )
                    )
            # Current term -> REGISTERED, on distinct days, respecting capacity.
            target = random.randint(2, 4)
            used_days: set[str] = set()
            added = 0
            for offering in random.sample(
                by_term[current_term.id], k=len(by_term[current_term.id])
            ):
                if added >= target:
                    break
                if offering.status != "OPEN" or offering.day_of_week in used_days:
                    continue
                if reg_count[offering.id] >= offering.capacity:
                    continue
                enrollments.append(
                    Enrollment(student_id=student.id, offering_id=offering.id, status="REGISTERED")
                )
                used_days.add(offering.day_of_week)
                reg_count[offering.id] += 1
                added += 1

        db.add_all(enrollments)
        await db.commit()

        print(
            f"Seeded {len(students)} students, {len(courses)} courses, {len(terms)} terms, "
            f"{len(offerings)} offerings, {len(enrollments)} enrollments."
        )
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
