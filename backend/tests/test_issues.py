
def test_create_issue(client):
    response = client.post(
        "/api/issues",
        json={
            "title": "Checkout page crashes",
            "description": "The checkout page crashes when users submit an order.",
            "priority": "critical",
        },
    )

    assert response.status_code == 201
    data = response.get_json()
    assert data["title"] == "Checkout page crashes"
    assert data["status"] == "open"
    assert data["priority"] == "critical"
    assert "id" in data


def test_reject_issue_without_title(client):
    response = client.post(
        "/api/issues",
        json={
            "description": "The login page is failing.",
        },
    )

    assert response.status_code == 400
    assert "Title is required" in response.get_json()["error"]


def test_get_issue(client, sample_issue):
    issue_id = sample_issue["id"]

    response = client.get(f"/api/issues/{issue_id}")

    assert response.status_code == 200
    assert response.get_json()["id"] == issue_id


def test_issue_not_found(client):
    response = client.get("/api/issues/999999")

    assert response.status_code == 404


def test_update_issue(client, sample_issue):
    issue_id = sample_issue["id"]

    response = client.patch(
        f"/api/issues/{issue_id}",
        json={"status": "in_progress"},
    )

    assert response.status_code == 200
    assert response.get_json()["status"] == "in_progress"


def test_delete_issue(client, sample_issue):
    issue_id = sample_issue["id"]

    response = client.delete(f"/api/issues/{issue_id}")

    assert response.status_code == 204
    assert client.get(f"/api/issues/{issue_id}").status_code == 404

def test_partial_update_preserves_other_fields(client, sample_issue):
    issue_id = sample_issue["id"]
    original = client.get(f"/api/issues/{issue_id}").get_json()

    response = client.patch(
        f"/api/issues/{issue_id}",
        json={"status": "in_progress"},
    )

    assert response.status_code == 200
    updated = response.get_json()

    assert updated["status"] == "in_progress"
    assert updated["title"] == original["title"]
    assert updated["description"] == original["description"]
    assert updated["priority"] == original["priority"]


def test_delete_issue_then_get_returns_404(client, sample_issue):
    issue_id = sample_issue["id"]

    delete_response = client.delete(f"/api/issues/{issue_id}")
    get_response = client.get(f"/api/issues/{issue_id}")

    assert delete_response.status_code == 204
    assert get_response.status_code == 404


def test_create_issue_returns_timestamps(client):
    response = client.post(
        "/api/issues",
        json={
            "title": "Test issue with timestamps",
            "description": "Verify creation timestamps are returned.",
            "priority": "medium",
        },
    )

    assert response.status_code == 201
    data = response.get_json()

    assert data["created_at"] is not None
    assert data["updated_at"] is not None

def test_reject_blank_title(client):
    response = client.post(
        "/api/issues",
        json={
            "title": "   ",
            "description": "A valid issue description.",
        },
    )

    assert response.status_code == 400
    assert "Title is required" in response.get_json()["error"]


def test_reject_title_over_200_characters(client):
    response = client.post(
        "/api/issues",
        json={
            "title": "A" * 201,
            "description": "A valid issue description.",
        },
    )

    assert response.status_code == 400
    assert "200 characters" in response.get_json()["error"]


