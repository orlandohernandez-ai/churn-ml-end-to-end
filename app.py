import streamlit as st

st.set_page_config(
    page_title="Customer Retention Dashboard",
    layout="wide"
)

import pandas as pd

DATA_PATH = "reports/retention_dashboard_data.csv"

@st.cache_data
def load_data(path=DATA_PATH):
    df = pd.read_csv(path)
    return df

df = load_data()
required = {
    "CustomerID",
    "churn_probability",
    "CLTV",
    "retention_priority",
    "retention_tier"
}
missing = required - set(df.columns)
if missing:
    st.error(f"Missing required columns: {sorted(missing)}. Re-run 04 notebook export.")
    st.stop()

# -------------------------
# App Config
# -------------------------

st.title("📊 Customer Retention Priority Dashboard")
st.caption("Churn risk × Customer Lifetime Value")

# -------------------------
# Load Data
# -------------------------
# -------------------------
# Sidebar Filters
# -------------------------
st.sidebar.header("Filters")

tier_filter = st.sidebar.multiselect(
    "Retention Tier",
    options=sorted(df["retention_tier"].dropna().unique()),
    default=sorted(df["retention_tier"].dropna().unique())
)

# Cluster is optional (only if the column exists in your CSV)
if "Cluster" in df.columns:
    cluster_filter = st.sidebar.multiselect(
        "Cluster",
        options=sorted(df["Cluster"].dropna().unique()),
        default=sorted(df["Cluster"].dropna().unique())
    )
else:
    cluster_filter = None

df_filtered = df[df["retention_tier"].isin(tier_filter)]

if cluster_filter is not None:
    df_filtered = df_filtered[df_filtered["Cluster"].isin(cluster_filter)]

# -------------------------
# KPI Metrics
# -------------------------
col1, col2, col3 = st.columns(3)

col1.metric(
    "Customers",
    f"{len(df_filtered):,}"
)

col2.metric(
    "Avg Churn Probability",
    f"{df_filtered['churn_probability'].mean():.2%}"
)

col3.metric(
    "Avg CLTV",
    f"${df_filtered['CLTV'].mean():,.0f}"
)

st.divider()

# -------------------------
# Top Priority Customers
# -------------------------
st.subheader("🔥 Top Retention Priority Customers")

top_n = st.slider("Show Top N Customers", 5, 100, 20)

st.dataframe(
    df_filtered
    .sort_values("retention_priority", ascending=False)
    .head(top_n),
    use_container_width=True
)

# -------------------------
# Retention Tier Breakdown
# -------------------------
st.subheader("📌 Retention Tier Distribution")

tier_counts = df_filtered["retention_tier"].value_counts().reset_index()
tier_counts.columns = ["Retention Tier", "Customers"]

st.bar_chart(
    tier_counts.set_index("Retention Tier")
)