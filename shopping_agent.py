"""Core intelligence for VocaCart.

Handles intent parsing (LLM + Regex fallbacks), product resolution,
command execution, budget tracking, seasonal recommendations, and item substitution alerts.
"""
from __future__ import annotations

import json
import os
import re
from typing import Any

from database import (
    add_to_list,
    category_for,
    find_products,
    get_product,
    get_settings,
    record_message,
    remove_from_list,
    update_list_item,
)
from recommendations import (
    budget_status,
    cheaper_substitutes,
    seasonal_recommendations,
    smart_basket,
)
from voice import normalize_hinglish

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

try:
    from langchain_groq import ChatGroq
except Exception:
    ChatGroq = None

_llm_instance = None

UNIT_WORDS = {
    "bottle", "bottles", "litre", "litres", "liter", "liters",
    "kg", "kgs", "kilogram", "kilograms", "gram", "grams",
    "packet", "packets", "pack", "packs", "dozen", "dozens",
    "box", "boxes", "can", "cans", "jar", "jars", "item", "items",
}

NUMBER_WORDS = {
    "one": 1, "a": 1, "an": 1, "two": 2, "three": 3, "four": 4,
    "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
}


def _get_llm():
    global _llm_instance
    if _llm_instance is not None:
        return _llm_instance
    if ChatGroq is None:
        return None

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        try:
            import streamlit as st
            api_key = st.secrets.get("GROQ_API_KEY")
        except Exception:
            api_key = None
    if not api_key:
        return None

    model_name = "qwen/qwen3-32b"
    try:
        import streamlit as st
        if "GROQ_MODEL" in st.secrets:
            model_name = st.secrets["GROQ_MODEL"]
        else:
            model_name = os.getenv("GROQ_MODEL", model_name)
    except Exception:
        model_name = os.getenv("GROQ_MODEL", model_name)

    try:
        _llm_instance = ChatGroq(
            model=model_name,
            temperature=0,
            api_key=api_key,
        )
        return _llm_instance
    except Exception:
        return None


def _extract_json(text: str) -> dict[str, Any] | None:
    match = re.search(r"\{.*\}", text, re.S)
    if not match:
        return None
    try:
        data = json.loads(match.group(0))
        return data if isinstance(data, dict) else None
    except json.JSONDecodeError:
        return None


def _llm_parse(text: str, last_item: str | None = None) -> dict[str, Any] | None:
    llm = _get_llm()
    if llm is None:
        return None
    prompt = f"""
You are the intent parser for a voice-first grocery shopping assistant.
Return ONLY valid JSON. No markdown.

Allowed intent values:
add, remove, update, search, budget, smart_basket, seasonal, unknown

Schema:
{{
  "intent": "add",
  "commands": [
    {{
      "item": "milk",
      "quantity": 2,
      "unit": "bottles"
    }}
  ],
  "query": "organic honey",
  "max_price": 15,
  "min_rating": 4.0,
  "organic": true,
  "budget": null
}}

Rules:
- commands may contain multiple items.
- For "actually make that five", use last_item when supplied.
- For search, query should contain the product/category, not the whole sentence.
- Quantity defaults to 1 and unit defaults to "item".
- If the user says "under $20", max_price is 20.
- "4+ stars" means min_rating 4.
- "set my budget to $100" is budget.
- "prepare my weekly grocery list" is smart_basket.
- "what is in season" or "seasonal items" is seasonal.
- For Hinglish/Hindi, normalize obvious grocery words to English where possible.

Last referenced item: {last_item or "none"}
User command: {text}
"""
    try:
        response = llm.invoke(prompt)
        content = response.content if hasattr(response, "content") else str(response)
        return _extract_json(content)
    except Exception:
        return None


