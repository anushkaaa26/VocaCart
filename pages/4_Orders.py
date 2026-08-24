import streamlit as st
from database import get_transactions, get_transaction_items


def fmt_money(amount: float) -> str:
    """Format numeric values to currency strings safely."""
    try:
        return f"${float(amount):,.2f}"
    except (ValueError, TypeError):
        return "$0.00"


st.set_page_config(page_title="Order History", page_icon="📦")
st.title("Order History")
st.caption("View past purchases and receipt details")

# Retrieve transactions from database, fallback to empty list if function fails
try:
    orders = get_transactions()
except Exception:
    orders = []

# If no DB transactions exist, check for last order in session state
if not orders and st.session_state.get("last_order"):
    orders = [st.session_state.last_order]

if not orders:
    st.info("No past orders found.")
    st.page_link("pages/1_Catalog.py", label="Start shopping", use_container_width=True)
else:
    for order in orders:
        # Safe extractions to prevent KeyErrors
        order_id = order.get("id", order.get("transaction_id", "N/A"))
        total_amt = fmt_money(order.get("total", order.get("total_amount", 0.0)))
        created_at = order.get("created_at", order.get("timestamp", "Recent"))
        payment_method = order.get("payment_method", "Card").capitalize()
        status_str = order.get("status", "Completed").capitalize()

        # Fetch items safely
        items = order.get("items")
        if items is None:
            try:
                items = get_transaction_items(order_id)
            except Exception:
                items = []

        item_count = order.get("item_count")
        if item_count is None:
            item_count = sum(int(item.get("quantity", 1)) for item in items) if isinstance(items, list) else len(items)

        # Render Order Container Card
        with st.expander(f"Order #{order_id} — {total_amt} ({created_at})", expanded=False):
            st.markdown(
                f'<div style="font-size:13px;color:var(--muted);margin-bottom:12px;">'
                f'Status: <strong>{status_str}</strong> &middot; '
                f'Items: <strong>{item_count}</strong> &middot; '
                f'Payment: <strong>{payment_method}</strong>'
                f'</div>',
                unsafe_allow_html=True,
            )

            if items:
                for item in items:
                    name = item.get("name", item.get("product_name", "Item"))
                    qty = item.get("quantity", 1)
                    price = item.get("unit_price", item.get("price", 0.0))
                    st.write(f"• **{name}** x{qty} — {fmt_money(float(price) * float(qty))}")
            else:
                st.caption("No itemized details available for this order.")