
def test_detect_similar_issue(client, sample_issue):
    response = client.post(
        "/api/issues/check-duplicates",
        json={
            "title": "Server error on sign-in",
            "description": (
                "Logging in with correct credentials "
                "causes an internal server error."
            ),
            "threshold": 0.2,
        },
    )

    assert response.status_code == 200

    data = response.get_json()
    assert data["count"] >= 1
    assert data["matches"][0]["issue"]["id"] == sample_issue["id"]
    assert 0 <= data["matches"][0]["similarity"] <= 1


def test_no_duplicate_for_unrelated_issue(client, sample_issue):
    response = client.post(
        "/api/issues/check-duplicates",
        json={
            "title": "Update profile picture",
            "description": (
                "Users cannot upload a new profile photograph."
            ),
            "threshold": 0.8,
        },
    )

    assert response.status_code == 200
    assert response.get_json()["matches"] == []


def test_reject_invalid_threshold(client):
    response = client.post(
        "/api/issues/check-duplicates",
        json={
            "title": "Login error",
            "description": "Login fails.",
            "threshold": 1.5,
        },
    )

    assert response.status_code == 400


def test_reject_missing_title(client):
    response = client.post(
        "/api/issues/check-duplicates",
        json={
            "description": "Login fails.",
        },
    )

    assert response.status_code == 400

def test_no_duplicates_when_database_is_empty(client):
    response = client.post(
        "/api/issues/check-duplicates",
        json={
            "title": "A completely new issue",
            "description": "This issue has no existing candidates.",
        },
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["matches"] == []
    assert data["count"] == 0


def test_reject_missing_description(client):
    response = client.post(
        "/api/issues/check-duplicates",
        json={"title": "Missing description"},
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Description is required."


def test_reject_boolean_threshold(client):
    response = client.post(
        "/api/issues/check-duplicates",
        json={
            "title": "Threshold validation",
            "description": "Check that a boolean is not accepted.",
            "threshold": True,
        },
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == (
        "Threshold must be a number between 0 and 1."
    )


def test_normalize_common_login_synonyms():
    from app.services.duplicate_service import DuplicateIssueService

    normalized = DuplicateIssueService._normalize_text(
        "Signing in failed with a 500 error!"
    )

    assert "login" in normalized
    assert "servererror" in normalized
    assert "!" not in normalized
