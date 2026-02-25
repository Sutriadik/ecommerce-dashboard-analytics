import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import warnings
import json
import urllib.request
import folium
from streamlit_folium import st_folium

warnings.filterwarnings("ignore")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Brazil E-Commerce Analytics",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════════════
# GLOBAL STYLE
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(160deg, #0f172a 0%, #1e293b 100%);
    border-right: 1px solid #334155;
}
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
[data-testid="stSidebar"] .stMarkdown h2 {
    color: #38bdf8 !important;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    font-weight: 700;
    margin-bottom: 0.5rem;
}

/* ── Main background ── */
.main .block-container {
    background: #f8fafc;
    padding: 2rem 2.5rem;
    max-width: 1400px;
}

/* ── KPI Cards ── */
.kpi-grid { display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 1.5rem; }
.kpi-card {
    flex: 1; min-width: 180px;
    background: white;
    border-radius: 16px;
    padding: 1.25rem 1.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
    border-top: 3px solid var(--accent);
    transition: transform 0.2s, box-shadow 0.2s;
}
.kpi-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.1);
}
.kpi-label {
    font-size: 0.7rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.1em;
    color: #64748b; margin-bottom: 0.35rem;
}
.kpi-value {
    font-size: 1.7rem; font-weight: 800;
    color: #0f172a; line-height: 1;
    font-family: 'JetBrains Mono', monospace;
}
.kpi-delta {
    font-size: 0.72rem; margin-top: 0.3rem;
    color: #10b981; font-weight: 600;
}

/* ── Section headers ── */
.section-header {
    display: flex; align-items: center; gap: 0.75rem;
    margin: 2rem 0 1rem;
    padding-bottom: 0.75rem;
    border-bottom: 2px solid #e2e8f0;
}
.section-header .icon {
    width: 36px; height: 36px;
    background: #eff6ff;
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem;
}
.section-header h2 {
    font-size: 1.1rem; font-weight: 700;
    color: #1e293b; margin: 0;
}
.section-header p {
    font-size: 0.78rem; color: #64748b;
    margin: 0.1rem 0 0;
}

/* ── Chart containers ── */
.chart-card {
    background: white;
    border-radius: 16px;
    padding: 1.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    margin-bottom: 1rem;
}

