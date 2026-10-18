
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.services.duplicate_service import DuplicateIssueService
from app.services.semantic_duplicate_service import SemanticDuplicateService

EVALUATION_CASES = [
    {
        "title_a": "Login fails with valid credentials",
        "description_a": "Users receive a 500 error when signing in.",
        "title_b": "Server error during sign in",
        "description_b": (
            "Logging in with a correct password returns "
            "an internal server error."
        ),
        "is_duplicate": True,
    },
    {
        "title_a": "Checkout page crashes",
        "description_a": "Submitting an order crashes the checkout page.",
        "title_b": "Order submission causes checkout failure",
        "description_b": (
            "The checkout process fails when a customer places an order."
        ),
        "is_duplicate": True,
    },
    {
        "title_a": "Password reset email missing",
        "description_a": "Users do not receive password reset emails.",
        "title_b": "Reset password email never arrives",
        "description_b": "The password recovery email is not delivered.",
        "is_duplicate": True,
    },
    {
        "title_a": "Profile picture upload fails",
        "description_a": "Users cannot upload a new profile image.",
        "title_b": "Dashboard chart displays incorrect values",
        "description_b": (
            "The analytics chart shows totals that do not "
            "match the source data."
        ),
        "is_duplicate": False,
    },
    {
        "title_a": "Application crashes on startup",
        "description_a": "The application closes immediately after launch.",
        "title_b": "Email notifications arrive late",
        "description_b": (
            "Notification emails are delivered several minutes after an event."
        ),
        "is_duplicate": False,
    },
    {
        "title_a": "Cannot update profile picture",
        "description_a": "Saving a new avatar fails on the profile page.",
        "title_b": "Profile image upload returns an error",
        "description_b": (
            "Uploading an avatar fails for users on the profile screen."
        ),
        "is_duplicate": True,
    },
    {
        "title_a": "Search returns no matching products",
        "description_a": (
            "Product search shows an empty result for existing items."
        ),
        "title_b": "Payment declined for valid card",
        "description_b": "The payment processor rejects valid card details.",
        "is_duplicate": False,
    },
    {
        "title_a": "Slow dashboard loading",
        "description_a": "The dashboard takes too long to load.",
        "title_b": "Dashboard fails to load",
        "description_b": (
            "The dashboard displays a blank page instead of loading."
        ),
        "is_duplicate": False,
    },
    {
        "title_a": "API returns unauthorized after token expires",
        "description_a": "Requests fail with a 401 response when the access token expires.",
        "title_b": "Expired access token causes 401 errors",
        "description_b": "The API rejects requests after the user's authentication token expires.",
        "is_duplicate": True,
    },
    {
        "title_a": "File upload rejected when file is too large",
        "description_a": "Uploading files above the configured size limit fails.",
        "title_b": "Maximum upload size causes an error",
        "description_b": "Users cannot upload files that exceed the allowed size.",
        "is_duplicate": True,
    },
    {
        "title_a": "New comment email notification missing",
        "description_a": "Users do not receive an email when someone comments on their post.",
        "title_b": "Comment notifications are not sent",
        "description_b": "Email alerts are missing when another user adds a comment.",
        "is_duplicate": True,
    },
    {
        "title_a": "Exported CSV file contains duplicate rows",
        "description_a": "Exporting reports produces repeated records in the CSV file.",
        "title_b": "Report export repeats records",
        "description_b": "The generated report contains duplicate entries.",
        "is_duplicate": True,
    },
    {
        "title_a": "User receives 401 error during login",
        "description_a": "The authentication endpoint rejects valid credentials.",
        "title_b": "Expired access token causes 401 errors",
        "description_b": "The API rejects requests after the user's authentication token expires.",
        "is_duplicate": False,
    },
    {
        "title_a": "Image upload fails on profile page",
        "description_a": "The profile picture cannot be saved.",
        "title_b": "File upload rejected when file is too large",
        "description_b": "Uploading files above the configured size limit fails.",
        "is_duplicate": False,
    },
    {
        "title_a": "Checkout page loads slowly",
        "description_a": "The checkout screen takes several seconds to appear.",
        "title_b": "Payment declined for valid card",
        "description_b": "The payment processor rejects valid card details.",
        "is_duplicate": False,
    },
    {
        "title_a": "Comment notification email missing",
        "description_a": "Users do not receive an email after a new comment.",
        "title_b": "Email notification arrives late",
        "description_b": "Notification emails arrive several minutes after an event.",
        "is_duplicate": False,
    },
    
    # Additional challenging duplicate pairs

    {
        "title_a": "Password reset email never arrives",
        "description_a": "The user requests a password reset, but no reset email is delivered.",
        "title_b": "Reset password message is missing",
        "description_b": "After requesting a password reset, the user does not receive the email.",
        "is_duplicate": True,
    },
    {
        "title_a": "Profile picture upload fails",
        "description_a": "Uploading a new profile picture returns an error and the image is not saved.",
        "title_b": "Avatar cannot be uploaded",
        "description_b": "Users receive an error when uploading an avatar, and the profile image remains unchanged.",
        "is_duplicate": True,
    },
    {
        "title_a": "Checkout crashes after payment",
        "description_a": "The application crashes after the payment provider confirms a successful payment.",
        "title_b": "App errors when confirming a completed payment",
        "description_b": "After successful payment, the checkout page throws an error instead of showing confirmation.",
        "is_duplicate": True,
    },
    {
        "title_a": "Search results disappear when changing pages",
        "description_a": "Moving to the next page of search results clears the result list unexpectedly.",
        "title_b": "Pagination clears the search results",
        "description_b": "When a user selects another results page, the search results become empty.",
        "is_duplicate": True,
    },
    {
        "title_a": "Login fails with an incorrect password",
        "description_a": "The login form correctly rejects a password that does not match the account.",
        "title_b": "Password reset email never arrives",
        "description_b": "The password recovery email is not delivered after the user requests a reset.",
        "is_duplicate": False,
    },
    {
        "title_a": "Profile picture upload fails",
        "description_a": "Uploading an image returns an error and the profile picture is not saved.",
        "title_b": "Profile page loads slowly",
        "description_b": "The profile page takes several seconds to load, but images upload successfully.",
        "is_duplicate": False,
    },
    {
        "title_a": "Payment confirmation email is missing",
        "description_a": "The payment succeeds, but the customer never receives a confirmation email.",
        "title_b": "Checkout crashes after payment",
        "description_b": "The application crashes after the payment provider confirms a successful payment.",
        "is_duplicate": False,
    },
    {
        "title_a": "Search returns no results",
        "description_a": "Searching for existing products incorrectly displays an empty result list.",
        "title_b": "Search results disappear when changing pages",
        "description_b": "Moving to the next page of search results clears the result list unexpectedly.",
        "is_duplicate": False,
    },

]

