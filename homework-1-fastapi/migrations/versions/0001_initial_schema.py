"""initial schema: students, courses, terms, course_offerings, enrollments, idempotency_keys

Revision ID: 0001
Revises:
Create Date: 2026-07-12
"""

from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "students",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("student_code", sa.String(length=20), nullable=False),
        sa.Column("full_name", sa.String(length=200), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("major", sa.String(length=100), nullable=True),
        sa.Column("enrollment_year", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_students_student_code", "students", ["student_code"], unique=True)
    op.create_index("ix_students_email", "students", ["email"], unique=True)

    op.create_table(
        "courses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("course_code", sa.String(length=20), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("credits", sa.Integer(), nullable=False),
        sa.Column("department", sa.String(length=100), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_courses_course_code", "courses", ["course_code"], unique=True)

    op.create_table(
        "terms",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=20), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("starts_on", sa.Date(), nullable=False),
        sa.Column("ends_on", sa.Date(), nullable=False),
        sa.Column("registration_starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("registration_ends_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_terms_code", "terms", ["code"], unique=True)

    op.create_table(
        "course_offerings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.Column("term_id", sa.Integer(), nullable=False),
        sa.Column("section_no", sa.String(length=10), nullable=False),
        sa.Column("capacity", sa.Integer(), nullable=False),
        sa.Column("instructor", sa.String(length=200), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("day_of_week", sa.String(length=3), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.Column("room", sa.String(length=50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["term_id"], ["terms.id"], ondelete="CASCADE"),
        sa.UniqueConstraint(
            "course_id", "term_id", "section_no", name="uq_offering_course_term_section"
        ),
    )
    op.create_index("ix_course_offerings_course_id", "course_offerings", ["course_id"])
    op.create_index("ix_course_offerings_term_id", "course_offerings", ["term_id"])

    op.create_table(
        "enrollments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("offering_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("grade", sa.Float(), nullable=True),
        sa.Column("registered_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("dropped_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["offering_id"], ["course_offerings.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_enrollments_student_id", "enrollments", ["student_id"])
    op.create_index("ix_enrollments_offering_id", "enrollments", ["offering_id"])
    # Partial unique index: at most one ACTIVE registration per (student, offering).
    op.create_index(
        "uq_active_enrollment",
        "enrollments",
        ["student_id", "offering_id"],
        unique=True,
        postgresql_where=sa.text("status = 'REGISTERED'"),
    )

    op.create_table(
        "idempotency_keys",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("key", sa.String(length=255), nullable=False),
        sa.Column("method", sa.String(length=10), nullable=False),
        sa.Column("path", sa.String(length=500), nullable=False),
        sa.Column("status_code", sa.Integer(), nullable=False),
        sa.Column("resource_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_idempotency_keys_key", "idempotency_keys", ["key"], unique=True)


def downgrade() -> None:
    op.drop_table("idempotency_keys")
    op.drop_table("enrollments")
    op.drop_table("course_offerings")
    op.drop_table("terms")
    op.drop_table("courses")
    op.drop_table("students")
