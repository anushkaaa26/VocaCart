import streamlit as st

from database import checkout as db_checkout
from database import get_settings, get_shopping_list, init_app_schema
from recommendations import budget_status
from theme import budget_tone, configure_page, fmt_money, render_header

configure_page("Checkout")
init_app_schema()
render_header("Checkout")

if "last_order" not in st.session_state:
    st.session_state.last_order = None

settings = get_settings()
items = get_shopping_list()

st.markdown(
    """
<div class="section fade-in" style="margin-top:0;">
  <div class="section-title" style="font-size:22px;">Checkout</div>
  <div class="section-meta">Review your order and confirm</div>
</div>
""",
    unsafe_allow_html=True,
)

if st.session_state.get("last_order"):
    order = st.session_state.last_order
    
    # Safely extract order details to prevent KeyErrors
    order_id = order.get("id", "N/A")
    total_val = fmt_money(order.get("total", 0.0))
    pay_method = order.get("payment_method", "N/A")
    
    # Safely compute item count if missing from order dict
    item_count = order.get("item_count")
    if item_count is None:
        items = order.get("items", [])
        item_count = sum(int(item.get("quantity", 1)) for item in items) if isinstance(items, list) else 0

    st.markdown(
        f'''<div class="card fade-in" style="text-align:center;padding:32px 20px;">
        <div class="tag tag-green" style="margin-bottom:10px;">Order placed</div>
        <div style="font-size:20px;font-weight:900;margin-bottom:6px;">Order #{order_id} confirmed</div>
        <div style="color:var(--muted);font-size:13px;">Total charged: {total_val} &middot; {item_count} item(s) &middot; paid via {pay_method}</div>
        </div>''',
        unsafe_allow_html=True,
    )
    o1, o2 = st.columns(2)
    with o1:
        st.page_link("pages/4_Orders.py", label="View order history", use_container_width=True)
    with o2:
        st.page_link("pages/1_Catalog.py", label="Continue shopping", use_container_width=True)
    if st.button("Start a new order", use_container_width=True):
        st.session_state.last_order = None
        st.rerun()

elif not items:
    st.markdown(
        '<div class="card empty-state"><div class="mark">VC</div><b>Your cart is empty</b>'
        '<div style="font-size:12px;margin-top:5px;">Add items from the catalog before checking out.</div></div>',
        unsafe_allow_html=True,
    )
    st.page_link("pages/1_Catalog.py", label="Go to catalog")

else:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    for item in items:
        st.markdown(
            f'<div class="cart-row"><div class="cart-icon">{item["item_name"][:2].upper()}</div>'
            f'<div style="flex:1"><div class="cart-name">{item["item_name"].title()}</div>'
            f'<div class="cart-meta">{item["quantity"]:g} {item["unit"]} &middot; {fmt_money(item["unit_price"])} each</div></div>'
            f'<div class="cart-total">{fmt_money(item["quantity"] * item["unit_price"])}</div></div>',
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

    status = budget_status()
    tone, bar_color, tag = budget_tone(status)
    pct = min(status["percent"] / 100, 1.0) if status["budget"] else 0

    st.markdown(
        f'''<div class="section"><div class="totals totals-{tone}">
        <div class="totals-row"><span>Subtotal</span><span>{fmt_money(status.get("total", status.get("spent", 0.0)))}</span></div>
        <div class="totals-row"><span>Delivery</span><span>Free</span></div>
        <div class="totals-row grand"><span>Total due</span><span>{fmt_money(status.get("total", status.get("spent", 0.0)))}</span></div>
        <div class="bar"><div class="bar-fill" style="width:{pct*100:.1f}%;background:{bar_color};"></div></div>
        <div style="font-size:11px;margin-top:8px;color:rgba(255,255,255,.75);">{tag} against your {fmt_money(status["budget"])} budget</div>
        </div></div>''',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section"><div class="section-title">Delivery details</div></div>', unsafe_allow_html=True)
    with st.form("checkout_form"):
        name = st.text_input("Full name", placeholder="Your name")
        address = st.text_area("Delivery address", placeholder="Address line, city, PIN code", height=80)
        payment_method = st.radio("Payment method", ["Card", "UPI", "Cash on delivery"], horizontal=True)
        agree = st.checkbox("This is a demo checkout - no real payment will be taken", value=True, disabled=True)
        submitted = st.form_submit_button("Place order", use_container_width=True, type="primary")

        if submitted:
            if not name.strip() or not address.strip():
                st.warning("Please fill in your name and delivery address.")
            else:
                outcome = db_checkout(
                    payment_method=payment_method,
                    customer_name=name.strip(),
                    address=address.strip(),
                )
                if outcome.get("success"):
                    st.session_state.last_order = outcome.get("transaction", outcome.get("order", outcome))
                    st.rerun()
                else:
                    st.error("Could not place the order. Your cart may have just emptied out.")