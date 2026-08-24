"""Budget Guardian helpers."""
from __future__ import annotations

from database import basket_total
from recommendations import cheaper_substitutes


def budget_message(budget: float) -> str:
    total = basket_total()
    remaining = round(budget - total, 2)
    if remaining >= 0:
        return f"💰 Basket is ${total:.2f} / ${budget:.2f}. You have ${remaining:.2f} left."
    return f"⚠️ Basket is ${total:.2f} / ${budget:.2f}. You are ${abs(remaining):.2f} over budget."


def alternative_for_over_budget(product_name: str, price: float, budget: float) -> list[dict]:
    return cheaper_substitutes(product_name, price)