# First 16 examples: development set for threshold selection.
DEV_EVALUATION_CASES = EVALUATION_CASES[:16]

# Last 8 examples: provisional validation set.
# These are not a truly unseen test set because their scores
# have already been examined.
HELD_OUT_EVALUATION_CASES = EVALUATION_CASES[16:]


# Fresh final evaluation examples.
# Keep these separate from threshold selection and do not tune thresholds
# based on their results.
FINAL_TEST_CASES = [
    {
        "title_a": "Expired MFA code is rejected",
        "description_a": "The login form rejects a one-time verification code after it expires.",
        "title_b": "One-time password fails after expiration",
        "description_b": "Users cannot authenticate using a verification code that has expired.",
        "is_duplicate": True,
    },
    {
        "title_a": "Invoice PDF download produces a corrupt file",
        "description_a": "Downloaded invoice PDFs cannot be opened because the files are corrupted.",
        "title_b": "Downloaded invoices are unreadable",
        "description_b": "The invoice download returns a damaged PDF that PDF readers cannot open.",
        "is_duplicate": True,
    },
    {
        "title_a": "Product price sorting uses the wrong order",
        "description_a": "Selecting highest price first displays the cheapest products at the top.",
        "title_b": "Descending price sort displays ascending results",
        "description_b": "The product list sorts from low to high instead of high to low.",
        "is_duplicate": True,
    },
    {
        "title_a": "Account locks after repeated failed logins",
        "description_a": "After five incorrect passwords, the account becomes locked as expected, but never unlocks.",
        "title_b": "Locked account remains inaccessible",
        "description_b": "Users cannot regain access after the failed-login lockout period has ended.",
        "is_duplicate": True,
    },
    {
        "title_a": "Expired MFA code is rejected",
        "description_a": "The login form rejects a one-time verification code after it expires.",
        "title_b": "MFA setup QR code is missing",
        "description_b": "The security settings page does not display a QR code when enabling two-factor authentication.",
        "is_duplicate": False,
    },
    {
        "title_a": "Invoice PDF download produces a corrupt file",
        "description_a": "Downloaded invoice PDFs cannot be opened because the files are corrupted.",
        "title_b": "Invoice email is never delivered",
        "description_b": "Customers do not receive the email containing their invoice after an order is completed.",
        "is_duplicate": False,
    },
    {
        "title_a": "Product price sorting uses the wrong order",
        "description_a": "Selecting highest price first displays the cheapest products at the top.",
        "title_b": "Product search filters hide matching items",
        "description_b": "Applying a category filter removes products that match the selected category.",
        "is_duplicate": False,
    },
    {
        "title_a": "Account locks after repeated failed logins",
        "description_a": "The account remains inaccessible after the failed-login lockout period ends.",
        "title_b": "Account settings changes are not saved",
        "description_b": "Clicking Save on the account settings page does not persist updated profile details.",
        "is_duplicate": False,
    },
]


