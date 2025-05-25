import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np

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

def calculate_macd(df, short=12, long=26, signal=9):
    df = df.copy()
    df["EMA_short"] = df["ราคาปิด"].ewm(span=short, adjust=False).mean()
    df["EMA_long"] = df["ราคาปิด"].ewm(span=long, adjust=False).mean()
    df["MACD"] = df["EMA_short"] - df["EMA_long"]
    df["Signal"] = df["MACD"].ewm(span=signal, adjust=False).mean()
    return df[["วันที่", "MACD", "Signal"]]

def calculate_rsi(df, period=14):
    df = df.copy()
    delta = df["ราคาปิด"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    df["RSI"] = 100 - (100 / (1 + rs))
    return df[["วันที่", "RSI"]]

def calculate_parabolic_sar(df, af=0.02, max_af=0.2):
    df = df.copy()
    high = df["ราคาสูงสุด"].values
    low = df["ราคาต่ำสุด"].values
    close = df["ราคาปิด"].values

    psar = close.copy()
    psar[0] = low[0]  # start with initial PSAR
    bull = True
    ep = high[0]  # extreme point
    af_val = af

    for i in range(1, len(close)):
        prev_psar = psar[i - 1]

        if bull:
            psar[i] = prev_psar + af_val * (ep - prev_psar)
            if low[i] < psar[i]:
                bull = False
                psar[i] = ep
                ep = low[i]
                af_val = af
        else:
            psar[i] = prev_psar + af_val * (ep - prev_psar)
            if high[i] > psar[i]:
                bull = True
                psar[i] = ep
                ep = high[i]
                af_val = af

        if bull:
            if high[i] > ep:
                ep = high[i]
                af_val = min(af_val + af, max_af)
        else:
            if low[i] < ep:
                ep = low[i]
                af_val = min(af_val + af, max_af)

    df["Parabolic_SAR"] = psar
    return df[["วันที่", "Parabolic_SAR"]]