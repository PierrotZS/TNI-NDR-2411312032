import streamlit as st
import pandas as pd
import altair as alt
from annotated_text import annotated_text
from sklearn.linear_model import LinearRegression

st.set_page_config(layout="wide")

with st.sidebar:
    st.title("**:money_with_wings: :orange[Set] Thailand :green[Stock]**")
    select_stock = st.selectbox(
        "เลือกหุ้น",
        ("ADVANC", "KBANK"),
        index=0,
        placeholder="เลือกหุ้นเพื่อแสดงข้อมูล",
    )

meta_df = pd.read_excel("Stock-Price.xlsx", sheet_name=select_stock, nrows=2, header=None)
stock_name = meta_df.iloc[0, 0]  
company_name = meta_df.iloc[1, 0] 

# Define Stock-Price file location
df = pd.read_excel("Stock-Price.xlsx", sheet_name="ADVANC", skiprows=3)

# Rename columns
df.columns = [
    "วันที่", "ราคาเปิด", "ราคาสูงสุด", "ราคาต่ำสุด", "ราคาเฉลี่ย", "ราคาปิด",
    "เปลี่ยนแปลง", "เปลี่ยนแปลง(%)", "ปริมาณ(พันหุ้น)", "มูลค่า(ล้านบาท)",
    "SET Index", "SET เปลี่ยนแปลง(%)"
]

# Thai month conversion
thai_months = {
    "ม.ค.": "01", "ก.พ.": "02", "มี.ค.": "03", "เม.ย.": "04",
    "พ.ค.": "05", "มิ.ย.": "06", "ก.ค.": "07", "ส.ค.": "08",
    "ก.ย.": "09", "ต.ค.": "10", "พ.ย.": "11", "ธ.ค.": "12"
}

def convert_thai_date(thai_date_str):
    for th, num in thai_months.items():
        if th in thai_date_str:
            parts = thai_date_str.replace(",", "").split()
            if len(parts) == 3:
                day, month_th, year_th = parts
                month = thai_months.get(month_th)
                year = int(year_th) - 543
                return f"{year}-{month}-{int(day):02d}"
    return None

# Clean and convert date column
df = df[~df["วันที่"].isna() & ~df["วันที่"].astype(str).str.contains("วันที่")]
df["วันที่"] = df["วันที่"].astype(str).apply(convert_thai_date)
df["วันที่"] = pd.to_datetime(df["วันที่"], errors="coerce")
df = df.dropna()
df["วันที่"] = df["วันที่"].dt.date

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

    annotated_text(
        (f"**{stock_name}**", f"{company_name}"),
    )
    st.metric(
        label="**ราคาปิดล่าสุด (Latest Closing Price)**",
        value=closing_price_str,
        delta=f"{change_str} ({change_percent_str})",
        border=True
    )

    p1, p2 = st.columns(2)
    with p1:
        st.subheader(f"**ต่ำสุด: :red[{low_price}]**")
    with p2:
        st.subheader(f"**สูงสุด: :green[{high_price}]**")
    st.metric(
        label="**ปริมาณการซื้อขาย ('000 หุ้น)**",
        value=volumn_str,
        border=True
    )
    st.metric(
        label="**มูลค่าการซื้อขาย (ล้านบาท)**",
        value=value_str,
        border=True
    )

# Main content
with st.container(border=True):
    st.title(f"**:green[{stock_name}]**")
    st.subheader(f":blue[{company_name}]")

st.header(":orange[กราฟราคาย้อนหลัง**]")
# Prepare data
chart_df = df[["วันที่", "ราคาปิด", "ราคาสูงสุด", "ราคาต่ำสุด"]].copy()

# Calculate Y-axis limits
y_min = chart_df["ราคาต่ำสุด"].min() 
y_max = chart_df["ราคาสูงสุด"].max() 

# Build the chart
line_chart = alt.Chart(chart_df).mark_line(point=False,color="green").encode(
    x=alt.X("วันที่:T", title="เดือน", axis=alt.Axis(format="%b", tickCount="month")),
    y=alt.Y("ราคาปิด:Q", scale=alt.Scale(domain=[y_min, y_max]), title="ราคา"),
    tooltip=["วันที่", "ราคาปิด"]
).properties(
    width=700,
    height=400,
)

tab1, tab2 = st.tabs(["📈 Price Chart", "📉 Price Trend"])

# Show chart
tab1.altair_chart(line_chart, use_container_width=True)

# Sort and convert date
df_sorted = df.sort_values("วันที่").copy()
df_sorted["วันที่"] = pd.to_datetime(df_sorted["วันที่"])  # Ensure datetime64[ns]

# Prepare regression
X = df_sorted["วันที่"].map(pd.Timestamp.toordinal).values.reshape(-1, 1)
y = df_sorted["ราคาปิด"].values
model = LinearRegression()
model.fit(X, y)
df_sorted["Trend"] = model.predict(X)

# Calculate Y-axis limits from ราคาต่ำสุด and ราคาสูงสุด
y_min = df_sorted["ราคาต่ำสุด"].min()
y_max = df_sorted["ราคาสูงสุด"].max()

# Chart setup
base = alt.Chart(df_sorted).encode(
    x=alt.X("วันที่:T", title="เดือน", axis=alt.Axis(format="%b", tickCount="month"))  # Month only
)

actual_line = base.mark_line(color="blue").encode(
    y=alt.Y("ราคาปิด:Q", title="ราคาปิด", scale=alt.Scale(domain=[y_min, y_max])),
    tooltip=["วันที่", "ราคาปิด"]
)

trend_line = base.mark_line(color="red", strokeDash=[5, 5]).encode(
    y=alt.Y("Trend:Q")
)

# Combine chart
chart = (actual_line + trend_line).properties(
    title="📈 แนวโน้มราคาปิด (พร้อมเส้นแนวโน้ม)",
    width=800,
    height=400
)

# Show in Streamlit
tab2.altair_chart(chart, use_container_width=True)

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
    option = st.selectbox(
        "แสดงข้อมูล",
        ("10", "20", "50", "100", "ทั้งหมด"),
        index=1,
        placeholder="เลือกแสดงข้อมูล",
    )

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

# Filter rows
if option == "ทั้งหมด":
    filtered_df = df[selected_columns]
else:
    filtered_df = df[selected_columns].head(int(option))

# Display table
if not filtered_df.empty:
    st.dataframe(filtered_df)