def similarity_score(title_a, title_b, description_a, description_b):
    """Calculate similarity using titles and descriptions separately."""

    title_a = DuplicateIssueService._normalize_text(title_a)
    title_b = DuplicateIssueService._normalize_text(title_b)
    description_a = DuplicateIssueService._normalize_text(description_a)
    description_b = DuplicateIssueService._normalize_text(description_b)

    title_vectorizer = TfidfVectorizer(ngram_range=(1, 2))
    title_matrix = title_vectorizer.fit_transform([title_a, title_b])

    title_score = cosine_similarity(
        title_matrix[0:1], title_matrix[1:2]
    )[0][0]

    description_vectorizer = TfidfVectorizer(ngram_range=(1, 2))
    description_matrix = description_vectorizer.fit_transform(
        [description_a, description_b]
    )

    description_score = cosine_similarity(
        description_matrix[0:1], description_matrix[1:2]
    )[0][0]

    return float(0.5 * title_score + 0.5 * description_score)


def evaluate_threshold(threshold):
    true_positive = 0
    false_positive = 0
    false_negative = 0
    true_negative = 0

    for case in DEV_EVALUATION_CASES:
        score = similarity_score(
            case["title_a"],
            case["title_b"],
            case["description_a"],
            case["description_b"],
        )

        predicted_duplicate = score >= threshold
        actual_duplicate = case["is_duplicate"]

        if predicted_duplicate and actual_duplicate:
            true_positive += 1
        elif predicted_duplicate and not actual_duplicate:
            false_positive += 1
        elif not predicted_duplicate and actual_duplicate:
            false_negative += 1
        else:
            true_negative += 1

    precision = (
        true_positive / (true_positive + false_positive)
        if true_positive + false_positive
        else 0.0
    )

    recall = (
        true_positive / (true_positive + false_negative)
        if true_positive + false_negative
        else 0.0
    )

    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall
        else 0.0
    )

    return {
        "threshold": threshold,
        "true_positive": true_positive,
        "false_positive": false_positive,
        "false_negative": false_negative,
        "true_negative": true_negative,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }



def test_evaluation_metrics_are_valid():
    result = evaluate_threshold(0.08)

    actual_duplicates = sum(
        case["is_duplicate"] for case in DEV_EVALUATION_CASES
    )
    actual_non_duplicates = len(DEV_EVALUATION_CASES) - actual_duplicates

    assert (
        result["true_positive"] + result["false_negative"]
        == actual_duplicates
    )
    assert (
        result["false_positive"] + result["true_negative"]
        == actual_non_duplicates
    )
    assert 0.0 <= result["precision"] <= 1.0
    assert 0.0 <= result["recall"] <= 1.0
    assert 0.0 <= result["f1"] <= 1.0



def test_evaluation_covers_both_classes():
    assert any(case["is_duplicate"] for case in DEV_EVALUATION_CASES)
    assert any(not case["is_duplicate"] for case in DEV_EVALUATION_CASES)


def test_compare_thresholds():
    print("\nDuplicate detection threshold comparison")

    for threshold in [0.05, 0.08, 0.09, 0.10, 0.12, 0.15, 0.20]:
        result = evaluate_threshold(threshold)

        print(
            f"Threshold={threshold:.2f} | "
            f"Precision={result['precision']:.2f} | "
            f"Recall={result['recall']:.2f} | "
            f"F1={result['f1']:.2f} | "
            f"False positives={result['false_positive']}"
        )


def test_print_individual_similarity_scores():
    print("\nIndividual issue-pair similarity scores")

    for index, case in enumerate(DEV_EVALUATION_CASES, start=1):
        score = similarity_score(
            case["title_a"],
            case["title_b"],
            case["description_a"],
            case["description_b"],
        )

        print(
            f"Pair {index}: Similarity={score:.4f} | "
            f"Actual duplicate={case['is_duplicate']}"
        )


_SEMANTIC_SCORES = {}


def semantic_similarity_scores(cases=DEV_EVALUATION_CASES):
    """Calculate and cache semantic scores for a specific dataset."""
    global _SEMANTIC_SCORES

    cache_key = tuple(id(case) for case in cases)

    if cache_key in _SEMANTIC_SCORES:
        return _SEMANTIC_SCORES[cache_key]

    # Reuse the model already loaded for this Python process.
    model = SemanticDuplicateService._get_model()

    texts = []
    for case in cases:
        texts.append(
            SemanticDuplicateService._build_issue_text(
                case["title_a"], case["description_a"]
            )
        )
        texts.append(
            SemanticDuplicateService._build_issue_text(
                case["title_b"], case["description_b"]
            )
        )

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        convert_to_numpy=True,
        batch_size=32,
    )

    scores = [
        float(embeddings[i] @ embeddings[i + 1])
        for i in range(0, len(embeddings), 2)
    ]

    _SEMANTIC_SCORES[cache_key] = scores
    return scores



