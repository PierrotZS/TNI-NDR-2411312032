import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
import plotly.graph_objects as go

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
    return stock_name, company_name, df.reset_index(drop=True)

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
    rs = avg_gain / avg_loss.replace(0, np.nan)  # ป้องกัน division by zero
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

def calculate_signal_score(df):
    latest = df.iloc[-1]

    score = 50  # เริ่มต้นกลางที่ 'ถือหุ้นไว้'
    
    # MACD
    if "MACD" in df.columns and "Signal" in df.columns:
        if latest["MACD"] > latest["Signal"]:
            score += 15  # Bullish
        else:
            score -= 15  # Bearish

    # RSI
    if "RSI" in df.columns:
        if latest["RSI"] > 70:
            score -= 10  # Overbought
        elif latest["RSI"] < 30:
            score += 10  # Oversold

    # Parabolic SAR
    if "Parabolic_SAR" in df.columns:
        if latest["ราคาปิด"] > latest["Parabolic_SAR"]:
            score += 10
        else:
            score -= 10

    return max(0, min(100, score))  # clamp between 0-100

def enrich_indicators(df):
    df = df.copy()
    macd_df = calculate_macd(df)
    rsi_df = calculate_rsi(df)
    sar_df = calculate_parabolic_sar(df)
    
    df = df.merge(macd_df, on="วันที่", how="left")
    df = df.merge(rsi_df, on="วันที่", how="left")
    df = df.merge(sar_df, on="วันที่", how="left")
    
    return df

def calculate_moving_average_signal(df):
    df = df.copy()
    df["MA5"] = df["ราคาปิด"].rolling(window=5).mean()
    df["MA10"] = df["ราคาปิด"].rolling(window=10).mean()
    df["MA20"] = df["ราคาปิด"].rolling(window=20).mean()

    latest = df.iloc[-1]
    score = 50

    if latest["ราคาปิด"] > latest["MA5"]:
        score += 10
    else:
        score -= 10

    if latest["ราคาปิด"] > latest["MA10"]:
        score += 10
    else:
        score -= 10

    if latest["ราคาปิด"] > latest["MA20"]:
        score += 10
    else:
        score -= 10

    return max(0, min(100, score))  # clamp 0-100


def calculate_summary_score(tech_score, ma_score):
    return int((tech_score + ma_score) / 2)

def get_signal_text(score):
    if score < 20:
        return "เท"
    elif score < 40:
        return "ขาย"
    elif score < 60:
        return "ถือหุ้นไว้"
    elif score < 80:
        return "ซื้อ"
    else:
        return "ซื้อทันที"

def create_gauge_chart(value, title, color, signal_text):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number={'font': {'color': 'rgba(0,0,0,0)', 'size': 1}},  # ซ่อนตัวเลข
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 20}},
        gauge={
            'axis': {'range': [0, 100], 'tickvals': [0, 20, 40, 60, 80, 100],
                     'ticktext': ["0", "20", "40", "60", "80", "100"]},
            'bar': {'color': color},
            'steps': [
                {'range': [0, 20], 'color': '#ff4d4f'},
                {'range': [20, 40], 'color': '#ffa39e'},
                {'range': [40, 60], 'color': '#d9d9d9'},
                {'range': [60, 80], 'color': '#b7eb8f'},
                {'range': [80, 100], 'color': '#52c41a'}
            ],
        }
    ))

    # เพิ่มข้อความตรงกลางด้วย annotation
    fig.add_annotation(
        x=0.5, y=0.5,
        text=f"<b>{signal_text}</b>",
        showarrow=False,
        font=dict(size=28, color="white")
    )

    fig.update_layout(height=300, margin=dict(t=40, b=0, l=20, r=20))
    return fig