from decimal import Decimal

import pytest

from app.domain.ApprovalPolicy import ApprovalPolicy
from app.domain.PurchaseRequest import ApprovalLevel


@pytest.fixture
def policy():
    return ApprovalPolicy()


def test_below_threshold_auto_approves(policy):
    route = policy.evaluate(Decimal("250.00"))
    assert route.required_level == ApprovalLevel.AUTO
    assert route.auto_approve is True


def test_exactly_threshold_is_not_escalated(policy):
    # 1000 PLN — na progu — nie wymaga Dyrektora (warunek: > 1000).
    route = policy.evaluate(Decimal("1000.00"))
    assert route.required_level == ApprovalLevel.AUTO


def test_above_threshold_requires_director(policy):
    route = policy.evaluate(Decimal("1000.01"))
    assert route.required_level == ApprovalLevel.DIRECTOR
    assert route.auto_approve is False


def test_rejects_non_pln_currency(policy):
    with pytest.raises(ValueError):
        policy.evaluate(Decimal("100"), currency="EUR")
