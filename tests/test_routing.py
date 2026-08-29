from src.classification_models import ClassificationResult
from src.routing import route_after_classification

def make_result(classification: str) -> ClassificationResult:
    return ClassificationResult(
        item_id="email-test",
        classification=classification,
        confidence=0.95,
        reason="Test classification result.",
    )

def test_action_required_routes_to_commitment_extraction():
    result = make_result("action_required")

    route = route_after_classification(result)

    assert route == "extract_commitments"

def test_decision_required_routes_to_commitment_extraction():
    result = make_result("decision_required")

    route = route_after_classification(result)

    assert route == "extract_commitments"

def test_needs_clarification_routes_to_clarification():
    result = make_result("needs_clarification")

    route = route_after_classification(result)

    assert route == "request_clarification"

def test_information_only_skips_commitment_extraction():
    result = make_result("information_only")

    route = route_after_classification(result)

    assert route == "skip_extraction"

def test_waiting_on_someone_skips_commitment_extraction():
    result = make_result("waiting_on_someone")

    route = route_after_classification(result)

    assert route == "skip_extraction"

def test_reference_material_skips_commitment_extraction():
    result = make_result("reference_material")

    route = route_after_classification(result)

    assert route == "skip_extraction"

def test_potential_project_skips_commitment_extraction():
    result = make_result("potential_project")

    route = route_after_classification(result)

    assert route == "skip_extraction"

def test_noise_skips_commitment_extraction():
    result = make_result("noise")

    route = route_after_classification(result)

    assert route == "skip_extraction"
