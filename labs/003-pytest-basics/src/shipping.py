from __future__ import annotations

from decimal import Decimal


STANDARD_FREE_THRESHOLD = Decimal("99.00")
MEMBER_FREE_THRESHOLD = Decimal("59.00")
STANDARD_FEE = Decimal("8.00")
REMOTE_SURCHARGE = Decimal("10.00")


def calculate_shipping_fee(
    order_amount: Decimal,
    *,
    is_member: bool = False,
    remote_area: bool = False,
) -> Decimal:
    """按订单金额、会员状态和地区计算运费。"""
    if order_amount < 0:
        raise ValueError("order_amount不能小于0")

    free_threshold = MEMBER_FREE_THRESHOLD if is_member else STANDARD_FREE_THRESHOLD
    base_fee = Decimal("0.00") if order_amount >= free_threshold else STANDARD_FEE
    surcharge = REMOTE_SURCHARGE if remote_area else Decimal("0.00")
    return base_fee + surcharge
