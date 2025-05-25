import pandas as pd
from sklearn.linear_model import LinearRegression

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

def load_stock_data(filepath, sheet):
    meta_df = pd.read_excel(filepath, sheet_name=sheet, nrows=2, header=None)
    stock_name = meta_df.iloc[0, 0]
    company_name = meta_df.iloc[1, 0]
    df = pd.read_excel(filepath, sheet_name=sheet, skiprows=3)
    df.columns = [
        "วันที่", "ราคาเปิด", "ราคาสูงสุด", "ราคาต่ำสุด", "ราคาเฉลี่ย", "ราคาปิด",
        "เปลี่ยนแปลง", "เปลี่ยนแปลง(%)", "ปริมาณ(พันหุ้น)", "มูลค่า(ล้านบาท)",
        "SET Index", "SET เปลี่ยนแปลง(%)"
    ]
    df = df[~df["วันที่"].isna() & ~df["วันที่"].astype(str).str.contains("วันที่")]
    df["วันที่"] = df["วันที่"].astype(str).apply(convert_thai_date)
    df["วันที่"] = pd.to_datetime(df["วันที่"], errors="coerce")
    df = df.dropna()
    df["วันที่"] = df["วันที่"].dt.date
    return stock_name, company_name, df

def calculate_trend(df):
    df_sorted = df.sort_values("วันที่").copy()
    df_sorted["วันที่"] = pd.to_datetime(df_sorted["วันที่"])
    X = df_sorted["วันที่"].map(pd.Timestamp.toordinal).values.reshape(-1, 1)
    y = df_sorted["ราคาปิด"].values
    model = LinearRegression()
    model.fit(X, y)
    df_sorted["Trend"] = model.predict(X)
    return df_sorted