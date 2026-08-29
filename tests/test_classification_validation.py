from src.classification_models import ClassificationResult
from src.classification_validation import validate_classification

def make_result(
    item_id: str = "email-001",
    classification: str = "action_required",
    confidence: float = 0.95,
    reason: str = "The message directly asks the user to complete an action.",
) -> ClassificationResult:
    return ClassificationResult(
        item_id=item_id,
        classification=classification,
        confidence=confidence,
        reason=reason,
    )

def test_valid_classification_passes_validation():
    result = make_result()

    errors = validate_classification(
        result=result,
        expected_item_id="email-001",
    )

    assert errors == []

def test_mismatched_item_id_fails_validation():
    result = make_result(item_id="email-wrong")

    errors = validate_classification(
        result=result,
        expected_item_id="email-001",
    )

    assert errors == [
        "Classification item_id does not match the input item ID"
    ]

def test_empty_reason_fails_validation():
    result = make_result(reason="   ")

    errors = validate_classification(
        result=result,
        expected_item_id="email-001",
    )

    assert errors == [
        "Classification reason is empty"
    ]

def test_multiple_contract_errors_are_returned():
    result = make_result(
        item_id="email-wrong",
        reason="",
    )

    errors = validate_classification(
        result=result,
        expected_item_id="email-001",
    )

    assert errors == [
        "Classification item_id does not match the input item ID",
        "Classification reason is empty",
    ]