def test_reject_invalid_priority(client):
    response = client.post(
        "/api/issues",
        json={
            "title": "Invalid priority test",
            "description": "Testing priority validation.",
            "priority": "urgent",
        },
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Invalid issue priority."


def test_reject_invalid_status(client):
    response = client.post(
        "/api/issues",
        json={
            "title": "Invalid status test",
            "description": "Testing status validation.",
            "status": "pending",
        },
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Invalid issue status."


def test_reject_unsupported_update_field(client, sample_issue):
    response = client.patch(
        f"/api/issues/{sample_issue['id']}",
        json={"unexpected_field": "value"},
    )

    assert response.status_code == 400
    assert "Unsupported fields" in response.get_json()["error"]


def test_reject_empty_update(client, sample_issue):
    response = client.patch(
        f"/api/issues/{sample_issue['id']}",
        json={},
    )

    assert response.status_code == 400
    assert "at least one field" in response.get_json()["error"]

def test_reject_missing_description(client):
    response = client.post(
        "/api/issues",
        json={"title": "Missing description test"},
    )

    assert response.status_code == 400
    assert "Description is required" in response.get_json()["error"]


def test_reject_non_string_title(client):
    response = client.post(
        "/api/issues",
        json={
            "title": 123,
            "description": "Testing invalid title type.",
        },
    )

    assert response.status_code == 400
    assert "Title is required" in response.get_json()["error"]


def test_reject_blank_description(client):
    response = client.post(
        "/api/issues",
        json={
            "title": "Blank description test",
            "description": "   ",
        },
    )

    assert response.status_code == 400
    assert "Description is required" in response.get_json()["error"]


def test_reject_invalid_priority_on_update(client, sample_issue):
    response = client.patch(
        f"/api/issues/{sample_issue['id']}",
        json={"priority": "urgent"},
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Invalid issue priority."


def test_reject_invalid_status_on_update(client, sample_issue):
    response = client.patch(
        f"/api/issues/{sample_issue['id']}",
        json={"status": "pending"},
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Invalid issue status."

def test_create_issue_uses_default_status_and_priority(client):
    response = client.post(
        "/api/issues",
        json={
            "title": "Verify default values",
            "description": "Check the default status and priority.",
        },
    )

    assert response.status_code == 201
    data = response.get_json()
    assert data["status"] == "open"
    assert data["priority"] == "medium"


def test_create_issue_rejects_non_json_body(client):
    response = client.post(
        "/api/issues",
        data="this is not JSON",
        content_type="text/plain",
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == (
        "Request body must be a JSON object."
    )


def test_update_issue_rejects_non_json_body(client, sample_issue):
    response = client.patch(
        f"/api/issues/{sample_issue['id']}",
        data="this is not JSON",
        content_type="text/plain",
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == (
        "Request body must be a JSON object."
    )


def test_update_nonexistent_issue_returns_404(client):
    response = client.patch(
        "/api/issues/99999",
        json={"status": "resolved"},
    )

    assert response.status_code == 404
    assert response.get_json()["error"] == "Issue not found."


def test_update_issue_rejects_title_over_200_characters(
    client, sample_issue
):
    response = client.patch(
        f"/api/issues/{sample_issue['id']}",
        json={"title": "A" * 201},
    )

    assert response.status_code == 400
    assert "200 characters" in response.get_json()["error"]


def test_update_issue_rejects_blank_description(client, sample_issue):
    response = client.patch(
        f"/api/issues/{sample_issue['id']}",
        json={"description": "   "},
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == (
        "Description cannot be empty."
    )


def test_update_issue_rejects_non_string_description(
    client, sample_issue
):
    response = client.patch(
        f"/api/issues/{sample_issue['id']}",
        json={"description": 123},
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == (
        "Description cannot be empty."
    )

def test_list_issues_returns_created_issues(client):
    first = client.post(
        "/api/issues",
        json={
            "title": "Login page error",
            "description": "Login fails after submitting credentials.",
        },
    )
    second = client.post(
        "/api/issues",
        json={
            "title": "Checkout page error",
            "description": "Checkout fails after clicking Pay.",
        },
    )

    assert first.status_code == 201
    assert second.status_code == 201

    response = client.get("/api/issues")

    assert response.status_code == 200
    issues = response.get_json()
    assert len(issues) == 2
    assert {issue["title"] for issue in issues} == {
        "Login page error",
        "Checkout page error",
    }


def test_update_with_invalid_data_preserves_existing_issue(
    client, sample_issue
):
    issue_id = sample_issue["id"]
    original_title = sample_issue["title"]
    original_status = sample_issue["status"]

    response = client.patch(
        f"/api/issues/{issue_id}",
        json={"title": "   "},
    )

    assert response.status_code == 400

    saved_response = client.get(f"/api/issues/{issue_id}")
    saved_issue = saved_response.get_json()

    assert saved_response.status_code == 200
    assert saved_issue["title"] == original_title
    assert saved_issue["status"] == original_status


def test_create_issue_rejects_non_object_json(client):
    response = client.post(
        "/api/issues",
        json=["this", "is", "a", "list"],
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == (
        "Request body must be a JSON object."
    )


def test_update_issue_rejects_non_object_json(client, sample_issue):
    response = client.patch(
        f"/api/issues/{sample_issue['id']}",
        json=["invalid", "update"],
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == (
        "Request body must be a JSON object."
    )
