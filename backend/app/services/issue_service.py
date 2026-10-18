
from app.repositories.issue_repository import IssueRepository


class IssueService:
    """Contains issue-management business rules."""

    ALLOWED_STATUSES = {"open", "in_progress", "resolved", "closed"}
    ALLOWED_PRIORITIES = {"low", "medium", "high", "critical"}

    @staticmethod
    def create_issue(data):
        title = data.get("title")
        description = data.get("description")

        if not isinstance(title, str) or not title.strip():
            raise ValueError("Title is required.")

        if len(title.strip()) > 200:
            raise ValueError("Title must not exceed 200 characters.")

        if not isinstance(description, str) or not description.strip():
            raise ValueError("Description is required.")

        status = data.get("status", "open")
        priority = data.get("priority", "medium")

        if status not in IssueService.ALLOWED_STATUSES:
            raise ValueError("Invalid issue status.")

        if priority not in IssueService.ALLOWED_PRIORITIES:
            raise ValueError("Invalid issue priority.")

        issue_data = {
            "title": title.strip(),
            "description": description.strip(),
            "status": status,
            "priority": priority,
        }

        return IssueRepository.create(issue_data)

    @staticmethod
    def get_issue(issue_id):
        return IssueRepository.get_by_id(issue_id)

    @staticmethod
    def get_all_issues():
        return IssueRepository.get_all()

    @staticmethod
    def update_issue(issue, data):
        allowed_fields = {"title", "description", "status", "priority"}

        if not isinstance(data, dict) or not data:
            raise ValueError("Provide at least one field to update.")

        unknown_fields = set(data) - allowed_fields
        if unknown_fields:
            raise ValueError(
                f"Unsupported fields: {', '.join(sorted(unknown_fields))}"
            )

        updated = {}

        if "title" in data:
            title = data["title"]
            if not isinstance(title, str) or not title.strip():
                raise ValueError("Title cannot be empty.")
            if len(title.strip()) > 200:
                raise ValueError("Title must not exceed 200 characters.")
            updated["title"] = title.strip()

        if "description" in data:
            description = data["description"]
            if not isinstance(description, str) or not description.strip():
                raise ValueError("Description cannot be empty.")
            updated["description"] = description.strip()

        if "status" in data:
            if data["status"] not in IssueService.ALLOWED_STATUSES:
                raise ValueError("Invalid issue status.")
            updated["status"] = data["status"]

        if "priority" in data:
            if data["priority"] not in IssueService.ALLOWED_PRIORITIES:
                raise ValueError("Invalid issue priority.")
            updated["priority"] = data["priority"]

        return IssueRepository.update(issue, updated)

    @staticmethod
    def delete_issue(issue):
        IssueRepository.delete(issue)
