"""Shared UI theme, top navigation, and small helpers for the VocaCart
multipage app. Imported by Home.py and every file under pages/.

No emoji are used anywhere in this module or in the pages that use it.
"""
from __future__ import annotations

import re
from typing import Any

import streamlit as st

from database import get_settings, get_shopping_list

PAGES: dict[str, str] = {
    "Home": "Home.py",
    "Catalog": "pages/1_Catalog.py",
    "Cart": "pages/2_Cart.py",
    "Checkout": "pages/3_Checkout.py",
    "Orders": "pages/4_Orders.py",
}

# Matches pictographic / emoji characters so we can strip them out of text
# that comes back from shopping_agent.render_response()
_EMOJI_PATTERN = re.compile(
    "["
    "\U0001F300-\U0001FAFF"
    "\U00002600-\U000027BF"
    "\U0001F1E6-\U0001F1FF"
    "\U00002B00-\U00002BFF"
    "]+",
    flags=re.UNICODE,
)


def strip_emoji(text: str | None) -> str:
    """Remove emoji/pictographic characters and stray markdown bold markers."""
    if not text:
        return ""
    cleaned = _EMOJI_PATTERN.sub("", text)
    cleaned = cleaned.replace("**", "")
    cleaned = re.sub(r"[ \t]{2,}", " ", cleaned)
    return "\n".join(line.strip() for line in cleaned.split("\n")).strip()


def cart_count() -> int:
    return len(get_shopping_list())


def cart_total() -> float:
    items = get_shopping_list()
    return round(sum(float(x["quantity"]) * float(x["unit_price"]) for x in items), 2)


def fmt_money(amount: float, currency: str | None = None) -> str:
    if currency is None:
        try:
            currency = get_settings().get("currency", "$")
        except Exception:
            currency = "$"
    return f"{currency}{amount:,.2f}"


def _theme_css(dark: bool) -> str:
    theme_vars = (
        """
      --bg:#1a1817;
      --surface:#262321;
      --surface2:#332f2c;
      --text:#f4f1ea;
      --muted:#9e978e;
      --border:#3b3733;
      --accent:#de9b72;
      --accent-dark:#e5ad8a;
      --accent-soft:#423228;
      --green:#5bb974;
      --green-bg:#1b3323;
      --warn:#e3a246;
      --warn-bg:#3d2c14;
      --danger:#e86464;
      --danger-bg:#3d1a1a;
      --shadow:0 12px 32px rgba(0,0,0,.35);
      --mark-fg:#1a1817;
        """
        if dark
        else """
      --bg:#faf8f5;
      --surface:#ffffff;
      --surface2:#f4f0e8;
      --text:#2c2825;
      --muted:#8c857b;
      --border:#ebe7df;
      --accent:#c87d55;
      --accent-dark:#a8603b;
      --accent-soft:#f7efea;
      --green:#409156;
      --green-bg:#e5f5eb;
      --warn:#b37b2d;
      --warn-bg:#fcf2e3;
      --danger:#d94848;
      --danger-bg:#fae8e8;
      --shadow:0 8px 24px rgba(44,40,37,.04);
      --mark-fg:#ffffff;
        """
    )

    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&family=Playfair+Display:wght@600;700;800&display=swap');

:root {{
{theme_vars}
}}

* {{ box-sizing:border-box; }}
html, body, [class*="css"] {{ font-family:'DM Sans',sans-serif !important; }}
.stApp {{ background:var(--bg); color:var(--text); transition:background .3s ease, color .3s ease; }}
.block-container {{ max-width:820px; padding:1.1rem 1rem 4rem !important; }}
#MainMenu, footer, header {{ visibility:hidden; }}
h1,h2,h3,p {{ color:var(--text); }}
[data-testid="stSidebarNav"] {{ display:none; }}

@keyframes fadeUp {{
  from {{ opacity:0; transform:translateY(8px); }}
  to {{ opacity:1; transform:translateY(0); }}
}}
.fade-in {{ animation:fadeUp .4s ease both; }}

/* Brand mark */
.vc-brand {{ display:flex; align-items:center; gap:12px; }}
.vc-mark {{ width:44px; height:44px; border-radius:10px; background:var(--accent); color:var(--mark-fg); display:flex; align-items:center; justify-content:center; font-family:'Playfair Display', serif; font-size:18px; font-weight:800; letter-spacing:.02em; flex-shrink:0; }}
.vc-name {{ font-family:'Playfair Display', serif; font-size:24px; font-weight:800; letter-spacing:-.2px; line-height:1.1; color:var(--text); }}
.vc-sub {{ font-size:12px; color:var(--muted); margin-top:2px; font-weight:500; }}