def _number_and_unit(fragment: str) -> tuple[float, str, str]:
    fragment = fragment.strip(" ,.")
    quantity = 1.0
    unit = "item"

    m = re.search(r"\b(\d+(?:\.\d+)?)\b", fragment)
    if m:
        quantity = float(m.group(1))
        fragment = (fragment[:m.start()] + " " + fragment[m.end():]).strip()
    else:
        for word, value in NUMBER_WORDS.items():
            if re.search(rf"\b{re.escape(word)}\b", fragment, re.I):
                quantity = float(value)
                fragment = re.sub(rf"\b{re.escape(word)}\b", "", fragment, flags=re.I).strip()
                break

    m_unit = re.search(r"\b(" + "|".join(map(re.escape, sorted(UNIT_WORDS, key=len, reverse=True))) + r")\b", fragment, re.I)
    if m_unit:
        unit = m_unit.group(1).lower()
        fragment = (fragment[:m_unit.start()] + " " + fragment[m_unit.end():]).strip()

    return quantity, unit, fragment


def _rule_parse(text: str, last_item: str | None = None) -> dict[str, Any]:
    t = normalize_hinglish(text.lower().strip())

    if any(x in t for x in ["seasonal", "in season", "fresh now", "what is in season"]):
        return {"intent": "seasonal", "commands": []}

    if any(x in t for x in ["smart basket", "weekly basket", "weekly grocery", "prepare my basket", "prepare my grocery"]):
        return {"intent": "smart_basket", "commands": []}

    budget_match = re.search(r"(?:budget|spend|limit).{0,20}?(?:\$|₹|rs\.?|rupees?)?\s*(\d+(?:\.\d+)?)", t)
    if budget_match:
        return {"intent": "budget", "budget": float(budget_match.group(1)), "commands": []}

    remove = re.search(r"(?:remove|delete|take off|don't need|do not need|hatao|nikal)\s+(.+?)(?:\s+from my list|\s+off my list|$)", t)
    if remove:
        return {"intent": "remove", "commands": [{"item": remove.group(1).strip(), "quantity": 1, "unit": "item"}]}

    update = re.search(
        r"(?:change|make|update|set)\s+(?:(?:the\s+)?quantity\s+of\s+)?(.+?)\s+(?:to|as)\s+(\d+(?:\.\d+)?)\b",
        t,
    )
    if not update and last_item:
        update = re.search(r"(?:actually|instead).{0,20}?\b(\d+(?:\.\d+)?)\b", t)
        if update:
            return {"intent": "update", "commands": [{"item": last_item, "quantity": float(update.group(1)), "unit": "item"}]}
    if update:
        return {"intent": "update", "commands": [{"item": update.group(1).strip(), "quantity": float(update.group(2)), "unit": "item"}]}

    searchish = any(t.startswith(x) for x in ["find ", "search ", "show ", "look for ", "get me "])
    if searchish:
        max_price = None
        min_rating = None
        organic = True if "organic" in t else None

        if any(w in t for w in ["under budget", "within budget", "my budget"]):
            try:
                b = get_settings().get("budget")
                if b:
                    max_price = float(b)
            except Exception:
                pass
            t = re.sub(r"\b(?:under|within|in)\s+(?:my\s+)?budget\b", "", t).strip()

        p = re.search(r"(?:under|below|less than|max(?:imum)?(?: price)?(?: of)?)\s*(?:\$|₹|rs\.?|rupees?)?\s*(\d+(?:\.\d+)?)", t)
        if p:
            max_price = float(p.group(1))

        r = re.search(r"(\d(?:\.\d+)?)\s*\+?\s*(?:stars?|rating)", t)
        if r:
            min_rating = float(r.group(1))

        query = re.sub(r"\b(?:find|search|show|look for|get me)\b", "", t).strip()
        query = re.sub(r"\b(?:organic)\b", "", query).strip()
        query = re.sub(r"(?:under|below|less than|max(?:imum)?(?: price)?(?: of)?)\s*(?:\$|₹|rs\.?|rupees?)?\s*\d+(?:\.\d+)?", "", query)
        query = re.sub(r"\d(?:\.\d+)?\s*\+?\s*(?:stars?|rating)", "", query)
        query = re.sub(r"\bwith\s*$", "", query).strip(" ,")

        return {
            "intent": "search",
            "query": query or "grocery",
            "max_price": max_price,
            "min_rating": min_rating,
            "organic": organic,
            "commands": [],
        }

    if any(x in t for x in ["add ", "buy ", "need ", "want to buy", "want ", "get ", "jodo", "add karo", "buy karo", " add"]):
        t = re.sub(r"\b(?:add karo|jod do|jodo|buy karo)\b", "add", t).strip()
        t = re.sub(r"^(?:please\s+)?(?:add|buy|get|need|want to buy|want|please)\s+", "", t)
        t = re.sub(r"\b(?:to my list|on my list|in my list|please)\b", "", t).strip()
        t = re.sub(r"\badd\s*$", "", t).strip()
        pieces = re.split(r"\s+(?:and|&|aur)\s+", t)
        commands = []
        for piece in pieces:
            quantity, unit, item = _number_and_unit(piece)
            item = re.sub(r"\b(?:of|some|for me)\b", "", item).strip(" ,.")
            if item:
                commands.append({"item": item, "quantity": quantity, "unit": unit})
        return {"intent": "add", "commands": commands}

    return {"intent": "unknown", "commands": []}


