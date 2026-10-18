
import os

from flask import Blueprint, jsonify, request

from app.services.issue_service import IssueService

issues_bp = Blueprint("issues", __name__)


# --------------------------------------------------
# CREATE ISSUE
# --------------------------------------------------
@issues_bp.post("/issues")
def create_issue():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Request body must be a JSON object."
        }), 400

    try:
        issue = IssueService.create_issue(data)
        return jsonify(issue.to_dict()), 201

    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


# --------------------------------------------------
# GET ALL ISSUES
# --------------------------------------------------
@issues_bp.get("/issues")
def get_issues():
    issues = IssueService.get_all_issues()

    return jsonify([
        issue.to_dict() for issue in issues
    ]), 200


# --------------------------------------------------
# GET ISSUE BY ID
# --------------------------------------------------
@issues_bp.get("/issues/<int:issue_id>")
def get_issue(issue_id):
    issue = IssueService.get_issue(issue_id)

    if issue is None:
        return jsonify({
            "error": "Issue not found."
        }), 404

    return jsonify(issue.to_dict()), 200


# --------------------------------------------------
# UPDATE ISSUE
# --------------------------------------------------
@issues_bp.patch("/issues/<int:issue_id>")
def update_issue(issue_id):
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Request body must be a JSON object."
        }), 400

    issue = IssueService.get_issue(issue_id)

    if issue is None:
        return jsonify({
            "error": "Issue not found."
        }), 404

    try:
        updated_issue = IssueService.update_issue(issue, data)

        return jsonify(updated_issue.to_dict()), 200

    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


# --------------------------------------------------
# DELETE ISSUE
# --------------------------------------------------
@issues_bp.delete("/issues/<int:issue_id>")
def delete_issue(issue_id):
    issue = IssueService.get_issue(issue_id)

    if issue is None:
        return jsonify({
            "error": "Issue not found."
        }), 404

    IssueService.delete_issue(issue)

    return "", 204


# --------------------------------------------------
# TF-IDF DUPLICATE DETECTION
# --------------------------------------------------
@issues_bp.post("/issues/check-duplicates")
def check_duplicates():
    from app.services.duplicate_service import DuplicateIssueService

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Request body must be a JSON object."
        }), 400

    title = data.get("title")
    description = data.get("description")

    threshold = data.get(
        "threshold",
        DuplicateIssueService.DEFAULT_THRESHOLD,
    )

    if (
        isinstance(threshold, bool)
        or not isinstance(threshold, (int, float))
        or not 0 <= threshold <= 1
    ):
        return jsonify({
            "error": "Threshold must be a number between 0 and 1."
        }), 400

    try:
        matches = DuplicateIssueService.find_duplicates(
            title=title,
            description=description,
            threshold=float(threshold),
        )

        return jsonify({
            "matches": matches,
            "count": len(matches),
            "threshold": float(threshold),
        }), 200

    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


# --------------------------------------------------
# SEMANTIC DUPLICATE DETECTION
# --------------------------------------------------
@issues_bp.post("/issues/check-semantic-duplicates")
def check_semantic_duplicates():
    from app.services.semantic_duplicate_service import (
        SemanticDuplicateService,
    )

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Request body must be a JSON object."
        }), 400

    title = data.get("title")
    description = data.get("description")

    threshold = data.get(
        "threshold",
        SemanticDuplicateService.DEFAULT_THRESHOLD,
    )

    exclude_issue_id = data.get("exclude_issue_id")

    # Validate threshold.
    if (
        isinstance(threshold, bool)
        or not isinstance(threshold, (int, float))
        or not 0 <= threshold <= 1
    ):
        return jsonify({
            "error": "Threshold must be a number between 0 and 1."
        }), 400

    # Validate optional issue ID to exclude.
    if exclude_issue_id is not None:
        if (
            isinstance(exclude_issue_id, bool)
            or not isinstance(exclude_issue_id, int)
            or exclude_issue_id <= 0
        ):
            return jsonify({
                "error": (
                    "exclude_issue_id must be a positive integer."
                )
            }), 400

    try:
        matches = SemanticDuplicateService.find_duplicates(
            title=title,
            description=description,
            threshold=float(threshold),
            exclude_issue_id=exclude_issue_id,
        )

        # Report the configured method accurately.
        mode = os.getenv(
            "SEMANTIC_DUPLICATES_MODE", "semantic"
        ).lower()

        method = (
            "tfidf_fallback"
            if mode == "tfidf"
            else "semantic_similarity"
        )

        return jsonify({
            "matches": matches,
            "count": len(matches),
            "threshold": float(threshold),
            "method": method,
        }), 200

    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
