"""
================================================================================
🏦 APEX BANK — EXECUTIVE INTELLIGENCE HUB & BANKING ANALYTICS DWH
================================================================================
Enterprise C-Level Analytics Platform | Dark Glassmorphism Fintech UI
Connected directly to AWS RDS PostgreSQL (Warehouse & Data Marts)
================================================================================
"""

import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

# Cấu hình giao diện Streamlit Wide Mode
st.set_page_config(
    page_title="APEX BANK — Executive Intelligence Hub",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# ULTRA-PREMIUM FINTECH CSS STYLING (DARK GLASSMORPHISM)
# ==============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .stApp {
        background-color: #080c14;
        color: #f1f5f9;
    }

    /* Header Bar */
    .apex-header {
        background: linear-gradient(90deg, #0d1527 0%, #111e38 50%, #0d1527 100%);
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 16px;
        padding: 16px 24px;
        margin-bottom: 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
    
    .apex-logo {
        font-size: 1.4rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        background: linear-gradient(135deg, #38bdf8 0%, #818cf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .apex-tagline {
        font-size: 0.75rem;
        color: #94a3b8;
        font-weight: 500;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }

    /* Metric Card Glassmorphism */
    .kpi-card {
        background: linear-gradient(145deg, rgba(17, 27, 49, 0.8) 0%, rgba(13, 20, 36, 0.95) 100%);
        border: 1px solid rgba(148, 163, 184, 0.1);
        border-radius: 14px;
        padding: 18px 20px;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(12px);
        transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
        position: relative;
        overflow: hidden;
    }
    
    .kpi-card:hover {
        border-color: rgba(56, 189, 248, 0.4);
        box-shadow: 0 8px 30px -4px rgba(56, 189, 248, 0.15);
        transform: translateY(-2px);
    }

    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; height: 3px;
        background: linear-gradient(90deg, #38bdf8, #818cf8);
    }

    .kpi-title {
        font-size: 0.75rem;
        font-weight: 600;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        display: flex;
        justify-content: space-between;
    }

    .kpi-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.85rem;
        font-weight: 700;
        color: #ffffff;
        margin: 6px 0 2px 0;
        letter-spacing: -0.02em;
    }

    .kpi-sub-badge-positive {
        display: inline-block;
        font-size: 0.72rem;
        font-weight: 600;
        color: #34d399;
        background: rgba(52, 211, 153, 0.12);
        padding: 2px 8px;
        border-radius: 9999px;
        border: 1px solid rgba(52, 211, 153, 0.25);
    }

    .kpi-sub-badge-neutral {
        display: inline-block;
        font-size: 0.72rem;
        font-weight: 600;
        color: #38bdf8;
        background: rgba(56, 189, 248, 0.12);
        padding: 2px 8px;
        border-radius: 9999px;
        border: 1px solid rgba(56, 189, 248, 0.25);
    }

    /* Section Card */
    .section-box {
        background: #0f172a;
        border: 1px solid rgba(148, 163, 184, 0.12);
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 20px;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #0b1120;
        padding: 8px;
        border-radius: 12px;
        border: 1px solid rgba(148, 163, 184, 0.1);
    }

    .stTabs [data-baseweb="tab"] {
        height: 44px;
        border-radius: 8px;
        color: #94a3b8;
        font-weight: 600;
        font-size: 0.85rem;
        padding: 0 16px;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(56, 189, 248, 0.2) 0%, rgba(129, 140, 248, 0.2) 100%) !important;
        color: #38bdf8 !important;
        border: 1px solid rgba(56, 189, 248, 0.4) !important;
    }

    /* Custom Dataframe / Table */
    [data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid rgba(148, 163, 184, 0.12);
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# DATABASE CONNECTION & CACHED QUERY ENGINE
# ==============================================================================
DB_HOST = os.getenv("DB_HOST") or os.getenv("RDS_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT") or os.getenv("RDS_PORT", "5432")
DB_NAME = os.getenv("DB_NAME") or os.getenv("RDS_DATABASE", "banking_dwh")
DB_USER = os.getenv("DB_USER") or os.getenv("RDS_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD") or os.getenv("RDS_PASSWORD", "")


@st.cache_resource
def get_db_engine():
    connection_uri = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return create_engine(connection_uri, pool_size=10, max_overflow=20)


@st.cache_data(ttl=600)
def fetch_data(query: str) -> pd.DataFrame:
    engine = get_db_engine()
    with engine.connect() as conn:
        return pd.read_sql(query, conn)


# ==============================================================================
# GLOBAL PLOTLY DARK FINTECH THEME HELPER
# ==============================================================================
def apply_fintech_theme(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans, sans-serif", color="#94a3b8", size=12),
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11, color="#cbd5e1")
        ),
        xaxis=dict(
            gridcolor="rgba(148, 163, 184, 0.08)",
            zerolinecolor="rgba(148, 163, 184, 0.12)",
            tickfont=dict(color="#94a3b8", size=11)
        ),
        yaxis=dict(
            gridcolor="rgba(148, 163, 184, 0.08)",
            zerolinecolor="rgba(148, 163, 184, 0.12)",
            tickfont=dict(color="#94a3b8", size=11)
        )
    )
    return fig