/* Top nav */
.topnav-wrap {{ margin:14px 0 22px; padding:6px; background:var(--surface); border:1px solid var(--border); border-radius:12px; box-shadow:var(--shadow); }}
.topnav-wrap [data-testid="stPageLink"] a, .nav-pill {{
  display:block; text-align:center; padding:10px 8px; border-radius:8px;
  font-size:13px; font-weight:600; text-decoration:none !important;
  color:var(--muted) !important; transition:background .2s ease, color .2s ease;
}}
.topnav-wrap [data-testid="stPageLink"] a:hover {{ background:var(--surface2); color:var(--text) !important; }}
.nav-pill-active {{ background:var(--accent); color:var(--mark-fg) !important; }}

/* Hero Header */
.hero-wrap {{ text-align:center; padding:24px 12px 16px; }}
.hero-title {{ font-family:'Playfair Display', serif; font-size:32px; font-weight:800; color:var(--text); margin-bottom:8px; letter-spacing:-.5px; }}
.hero-subtitle {{ font-size:14px; color:var(--muted); max-width:480px; margin:0 auto 16px auto; line-height:1.5; }}

/* Custom Audio Input Container */
[data-testid="stAudioInput"] {{
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: 40px !important;
  padding: 6px 14px !important;
  box-shadow: var(--shadow) !important;
  max-width: 520px;
  margin: 16px auto 24px auto !important;
}}
[data-testid="stAudioInput"]:hover {{
  border-color: var(--accent) !important;
}}

/* Message Display Cards */
.msg-user {{ background:var(--surface2); border:1px solid var(--border); border-radius:14px 14px 2px 14px; padding:12px 16px; margin:10px 0 10px auto; max-width:85%; font-size:13.5px; color:var(--text); }}
.msg-agent {{ background:var(--surface); border:1px solid var(--border); border-radius:14px 14px 14px 2px; padding:14px 18px; margin:10px auto 10px 0; max-width:90%; font-size:13.5px; color:var(--text); box-shadow:var(--shadow); line-height:1.6; }}

/* Cards */
.card {{ background:var(--surface); border:1px solid var(--border); border-radius:12px; padding:20px; box-shadow:var(--shadow); }}
.section {{ margin-top:32px; }}
.section-head {{ display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; }}
.section-title {{ font-family:'Playfair Display', serif; font-size:20px; font-weight:700; color:var(--text); }}
.section-meta {{ color:var(--muted); font-size:12px; font-weight:500; }}
.hr {{ height:1px; background:var(--border); border:0; margin:16px 0; }}

/* Badges / tags */
.tag {{ display:inline-block; padding:4px 10px; border-radius:6px; font-size:11px; font-weight:600; background:var(--surface2); color:var(--text); border:1px solid var(--border); }}
.tag-green {{ background:var(--green-bg); color:var(--green); border-color:transparent; }}
.tag-warn {{ background:var(--warn-bg); color:var(--warn); border-color:transparent; }}
.tag-danger {{ background:var(--danger-bg); color:var(--danger); border-color:transparent; }}
.tag-accent {{ background:var(--accent-soft); color:var(--accent-dark); border-color:transparent; }}

/* Product grid */
.product-card {{ background:var(--surface); border:1px solid var(--border); border-radius:12px; padding:20px; height:100%; box-shadow:var(--shadow); transition:transform .2s ease; }}
.product-card:hover {{ transform:translateY(-3px); }}
.product-name {{ font-family:'Playfair Display', serif; font-size:17px; font-weight:700; line-height:1.2; margin-bottom:4px; color:var(--text); }}
.product-cat {{ font-size:11px; color:var(--muted); text-transform:uppercase; letter-spacing:.08em; font-weight:600; }}
.product-desc {{ font-size:13px; color:var(--muted); line-height:1.6; margin:12px 0; min-height:42px; }}
.product-price {{ font-size:18px; font-weight:600; color:var(--text); }}

/* Cart rows */
.cart-row {{ display:flex; align-items:center; gap:16px; padding:16px 4px; border-bottom:1px solid var(--border); }}
.cart-row:last-child {{ border-bottom:0; }}
.cart-icon {{ width:48px; height:48px; border-radius:8px; background:var(--accent-soft); color:var(--accent-dark); display:flex; align-items:center; justify-content:center; font-family:'Playfair Display', serif; font-size:16px; font-weight:700; flex-shrink:0; }}
.cart-name {{ font-family:'Playfair Display', serif; font-size:15px; font-weight:700; color:var(--text); }}
.cart-meta {{ font-size:12px; color:var(--muted); margin-top:4px; }}
.cart-total {{ font-size:15px; font-weight:600; color:var(--text); white-space:nowrap; }}

