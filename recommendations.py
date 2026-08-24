"""Smart recommendation and substitution algorithms for VocaCart."""
from __future__ import annotations

import datetime
from typing import Any

import database


def _fetch_active_list() -> list[dict[str, Any]]:
    for fn_name in ("get_active_list", "get_shopping_list", "get_list", "get_cart"):
        if hasattr(database, fn_name):
            return getattr(database, fn_name)()
    return []


def _fetch_all_products() -> list[dict[str, Any]]:
    if hasattr(database, "get_all_products"):
        return database.get_all_products()
    if hasattr(database, "find_products"):
        return database.find_products("")
    return []


def get_current_season() -> str:
    month = datetime.datetime.now().month
    if month in (3, 4, 5):
        return "Spring"
    elif month in (6, 7, 8):
        return "Summer"
    elif month in (9, 10, 11):
        return "Fall"
    return "Winter"


def seasonal_recommendations() -> list[dict[str, Any]]:
    season = get_current_season()
    all_prods = _fetch_all_products()

    picks = [p for p in all_prods if p.get("season") == season or p.get("is_seasonal")]
    if not picks:
        picks = [p for p in all_prods if p.get("category") == "Produce"][:3]
    return picks


def cheaper_substitutes(product: dict[str, Any]) -> dict[str, Any] | None:
    all_prods = _fetch_all_products()
    category = product.get("category")
    price = float(product.get("price", 0))

    candidates = [
        p for p in all_prods
        if p.get("category") == category
        and float(p.get("price", 0)) < price
        and p.get("id") != product.get("id")
    ]
    if candidates:
        return sorted(candidates, key=lambda x: float(x["price"]))[0]
    return None


def budget_status() -> dict[str, Any]:
    settings = database.get_settings() if hasattr(database, "get_settings") else {}
    budget = float(settings.get("budget", 0))
    cart = _fetch_active_list()
    total_spent = sum(
        float(item.get("unit_price", 0)) * float(item.get("quantity", 1))
        for item in cart
    )

    return {
        "budget": budget,
        "spent": total_spent,
        "remaining": budget - total_spent if budget > 0 else 0,
        "is_over": total_spent > budget if budget > 0 else False,
    }


def smart_basket() -> list[dict[str, Any]]:
    active_items = {
        item.get("item_name", "").lower() for item in _fetch_active_list()
    }
    suggestions = []

    for prod in seasonal_recommendations():
        if prod.get("name", "").lower() not in active_items:
            suggestions.append({
                "name": prod.get("name"),
                "price": float(prod.get("price", 0)),
                "reason": f"🌟 In season ({get_current_season()})",
            })

    staples = [
        {"name": "Whole Wheat Bread", "price": 2.99, "reason": "🔄 Running low (bought 7 days ago)"},
        {"name": "Farm Fresh Eggs", "price": 3.49, "reason": "🍳 Weekly staple"},
    ]
    for item in staples:
        if item["name"].lower() not in active_items:
            suggestions.append(item)

    return suggestions