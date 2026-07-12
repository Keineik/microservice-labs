"""End-to-end tests over the real routers/services/repositories on an in-memory
database (see the `sample` fixture in conftest.py for the dataset)."""


async def _register(client, student_id, offering_id, key=None):
    headers = {"Idempotency-Key": key} if key else {}
    return await client.post(
        "/api/v1/enrollments",
        json={"student_id": student_id, "offering_id": offering_id},
        headers=headers,
    )


async def test_browse_offerings_and_terms(client, sample):
    r = await client.get(f"/api/v1/offerings?term_id={sample['term']}")
    assert r.status_code == 200
    off = next(o for o in r.json()["items"] if o["id"] == sample["off"])
    assert off["available_seats"] == 1
    assert off["can_register"] is True

    terms = (await client.get("/api/v1/terms")).json()
    open_term = next(t for t in terms if t["id"] == sample["term"])
    assert open_term["is_registration_open"] is True


async def test_register_success_decrements_seats(client, sample):
    assert (await _register(client, sample["s1"], sample["off"])).status_code == 201
    detail = (await client.get(f"/api/v1/offerings/{sample['off']}")).json()
    assert detail["available_seats"] == 0
    assert detail["can_register"] is False


async def test_offering_full_is_409(client, sample):
    assert (await _register(client, sample["s1"], sample["off"])).status_code == 201
    r = await _register(client, sample["s2"], sample["off"])  # capacity is 1
    assert r.status_code == 409
    assert r.headers["content-type"].startswith("application/problem+json")


async def test_duplicate_registration_is_409(client, sample):
    assert (await _register(client, sample["s1"], sample["off2"])).status_code == 201
    assert (await _register(client, sample["s1"], sample["off2"])).status_code == 409


async def test_idempotent_registration_returns_same_row(client, sample):
    r1 = await _register(client, sample["s1"], sample["off2"], key="reg-1")
    r2 = await _register(client, sample["s1"], sample["off2"], key="reg-1")
    assert r1.status_code == 201 and r2.status_code == 201
    assert r1.json()["id"] == r2.json()["id"]


async def test_schedule_clash_is_409(client, sample):
    assert (await _register(client, sample["s1"], sample["off"])).status_code == 201
    r = await _register(client, sample["s1"], sample["off2"])  # overlaps off on MON
    assert r.status_code == 409


async def test_registration_closed_term_is_409(client, sample):
    r = await _register(client, sample["s1"], sample["off_closed"])
    assert r.status_code == 409


async def test_register_unknown_offering_is_404(client, sample):
    r = await _register(client, sample["s1"], 999999)
    assert r.status_code == 404


async def test_cancel_frees_seat_and_second_cancel_404(client, sample):
    reg = await _register(client, sample["s1"], sample["off"])
    enrollment_id = reg.json()["id"]

    dropped = await client.delete(f"/api/v1/enrollments/{enrollment_id}")
    assert dropped.status_code == 204

    detail = (await client.get(f"/api/v1/offerings/{sample['off']}")).json()
    assert detail["available_seats"] == 1  # seat freed

    again = await client.delete(f"/api/v1/enrollments/{enrollment_id}")
    assert again.status_code == 404  # no longer an active registration


async def test_student_enrollments_and_schedule(client, sample):
    await _register(client, sample["s1"], sample["off"])

    enrollments = (await client.get(f"/api/v1/students/{sample['s1']}/enrollments")).json()
    assert len(enrollments) == 1
    assert enrollments[0]["offering"]["course"]["course_code"] == "CS101"

    schedule = (
        await client.get(f"/api/v1/students/{sample['s1']}/schedule?term_id={sample['term']}")
    ).json()
    assert len(schedule) == 1
    assert schedule[0]["day_of_week"] == "MON"


async def test_validation_error_is_422_problem(client, sample):
    r = await client.post("/api/v1/enrollments", json={"student_id": sample["s1"]})
    assert r.status_code == 422
    assert r.headers["content-type"].startswith("application/problem+json")
