import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# 1. Page Configuration
st.set_page_config(page_title='RaySports Analytics', layout='wide')

# 2. Data Loading
filepath = 'RaySports_Sales_Data_2022_2025_v2.xlsx'

@st.cache_data
def load_data(path):
    df = pd.read_excel(path)
    df = df[['Invoice Date', 'Sales Order Date', 'Platform', 'Brand', 'Order Status', 'Quantity', 'Sales Amount', 'Cost Price']]
    df['Year'] = df['Sales Order Date'].dt.year
    df['MonthNum'] = df['Sales Order Date'].dt.month
    df['MonthName'] = df['Sales Order Date'].dt.strftime('%b')
    df['Profit'] = df['Sales Amount'] - df['Cost Price']
    return df

try:
    df = load_data(filepath)
except Exception as e:
    st.error(f"Error loading file: {e}")
    st.stop()

# --- Helper for Sidebar ---
month_lookup = df[['MonthNum', 'MonthName']].drop_duplicates().sort_values('MonthNum')
all_months = month_lookup['MonthName'].tolist()

def update_months(status):
    for m in all_months: st.session_state[f"chk_{m}"] = status

if 'chk_Jan' not in st.session_state: # Initialize state
    update_months(True)

# --------------------
# 3. Sidebar Filters & Configuration
# --------------------
with st.sidebar:
    st.markdown("## 🎯 Control Center")
    st.caption("Adjust goals and filter business dimensions")

    # --- GOAL SETTING SECTION ---
    with st.expander("📈 Target Configuration", expanded=True):
        sales_target = st.slider(
            "Target Sales Goal ($)",
            min_value=10000, max_value=1000000, value=500000, step=10000,
            help="This updates the Gauge and Progress indicators in real-time."
        )
        st.info(f"Target: **${sales_target:,.0f}**")

    # --- DATE & CHANNEL FILTERS ---
    with st.expander("🗓️ Reporting Period", expanded=True):
        year_filter = st.multiselect(
            "Select Year(s)",
            options=sorted(df['Year'].unique(), reverse=True),
            default=df['Year'].unique()
        )

        st.write("Select Month(s):")
        col_s1, col_s2 = st.columns(2)
        col_s1.button("All", on_click=update_months, args=(True,), use_container_width=True)
        col_s2.button("None", on_click=update_months, args=(False,), use_container_width=True)

        selected_months = []
        with st.container(height=180, border=True):
            for month in all_months:
                if st.checkbox(month, key=f"chk_{month}"):
                    selected_months.append(month)

    with st.expander("🌐 Channel & Platforms", expanded=False):
        platform_filter = st.multiselect(
            "Filter Platforms",
            options=sorted(df['Platform'].unique()),
            default=df['Platform'].unique()
        )

    st.divider()
    st.markdown("### 🛠️ Quick Stats")
    st.caption(f"**Period:** {', '.join(map(str, year_filter)) if year_filter else 'None'}")
    st.caption(f"**Months:** {len(selected_months)} selected")
    st.caption(f"**Channels:** {len(platform_filter)} active")

# Apply Filter
filtered_df = df[(df['Year'].isin(year_filter)) & (df['MonthName'].isin(selected_months)) & (df['Platform'].isin(platform_filter))]

# --------------------
# 4. Dashboard Layout
# --------------------
# --------------------
# 4. Dashboard Header Logic
# --------------------
from datetime import datetime

# Define the header layout
head_col1, head_col2 = st.columns([3, 1])

with head_col1:
    st.markdown(f"""
        <div style="padding-bottom: 20px;">
            <h1 style="margin-bottom: 0px; color: #161B33; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
                RaySports Market Momentum Dashboard
            </h1>
            <p style="font-size: 18px; color: #5E6278; margin-top: 0px;">
                Strategic Performance & Revenue Intelligence
            </p>
        </div>
    """, unsafe_allow_html=True)

with head_col2:
    # Live Status Badge
    current_time = datetime.now().strftime("%d %b %Y | %H:%M")
    st.markdown(f"""
        <div style="background-color: #F1FAFF; border: 1px solid #009EF7; padding: 10px; border-radius: 8px; text-align: right;">
            <span style="color: #009EF7; font-weight: bold; font-size: 12px;">LIVE REPORT STATUS</span><br>
            <span style="color: #161B33; font-size: 14px; font-family: monospace;">{current_time}</span>
        </div>
    """, unsafe_allow_html=True)

top_left, top_right = st.columns([1.2, 2])
current_sales = filtered_df['Sales Amount'].sum()

