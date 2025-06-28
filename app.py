import streamlit as st
import pandas as pd
import altair as alt

# --- Page Configuration ---
st.set_page_config(layout="wide")

# --- Main Title & Data Source ---
st.title("NAND Flash 現貨價格追蹤 (Spot Price Tracker)")
st.markdown("資料來源：[TrendForce](https://trendforce.com.tw/price/flash/flash_spot)")

# --- Data Loading and Caching ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("nand_prices.csv")
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        df['Average Price'] = pd.to_numeric(df['Average Price'], errors='coerce')
        df.dropna(subset=['Average Price'], inplace=True)
        return df
    except FileNotFoundError:
        return None

df = load_data()

if df is None:
    st.error("資料檔案 'nand_prices.csv' 不存在。請先執行爬蟲程式。")
    st.stop()

# --- Sidebar for Controls ---
st.sidebar.header("Control Panel")

# View selector in the sidebar
view_option = st.sidebar.selectbox(
    "Select View Mode:",
    ("Price Data", "Price Trend")
)

# Product selector in the sidebar
product_list = df['Product'].unique()
selected_products = st.sidebar.multiselect(
    'Select Products:',
    options=product_list,
    default=list(product_list)
)

# Filter the dataframe based on sidebar selection
filtered_df = df[df['Product'].isin(selected_products)]


# --- Main Panel Display ---
if view_option == "Price Data":
    st.write("## Price Data")

    def style_price_change(val):
        if isinstance(val, str):
            if val.startswith('▲'):
                return 'color: red'
            elif val.startswith('▼'):
                return 'color: green'
        return ''

    if not filtered_df.empty:
        st.dataframe(filtered_df.style.applymap(style_price_change, subset=['Price Change']))
    else:
        st.warning("請在左方側邊欄選擇至少一項產品。")


elif view_option == "Price Trend":
    st.write("## Price Trend")

    if not filtered_df.empty:
        chart_df = filtered_df.copy()

        # --- Timeframe Selector for the chart ---
        timeframe = st.radio(
            "Select Timeframe:",
            ('Daily', 'Monthly', 'Quarterly', 'Yearly'),
            horizontal=True,
            key='timeframe_selector'
        )

        # --- Resample data based on selection ---
        resample_rule = {
            'Daily': 'D',
            'Monthly': 'M',
            'Quarterly': 'Q',
            'Yearly': 'Y'
        }[timeframe]

        resampled_data = chart_df.set_index('Timestamp').groupby('Product')['Average Price'].resample(resample_rule).mean().reset_index()
        resampled_data.dropna(subset=['Average Price'], inplace=True)

        # --- Create Altair Chart ---
        if not resampled_data.empty:
            base = alt.Chart(resampled_data).encode(
                x=alt.X('Timestamp:T', title='Date'),
                y=alt.Y('Average Price:Q', title='USD', scale=alt.Scale(zero=False)),
                color=alt.Color('Product:N', title='Product')
            )
            lines = base.mark_line()
            points = base.mark_circle(size=60).encode(
                tooltip=[
                    alt.Tooltip('Timestamp:T', title='Date', format='%Y-%m-%d'),
                    alt.Tooltip('Product:N', title='Product'),
                    alt.Tooltip('Average Price:Q', title='USD', format='.3f')
                ]
            )
            chart = (lines + points).interactive()
            st.altair_chart(chart, use_container_width=True)
        else:
            st.write("此時間區間內沒有可顯示的數據。")
    else:
        st.warning("請在左方側邊欄選擇至少一項產品以顯示趨勢圖。")