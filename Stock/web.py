import streamlit as st
from annotated_text import annotated_text
import altair as alt
import pandas as pd
from functions import load_stock_data, calculate_trend, calculate_macd, calculate_rsi, calculate_parabolic_sar

# Set page to wide
st.set_page_config(layout="wide")

# Sidebar
with st.sidebar:
    st.title("**:money_with_wings: :orange[Set] Thailand :green[Stock]**")
    select_stock = st.selectbox("เลือกหุ้น", ("ADVANC", "KBANK"), index=0)

stock_name, company_name, df = load_stock_data("Stock/Stock-Price.xlsx", select_stock)

# Get the first row (latest data)
latest_row = df.iloc[0]
closing_price_str = f"{latest_row['ราคาปิด']:.2f} Baht"
change_str = f"{latest_row['เปลี่ยนแปลง']:+.2f}"
change_percent_str = f"{latest_row['เปลี่ยนแปลง(%)']:+.2f}%"
volumn_str = f"{latest_row['ปริมาณ(พันหุ้น)']:.2f}"
value_str = f"{latest_row['มูลค่า(ล้านบาท)']:.2f}"
low_price = f"{latest_row['ราคาต่ำสุด']:.2f}"
high_price = f"{latest_row['ราคาสูงสุด']:.2f}"

# Sidebar
with st.sidebar:
    annotated_text((f"**{stock_name}**", f"{company_name}"))
    st.metric("**ราคาปิดล่าสุด (Latest Closing Price)**", closing_price_str, f"{change_str} ({change_percent_str})", border=True)
    p1, p2 = st.columns(2)
    with p1: st.subheader(f"**ต่ำสุด: :red[{low_price}]**")
    with p2: st.subheader(f"**สูงสุด: :green[{high_price}]**")
    st.metric("**ปริมาณการซื้อขาย ('000 หุ้น)**", volumn_str, border=True)
    st.metric("**มูลค่าการซื้อขาย (ล้านบาท)**", value_str, border=True)

# Main content
with st.container(border=True):
    st.title(f"**:green[{stock_name}]**")
    st.subheader(f":blue[{company_name}]")

#Graph of Price
st.header(":orange[กราฟราคาย้อนหลัง**]")
chart_df = df[["วันที่", "ราคาปิด", "ราคาสูงสุด", "ราคาต่ำสุด"]].copy()
y_min, y_max = chart_df["ราคาต่ำสุด"].min(), chart_df["ราคาสูงสุด"].max()

line_chart = alt.Chart(chart_df).mark_line(point=False, color="green").encode(
    x=alt.X("วันที่:T", title="เดือน", axis=alt.Axis(format="%b", tickCount="month")),
    y=alt.Y("ราคาปิด:Q", scale=alt.Scale(domain=[y_min, y_max]), title="ราคา"),
    tooltip=["วันที่", "ราคาปิด"]
).properties(width=700, height=400)

tab1, tab2 = st.tabs(["📈 Price Chart", "📉 Price Trend :orange-badge[:material/star: New Feature]"])

# Show chart in TAB1
df_sar = calculate_parabolic_sar(df)

sar_line = alt.Chart(df_sar).mark_circle(color="red", size=20).encode(
    x=alt.X("วันที่:T"),
    y=alt.Y("Parabolic_SAR:Q"),
    tooltip=["วันที่", "Parabolic_SAR"]
)

price_with_sar = (line_chart + sar_line).properties(title="📈 ราคาปิดพร้อม Parabolic SAR")
tab1.altair_chart(price_with_sar, use_container_width=True)

#Trend of Price
df_trend = calculate_trend(df)
y_min, y_max = df_trend["ราคาต่ำสุด"].min(), df_trend["ราคาสูงสุด"].max()

base = alt.Chart(df_trend).encode(
    x=alt.X("วันที่:T", title="เดือน", axis=alt.Axis(format="%b", tickCount="month"))
)
actual_line = base.mark_line(color="blue").encode(
    y=alt.Y("ราคาปิด:Q", title="ราคาปิด", scale=alt.Scale(domain=[y_min, y_max])),
    tooltip=["วันที่", "ราคาปิด"]
)
trend_line = base.mark_line(color="red", strokeDash=[5, 5]).encode(y="Trend:Q")
chart = (actual_line + trend_line).properties(title="📈 แนวโน้มราคาปิด (พร้อมเส้นแนวโน้ม)", width=800, height=400)

# Show chart in TAB2
with tab2:
    with st.expander("📈 แนวโน้มราคาปิด"):
        st.altair_chart(chart, use_container_width=True)

    with st.expander("📉 MACD Indicator"):
        df_macd = calculate_macd(df_trend)
        macd_chart = alt.Chart(df_macd).transform_fold(
            ["MACD", "Signal"]
        ).mark_line().encode(
            x="วันที่:T",
            y="value:Q",
            color="key:N"
        ).properties(width=800, height=300)
        st.altair_chart(macd_chart, use_container_width=True)

    with st.expander("📊 RSI Indicator"):
        df_rsi = calculate_rsi(df_trend)
        rsi_chart = alt.Chart(df_rsi).mark_line(color="orange").encode(
            x="วันที่:T",
            y=alt.Y("RSI:Q", scale=alt.Scale(domain=[0, 100]))
        ).properties(width=800, height=300)
        st.altair_chart(rsi_chart, use_container_width=True)

# Table of Price Details
st.header(":orange[ราคาย้อนหลัง] :violet-badge[:material/star: New Feature]")
col1, col2, col3, col4 = st.columns(4)

# Column selection using checkboxes
with col1:
    st.subheader("ข้อมูลย้อนหลัง 6 เดือน")
    popover = st.popover("Customize")
    opp = popover.checkbox("ราคาเปิด", True)
    mxp = popover.checkbox("ราคาสูงสุด", True)
    lwp = popover.checkbox("ราคาต่ำสุด", True)
    avp = popover.checkbox("ราคาเฉลี่ย", True)
    clp = popover.checkbox("ราคาปิด", True)
    chg = popover.checkbox("เปลี่ยนแปลง", True)
    cgp = popover.checkbox("เปลี่ยนแปลง (%)", True)
    vol = popover.checkbox("ปริมาณ ('000 หุ้น)", True)
    val = popover.checkbox("มูลค่า (ล้านบาท)", True)
    sti = popover.checkbox("SET Index", True)
    scp = popover.checkbox("เปลี่ยนแปลง SET (%)", True)

# Number of rows to show
with col4:
    option = st.selectbox("แสดงข้อมูล", ("10", "20", "50", "100", "ทั้งหมด"), index=1)

# Determine selected columns
selected_columns = ["วันที่"]
if opp: selected_columns.append("ราคาเปิด")
if mxp: selected_columns.append("ราคาสูงสุด")
if lwp: selected_columns.append("ราคาต่ำสุด")
if avp: selected_columns.append("ราคาเฉลี่ย")
if clp: selected_columns.append("ราคาปิด")
if chg: selected_columns.append("เปลี่ยนแปลง")
if cgp: selected_columns.append("เปลี่ยนแปลง(%)")
if vol: selected_columns.append("ปริมาณ(พันหุ้น)")
if val: selected_columns.append("มูลค่า(ล้านบาท)")
if sti: selected_columns.append("SET Index")
if scp: selected_columns.append("SET เปลี่ยนแปลง(%)")

# Filter rows and Display
filtered_df = df[selected_columns] if option == "ทั้งหมด" else df[selected_columns].head(int(option))
if not filtered_df.empty:
    st.dataframe(filtered_df)