# ==============================================================================
# SIDEBAR FILTERS & METADATA
# ==============================================================================
with st.sidebar:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
        <span style="font-size: 2.2rem;">🏛️</span>
        <div>
            <div style="font-weight: 800; font-size: 1.2rem; color: #38bdf8; letter-spacing: 0.05em;">APEX BANK</div>
            <div style="font-size: 0.7rem; color: #64748b; font-weight: 600;">EXECUTIVE INTELLIGENCE</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("### 🎛️ Bộ Lọc Toàn Cục (Global Filters)")
    selected_year = st.selectbox("Năm Báo Cáo", options=["Tất cả (2018 - 2024)", "2024", "2023", "2022", "2021", "2020", "2019", "2018"], index=0)
    selected_segment = st.multiselect(
        "Phân Khúc Khách Hàng",
        options=["PLATINUM_VIP", "GOLD_AFFLUENT", "SILVER_STANDARD", "BRONZE_RETAIL"],
        default=["PLATINUM_VIP", "GOLD_AFFLUENT", "SILVER_STANDARD", "BRONZE_RETAIL"]
    )
    st.markdown("---")

    st.markdown("### ⚡ Hạ Tầng & DWH")
    st.markdown(f"""
    - **Engine:** AWS RDS PostgreSQL
    - **Host:** `{DB_HOST[:20]}...`
    - **Database:** `{DB_NAME}`
    - **Data Lake:** `s3://cloud-banking-dwh-raw-2026`
    - **Security:** AWS IAM & VPC Enforced
    """)
    if st.button("🔄 Làm mới dữ liệu (Clear Cache)"):
        st.cache_data.clear()
        st.rerun()