def test_compare_semantic_thresholds():
    print("\nSemantic duplicate detection threshold comparison")

    scores = semantic_similarity_scores(DEV_EVALUATION_CASES)

    for threshold in [0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70]:
        true_positive = 0
        false_positive = 0
        false_negative = 0
        true_negative = 0

        for case, score in zip(DEV_EVALUATION_CASES, scores):
            predicted = score >= threshold
            actual = case["is_duplicate"]

            if predicted and actual:
                true_positive += 1
            elif predicted and not actual:
                false_positive += 1
            elif not predicted and actual:
                false_negative += 1
            else:
                true_negative += 1

        precision = (
            true_positive / (true_positive + false_positive)
            if true_positive + false_positive else 0.0
        )
        recall = (
            true_positive / (true_positive + false_negative)
            if true_positive + false_negative else 0.0
        )
        f1 = (
            2 * precision * recall / (precision + recall)
            if precision + recall else 0.0
        )

        print(
            f"Threshold={threshold:.2f} | "
            f"Precision={precision:.2f} | "
            f"Recall={recall:.2f} | "
            f"F1={f1:.2f} | "
            f"False positives={false_positive}"
        )

    print("\nIndividual semantic similarity scores")
    for index, (case, score) in enumerate(
        zip(DEV_EVALUATION_CASES, scores), start=1
    ):
        print(
            f"Pair {index}: Similarity={score:.4f} | "
            f"Actual duplicate={case['is_duplicate']}"
        )

def test_validate_on_held_out_examples():
    """Evaluate fixed thresholds on the separate validation examples."""
    cases = HELD_OUT_EVALUATION_CASES

    # Fixed thresholds selected from the development evaluation.
    tfidf_threshold = 0.05
    semantic_threshold = 0.65

    semantic_scores = semantic_similarity_scores(cases)

    print("\nHeld-out validation results")

    for method, threshold, score_function in [
        (
            "TF-IDF",
            tfidf_threshold,
            lambda case, index: similarity_score(
                case["title_a"],
                case["title_b"],
                case["description_a"],
                case["description_b"],
            ),
        ),
        (
            "Semantic",
            semantic_threshold,
            lambda case, index: semantic_scores[index],
        ),
    ]:
        tp = fp = fn = tn = 0

        for index, case in enumerate(cases):
            actual = case["is_duplicate"]
            predicted = score_function(case, index) >= threshold

            if predicted and actual:
                tp += 1
            elif predicted and not actual:
                fp += 1
            elif not predicted and actual:
                fn += 1
            else:
                tn += 1

        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = (
            2 * precision * recall / (precision + recall)
            if precision + recall
            else 0.0
        )

        print(
            f"{method} | threshold={threshold:.2f} | "
            f"precision={precision:.2f} | recall={recall:.2f} | "
            f"F1={f1:.2f} | FP={fp} | FN={fn}"
        )

        assert tp + fp + fn + tn == len(cases)


def test_final_evaluation_on_fresh_examples():
    """Compare fixed thresholds on the separate final evaluation examples."""
    cases = FINAL_TEST_CASES
    semantic_scores = semantic_similarity_scores(cases)

    methods = [
        (
            "TF-IDF",
            0.05,
            [
                similarity_score(
                    case["title_a"],
                    case["title_b"],
                    case["description_a"],
                    case["description_b"],
                )
                for case in cases
            ],
        ),
        ("Semantic", 0.65, semantic_scores),
    ]

    print("\nFresh final evaluation")

    for name, threshold, scores in methods:
        tp = fp = fn = tn = 0

        for case, score in zip(cases, scores):
            actual = case["is_duplicate"]
            predicted = score >= threshold

            if predicted and actual:
                tp += 1
            elif predicted and not actual:
                fp += 1
            elif not predicted and actual:
                fn += 1
            else:
                tn += 1

        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = (
            2 * precision * recall / (precision + recall)
            if precision + recall
            else 0.0
        )

        print(
            f"{name} | threshold={threshold:.2f} | "
            f"precision={precision:.2f} | recall={recall:.2f} | "
            f"F1={f1:.2f} | FP={fp} | FN={fn}"
        )

        assert tp + fp + fn + tn == len(cases)

    assert len(cases) == 8
    assert sum(case["is_duplicate"] for case in cases) == 4