def parse_command(text: str, last_item: str | None = None) -> dict[str, Any]:
    parsed = _llm_parse(text, last_item)
    if parsed and parsed.get("intent") in {"add", "remove", "update", "search", "budget", "smart_basket", "seasonal"}:
        return parsed
    return _rule_parse(text, last_item)


def _resolve_product(item: str) -> dict[str, Any] | None:
    normalized = item.lower().strip()
    aliases = {
        "milk": "Classic Milk",
        "doodh": "Classic Milk",
        "water": "Drinking Water",
        "pani": "Drinking Water",
        "apples": "Fresh Apples",
        "apple": "Fresh Apples",
        "bananas": "Bananas",
        "banana": "Bananas",
        "bread": "Whole Wheat Bread",
        "eggs": "Farm Fresh Eggs",
        "egg": "Farm Fresh Eggs",
    }
    preferred = aliases.get(normalized)
    if preferred:
        exact = find_products(preferred)
        if exact:
            return exact[0]

    products = find_products(item)
    if not products:
        return None
    exact = [p for p in products if p["name"].lower() == normalized]
    if exact:
        return exact[0]
    starts = [p for p in products if p["name"].lower().startswith(normalized)]
    if starts:
        return sorted(starts, key=lambda p: p["price"])[0]
    return sorted(products, key=lambda p: (not bool(p["is_organic"]), p["price"]))[0]


def execute_command(text: str, last_item: str | None = None) -> dict[str, Any]:
    parsed = parse_command(text, last_item)
    intent = parsed.get("intent", "unknown")
    result: dict[str, Any] = {"intent": intent, "parsed": parsed, "items": [], "last_item": last_item}

    try:
        if intent == "add":
            for cmd in parsed.get("commands", []):
                item = str(cmd.get("item", "")).strip()
                if not item:
                    continue
                product = _resolve_product(item)
                if not product:
                    result["items"].append({"item": item, "error": "not_found"})
                    continue
                qty = float(cmd.get("quantity") or 1)
                unit = cmd.get("unit") or "item"
                saved = add_to_list(
                    item_name=product["name"],
                    quantity=qty,
                    unit=unit,
                    product_id=product["id"],
                    category=category_for(product["name"]),
                    unit_price=float(product["price"]),
                )
                sub = cheaper_substitutes(product)
                result["items"].append({**saved, "product": product, "substitute": sub})
                result["last_item"] = product["name"]

        elif intent == "remove":
            for cmd in parsed.get("commands", []):
                item = str(cmd.get("item", "")).strip()
                removed = remove_from_list(item)
                result["items"].extend(removed)
                if removed:
                    result["last_item"] = removed[0]["item_name"]

        elif intent == "update":
            for cmd in parsed.get("commands", []):
                item = str(cmd.get("item", "")).strip() or (last_item or "")
                if not item:
                    continue
                unit = cmd.get("unit") if cmd.get("unit") not in (None, "", "item") else None
                updated = update_list_item(item, float(cmd.get("quantity") or 1), unit)
                result["items"].append(updated or {"item": item, "error": "not_found"})
                if updated:
                    result["last_item"] = updated["item_name"]

        elif intent == "budget":
            from database import update_settings
            budget = float(parsed.get("budget") or 0)
            result["settings"] = update_settings(budget=budget)

        elif intent == "smart_basket":
            result["suggestions"] = smart_basket()

        elif intent == "seasonal":
            result["seasonal_picks"] = seasonal_recommendations()

        elif intent == "search":
            products = find_products(
                parsed.get("query") or "grocery",
                parsed.get("max_price"),
                parsed.get("organic"),
            )
            enriched = []
            from reviews_api import get_product_rating
            for p in products[:8]:
                enriched.append({**p, **get_product_rating(p["id"])})
            if parsed.get("min_rating") is not None:
                enriched = [p for p in enriched if p["average_rating"] >= float(parsed["min_rating"])]
            result["products"] = enriched
            result["query"] = parsed.get("query")

        else:
            result["error"] = "I can add, remove, update, search, manage your budget, check seasonal items, or build a smart basket."

    except Exception as exc:
        result["error"] = str(exc)

    record_message("user", text, intent)
    return result


