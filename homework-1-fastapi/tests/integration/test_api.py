"""End-to-end tests exercising the real routers/services/repositories over an
in-memory database."""


async def _make_student(client, code="SV0001", email="sv0001@univ.edu"):
    return await client.post(
        "/api/v1/students",
        json={"student_code": code, "full_name": "Nguyen Van A", "email": email},
    )


async def test_create_list_and_get_student(client):
    resp = await _make_student(client)
    assert resp.status_code == 201
    body = resp.json()
    assert body["id"] > 0
    assert body["student_code"] == "SV0001"

    got = await client.get(f"/api/v1/students/{body['id']}")
    assert got.status_code == 200

    listed = await client.get("/api/v1/students?page=1&size=10")
    assert listed.status_code == 200
    assert listed.json()["total"] == 1


async def test_duplicate_student_code_is_409_problem(client):
    assert (await _make_student(client)).status_code == 201
    dup = await _make_student(client, email="other@univ.edu")  # same code
    assert dup.status_code == 409
    assert dup.headers["content-type"].startswith("application/problem+json")
    assert dup.json()["status"] == 409


async def test_missing_student_is_404_problem(client):
    resp = await client.get("/api/v1/students/999999")
    assert resp.status_code == 404
    body = resp.json()
    assert body["status"] == 404
    assert body["type"]  # RFC 7807 members present


async def test_bad_payload_is_422_problem(client):
    resp = await client.post("/api/v1/students", json={"full_name": "missing code"})
    assert resp.status_code == 422
    assert resp.headers["content-type"].startswith("application/problem+json")


async def test_enrollment_is_idempotent(client):
    student = (await _make_student(client)).json()
    course = (
        await client.post(
            "/api/v1/courses",
            json={"course_code": "CS101", "title": "Intro", "credits": 3},
        )
    ).json()

    payload = {"student_id": student["id"], "course_id": course["id"], "semester": "2025-1"}
    headers = {"Idempotency-Key": "key-123"}

    first = await client.post("/api/v1/enrollments", json=payload, headers=headers)
    second = await client.post("/api/v1/enrollments", json=payload, headers=headers)

    assert first.status_code == 201
    assert second.status_code == 201
    # Same key -> same resource, not a duplicate row.
    assert first.json()["id"] == second.json()["id"]


async def test_duplicate_enrollment_without_key_is_409(client):
    student = (await _make_student(client)).json()
    course = (
        await client.post(
            "/api/v1/courses",
            json={"course_code": "CS101", "title": "Intro", "credits": 3},
        )
    ).json()
    payload = {"student_id": student["id"], "course_id": course["id"], "semester": "2025-1"}

    assert (await client.post("/api/v1/enrollments", json=payload)).status_code == 201
    clash = await client.post("/api/v1/enrollments", json=payload)
    assert clash.status_code == 409


async def test_enroll_missing_course_is_404(client):
    student = (await _make_student(client)).json()
    payload = {"student_id": student["id"], "course_id": 4242, "semester": "2025-1"}
    resp = await client.post("/api/v1/enrollments", json=payload)
    assert resp.status_code == 404