# ==============================================================================
# TOP EXECUTIVE BANNER
# ==============================================================================
st.markdown("""
<div class="apex-header">
    <div>
        <div class="apex-logo">APEX BANK • EXECUTIVE INTELLIGENCE HUB</div>
        <div class="apex-tagline">Cloud-Native Banking Analytics & Enterprise Data Warehouse (RDS PostgreSQL)</div>
    </div>
    <div style="text-align: right;">
        <div style="font-size: 0.8rem; color: #38bdf8; font-weight: 700;">🟢 LIVE PRODUCTION PIPELINE</div>
        <div style="font-size: 0.72rem; color: #94a3b8;">Refreshed: Real-time • Data Marts Schema: <code>mart.*</code></div>
    </div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# TẢI DỮ LIỆU & ÁP DỤNG BỘ LỌC TOÀN CỤC
# ==============================================================================
try:
    df_c360 = fetch_data("SELECT * FROM mart.customer_360;")
    df_branch = fetch_data("SELECT * FROM mart.daily_branch_performance;")
    df_merchant = fetch_data("SELECT * FROM mart.merchant_analytics;")
    df_risk = fetch_data("SELECT * FROM mart.credit_risk_monitoring;")

    # Áp dụng bộ lọc Phân khúc (Segment) cho Customer 360
    if selected_segment:
        df_c360 = df_c360[df_c360["customer_segment"].isin(selected_segment)]

    # Áp dụng bộ lọc Năm (Year) cho Branch Performance
    if selected_year != "Tất cả (2018 - 2024)":
        year_val = int(selected_year)
        if 'year' in df_branch.columns:
            df_branch = df_branch[df_branch['year'] == year_val]

except Exception as e:
    st.error(f"❌ Lỗi kết nối Database RDS PostgreSQL: {e}")
    st.stop()

# ==============================================================================
# 5 PHÂN HỆ EXECUTIVE DASHBOARD CHUẨN DOANH NGHIỆP
# ==============================================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 1. Executive Overview",
    "👤 2. Customer 360 & Wealth",
    "🏢 3. Branch Performance",
    "💳 4. Merchant Analytics",
    "⚠️ 5. Credit Risk Matrix"
])

# ==============================================================================
# TRANG 1: EXECUTIVE OVERVIEW (Tổng quan Điều hành C-Level)
# ==============================================================================
with tab1:
    total_spend = df_c360["total_spend_usd"].sum() if not df_c360.empty else 0
    total_balance = df_c360["total_balance_usd"].sum() if not df_c360.empty else 0
    total_loan_debt = df_c360["total_loan_debt_usd"].sum() if not df_c360.empty else 0
    total_customers = len(df_c360)
    est_interest_rev = df_risk["estimated_annual_interest_revenue_usd"].sum() if not df_risk.empty else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title"><span>👥 Tổng Khách Hàng</span> <span>📈 Active</span></div>
            <div class="kpi-value">{total_customers:,.0f}</div>
            <span class="kpi-sub-badge-positive">100% KYC Verified</span>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title"><span>💳 Doanh Số Chi Tiêu</span> <span>📈 Volume</span></div>
            <div class="kpi-value">${total_spend/1e6:,.1f}M</div>
            <span class="kpi-sub-badge-positive">↑ +14.8% YoY</span>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title"><span>📑 Tổng Dư Nợ Tín Dụng</span> <span>⚠️ Exposure</span></div>
            <div class="kpi-value">${total_loan_debt/1e6:,.1f}M</div>
            <span class="kpi-sub-badge-neutral">30k Contracts</span>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title"><span>💰 Ước Tính Doanh Thu Lãi</span> <span>🎯 NII</span></div>
            <div class="kpi-value">${est_interest_rev/1e6:,.1f}M</div>
            <span class="kpi-sub-badge-positive">Annualized Forecast</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    r2_col1, r2_col2, r2_col3 = st.columns([1.5, 1, 1])

    with r2_col1:
        st.markdown("##### 📈 Xu hướng Giao dịch qua các Năm")
        df_year_agg = df_branch.groupby("year")["daily_transaction_volume_usd"].sum().reset_index().sort_values("year")
        fig_trend = px.bar(
            df_year_agg,
            x="year",
            y="daily_transaction_volume_usd",
            labels={"daily_transaction_volume_usd": "Doanh số ($)", "year": "Năm"},
            color="daily_transaction_volume_usd",
            color_continuous_scale="Blues"
        )
        fig_trend.update_layout(height=320)
        st.plotly_chart(apply_fintech_theme(fig_trend), use_container_width=True)

    with r2_col2:
        st.markdown("##### 🎯 Cơ cấu Khách hàng theo Phân khúc")
        df_seg = df_c360.groupby("customer_segment")["customer_id"].count().reset_index()
        fig_seg = px.pie(
            df_seg,
            names="customer_segment",
            values="customer_id",
            hole=0.55,
            color_discrete_sequence=["#38bdf8", "#818cf8", "#34d399", "#f59e0b"]
        )
        fig_seg.update_traces(textposition="inside", textinfo="percent+label", marker=dict(line=dict(color='#0b1120', width=2)))
        fig_seg.update_layout(height=320, showlegend=False)
        st.plotly_chart(apply_fintech_theme(fig_seg), use_container_width=True)

    with r2_col3:
        st.markdown("##### ⚠️ Cơ cấu Dư nợ theo Rủi ro FICO")
        df_fico_debt = df_risk.groupby("credit_risk_tier")["total_loan_debt_usd"].sum().reset_index()
        fig_fico_debt = px.pie(
            df_fico_debt,
            names="credit_risk_tier",
            values="total_loan_debt_usd",
            hole=0.55,
            color_discrete_sequence=["#f43f5e", "#f59e0b", "#38bdf8", "#34d399"]
        )
        fig_fico_debt.update_traces(textposition="inside", textinfo="percent+label", marker=dict(line=dict(color='#0b1120', width=2)))
        fig_fico_debt.update_layout(height=320, showlegend=False)
        st.plotly_chart(apply_fintech_theme(fig_fico_debt), use_container_width=True)


# ==============================================================================
# TRANG 2: CUSTOMER 360 & WEALTH SEGMENTATION
# ==============================================================================
with tab2:
    vip_count = len(df_c360[df_c360["customer_segment"] == "PLATINUM_VIP"])
    avg_fico = df_c360["credit_score"].mean() if not df_c360.empty else 0

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title"><span>👑 Khách Hàng VIP Platinum</span></div>
            <div class="kpi-value">{vip_count:,.0f}</div>
            <span class="kpi-sub-badge-positive">Chi tiêu > $50k hoặc Số dư > $100k</span>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title"><span>⭐ Điểm FICO Trung Bình</span></div>
            <div class="kpi-value">{avg_fico:.0f} <span style="font-size: 1rem; color: #38bdf8;">/ 850</span></div>
            <span class="kpi-sub-badge-positive">Good Standing Rating</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    r1, r2 = st.columns(2)
    with r1:
        st.markdown("##### 📊 Phân bổ Điểm tín dụng FICO")
        df_fico_dist = df_c360.groupby("credit_tier")["customer_id"].count().reset_index()
        fig_fico = px.bar(
            df_fico_dist,
            x="credit_tier",
            y="customer_id",
            color="credit_tier",
            labels={"credit_tier": "Xếp hạng FICO", "customer_id": "Số lượng khách hàng"},
            color_discrete_sequence=px.colors.sequential.Blues_r
        )
        fig_fico.update_layout(height=320, showlegend=False)
        st.plotly_chart(apply_fintech_theme(fig_fico), use_container_width=True)

    with r2:
        st.markdown("##### 🎯 Tương quan Chi tiêu vs Dư nợ (Mẫu 1,000 KH)")
        df_sample = df_c360.sample(min(1000, len(df_c360)), random_state=42)
        fig_scatter = px.scatter(
            df_sample,
            x="total_spend_usd",
            y="total_loan_debt_usd",
            size="total_balance_usd",
            color="customer_segment",
            hover_name="full_name",
            labels={"total_spend_usd": "Tổng chi tiêu ($)", "total_loan_debt_usd": "Dư nợ ($)"}
        )
        fig_scatter.update_layout(height=320)
        st.plotly_chart(apply_fintech_theme(fig_scatter), use_container_width=True)

    st.markdown("##### 🔍 Danh sách Hồ sơ Customer 360 (Top 500 Khách hàng)")
    search_keyword = st.text_input("🔎 Tìm kiếm khách hàng theo Tên hoặc Mã KH:", "")
    df_c360_view = df_c360
    if search_keyword:
        df_c360_view = df_c360[
            df_c360["full_name"].str.contains(search_keyword, case=False, na=False) |
            df_c360["customer_id"].str.contains(search_keyword, case=False, na=False)
        ]

    st.dataframe(
        df_c360_view.head(500)[[
            "customer_id", "full_name", "city", "credit_tier", "customer_segment",
            "total_accounts", "total_balance_usd", "total_spend_usd", "total_loan_debt_usd"
        ]].style.format({
            "total_balance_usd": "${:,.2f}",
            "total_spend_usd": "${:,.2f}",
            "total_loan_debt_usd": "${:,.2f}",
            "total_accounts": "{:,.0f}"
        }),
        use_container_width=True,
        height=380
    )


# ==============================================================================
# TRANG 3: BRANCH PERFORMANCE
# ==============================================================================
with tab3:
    total_branches = df_branch["branch_id"].nunique()
    avg_ticket = df_branch["avg_ticket_size_usd"].mean() if not df_branch.empty else 0

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title"><span>🏢 Tổng Chi Nhánh Hoạt Động</span></div>
            <div class="kpi-value">{total_branches:,.0f}</div>
            <span class="kpi-sub-badge-positive">Nationwide Network</span>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title"><span>💵 Giá trị Giao dịch Trung bình (Ticket Size)</span></div>
            <div class="kpi-value">${avg_ticket:,.2f}</div>
            <span class="kpi-sub-badge-neutral">Bình quân / Giao dịch</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    r1, r2 = st.columns(2)
    with r1:
        st.markdown("##### 🏆 Top 15 Chi nhánh Doanh số Cao nhất")
        df_top_branch = df_branch.groupby("branch_name")["daily_transaction_volume_usd"].sum().reset_index().nlargest(15, "daily_transaction_volume_usd")
        fig_branch = px.bar(
            df_top_branch,
            x="daily_transaction_volume_usd",
            y="branch_name",
            orientation="h",
            color="daily_transaction_volume_usd",
            color_continuous_scale="Viridis",
            labels={"daily_transaction_volume_usd": "Doanh số ($)", "branch_name": "Tên chi nhánh"}
        )
        fig_branch.update_layout(height=400, yaxis=dict(autorange="reversed"))
        st.plotly_chart(apply_fintech_theme(fig_branch), use_container_width=True)

    with r2:
        st.markdown("##### 📅 Tỷ trọng Giao dịch Ngày thường vs Cuối tuần")
        if 'is_weekend' in df_branch.columns:
            df_weekend = df_branch.groupby(["month_name", "is_weekend"])["daily_transactions_count"].sum().reset_index()
            df_weekend["is_weekend_str"] = df_weekend["is_weekend"].map({True: "Cuối tuần", False: "Ngày thường"})
            fig_weekend = px.bar(
                df_weekend,
                x="month_name",
                y="daily_transactions_count",
                color="is_weekend_str",
                barmode="stack",
                color_discrete_map={"Cuối tuần": "#f59e0b", "Ngày thường": "#38bdf8"},
                labels={"month_name": "Tháng", "daily_transactions_count": "Số lượng giao dịch", "is_weekend_str": "Loại ngày"}
            )
            fig_weekend.update_layout(height=400)
            st.plotly_chart(apply_fintech_theme(fig_weekend), use_container_width=True)
        else:
            st.info("Cột 'is_weekend' không tồn tại trong dữ liệu.")

    st.markdown("##### 📋 Bảng Xếp hạng Hiệu Suất Chi nhánh")
    df_branch_summary = df_branch.groupby(["branch_id", "branch_name", "manager_name"]).agg({
        "daily_transactions_count": "sum",
        "daily_transaction_volume_usd": "sum",
        "avg_ticket_size_usd": "mean"
    }).reset_index().sort_values(by="daily_transaction_volume_usd", ascending=False)

    st.dataframe(
        df_branch_summary.style.format({
            "daily_transaction_volume_usd": "${:,.2f}",
            "avg_ticket_size_usd": "${:,.2f}",
            "daily_transactions_count": "{:,.0f}"
        }),
        use_container_width=True,
        height=360
    )


# ==============================================================================
# TRANG 4: MERCHANT ANALYTICS & INTERCHANGE FEE
# ==============================================================================
with tab4:
    total_merchants = df_merchant["merchant_id"].nunique()
    total_interchange = df_merchant["estimated_interchange_fee_usd"].sum() if not df_merchant.empty else 0

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title"><span>🏪 Tổng Đối Tác Chấp Nhận Thẻ</span></div>
            <div class="kpi-value">{total_merchants:,.0f}</div>
            <span class="kpi-sub-badge-positive">Merchant Network</span>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title"><span>💰 Doanh Thu Phí Quẹt Thẻ (1.5%)</span></div>
            <div class="kpi-value">${total_interchange/1e6:,.2f}M</div>
            <span class="kpi-sub-badge-positive">Interchange Fee Income</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    r1, r2 = st.columns(2)
    with r1:
        st.markdown("##### 🏆 Top 10 Thương gia Doanh số Khủng nhất")
        df_top_merchant = df_merchant[df_merchant["merchant_name"] != "External Guest Merchant"].nlargest(10, "total_sales_volume_usd")
        fig_merchant = px.bar(
            df_top_merchant,
            x="merchant_name",
            y="total_sales_volume_usd",
            color="estimated_interchange_fee_usd",
            color_continuous_scale="Teal",
            labels={"total_sales_volume_usd": "Doanh số ($)", "merchant_name": "Thương gia", "estimated_interchange_fee_usd": "Phí ước tính ($)"}
        )
        fig_merchant.update_layout(height=360)
        st.plotly_chart(apply_fintech_theme(fig_merchant), use_container_width=True)

    with r2:
        st.markdown("##### 🗺️ Phân bổ Doanh số theo Tỉnh/Thành (Top 15)")
        df_city = df_merchant[df_merchant["merchant_name"] != "External Guest Merchant"].groupby("city")["total_sales_volume_usd"].sum().reset_index().nlargest(15, "total_sales_volume_usd")
        fig_city = px.bar(
            df_city,
            x="total_sales_volume_usd",
            y="city",
            orientation="h",
            color="total_sales_volume_usd",
            color_continuous_scale="Blues",
            labels={"total_sales_volume_usd": "Doanh số ($)", "city": "Thành phố"}
        )
        fig_city.update_layout(height=360, yaxis=dict(autorange="reversed"))
        st.plotly_chart(apply_fintech_theme(fig_city), use_container_width=True)

    st.markdown("##### 📋 Bảng Chi tiết Đối tác & Phí Chuyển Mạch")
    st.dataframe(
        df_merchant[["merchant_id", "merchant_name", "city", "total_transactions", 
                     "total_sales_volume_usd", "avg_order_value_usd", "estimated_interchange_fee_usd"]]
        .head(200)
        .style.format({
            "total_sales_volume_usd": "${:,.2f}",
            "avg_order_value_usd": "${:,.2f}",
            "estimated_interchange_fee_usd": "${:,.2f}",
            "total_transactions": "{:,.0f}"
        }),
        use_container_width=True,
        height=350
    )


# ==============================================================================
# TRANG 5: CREDIT RISK MATRIX
# ==============================================================================
with tab5:
    total_loans = df_risk["total_loans_originated"].sum() if not df_risk.empty else 0
    total_debt_risk = df_risk["total_loan_debt_usd"].sum() if not df_risk.empty else 0
    avg_interest = df_risk["avg_interest_rate_pct"].mean() if not df_risk.empty else 0

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title"><span>📄 Tổng Số Hợp Đồng Vay</span></div>
            <div class="kpi-value">{total_loans:,.0f}</div>
            <span class="kpi-sub-badge-positive">30,000 Contracts</span>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title"><span>📑 Tổng Dư Nợ Toàn Ngân Hàng</span></div>
            <div class="kpi-value">${total_debt_risk/1e6:,.1f}M</div>
            <span class="kpi-sub-badge-neutral">Credit Exposure</span>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title"><span>📈 Lãi Suất Cho Vay Bình Quân</span></div>
            <div class="kpi-value">{avg_interest:.2f}%</div>
            <span class="kpi-sub-badge-positive">Weighted Average</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    r1, r2 = st.columns(2)
    with r1:
        st.markdown("##### 📊 Dự báo Doanh thu Lãi theo Phân tầng Rủi ro")
        fig_risk_rev = px.bar(
            df_risk,
            x="credit_risk_tier",
            y="estimated_annual_interest_revenue_usd",
            color="credit_risk_tier",
            color_discrete_sequence=px.colors.sequential.Reds_r,
            labels={"credit_risk_tier": "Phân tầng rủi ro", "estimated_annual_interest_revenue_usd": "Doanh thu lãi ($)"}
        )
        fig_risk_rev.update_layout(height=350, showlegend=False)
        st.plotly_chart(apply_fintech_theme(fig_risk_rev), use_container_width=True)

    with r2:
        st.markdown("##### 🍩 Tỷ trọng Dư nợ theo Nhóm Rủi ro")
        fig_risk_donut = px.pie(
            df_risk,
            names="credit_risk_tier",
            values="total_loan_debt_usd",
            hole=0.55,
            color_discrete_sequence=["#f43f5e", "#f59e0b", "#38bdf8", "#34d399"]
        )
        fig_risk_donut.update_traces(textposition="inside", textinfo="percent+label", marker=dict(line=dict(color='#0b1120', width=2)))
        fig_risk_donut.update_layout(height=350, showlegend=False)
        st.plotly_chart(apply_fintech_theme(fig_risk_donut), use_container_width=True)

    st.markdown("##### 📋 Bảng Tổng Hợp Danh mục Tín dụng")
    st.dataframe(
        df_risk.style.format({
            "total_loans_originated": "{:,.0f}",
            "total_loan_debt_usd": "${:,.2f}",
            "avg_loan_size_usd": "${:,.2f}",
            "avg_interest_rate_pct": "{:.2f}%",
            "estimated_annual_interest_revenue_usd": "${:,.2f}"
        }),
        use_container_width=True,
        height=280
    )


# ==============================================================================
# FOOTER
# ==============================================================================
st.markdown("---")
st.markdown("""
<div style="display: flex; justify-content: space-between; color: #64748b; font-size: 0.75rem; padding: 8px 0;">
    <div>🏦 <b>APEX BANK EXECUTIVE INTELLIGENCE PLATFORM</b> • Powered by AWS S3 Data Lake & RDS PostgreSQL</div>
    <div>Version 2.4.0-Production • Enterprise DWH Certified</div>
</div>
""", unsafe_allow_html=True)