def render_response(result: dict[str, Any]) -> str:
    intent = result.get("intent")
    if result.get("error") and intent == "unknown":
        return "I can add, remove, update, search, manage your budget, check seasonal items, or build a smart basket."

    if intent == "add":
        good = [x for x in result["items"] if "error" not in x]
        missing = [x["item"] for x in result["items"] if x.get("error") == "not_found"]
        lines = []
        for x in good:
            item_line = (
                f"✓ Added {x['quantity']:g} {x['item_name']}."
                if x["unit"] == "item"
                else f"✓ Added {x['quantity']:g} {x['unit']} of {x['item_name']}."
            )
            if x.get("substitute"):
                sub = x["substitute"]
                item_line += f"\n💡 *Savings Tip:* Consider **{sub['name']}** at ${sub['price']:.2f} instead!"
            lines.append(item_line)

        if missing:
            lines.append("I couldn't find: " + ", ".join(missing) + ". Try a product name or ask me to search.")
        return "\n\n".join(lines) or "I couldn't find anything to add."

    if intent == "remove":
        return (
            "✓ Removed " + ", ".join(x["item_name"] for x in result["items"])
            if result["items"] else "I couldn't find that item on your active list."
        )

    if intent == "update":
        good = [x for x in result["items"] if x and "error" not in x]
        return (
            "\n\n".join(
                f"✓ Updated {x['item_name']} to {x['quantity']:g}."
                if x["unit"] == "item"
                else f"✓ Updated {x['item_name']} to {x['quantity']:g} {x['unit']}."
                for x in good
            )
            if good else "I couldn't find that item on your active list."
        )

    if intent == "budget":
        s = result["settings"]
        return f"✓ Budget set to ${s['budget']:.2f}. I'll warn you before the basket goes over."

    if intent == "smart_basket":
        if not result.get("suggestions"):
            return "Your current list already covers the items I found from your shopping memory."
        lines = ["🧠 Smart Basket suggestions:"]
        for x in result["suggestions"]:
            lines.append(f"• {x['name']} — ${x['price']:.2f} — {x['reason']}")
        return "\n".join(lines)

    if intent == "seasonal":
        picks = result.get("seasonal_picks", [])
        if not picks:
            return "No seasonal items currently tagged."
        lines = ["🌿 **Fresh In-Season Items:**"]
        for p in picks:
            lines.append(f"• **{p['name']}** — ${p['price']:.2f} ({p.get('category', 'Produce')})")
        return "\n".join(lines)

    if intent == "search":
        products = result.get("products", [])
        if not products:
            return f"I couldn't find a match for '{result.get('query', 'that')}'."
        lines = [f"🔎 Matches for **{result.get('query')}**:"]
        for i, p in enumerate(products, 1):
            organic = "🌿 Organic" if p["is_organic"] else "Standard"
            lines.append(
                f"{i}. **{p['name']}** — ${p['price']:.2f} · ★ {p['average_rating']:.2f} "
                f"({p['review_count']} reviews) · {organic}"
            )
        return "\n\n".join(lines)

    return "I’m ready. What would you like to shop for?"