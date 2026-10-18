
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from app.models import Issue
from app.services.duplicate_service import DuplicateIssueService


class SemanticDuplicateService:
    """Find potentially duplicate issues using semantic similarity."""

    DEFAULT_THRESHOLD = 0.65
    MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

    _model = None

    @classmethod
    def _get_model(cls):
        """Load the model once and reuse it."""
        if cls._model is None:
            cls._model = SentenceTransformer(cls.MODEL_NAME)
        return cls._model

    @classmethod
    def _build_issue_text(cls, title, description):
        """Combine normalized title and description."""
        title = DuplicateIssueService._normalize_text(title)
        description = DuplicateIssueService._normalize_text(description)
        return f"{title}. {description}"

    @classmethod
    def find_duplicates(
        cls,
        title,
        description,
        threshold=DEFAULT_THRESHOLD,
        exclude_issue_id=None,
    ):
        """Return existing issues with sufficiently similar meanings."""

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

        new_text = cls._build_issue_text(title, description)

        existing_texts = [
            cls._build_issue_text(issue.title, issue.description)
            for issue in candidates
        ]

        model = cls._get_model()

        embeddings = model.encode(
            [new_text, *existing_texts],
            normalize_embeddings=True,
            convert_to_numpy=True,
        )

        scores = cosine_similarity(
            embeddings[0:1],
            embeddings[1:],
        ).flatten()

        matches = []

        for issue, score in zip(candidates, scores):
            similarity = float(score)

            if similarity >= threshold:
                matches.append(
                    {
                        "issue": issue.to_dict(),
                        "similarity": round(similarity, 4),
                    }
                )

        matches.sort(
            key=lambda item: item["similarity"],
            reverse=True,
        )

        return matches
