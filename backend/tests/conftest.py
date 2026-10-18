
import pytest

from app import create_app, db


@pytest.fixture
def app():
    test_app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })

    with test_app.app_context():
        db.create_all()
        try:
            yield test_app
        finally:
            db.session.remove()
            db.drop_all()
            db.engine.dispose()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def sample_issue(client):
    response = client.post(
        "/api/issues",
        json={
            "title": "Login page returns a 500 error",
            "description": (
                "Submitting valid login credentials "
                "causes an internal server error."
            ),
            "priority": "high",
        },
    )

    assert response.status_code == 201
    return response.get_json()