with top_left:
    progress_ratio = current_sales / sales_target if sales_target > 0 else 0
    bar_color = "#32CD32" if progress_ratio >= 1 else "#F4A460"

    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=current_sales,
        delta={'reference': sales_target, 'position': "bottom", 'increasing': {'color': "green"}, 'decreasing': {'color': "red"}},
        number={'font': {'size': 48, 'color': "#161B33", 'family': "Arial Black"}, 'valueformat': "$,.0f"},
        gauge={
            'axis': {'range': [0, max(sales_target, current_sales) * 1.1], 'tickwidth': 1, 'tickcolor': "gray", 'tickformat': "$,.2s"},
            'bar': {'color': bar_color},
            'bgcolor': "#F0F2F6",
            'borderwidth': 0,
            'threshold': {'line': {'color': "red", 'width': 3}, 'thickness': 0.75, 'value': sales_target}
        }
    ))
    fig_gauge.add_annotation(x=0.5, y=1.25, text=f"<b>TARGET VELOCITY</b><br><span style='font-size:14px; color:gray'>Goal: ${sales_target:,.0f}</span>", showarrow=False, font=dict(size=20, color="#161B33"))
    fig_gauge.update_layout(paper_bgcolor='rgba(0,0,0,0)', height=400, margin=dict(l=40, r=40, t=100, b=40))
    st.plotly_chart(fig_gauge, use_container_width=True)

with top_right:
    st.write("### Executive Summary")
    st.markdown("<style>[data-testid='stMetricValue'] { font-size: 32px; font-weight: bold; color: #161B33; }</style>", unsafe_allow_html=True)

    m1, m2, m3 = st.columns(3)
    total_profit = filtered_df['Profit'].sum()
    margin = (total_profit / current_sales * 100 if current_sales > 0 else 0)

    m1.metric("Gross Revenue", f"${current_sales:,.0f}", delta=f"{progress_ratio * 100:.1f}% of Target")
    m2.metric("Net Profit", f"${total_profit:,.0f}", delta=f"${(current_sales - total_profit):,.0f} Costs", delta_color="inverse")
    m3.metric("Profit Margin", f"{margin:.1f}%", delta="Target: 15%+" if margin < 15 else "Healthy Margin")

    st.divider()
    rem_to_goal = max(sales_target - current_sales, 0)
    col_prog1, col_prog2 = st.columns([3, 1])
    with col_prog1:
        st.write("**Goal Progress**")
        st.progress(min(progress_ratio, 1.0))
    with col_prog2:
        if rem_to_goal > 0: st.write(f":red[**Gap:** ${rem_to_goal:,.0f}]")
        else: st.write(f":green[**Surplus:** ${(current_sales - sales_target):,.0f}]")

# --- ROW 1: Trends & Platforms ---
st.divider()
c1, c2 = st.columns([2, 1])

with c1:
    st.subheader("The Revenue Rhythm")
    monthly_perf = filtered_df.groupby(["MonthNum", "MonthName"], as_index=False)[['Sales Amount', 'Profit']].sum().sort_values("MonthNum")
    fig_trend = px.line(monthly_perf, x="MonthName", y=["Sales Amount", "Profit"], markers=True, template="plotly_white", color_discrete_sequence=["#1f77b4", "#00cc96"])
    fig_trend.update_layout(hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig_trend, use_container_width=True)

with c2:
    st.subheader("Channel Mix")
    fig_donut = px.pie(filtered_df, values='Sales Amount', names='Platform', hole=0.6, template="plotly_white", color_discrete_sequence=px.colors.sequential.Blues_r)
    fig_donut.update_traces(textposition='outside', textinfo='percent+label')
    fig_donut.add_annotation(text=f"Total<br>${current_sales / 1000:.0f}K", showarrow=False, font=dict(size=16, family="Arial Black"))
    fig_donut.update_layout(showlegend=False)
    st.plotly_chart(fig_donut, use_container_width=True)

# --- ROW 2: Advanced Visuals ---
st.divider()
row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.subheader("The Brand Breakdown")
    fig_tree = px.treemap(filtered_df, path=['Platform', 'Brand'], values='Sales Amount', color='Profit', color_continuous_scale='RdYlGn', color_continuous_midpoint=0, template="plotly_white")
    fig_tree.update_layout(margin=dict(t=30, l=10, r=10, b=10))
    st.plotly_chart(fig_tree, use_container_width=True)

with row2_col2:
    st.subheader("The Heavy Hitters")
    brand_sales = filtered_df.groupby('Brand')['Sales Amount'].sum().reset_index()
    top_5 = brand_sales.nlargest(5, 'Sales Amount')['Brand'].tolist()
    brand_plat_filtered = filtered_df[filtered_df['Brand'].isin(top_5)].groupby(['Brand', 'Platform'])['Sales Amount'].sum().reset_index()
    fig_grouped = px.bar(brand_plat_filtered, x='Brand', y='Sales Amount', color='Platform', barmode='group', text_auto='.2s', template="plotly_white")
    fig_grouped.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig_grouped, use_container_width=True)

# --- 5. Data Preview & Export ---
st.divider()
exp_c1, exp_c2 = st.columns([3, 1])
with exp_c1:
    with st.expander("🔍 Inspect Filtered Transactions"):
        st.dataframe(filtered_df.sort_values("Sales Order Date", ascending=False), use_container_width=True,
            column_config={"Sales Amount": st.column_config.NumberColumn(format="$%.2f"), "Profit": st.column_config.NumberColumn(format="$%.2f"),
                           "Margin %": st.column_config.ProgressColumn(format="%.1f%%", min_value=0, max_value=100)})
with exp_c2:
    st.write("### Data Export")

    st.download_button("📥 Download as CSV", data=filtered_df.to_csv(index=False).encode('utf-8'), file_name='RaySports_Data.csv', mime='text/csv', use_container_width=True)
