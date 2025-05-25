import streamlit as st
import pandas as pd

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