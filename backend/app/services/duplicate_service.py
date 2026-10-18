
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.models import Issue


class DuplicateIssueService:
    """Find potentially duplicate issues using text similarity."""

    DEFAULT_THRESHOLD = 0.08

    @staticmethod
    def _normalize_text(text):
        """Normalize text before comparing issue reports."""
        text = text.lower()
        synonyms = [
            (r"\binternal server error\b", " servererror "),
            (r"\bserver error\b", " servererror "),
            (r"\b500 error\b", " servererror "),
            (r"\blogging in\b", " login "),
            (r"\blog in\b", " login "),
            (r"\bsign in\b", " login "),
            (r"\bsigning in\b", " login "),
            (r"\bpassword recovery\b", " passwordreset "),
            (r"\bpassword reset\b", " passwordreset "),
            (r"\breset password\b", " passwordreset "),
            (r"\bprofile picture\b", " profileimage "),
            (r"\bprofile photograph\b", " profileimage "),
            (r"\bprofile image\b", " profileimage "),
            (r"\bavatar\b", " profileimage "),
        ]

        for pattern, replacement in synonyms:
            text = re.sub(pattern, replacement, text)
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        return " ".join(text.split())

    
    @classmethod
    def find_duplicates(
        cls,
        title,
        description,
        threshold=DEFAULT_THRESHOLD,
        exclude_issue_id=None,
    ):
        if not isinstance(title, str) or not title.strip():
            raise ValueError("Title is required.")

        if not isinstance(description, str) or not description.strip():
            raise ValueError("Description is required.")

        if (
            isinstance(threshold, bool)
            or not isinstance(threshold, (int, float))
            or not 0 <= threshold <= 1
        ):
            raise ValueError("Threshold must be between 0 and 1.")

        candidates_query = Issue.query

        if exclude_issue_id is not None:
            candidates_query = candidates_query.filter(
                Issue.id != exclude_issue_id
            )

        candidates = candidates_query.all()

        if not candidates:
            return []

        new_title = cls._normalize_text(title)
        new_description = cls._normalize_text(description)

        existing_titles = [
            cls._normalize_text(issue.title)
            for issue in candidates
        ]

        existing_descriptions = [
            cls._normalize_text(issue.description)
            for issue in candidates
        ]

        # Compare titles independently.
        title_vectorizer = TfidfVectorizer(
            ngram_range=(1, 2)
        )

        title_matrix = title_vectorizer.fit_transform(
            [new_title, *existing_titles]
        )

        title_scores = cosine_similarity(
            title_matrix[0:1],
            title_matrix[1:],
        ).flatten()

        # Compare descriptions independently.
        description_vectorizer = TfidfVectorizer(
            ngram_range=(1, 2)
        )

        description_matrix = description_vectorizer.fit_transform(
            [new_description, *existing_descriptions]
        )

        description_scores = cosine_similarity(
            description_matrix[0:1],
            description_matrix[1:],
        ).flatten()

        # Combine the scores using equal weights.
        scores = (
            0.5 * title_scores
            + 0.5 * description_scores
        )

        matches = []

        for issue, score in zip(candidates, scores):
            similarity = float(score)

            if similarity >= threshold:
                matches.append({
                    "issue": issue.to_dict(),
                    "similarity": round(similarity, 4),
                })

        matches.sort(
            key=lambda item: item["similarity"],
            reverse=True,
        )

        return matches

