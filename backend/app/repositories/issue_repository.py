
from app import db
from app.models import Issue


class IssueRepository:
    """Handles database operations for issues."""

    @staticmethod
    def create(issue_data):
        issue = Issue(**issue_data)
        db.session.add(issue)
        db.session.commit()
        return issue

    @staticmethod
    def get_by_id(issue_id):
        return db.session.get(Issue, issue_id)

    @staticmethod
    def get_all():
        return Issue.query.order_by(Issue.created_at.desc()).all()

    @staticmethod
    def update(issue, update_data):
        for field, value in update_data.items():
            setattr(issue, field, value)

        db.session.commit()
        return issue

    @staticmethod
    def delete(issue):
        db.session.delete(issue)
        db.session.commit()
