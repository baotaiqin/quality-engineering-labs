from decimal import Decimal

from shipping import calculate_shipping_fee


def test_free_shipping_boundary_with_wrong_expectation() -> None:
    fee = calculate_shipping_fee(Decimal("99.00"))

    assert fee == Decimal("8.00")