/* Budget / totals block */
.totals {{ border-radius:12px; padding:24px; box-shadow:var(--shadow); }}
.totals-ok {{ background:var(--surface2); color:var(--text); border:1px solid var(--border); }}
.totals-warn {{ background:var(--warn-bg); color:var(--warn); }}
.totals-over {{ background:var(--danger-bg); color:var(--danger); }}
.totals-row {{ display:flex; justify-content:space-between; font-size:13px; padding:6px 0; font-weight:500; }}
.totals-row.grand {{ font-family:'Playfair Display', serif; font-size:18px; font-weight:700; border-top:1px solid var(--border); margin-top:12px; padding-top:16px; }}
.bar {{ height:6px; background:var(--border); border-radius:4px; overflow:hidden; margin-top:14px; }}
.bar-fill {{ height:100%; border-radius:4px; background:var(--accent); transition:width .5s ease; }}

/* Empty state */
.empty-state {{ text-align:center; padding:40px 20px; color:var(--muted); }}
.empty-state .mark {{ width:52px; height:52px; margin:0 auto 14px; border-radius:12px; background:var(--surface2); display:flex; align-items:center; justify-content:center; font-weight:700; font-size:14px; color:var(--muted); }}

/* Streamlit controls */
.stButton button {{ border-radius:8px !important; border:1px solid var(--border) !important; background:var(--surface) !important; color:var(--text) !important; font-weight:600 !important; font-size:13px !important; transition:all .2s ease !important; }}
.stButton button:hover {{ border-color:var(--accent) !important; color:var(--accent-dark) !important; }}
button[kind="primary"] {{ background:var(--accent) !important; border-color:var(--accent) !important; color:var(--mark-fg) !important; }}
button[kind="primary"]:hover {{ background:var(--accent-dark) !important; color:var(--mark-fg) !important; }}
[data-testid="stChatInput"] {{ border:1px solid var(--border) !important; border-radius:12px !important; background:var(--surface) !important; }}
.stTabs [data-baseweb="tab-list"] {{ gap:4px; }}
.stTabs [data-baseweb="tab"] {{ font-size:13px; font-weight:600; }}
[data-testid="stExpander"] {{ border:1px solid var(--border) !important; border-radius:12px !important; background:var(--surface) !important; }}
[data-testid="stTextInput"] input, [data-testid="stNumberInput"] input, [data-testid="stSelectbox"] {{ border-radius:8px !important; }}

@media (max-width:600px) {{
  .block-container {{ padding-left:16px !important; padding-right:16px !important; }}
  .vc-sub {{ display:none; }}
}}
</style>
"""


def configure_page(title: str) -> None:
    """Must be the first Streamlit call in a page script."""
    st.set_page_config(
        page_title=f"VocaCart | {title}",
        page_icon="VC",
        layout="centered",
        initial_sidebar_state="collapsed",
    )
    if "dark_mode" not in st.session_state:
        st.session_state.dark_mode = False
    st.markdown(_theme_css(st.session_state.dark_mode), unsafe_allow_html=True)


def render_header(active: str) -> None:
    left, right = st.columns([3, 1.2])
    with left:
        st.markdown(
            """
<div class="vc-brand fade-in">
  <div class="vc-mark">VC</div>
  <div><div class="vc-name">VocaCart</div><div class="vc-sub">Voice-first grocery shopping</div></div>
</div>
""",
            unsafe_allow_html=True,
        )
    with right:
        b1, b2 = st.columns([1, 1])
        with b1:
            if st.button("Dark" if not st.session_state.dark_mode else "Light", key=f"theme_toggle_{active}"):
                st.session_state.dark_mode = not st.session_state.dark_mode
                st.rerun()
        with b2:
            st.markdown(
                f'<div class="tag tag-accent" style="text-align:center;padding-top:10px;padding-bottom:10px;">'
                f'{cart_count()} in cart</div>',
                unsafe_allow_html=True,
            )

    render_nav(active)


def render_nav(active: str) -> None:
    st.markdown('<div class="topnav-wrap">', unsafe_allow_html=True)
    cols = st.columns(len(PAGES))
    count = cart_count()
    for col, (label, path) in zip(cols, PAGES.items()):
        with col:
            display = f"Cart ({count})" if label == "Cart" and count else label
            if label == active:
                st.markdown(f'<div class="nav-pill nav-pill-active">{display}</div>', unsafe_allow_html=True)
            else:
                st.page_link(path, label=display)
    st.markdown("</div>", unsafe_allow_html=True)


def budget_tone(status: dict[str, Any]) -> tuple[str, str, str]:
    """Returns (css_class_suffix, bar_color, tag_text) for a budget_status dict."""
    pct = min(status.get("percent", 0) / 100, 1.0) if status.get("budget") else 0
    if status.get("over"):
        return "over", "var(--danger)", "Over budget"
    if pct >= 0.85:
        return "warn", "var(--warn)", "Getting close"
    return "ok", "#ffffff", "On track"


def initials(name: str) -> str:
    parts = [p for p in re.split(r"\s+", name.strip()) if p]
    if not parts:
        return "?"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[1][0]).upper()