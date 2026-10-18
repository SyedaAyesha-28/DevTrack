
from app.services.semantic_duplicate_service import SemanticDuplicateService


def test_detect_semantically_similar_issue(sample_issue):
    matches = SemanticDuplicateService.find_duplicates(
        title="Login fails with valid credentials",
        description=(
            "Users cannot sign in because authentication "
            "returns an internal server error."
        ),
        threshold=0.65,
    )

    matching_ids = [match["issue"]["id"] for match in matches]

    assert sample_issue["id"] in matching_ids


def test_exclude_unrelated_issue(sample_issue):
    matches = SemanticDuplicateService.find_duplicates(
        title="Garden plants are wilting",
        description="Indoor plants are losing leaves due to dry soil.",
        threshold=0.65,
    )

    matching_ids = [match["issue"]["id"] for match in matches]

    assert sample_issue["id"] not in matching_ids


def test_reject_invalid_semantic_threshold():
    try:
        SemanticDuplicateService.find_duplicates(
            title="Login failure",
            description="Users cannot log in.",
            threshold=1.5,
        )
    except ValueError as exc:
        assert "Threshold" in str(exc)
    else:
        raise AssertionError("An invalid threshold should be rejected.")


def test_reject_missing_semantic_title():
    try:
        SemanticDuplicateService.find_duplicates(
            title=" ",
            description="Users cannot log in.",
        )
    except ValueError as exc:
        assert "Title" in str(exc)
    else:
        raise AssertionError("A missing title should be rejected.")


def test_semantic_model_is_reused():
    first_model = SemanticDuplicateService._get_model()
    second_model = SemanticDuplicateService._get_model()

    assert first_model is second_model

def test_semantic_duplicate_endpoint(client, sample_issue):
    response = client.post(
        "/api/issues/check-semantic-duplicates",
        json={
            "title": "Login fails with valid credentials",
            "description": (
                "Users cannot sign in because authentication "
                "returns an internal server error."
            ),
            "threshold": 0.65,
        },
    )

    assert response.status_code == 200

    data = response.get_json()
    assert "matches" in data
    assert "count" in data
    assert data["method"] == "semantic_similarity"

    matching_ids = [
        match["issue"]["id"] for match in data["matches"]
    ]
    assert sample_issue["id"] in matching_ids


def test_semantic_duplicate_endpoint_rejects_invalid_threshold(client):
    response = client.post(
        "/api/issues/check-semantic-duplicates",
        json={
            "title": "Login failure",
            "description": "Users cannot log in.",
            "threshold": 1.5,
        },
    )

    assert response.status_code == 400
    assert "error" in response.get_json()

def test_semantic_endpoint_excludes_specified_issue(client, sample_issue):
    response = client.post(
        "/api/issues/check-semantic-duplicates",
        json={
            "title": "Login page returns a 500 error",
            "description": (
                "Submitting valid login credentials causes "
                "an internal server error."
            ),
            "threshold": 0.65,
            "exclude_issue_id": sample_issue["id"],
        },
    )

    assert response.status_code == 200

    data = response.get_json()
    assert data["count"] == 0
    assert data["matches"] == []


def test_semantic_endpoint_rejects_invalid_exclude_issue_id(client):
    response = client.post(
        "/api/issues/check-semantic-duplicates",
        json={
            "title": "Login fails",
            "description": "Users cannot log in.",
            "threshold": 0.65,
            "exclude_issue_id": -2,
        },
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == (
        "exclude_issue_id must be a positive integer."
    )

def test_semantic_duplicate_response_contains_issue_details(
    client, sample_issue
):
    response = client.post(
        "/api/issues/check-semantic-duplicates",
        json={
            "title": "Login fails with valid credentials",
            "description": (
                "Users cannot sign in because authentication "
                "returns an internal server error."
            ),
            "threshold": 0.65,
        },
    )

    assert response.status_code == 200
    data = response.get_json()

    assert data["count"] == len(data["matches"])
    assert data["method"] == "semantic_similarity"

    matching = next(
        (
            match
            for match in data["matches"]
            if match["issue"]["id"] == sample_issue["id"]
        ),
        None,
    )

    assert matching is not None
    assert matching["issue"]["title"] == sample_issue["title"]
    assert 0.0 <= matching["similarity"] <= 1.0
