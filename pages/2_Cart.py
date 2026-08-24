import streamlit as st

from database import (
    clear_cart,
    get_settings,
    get_shopping_list,
    init_app_schema,
    remove_list_item_by_id,
    update_list_item_by_id,
)
from recommendations import budget_status
from theme import budget_tone, configure_page, fmt_money, render_header

configure_page("Cart")
init_app_schema()
render_header("Cart")

settings = get_settings()
items = get_shopping_list()

st.markdown(
    f"""
<div class="section fade-in" style="margin-top:0;">
  <div class="section-title" style="font-size:22px;">Your cart</div>
  <div class="section-meta">{len(items)} item(s)</div>
</div>
""",
    unsafe_allow_html=True,
)

if not items:
    st.markdown(
        '<div class="card empty-state"><div class="mark">VC</div><b>Your cart is empty</b>'
        '<div style="font-size:12px;margin-top:5px;">Browse the catalog or ask the assistant on Home to add something.</div></div>',
        unsafe_allow_html=True,
    )
    st.page_link("pages/1_Catalog.py", label="Go to catalog")
else:
    for item in items:
        row = st.container()
        with row:
            c1, c2, c3, c4, c5 = st.columns([0.6, 2.6, 1.2, 1, 0.8])
            with c1:
                st.markdown(f'<div class="cart-icon">{item["item_name"][:2].upper()}</div>', unsafe_allow_html=True)
            with c2:
                st.markdown(
                    f'<div class="cart-name">{item["item_name"].title()}</div>'
                    f'<div class="cart-meta">{fmt_money(item["unit_price"])} each &middot; {item["category"] or "Other"}</div>',
                    unsafe_allow_html=True,
                )
            with c3:
                new_qty = st.number_input(
                    "Qty",
                    min_value=0.0,
                    step=1.0,
                    value=float(item["quantity"]),
                    key=f"qty_{item['id']}",
                    label_visibility="collapsed",
                )
                if new_qty != float(item["quantity"]):
                    update_list_item_by_id(item["id"], new_qty)
                    st.rerun()
            with c4:
                st.markdown(
                    f'<div class="cart-total" style="text-align:right;padding-top:8px;">'
                    f'{fmt_money(item["quantity"] * item["unit_price"])}</div>',
                    unsafe_allow_html=True,
                )
            with c5:
                if st.button("Remove", key=f"remove_{item['id']}", use_container_width=True):
                    remove_list_item_by_id(item["id"])
                    st.rerun()
        st.markdown('<hr class="hr">', unsafe_allow_html=True)

    status = budget_status()
    tone, bar_color, tag = budget_tone(status)
    pct = min(status["percent"] / 100, 1.0) if status["budget"] else 0
    item_count = sum(x["quantity"] for x in items)

    st.markdown(
        f'''<div class="section"><div class="totals totals-{tone}">
        <div class="totals-row"><span>Items</span><span>{item_count:g}</span></div>
        <div class="totals-row"><span>Budget</span><span>{fmt_money(status["budget"])}</span></div>
        <div class="totals-row grand"><span>Cart total</span><span>{fmt_money(status.get("total", status.get("spent", 0.0)))}</span></div>
        <div class="bar"><div class="bar-fill" style="width:{pct*100:.1f}%;background:{bar_color};"></div></div>
        <div style="font-size:11px;margin-top:8px;color:rgba(255,255,255,.75);">{tag}</div>
        </div></div>''',
        unsafe_allow_html=True,
    )

    action_cols = st.columns([1, 1.4])
    with action_cols[0]:
        if st.button("Clear cart", use_container_width=True):
            clear_cart()
            st.rerun()
    with action_cols[1]:
        st.page_link("pages/3_Checkout.py", label="Proceed to checkout", use_container_width=True)