/* ── Insight box ── */
.insight-box {
    background: linear-gradient(135deg, #eff6ff 0%, #f0fdf4 100%);
    border-left: 4px solid #3b82f6;
    border-radius: 0 12px 12px 0;
    padding: 1rem 1.25rem;
    margin-top: 1rem;
    font-size: 0.85rem;
    color: #1e293b;
    line-height: 1.6;
}
.insight-box strong { color: #1d4ed8; }

/* ── Tab styling ── */
[data-baseweb="tab"] { font-weight: 600 !important; font-size: 0.88rem !important; }
[data-baseweb="tab-list"] { gap: 0.25rem; }
[aria-selected="true"] { color: #2563eb !important; }

/* ── Segment badge ── */
.seg-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.05em;
}

/* ── Page title ── */
.page-title {
    font-size: 1.9rem; font-weight: 800;
    color: #0f172a; margin-bottom: 0.2rem;
}
.page-subtitle {
    font-size: 0.9rem; color: #64748b;
    margin-bottom: 1.5rem;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# COLOR PALETTE
# ══════════════════════════════════════════════════════════════════════════════
PRIMARY   = "#2563eb"
SECONDARY = "#0ea5e9"
SUCCESS   = "#10b981"
WARNING   = "#f59e0b"
DANGER    = "#ef4444"
PURPLE    = "#8b5cf6"

SEG_COLORS = {
    "Champions":           "#2563eb",
    "Loyal Customers":     "#0ea5e9",
    "Potential Loyalists": "#10b981",
    "At Risk":             "#f59e0b",
    "Lost":                "#ef4444",
}

STATE_NAMES = {
    "SP":"São Paulo",        "RJ":"Rio de Janeiro",   "MG":"Minas Gerais",
    "RS":"Rio Grande do Sul","PR":"Paraná",            "SC":"Santa Catarina",
    "BA":"Bahia",            "DF":"Distrito Federal", "GO":"Goiás",
    "ES":"Espírito Santo",   "PE":"Pernambuco",       "CE":"Ceará",
    "PA":"Pará",             "MA":"Maranhão",          "MT":"Mato Grosso",
    "MS":"Mato G. do Sul",   "RN":"Rio G. do Norte",  "PB":"Paraíba",
    "AL":"Alagoas",          "SE":"Sergipe",           "PI":"Piauí",
    "TO":"Tocantins",        "RO":"Rondônia",          "AC":"Acre",
    "AM":"Amazonas",         "RR":"Roraima",           "AP":"Amapá",
}

# ══════════════════════════════════════════════════════════════════════════════
# LOAD DATA
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data
def load_data():
    df = pd.read_csv("dashboard/main_data.csv")
    datetime_cols = [
        "order_purchase_timestamp", "order_approved_at",
        "order_delivered_carrier_date", "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]
    for c in datetime_cols:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce")
    df["product_category_name_english"] = df["product_category_name_english"].fillna("others")
    return df


@st.cache_data
def load_geojson():
    url = (
        "https://raw.githubusercontent.com/codeforamerica/"
        "click_that_hood/master/public/data/brazil-states.geojson"
    )
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            gj = json.load(resp)
        for f in gj["features"]:
            f["properties"]["state"] = f["properties"].get("sigla", "")
        return gj
    except Exception:
        return None


df = load_data()

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🛒 Brazil E-Commerce")
    st.markdown("---")

    st.markdown("## 📅 Date Range")
    min_d = df["order_purchase_timestamp"].dt.date.min()
    max_d = df["order_purchase_timestamp"].dt.date.max()
    date_range = st.date_input(
        "Order Date", value=[min_d, max_d],
        min_value=min_d, max_value=max_d, label_visibility="collapsed"
    )
    st.markdown("## 🏷️ Category Filter")
    all_cats = sorted(df["product_category_name_english"].dropna().unique())
    selected_cats = st.multiselect(
        "Categories", all_cats, default=[], placeholder="All categories",
        label_visibility="collapsed"
    )

    st.markdown("## 🌎 State Filter")
    all_states = sorted(df["customer_state"].dropna().unique())
    selected_states = st.multiselect(
        "States", all_states, default=[], placeholder="All states",
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("""
    <div style="font-size:0.72rem; color:#94a3b8; line-height:1.7;">
    📊 <b>Data Source</b><br>
    Olist Brazilian E-Commerce<br><br>
    📅 <b>Period</b><br>
    Oct 2016 – Aug 2018<br><br>
    🗂️ <b>Dataset</b><br>
    ~115K delivered orders
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# APPLY FILTERS
# ══════════════════════════════════════════════════════════════════════════════
filtered = df.copy()
if len(date_range) == 2:
    filtered = filtered[
        (filtered["order_purchase_timestamp"].dt.date >= date_range[0]) &
        (filtered["order_purchase_timestamp"].dt.date <= date_range[1])
    ]
if selected_cats:
    filtered = filtered[filtered["product_category_name_english"].isin(selected_cats)]
if selected_states:
    filtered = filtered[filtered["customer_state"].isin(selected_states)]

# ══════════════════════════════════════════════════════════════════════════════
# PAGE HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<p class="page-title">🛒 Brazil E-Commerce Analytics</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="page-subtitle">Dashboard analitik interaktif berbasis dataset publik Olist '
    '— mencakup tren penjualan, performa kategori, distribusi geografis, dan segmentasi pelanggan RFM.</p>',
    unsafe_allow_html=True,
)

# ══════════════════════════════════════════════════════════════════════════════
# KPI METRICS
# ══════════════════════════════════════════════════════════════════════════════
total_revenue   = filtered["payment_value"].sum()
total_orders    = filtered["order_id"].nunique()
total_customers = filtered["customer_unique_id"].nunique()
avg_order_val   = total_revenue / total_orders if total_orders else 0

# Delivery on-time
if "order_delivered_customer_date" in filtered.columns and "order_estimated_delivery_date" in filtered.columns:
    dlv = filtered.dropna(subset=["order_delivered_customer_date", "order_estimated_delivery_date"])
    dlv = dlv.drop_duplicates("order_id")
    on_time_pct = (~(dlv["order_delivered_customer_date"] > dlv["order_estimated_delivery_date"])).mean() * 100
else:
    on_time_pct = 0.0

st.markdown(f"""
<div class="kpi-grid">
  <div class="kpi-card" style="--accent:{PRIMARY}">
    <div class="kpi-label">💰 Total Revenue</div>
    <div class="kpi-value">${total_revenue/1e6:.2f}M</div>
    <div class="kpi-delta">Delivered orders only</div>
  </div>
  <div class="kpi-card" style="--accent:{SECONDARY}">
    <div class="kpi-label">📦 Total Orders</div>
    <div class="kpi-value">{total_orders:,}</div>
    <div class="kpi-delta">Unique order IDs</div>
  </div>
  <div class="kpi-card" style="--accent:{SUCCESS}">
    <div class="kpi-label">👥 Unique Customers</div>
    <div class="kpi-value">{total_customers:,}</div>
    <div class="kpi-delta">Distinct customer IDs</div>
  </div>
  <div class="kpi-card" style="--accent:{WARNING}">
    <div class="kpi-label">🧾 Avg Order Value</div>
    <div class="kpi-value">${avg_order_val:.0f}</div>
    <div class="kpi-delta">Per unique order</div>
  </div>
  <div class="kpi-card" style="--accent:{PURPLE}">
    <div class="kpi-label">🚚 On-Time Delivery</div>
    <div class="kpi-value">{on_time_pct:.1f}%</div>
    <div class="kpi-delta">Of delivered orders</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈  Sales Trend",
    "🏷️  Category Performance",
    "🗺️  Geographic Distribution",
    "👥  RFM Segmentation",
    "💳  Additional Insights",
])

# ═══════════════════════════════════════════════════════════════════════════
# TAB 1 ── SALES TREND (Pertanyaan 1)
# ═══════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("""
    <div class="section-header">
      <div class="icon">📈</div>
      <div>
        <h2>Tren Penjualan Bulanan</h2>
        <p>Pertanyaan 1: Bagaimana performa tren penjualan bulanan secara historis?</p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Compute monthly data ──────────────────────────────────────────────
    monthly_df = filtered.drop_duplicates("order_id").copy()
    monthly_df["order_month"] = monthly_df["order_purchase_timestamp"].dt.to_period("M")
    monthly_revenue = (
        monthly_df.groupby("order_month")
        .agg(revenue=("payment_value","sum"), orders=("order_id","nunique"))
        .reset_index()
    )
    monthly_revenue["month_str"] = monthly_revenue["order_month"].astype(str)
    monthly_revenue = monthly_revenue.sort_values("order_month")

    toggle = st.radio("Tampilkan:", ["Revenue", "Orders"], horizontal=True, key="trend_toggle")
    y_col  = "revenue" if toggle == "Revenue" else "orders"

    fig, ax = plt.subplots(figsize=(13, 4.5))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("#f8fafc")

    ax.fill_between(monthly_revenue["month_str"], monthly_revenue[y_col],
                    alpha=0.12, color=PRIMARY)
    ax.plot(monthly_revenue["month_str"], monthly_revenue[y_col],
            color=PRIMARY, linewidth=2.5, marker="o", markersize=5, zorder=3)

    # Peak highlight
    peak_i = monthly_revenue[y_col].idxmax()
    ax.scatter(
        monthly_revenue.loc[peak_i, "month_str"],
        monthly_revenue.loc[peak_i, y_col],
        color=DANGER, s=130, zorder=5, edgecolors="white", linewidths=1.5,
        label=f"🏆 Peak: {monthly_revenue.loc[peak_i,'month_str']}"
    )
    ax.annotate(
        f"Peak\n{monthly_revenue.loc[peak_i,'month_str']}",
        xy=(monthly_revenue.loc[peak_i,"month_str"], monthly_revenue.loc[peak_i, y_col]),
        xytext=(0, 18), textcoords="offset points",
        ha="center", fontsize=8, color=DANGER, fontweight="bold",
        arrowprops=dict(arrowstyle="->", color=DANGER, lw=1.2),
    )

    if toggle == "Revenue":
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x/1e6:.1f}M"))
    else:
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))

    ax.set_title(f"Monthly {toggle} Trend (2016–2018)", fontsize=13, fontweight="bold",
                 color="#0f172a", pad=12)
    ax.tick_params(axis="x", rotation=45, labelsize=8)
    ax.tick_params(axis="y", labelsize=9)
    ax.grid(axis="y", alpha=0.4, linestyle="--")
    ax.spines[["top","right","left"]].set_visible(False)
    ax.legend(fontsize=9)
    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close()

    # Monthly table
    peak_rev  = monthly_revenue.loc[monthly_revenue["revenue"].idxmax()]
    peak_ord  = monthly_revenue.loc[monthly_revenue["orders"].idxmax()]
    c1, c2, c3 = st.columns(3)
    c1.metric("🏆 Peak Revenue Month",  peak_rev["month_str"], f"$ {peak_rev['revenue']:,.0f}")
    c2.metric("📦 Peak Orders Month",   peak_ord["month_str"], f"{peak_ord['orders']:,} orders")
    c3.metric("📊 Total Months Tracked", f"{len(monthly_revenue)} bulan",
              f"Avg $ {monthly_revenue['revenue'].mean():,.0f}/bln")

    st.markdown("""
    <div class="insight-box">
    💡 <strong>Insight:</strong>
    Tren revenue menunjukkan pertumbuhan yang konsisten dari akhir 2016 hingga pertengahan 2018.
    <strong>November 2017</strong> menjadi puncak penjualan, didorong kemungkinan besar oleh event
    <strong>Black Friday</strong>. Periode Nov–Dec 2017 dan Feb–Mar 2018 menunjukkan lonjakan order
    yang juga disertai tekanan pada performa pengiriman (delivery time naik, on-time rate turun).
    Pertengahan 2018 mencatat performa terbaik secara operasional.
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# TAB 2 ── CATEGORY PERFORMANCE (Pertanyaan 2)
# ═══════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("""
    <div class="section-header">
      <div class="icon">🏷️</div>
      <div>
        <h2>Performa Kategori Produk</h2>
        <p>Pertanyaan 2: Kategori produk apa yang laris dan menghasilkan revenue tertinggi?</p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    cat_df = (
        filtered.groupby("product_category_name_english")
        .agg(total_revenue=("payment_value","sum"), total_orders=("order_id","nunique"))
        .reset_index()
        .sort_values("total_revenue", ascending=False)
    )

    col_n, col_sort = st.columns([1, 2])
    top_n = col_n.slider("Top N Kategori:", 5, 20, 10, key="cat_n")
    sort_by = col_sort.radio("Urutkan berdasarkan:", ["Revenue", "Orders"], horizontal=True, key="cat_sort")

    top_cat = cat_df.sort_values(
        "total_revenue" if sort_by == "Revenue" else "total_orders", ascending=False
    ).head(top_n)

    fig, axes = plt.subplots(1, 2, figsize=(15, max(5, top_n * 0.45 + 1)))
    fig.patch.set_facecolor("white")

    pal_blue  = sns.color_palette("Blues_d",  top_n)
    pal_green = sns.color_palette("Greens_d", top_n)

    for ax, col, palette, label, fmt in [
        (axes[0], "total_revenue", pal_blue,  "Total Revenue",  lambda v: f"${v/1e6:.1f}M"),
        (axes[1], "total_orders",  pal_green, "Total Orders",   lambda v: f"{int(v):,}"),
    ]:
        ax.set_facecolor("#f8fafc")
        bars = ax.barh(
            top_cat["product_category_name_english"][::-1],
            top_cat[col][::-1],
            color=palette, edgecolor="white", height=0.65
        )
        for bar in bars:
            ax.text(bar.get_width() * 1.01, bar.get_y() + bar.get_height()/2,
                    fmt(bar.get_width()), va="center", fontsize=8, color="#374151")
        ax.set_title(f"Top {top_n} by {label}", fontsize=12, fontweight="bold",
                     color="#0f172a", pad=10)
        ax.set_xlabel(label, fontsize=9)
        ax.tick_params(labelsize=8)
        ax.spines[["top","right","bottom"]].set_visible(False)
        ax.grid(axis="x", alpha=0.3, linestyle="--")

    plt.suptitle("Product Category Performance Analysis", fontsize=14,
                 fontweight="bold", color="#0f172a")
    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close()

    # Table
    with st.expander("📋 Lihat data lengkap semua kategori"):
        st.dataframe(
            cat_df.rename(columns={
                "product_category_name_english":"Category",
                "total_revenue":"Revenue ($)",
                "total_orders":"Orders"
            }).style.format({"Revenue ($)":"{:,.2f}","Orders":"{:,}"})
              .background_gradient(subset=["Revenue ($)"], cmap="Blues"),
            use_container_width=True, height=350
        )

    st.markdown("""
    <div class="insight-box">
    💡 <strong>Insight:</strong>
    Kategori <strong>bed_bath_table</strong> dan <strong>health_beauty</strong> secara konsisten
    berada di posisi teratas baik dari sisi revenue maupun jumlah transaksi — menjadikan keduanya
    sebagai kategori tulang punggung bisnis. Kategori <strong>health_beauty</strong> menunjukkan
    kombinasi terbaik antara volume tinggi dan nilai transaksi yang besar, mengindikasikan kebutuhan
    rutin dari pelanggan yang berpotensi membangun loyalitas jangka panjang.
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# TAB 3 ── GEOGRAPHIC DISTRIBUTION (Pertanyaan 3)
# ═══════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("""
    <div class="section-header">
      <div class="icon">🗺️</div>
      <div>
        <h2>Distribusi Geografis Pelanggan</h2>
        <p>Pertanyaan 3: State mana yang memiliki performa tertinggi dan bagaimana persebaran pelanggannya?</p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── State aggregation ─────────────────────────────────────────────────
    state_df = (
        filtered.drop_duplicates("order_id")
        .groupby("customer_state")
        .agg(total_orders=("order_id","nunique"), total_revenue=("payment_value","sum"))
        .reset_index()
        .rename(columns={"customer_state":"state"})
    )
    state_df["total_revenue"]  = state_df["total_revenue"].round(2)
    state_df["revenue_share"]  = (state_df["total_revenue"] / state_df["total_revenue"].sum() * 100).round(2)
    state_df["orders_share"]   = (state_df["total_orders"]  / state_df["total_orders"].sum()  * 100).round(2)
    state_df["state_name"]     = state_df["state"].map(STATE_NAMES).fillna(state_df["state"])
    state_df = state_df.sort_values("total_orders", ascending=False)

    # ── Bar charts (Top 10) ───────────────────────────────────────────────
    top10 = state_df.head(10)
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.patch.set_facecolor("white")

    for ax, col, pal, label, fmt in [
        (axes[0], "total_orders",  "Blues",   "Total Orders",   lambda v: f"{int(v):,}"),
        (axes[1], "total_revenue", "Oranges", "Total Revenue",  lambda v: f"${v/1e6:.1f}M"),
    ]:
        ax.set_facecolor("#f8fafc")
        colors = sns.color_palette(pal, 10)
        bars = ax.barh(top10["state_name"][::-1], top10[col][::-1],
                       color=colors, edgecolor="white", height=0.65)
        share_col = "orders_share" if col == "total_orders" else "revenue_share"
        for bar, share in zip(bars, top10[share_col][::-1]):
            ax.text(bar.get_width() * 1.01, bar.get_y() + bar.get_height()/2,
                    f"{share:.1f}%", va="center", fontsize=8, color="#6b7280")
        ax.set_title(f"Top 10 States — {label}", fontsize=11, fontweight="bold", color="#0f172a")
        ax.spines[["top","right","bottom"]].set_visible(False)
        ax.tick_params(labelsize=8)
        ax.grid(axis="x", alpha=0.3, linestyle="--")

    plt.suptitle("State Sales Performance", fontsize=13, fontweight="bold", color="#0f172a")
    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close()

    st.markdown("---")

    # ── Maps ──────────────────────────────────────────────────────────────
    map_metric = st.selectbox(
        "Metrik peta:", ["total_orders","total_revenue"],
        format_func=lambda x: "📦 Total Orders" if x=="total_orders" else "💰 Total Revenue ($)"
    )

    geo_col1, geo_col2 = st.columns(2)

    # ── Choropleth Map ────────────────────────────────────────────────────
    with geo_col1:
        st.markdown("#### 🗺️ Choropleth Map")
        brazil_geojson = load_geojson()

        if brazil_geojson:
            m1 = folium.Map(location=[-14.235, -51.925], zoom_start=3,
                            tiles="CartoDB positron")
            folium.Choropleth(
                geo_data=brazil_geojson, data=state_df,
                columns=["state", map_metric],
                key_on="feature.properties.state",
                fill_color="Blues" if map_metric=="total_orders" else "YlOrRd",
                fill_opacity=0.75, line_opacity=0.5,
                line_color="white", line_weight=1.5,
                nan_fill_color="#e0e0e0",
                legend_name=map_metric.replace("_"," ").title(),
                highlight=True,
            ).add_to(m1)

            # Popup per state
            state_lookup = state_df.set_index("state").to_dict("index")
            invisible = lambda x: {"fillColor":"transparent","color":"transparent","weight":0,"fillOpacity":0}
            for feat in brazil_geojson["features"]:
                code = feat["properties"].get("state","")
                d = state_lookup.get(code,{})
                if not d: continue
                popup_html = f"""
                <div style="font-family:Arial;width:200px;padding:8px;">
                <b style="color:#2563eb;font-size:13px;">{d.get('state_name',code)} ({code})</b>
                <hr style="margin:5px 0;border-color:#e2e8f0;">
                <table style="width:100%;font-size:12px;">
                <tr><td>📦 Orders</td><td align="right"><b>{d.get('total_orders',0):,}</b>
                    <span style="color:#9ca3af">({d.get('orders_share',0):.1f}%)</span></td></tr>
                <tr><td>💰 Revenue</td><td align="right"><b>$ {d.get('total_revenue',0):,.0f}</b>
                    <span style="color:#9ca3af">({d.get('revenue_share',0):.1f}%)</span></td></tr>
                </table></div>"""
                folium.GeoJson(feat, style_function=invisible,
                    highlight_function=lambda x:{"fillColor":"#fef08a","color":"#374151","weight":2,"fillOpacity":0.4},
                    popup=folium.Popup(popup_html, max_width=210),
                    tooltip=folium.GeoJsonTooltip(fields=["state"],aliases=["State:"],sticky=True),
                ).add_to(m1)

            st_folium(m1, width=None, height=400, returned_objects=[])
        else:
            st.warning("⚠️ GeoJSON tidak dapat dimuat (butuh koneksi internet).")

    # ── Symbol Map ────────────────────────────────────────────────────────
    with geo_col2:
        st.markdown("#### 🔵 Symbol Map (Persebaran Pelanggan)")

        if brazil_geojson and "geolocation_lat" in filtered.columns:
            m2 = folium.Map(location=[-14.235, -51.925], zoom_start=3,
                            tiles="CartoDB positron")

            # Boundary
            folium.GeoJson(brazil_geojson, style_function=lambda x:{
                "fillColor":"#f8fafc","color":"#94a3b8","weight":1.2,"fillOpacity":0.2
            }).add_to(m2)

            # Customer dots
            cust_pts = (
                filtered.drop_duplicates("customer_unique_id")
                .dropna(subset=["geolocation_lat","geolocation_lng"])
                .sample(n=min(3000, filtered["customer_unique_id"].nunique()), random_state=42)
            )
            cust_layer = folium.FeatureGroup(name="📍 Customers", show=True)
            for _, row in cust_pts.iterrows():
                folium.CircleMarker(
                    [row["geolocation_lat"], row["geolocation_lng"]],
                    radius=2, color=PRIMARY, fill=True,
                    fill_color=PRIMARY, fill_opacity=0.25, weight=0,
                ).add_to(cust_layer)
            cust_layer.add_to(m2)

            # State bubbles
            val_min = state_df[map_metric].min()
            val_max = state_df[map_metric].max()
            centroids = (
                filtered.dropna(subset=["geolocation_lat","geolocation_lng"])
                .groupby("customer_state")
                .agg(lat=("geolocation_lat","mean"), lon=("geolocation_lng","mean"))
                .reset_index().rename(columns={"customer_state":"state"})
            )
            bubble_layer = folium.FeatureGroup(name="🔵 State Bubbles", show=True)
            for _, row in centroids.iterrows():
                d = state_lookup.get(row["state"],{})
                if not d: continue
                radius = 8 + ((d.get(map_metric,0) - val_min) / (val_max - val_min + 1)) * 45
                popup_html = f"""
                <div style="font-family:Arial;width:200px;padding:8px;">
                <b style="color:#2563eb;">{d.get('state_name',row['state'])} ({row['state']})</b>
                <hr style="margin:5px 0;border-color:#e2e8f0;">
                <table style="width:100%;font-size:12px;">
                <tr><td>📦 Orders</td><td align="right"><b>{d.get('total_orders',0):,}</b>
                    <span style="color:#9ca3af">({d.get('orders_share',0):.1f}%)</span></td></tr>
                <tr><td>💰 Revenue</td><td align="right"><b>$ {d.get('total_revenue',0):,.0f}</b></td></tr>
                </table></div>"""
                folium.CircleMarker(
                    [row["lat"], row["lon"]], radius=radius,
                    color="white", weight=1.5, fill=True,
                    fill_color=PRIMARY, fill_opacity=0.80,
                    popup=folium.Popup(popup_html, max_width=210),
                    tooltip=f"<b>{d.get('state_name',row['state'])}</b> — Orders: {d.get('total_orders',0):,}",
                ).add_to(bubble_layer)
                folium.Marker([row["lat"], row["lon"]], icon=folium.DivIcon(
                    html=f'<div style="font-size:8px;font-weight:bold;color:white;text-align:center;width:30px;margin-left:-15px;">{row["state"]}</div>',
                    icon_size=(30,12),
                )).add_to(bubble_layer)
            bubble_layer.add_to(m2)
            folium.LayerControl(collapsed=False).add_to(m2)
            st_folium(m2, width=None, height=400, returned_objects=[])
        else:
            st.info("Symbol map membutuhkan kolom geolocation_lat & geolocation_lng di data.")

    st.markdown("""
    <div class="insight-box">
    💡 <strong>Insight:</strong>
    <strong>São Paulo (SP)</strong> mendominasi dengan ~40% total orders dan revenue nasional.
    <strong>Region Southeast</strong> (SP, RJ, MG) menguasai mayoritas transaksi, mencerminkan
    konsentrasi ekonomi Brazil. Persebaran titik pelanggan mengkonfirmasi konsentrasi di wilayah
    pesisir Southeast dan South, sementara <strong>North & Northeast</strong> (CE, BA, PA) menunjukkan
    potensi pertumbuhan yang belum tergarap optimal → peluang ekspansi pasar dan logistik.
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# TAB 4 ── RFM SEGMENTATION (Pertanyaan 4)
# ═══════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("""
    <div class="section-header">
      <div class="icon">👥</div>
      <div>
        <h2>RFM Customer Segmentation</h2>
        <p>Pertanyaan 4: Bagaimana profil segmentasi pelanggan untuk menentukan strategi pemasaran?</p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    @st.cache_data
    def compute_rfm(data):
        snapshot = data["order_purchase_timestamp"].max() + pd.Timedelta(days=1)
        rfm = (
            data.drop_duplicates(subset=["order_id","customer_unique_id"])
            .groupby("customer_unique_id")
            .agg(
                Recency   = ("order_purchase_timestamp", lambda x: (snapshot-x.max()).days),
                Frequency = ("order_id","nunique"),
                Monetary  = ("payment_value","sum"),
            ).reset_index()
        )
        rfm["R_score"] = pd.qcut(rfm["Recency"], q=5, labels=[5,4,3,2,1]).astype(int)
        rfm["F_score"] = pd.qcut(rfm["Frequency"].rank(method="first"), q=5, labels=[1,2,3,4,5]).astype(int)
        rfm["M_score"] = pd.qcut(rfm["Monetary"], q=5, labels=[1,2,3,4,5]).astype(int)
        rfm["RFM_Score"] = rfm["R_score"] + rfm["F_score"] + rfm["M_score"]

        def seg(s):
            if s >= 12: return "Champions"
            elif s >= 9: return "Loyal Customers"
            elif s >= 6: return "Potential Loyalists"
            elif s >= 4: return "At Risk"
            else: return "Lost"
        rfm["Segment"] = rfm["RFM_Score"].apply(seg)
        return rfm

    rfm_df = compute_rfm(filtered)

    seg_order = ["Champions","Loyal Customers","Potential Loyalists","At Risk","Lost"]
    seg_colors_list = [SEG_COLORS[s] for s in seg_order]

    # ── RFM Charts ────────────────────────────────────────────────────────
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    fig.patch.set_facecolor("white")

    metrics_rfm = [
        ("Count", rfm_df.groupby("Segment").size().reindex(seg_order).fillna(0), lambda v:f"{int(v):,}"),
        ("Avg Monetary ($)", rfm_df.groupby("Segment")["Monetary"].mean().reindex(seg_order).fillna(0), lambda v:f"${v:.0f}"),
        ("Avg Recency (days)", rfm_df.groupby("Segment")["Recency"].mean().reindex(seg_order).fillna(0), lambda v:f"{v:.0f}d"),
    ]

    for ax, (title, data, fmt) in zip(axes, metrics_rfm):
        ax.set_facecolor("#f8fafc")
        existing = data.dropna()
        colors = [SEG_COLORS.get(s,"#ccc") for s in existing.index]
        bars = ax.bar(existing.index, existing.values, color=colors, edgecolor="white", width=0.65)
        for bar, val in zip(bars, existing.values):
            ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()*1.01,
                    fmt(val), ha="center", fontsize=8, fontweight="bold", color="#374151")
        ax.set_title(title, fontsize=11, fontweight="bold", color="#0f172a")
        ax.tick_params(axis="x", rotation=18, labelsize=8)
        ax.spines[["top","right","left"]].set_visible(False)
        ax.grid(axis="y", alpha=0.3, linestyle="--")
        if title == "Avg Recency (days)":
            ax.invert_yaxis()

    plt.suptitle("RFM Customer Segmentation Analysis", fontsize=14,
                 fontweight="bold", color="#0f172a")
    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close()

    # ── Segment summary table ─────────────────────────────────────────────
    st.markdown("#### 📊 Segment Summary")
    summary = (
        rfm_df.groupby("Segment")
        .agg(Count=("customer_unique_id","count"),
             Pct=("customer_unique_id", lambda x: f"{len(x)/len(rfm_df)*100:.1f}%"),
             Avg_Recency=("Recency","mean"),
             Avg_Frequency=("Frequency","mean"),
             Avg_Monetary=("Monetary","mean"))
        .round(2).reindex(seg_order).dropna()
    )
    st.dataframe(
        summary.style.format({"Count":"{:,}","Avg_Recency":"{:.0f} days",
                              "Avg_Frequency":"{:.2f}","Avg_Monetary":"$ {:,.2f}"}),
        use_container_width=True
    )

    # ── Strategy cards ────────────────────────────────────────────────────
    st.markdown("#### 🎯 Rekomendasi Strategi per Segmen")
    strategy = {
        "Champions":           ("🏆","#dbeafe","#1d4ed8","Loyalty program & early access promo eksklusif — pertahankan dengan pengalaman premium"),
        "Loyal Customers":     ("💎","#dcfce7","#166534","Upsell produk premium & reward points — dorong menuju Champions"),
        "Potential Loyalists": ("🌱","#d1fae5","#065f46","Email campaign personal & voucher diskon — konversi menjadi pelanggan loyal"),
        "At Risk":             ("⚠️","#fef9c3","#854d0e","Win-back campaign dengan penawaran eksklusif time-limited — cegah churn"),
        "Lost":                ("💔","#fee2e2","#991b1b","Re-engagement campaign — evaluasi cost vs benefit sebelum invest lebih lanjut"),
    }
    cols = st.columns(5)
    for col, seg in zip(cols, seg_order):
        icon, bg, txt, desc = strategy[seg]
        count = int(rfm_df[rfm_df["Segment"]==seg].shape[0])
        col.markdown(f"""
        <div style="background:{bg};border-radius:12px;padding:12px;text-align:center;height:180px;">
          <div style="font-size:1.5rem">{icon}</div>
          <div style="font-size:0.75rem;font-weight:800;color:{txt};margin:4px 0">{seg}</div>
          <div style="font-family:'JetBrains Mono';font-size:1.1rem;font-weight:700;color:{txt}">{count:,}</div>
          <div style="font-size:0.65rem;color:{txt};opacity:0.8;margin-top:6px;line-height:1.4">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="insight-box">
    💡 <strong>Insight:</strong>
    Segmen <strong>Champions</strong> dan <strong>Loyal Customers</strong> menjadi tulang punggung
    pendapatan dengan monetary value tertinggi. Sementara <strong>Potential Loyalists</strong>
    berjumlah besar dengan recency mendekati 300 hari — ini adalah segmen terpenting untuk dikonversi.
    Lebih dari <strong>93% pelanggan hanya berbelanja sekali</strong>, mengindikasikan urgensi tinggi
    untuk strategi retensi dan repeat purchase.
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# TAB 5 ── ADDITIONAL INSIGHTS
# ═══════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown("""
    <div class="section-header">
      <div class="icon">💳</div>
      <div>
        <h2>Additional Insights</h2>
        <p>Payment methods, delivery performance, dan customer purchase frequency</p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    col_a, col_b = st.columns(2)

    # ── Payment Type Distribution ─────────────────────────────────────────
    with col_a:
        st.markdown("##### 💳 Metode Pembayaran")
        if "payment_type" in filtered.columns:
            pay_df = (
                filtered.groupby("payment_type")
                .agg(transactions=("order_id","count"), total_value=("payment_value","sum"))
                .reset_index().sort_values("transactions", ascending=False)
            )
            fig, ax = plt.subplots(figsize=(6, 4))
            fig.patch.set_facecolor("white")
            ax.set_facecolor("#f8fafc")
            colors_pay = [PRIMARY, SECONDARY, SUCCESS, WARNING, PURPLE][:len(pay_df)]
            wedges, texts, autotexts = ax.pie(
                pay_df["transactions"], labels=pay_df["payment_type"],
                autopct="%1.1f%%", colors=colors_pay,
                startangle=90, pctdistance=0.82,
                wedgeprops=dict(edgecolor="white", linewidth=2),
            )
            for at in autotexts:
                at.set_fontsize(8); at.set_fontweight("bold")
            ax.set_title("Transaction Share by Payment Type", fontsize=11,
                         fontweight="bold", color="#0f172a")
            st.pyplot(fig, use_container_width=True)
            plt.close()

            # Mini table
            pay_df["avg_value"] = (pay_df["total_value"] / pay_df["transactions"]).round(2)
            st.dataframe(
                pay_df.rename(columns={"payment_type":"Payment","transactions":"Transactions",
                                       "total_value":"Total Value","avg_value":"Avg Value"})
                .style.format({"Transactions":"{:,}","Total Value":"$ {:,.0f}","Avg Value":"$ {:,.2f}"}),
                use_container_width=True, hide_index=True
            )

    # ── Delivery Performance ──────────────────────────────────────────────
    with col_b:
        st.markdown("##### 🚚 Performa Pengiriman")
        if all(c in filtered.columns for c in ["order_delivered_customer_date","order_estimated_delivery_date"]):
            dlv2 = filtered.drop_duplicates("order_id").dropna(
                subset=["order_delivered_customer_date","order_estimated_delivery_date"]
            ).copy()
            dlv2["is_late"]    = dlv2["order_delivered_customer_date"] > dlv2["order_estimated_delivery_date"]
            dlv2["delay_days"] = (dlv2["order_delivered_customer_date"] - dlv2["order_estimated_delivery_date"]).dt.days

            on_t = (~dlv2["is_late"]).sum()
            late = dlv2["is_late"].sum()
            med_delay = dlv2.loc[dlv2["is_late"],"delay_days"].median()

            fig, axes = plt.subplots(1, 2, figsize=(6, 4))
            fig.patch.set_facecolor("white")

            # Pie
            axes[0].set_facecolor("#f8fafc")
            axes[0].pie([on_t, late], labels=["On-Time","Late"],
                        autopct="%1.1f%%", colors=[SUCCESS, DANGER],
                        startangle=90, pctdistance=0.8,
                        wedgeprops=dict(edgecolor="white", linewidth=2))
            axes[0].set_title("Delivery Status", fontsize=10, fontweight="bold", color="#0f172a")

            # Delay distribution (capped)
            axes[1].set_facecolor("#f8fafc")
            late_days = dlv2.loc[dlv2["is_late"],"delay_days"].clip(upper=30)
            axes[1].hist(late_days, bins=20, color=DANGER, alpha=0.8, edgecolor="white")
            axes[1].axvline(med_delay, color="#0f172a", linestyle="--", linewidth=1.5,
                           label=f"Median: {med_delay:.0f}d")
            axes[1].set_title("Late Delay Distribution", fontsize=10, fontweight="bold", color="#0f172a")
            axes[1].set_xlabel("Days Late", fontsize=8)
            axes[1].legend(fontsize=8)
            axes[1].spines[["top","right"]].set_visible(False)

            plt.tight_layout()
            st.pyplot(fig, use_container_width=True)
            plt.close()

            d1, d2, d3 = st.columns(3)
            d1.metric("✅ On-Time",  f"{on_t:,}", f"{on_t/(on_t+late)*100:.1f}%")
            d2.metric("⚠️ Late",    f"{late:,}", f"{late/(on_t+late)*100:.1f}%")
            d3.metric("📅 Med. Delay", f"{med_delay:.0f} hari", "when late")

    st.markdown("---")

    # ── Purchase Frequency Distribution ──────────────────────────────────
    st.markdown("##### 🔄 Frekuensi Pembelian Pelanggan")
    freq_df = (
        filtered.drop_duplicates(["order_id","customer_unique_id"])
        .groupby("customer_unique_id")["order_id"].nunique()
        .reset_index()
    )
    freq_df.columns = ["customer_unique_id","purchase_count"]
    freq_dist = freq_df["purchase_count"].value_counts().sort_index().reset_index()
    freq_dist.columns = ["Frekuensi Belanja","Jumlah Customer"]
    freq_dist = freq_dist[freq_dist["Frekuensi Belanja"] <= 10]

    fig, ax = plt.subplots(figsize=(12, 3.5))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("#f8fafc")
    bars = ax.bar(freq_dist["Frekuensi Belanja"].astype(str),
                  freq_dist["Jumlah Customer"],
                  color=[PRIMARY if x==1 else SECONDARY for x in freq_dist["Frekuensi Belanja"]],
                  edgecolor="white", width=0.65)
    for bar, val in zip(bars, freq_dist["Jumlah Customer"]):
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+200,
                f"{val:,}", ha="center", fontsize=8, fontweight="bold", color="#374151")
    ax.set_xlabel("Frekuensi Belanja (kali)", fontsize=9)
    ax.set_ylabel("Jumlah Customer", fontsize=9)
    ax.set_title("Distribusi Frekuensi Pembelian Pelanggan (1–10x)", fontsize=12,
                 fontweight="bold", color="#0f172a")
    ax.spines[["top","right","left"]].set_visible(False)
    ax.grid(axis="y", alpha=0.3, linestyle="--")
    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close()

    once = freq_df[freq_df["purchase_count"]==1].shape[0]
    pct_once = once / len(freq_df) * 100
    st.markdown(f"""
    <div class="insight-box">
    💡 <strong>Insight:</strong>
    Sebanyak <strong>{once:,} pelanggan ({pct_once:.1f}%)</strong> hanya berbelanja <strong>sekali</strong> —
    menandakan tingkat retensi yang sangat rendah. Segmen pelanggan berulang (2x, 3x, dst.) berjumlah
    kecil namun memiliki nilai strategis tinggi. Program <strong>loyalty, retargeting, dan personalized
    recommendation</strong> sangat krusial untuk meningkatkan repeat purchase rate.
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown("""
<div style="text-align:center; font-size:0.75rem; color:#94a3b8; padding:1rem 0;">
    📊 <strong>Brazil E-Commerce Analytics Dashboard</strong> &nbsp;|&nbsp;
    Data Source: <em>Olist Brazilian E-Commerce Public Dataset</em> &nbsp;|&nbsp;
    Built with Streamlit &amp; Folium &nbsp;|&nbsp;
    Sutriadi Kurniawan
</div>
""", unsafe_allow_html=True)
