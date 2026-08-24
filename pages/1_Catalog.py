import streamlit as st

from database import (
    add_to_list,
    category_for,
    get_all_products,
    get_categories,
    init_app_schema,
)
from theme import configure_page, fmt_money, render_header

configure_page("Catalog")
init_app_schema()
render_header("Catalog")

st.markdown(
    """
<div class="section fade-in" style="margin-top:0;">
  <div class="section-title" style="font-size:22px;">Browse the catalog</div>
  <div class="section-meta">Search, filter, and add items straight to your cart</div>
</div>
""",
    unsafe_allow_html=True,
)

try:
    categories = ["All"] + get_categories()
except Exception:
    categories = ["All"]

filter_cols = st.columns([2, 1.2, 1])
with filter_cols[0]:
    search = st.text_input("Search products", placeholder="Search products...", label_visibility="collapsed")
with filter_cols[1]:
    category = st.selectbox("Category", categories, label_visibility="collapsed")
with filter_cols[2]:
    organic_only = st.toggle("Organic only", value=False)

try:
    products = get_all_products(
        category=category if category != "All" else None,
        organic=True if organic_only else None,
        search=search or None,
    )
except Exception as exc:
    products = []
    st.error(f"Could not load the catalog: {exc}")

st.markdown(f'<div class="section-meta" style="margin:14px 0 6px;">{len(products)} product(s)</div>', unsafe_allow_html=True)

if not products:
    st.markdown(
        '<div class="card empty-state"><div class="mark">--</div><b>No products match your filters</b>'
        '<div style="font-size:12px;margin-top:5px;">Try a different search term or clear the category filter.</div></div>',
        unsafe_allow_html=True,
    )
else:
    cols_per_row = 2
    rows = [products[i:i + cols_per_row] for i in range(0, len(products), cols_per_row)]
    for row in rows:
        cols = st.columns(cols_per_row)
        for col, product in zip(cols, row):
            with col:
                organic_tag = '<span class="tag tag-green">Organic</span>' if product.get("is_organic") else '<span class="tag">Standard</span>'
                description = (product.get("description") or "").strip()
                st.markdown(
                    f'''<div class="product-card fade-in">
                        <div class="product-cat">{product.get("category", "Other")}</div>
                        <div class="product-name">{product["name"]}</div>
                        <div class="product-desc">{description[:90]}{"..." if len(description) > 90 else ""}</div>
                        <div style="display:flex;justify-content:space-between;align-items:center;margin-top:10px;">
                          <div class="product-price">{fmt_money(product["price"])}</div>
                          {organic_tag}
                        </div>
                    </div>''',
                    unsafe_allow_html=True,
                )
                if st.button("Add to cart", key=f"add_{product['id']}", use_container_width=True):
                    add_to_list(
                        item_name=product["name"],
                        quantity=1,
                        unit="item",
                        product_id=product["id"],
                        category=product.get("category") or category_for(product["name"]),
                        unit_price=float(product["price"]),
                    )
                    st.toast(f"Added {product['name']} to your cart", icon=None)
                    st.rerun()