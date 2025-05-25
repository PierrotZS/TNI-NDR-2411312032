import streamlit as st
from annotated_text import annotated_text
import altair as alt
import pandas as pd
from functions import load_stock_data, enrich_indicators, calculate_signal_score,calculate_moving_average_signal, calculate_summary_score,create_gauge_chart,calculate_macd,calculate_rsi,calculate_parabolic_sar,calculate_trend,get_signal_text
import plotly.graph_objects as go

# Set page to wide
st.set_page_config(layout="wide",page_title="Trade Pierrot")

excel_path = "Stock/Stock-Price.xlsx"
xls = pd.ExcelFile(excel_path)
stock_list = xls.sheet_names

# Sidebar
with st.sidebar:
    st.title("**:money_with_wings: :orange[Set] Thailand :green[Stock]**")
    select_stock = st.selectbox("เลือกหุ้น", stock_list, index=0)

stock_name, company_name, df = load_stock_data(excel_path, select_stock)

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
with tab1:
    st.altair_chart(line_chart, use_container_width=True)

    with st.expander("📊 Candlestick Chart"):
        candle_df = df.copy()
        candle_df["วันที่"] = pd.to_datetime(candle_df["วันที่"])
        candle_df = candle_df.sort_values("วันที่")

        fig = go.Figure(data=[go.Candlestick(
            x=candle_df["วันที่"],
            open=candle_df["ราคาเปิด"],
            high=candle_df["ราคาสูงสุด"],
            low=candle_df["ราคาต่ำสุด"],
            close=candle_df["ราคาปิด"],
            increasing_line_color='green',
            decreasing_line_color='red'
        )])

        fig.update_layout(
            title="Candlestick Chart",
            yaxis_title="Price (Baht)",
            xaxis_title="Date",
            xaxis_rangeslider_visible=False,
            height=500
        )

        st.plotly_chart(fig, use_container_width=True)

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
chart = (actual_line + trend_line).properties(width=800, height=400)

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

    with st.expander("📈 Parabolic SAR"):
        df_sar = calculate_parabolic_sar(df)

        sar_line = alt.Chart(df_sar).mark_circle(color="red", size=20).encode(
            x=alt.X("วันที่:T"),
            y=alt.Y("Parabolic_SAR:Q"),
            tooltip=["วันที่", "Parabolic_SAR"]
        )

        price_with_sar = (line_chart + sar_line)
        st.altair_chart(price_with_sar, use_container_width=True)

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

# enrich indicators
df = enrich_indicators(df)

# คำนวณคะแนนแต่ละตัว
tech_score = calculate_signal_score(df)
ma_score = calculate_moving_average_signal(df)
summary_score = calculate_summary_score(tech_score, ma_score)

# แปลงคะแนนเป็นข้อความ
tech_signal = get_signal_text(tech_score)
ma_signal = get_signal_text(ma_score)
summary_signal = get_signal_text(summary_score)

# แสดงใน 3 คอลัมน์
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### ตัวชี้วัดทางเทคนิค")
    st.plotly_chart(create_gauge_chart(tech_score, "ตัวชี้วัดทางเทคนิค", "black", tech_signal), use_container_width=True)

with col2:
    st.markdown("### สรุป")
    st.plotly_chart(create_gauge_chart(summary_score, "สรุป", "black", summary_signal), use_container_width=True)

with col3:
    st.markdown("#### ค่าเฉลี่ยเคลื่อนที่")
    st.plotly_chart(create_gauge_chart(ma_score, "ค่าเฉลี่ยเคลื่อนที่", "black", ma_signal), use_container_width=True)