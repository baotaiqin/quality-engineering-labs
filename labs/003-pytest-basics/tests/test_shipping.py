from decimal import Decimal

import pytest

from shipping import calculate_shipping_fee


def test_standard_order_reaches_free_shipping_threshold() -> None:
    fee = calculate_shipping_fee(Decimal("99.00"))

    assert fee == Decimal("0.00")


@pytest.mark.parametrize(
    ("order_amount", "is_member", "remote_area", "expected_fee"),
    [
        pytest.param("98.99", False, False, "8.00", id="standard-below-threshold"),
        pytest.param("99.00", False, False, "0.00", id="standard-at-threshold"),
        pytest.param("58.99", True, False, "8.00", id="member-below-threshold"),
        pytest.param("59.00", True, False, "0.00", id="member-at-threshold"),
        pytest.param("99.00", False, True, "10.00", id="remote-surcharge-remains"),
    ],
)
def test_shipping_fee_rules(
    order_amount: str,
    is_member: bool,
    remote_area: bool,
    expected_fee: str,
) -> None:
    fee = calculate_shipping_fee(
        Decimal(order_amount),
        is_member=is_member,
        remote_area=remote_area,
    )

    assert fee == Decimal(expected_fee)


def test_negative_order_amount_is_rejected() -> None:
    with pytest.raises(ValueError, match="不能小于0"):
        calculate_shipping_fee(Decimal("-0.01"))
