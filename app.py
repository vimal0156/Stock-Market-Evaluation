import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import yfinance as yf
import requests
from datetime import datetime
import warnings
from utils import *

warnings.filterwarnings("ignore")

# Page configuration
st.set_page_config(
    page_title="Stock Market Technical Analysis",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {padding: 0rem 1rem;}
    h1 {color: #1f77b4; font-weight: 700; padding-bottom: 1rem;}
    h2 {color: #ff7f0e; font-weight: 600; padding-top: 1rem;}
    h3 {color: #2ca02c; font-weight: 500;}
    .footer {text-align: center; padding: 2rem 0; color: #666; font-size: 0.9rem;}
    </style>
""", unsafe_allow_html=True)

PERIOD_OFFSETS = {
    "1mo": pd.DateOffset(months=1),
    "3mo": pd.DateOffset(months=3),
    "6mo": pd.DateOffset(months=6),
    "1y": pd.DateOffset(years=1),
    "2y": pd.DateOffset(years=2),
    "5y": pd.DateOffset(years=5),
}


def _filter_period(df: pd.DataFrame, period: str) -> pd.DataFrame:
    if df.empty or period == "max":
        return df

    offset = PERIOD_OFFSETS.get(period)
    if offset is None:
        return df

    cutoff = df["open_time"].max() - offset
    filtered = df[df["open_time"] >= cutoff]
    return filtered


@st.cache_data(ttl=900)
def fetch_stock_data_alpha_vantage(symbol: str, interval: str, period: str, api_key: str) -> pd.DataFrame:
    if not api_key:
        raise ValueError("Alpha Vantage API key is required.")

    base_url = "https://www.alphavantage.co/query"
    params = {"symbol": symbol.upper(), "apikey": api_key.strip()}

    interval_map = {
        "1h": ("TIME_SERIES_INTRADAY", "60min", "Time Series (60min)", {"interval": "60min"}),
        "4h": ("TIME_SERIES_INTRADAY", "60min", "Time Series (60min)", {"interval": "60min"}),
        "1d": ("TIME_SERIES_DAILY_ADJUSTED", None, "Time Series (Daily)", {}),
        "1wk": ("TIME_SERIES_WEEKLY", None, "Weekly Time Series", {}),
        "1mo": ("TIME_SERIES_MONTHLY", None, "Monthly Time Series", {}),
    }

    if interval not in interval_map:
        raise ValueError(f"Unsupported interval '{interval}' for Alpha Vantage.")

    function_name, av_interval, payload_key, extra_params = interval_map[interval]
    params.update({"function": function_name, "outputsize": "full"})
    params.update(extra_params)

    response = requests.get(base_url, params=params, timeout=30)

    if response.status_code != 200:
        raise ValueError(f"Alpha Vantage request failed with status {response.status_code}.")

    payload = response.json()

    if "Note" in payload:
        raise ValueError("Alpha Vantage API limit reached. Please wait a minute and try again.")

    if "Error Message" in payload:
        raise ValueError("Alpha Vantage returned an error. Please verify the ticker symbol and API key.")

    time_series = payload.get(payload_key)
    if not time_series:
        raise ValueError("Alpha Vantage response did not contain expected time series data.")

    records = []
    for timestamp, values in time_series.items():
        try:
            records.append(
                {
                    "open_time": pd.to_datetime(timestamp),
                    "Open": float(values.get("1. open", 0.0)),
                    "High": float(values.get("2. high", 0.0)),
                    "Low": float(values.get("3. low", 0.0)),
                    "Close": float(values.get("4. close", 0.0)),
                    "Volume": float(values.get("6. volume") or values.get("5. volume", 0.0)),
                }
            )
        except (TypeError, ValueError):
            continue

    df = pd.DataFrame(records)

    if df.empty:
        raise ValueError("No data returned from Alpha Vantage for the selected configuration.")

    df = df.sort_values("open_time").reset_index(drop=True)

    if interval == "4h":
        df = (
            df.set_index("open_time")
            .resample("4H", label="left", closed="left")
            .agg({
                "Open": "first",
                "High": "max",
                "Low": "min",
                "Close": "last",
                "Volume": "sum",
            })
            .dropna()
            .reset_index()
        )

    df = _filter_period(df, period)

    return df.reset_index(drop=True)


@st.cache_data(ttl=3600)
def fetch_stock_data_yfinance(symbol: str, interval: str, period: str) -> pd.DataFrame:
    ticker = yf.Ticker(symbol)
    df = ticker.history(period=period, interval=interval)

    if df.empty:
        return pd.DataFrame()

    df = df.reset_index()

    if "Datetime" in df.columns:
        df = df.rename(columns={"Datetime": "open_time"})
    elif "Date" in df.columns:
        df = df.rename(columns={"Date": "open_time"})

    return df

def load_uploaded_csv(uploaded_file) -> pd.DataFrame:
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as exc:
        raise ValueError("Failed to read the uploaded CSV file. Please ensure it is a valid CSV.") from exc

    if df.empty:
        raise ValueError("Uploaded CSV appears to be empty.")

    column_map = {}
    lower_columns = {col.lower(): col for col in df.columns}

    for candidate in ["open_time", "datetime", "date", "timestamp"]:
        if candidate in lower_columns:
            column_map[lower_columns[candidate]] = "open_time"
            break

    if "open_time" not in column_map.values():
        raise ValueError(
            "CSV must contain a date/time column (e.g., 'open_time', 'datetime', 'date', or 'timestamp')."
        )

    price_columns = {
        "open": "Open",
        "high": "High",
        "low": "Low",
        "close": "Close",
        "volume": "Volume",
    }

    for source, target in price_columns.items():
        if source in lower_columns:
            column_map[lower_columns[source]] = target

    required_targets = {"Open", "High", "Low", "Close"}
    if not required_targets.issubset(set(column_map.values())):
        raise ValueError(
            "CSV must contain columns for open, high, low, and close prices (case-insensitive)."
        )

    df = df.rename(columns=column_map)
    df["open_time"] = pd.to_datetime(df["open_time"], errors="coerce")
    df = df.dropna(subset=["open_time", "Open", "High", "Low", "Close"])

    if df.empty:
        raise ValueError("No valid rows found after parsing the uploaded CSV.")

    return df.sort_values("open_time").reset_index(drop=True)


def plot_candlesticks(df, title="Candlestick Chart"):
    """Plot basic candlestick chart"""
    fig = go.Figure(data=[go.Candlestick(
        x=df['open_time'],
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        increasing_line_color='#26a69a',
        decreasing_line_color='#ef5350'
    )])

    fig.update_layout(
        title=title,
        xaxis_title="Time",
        yaxis_title="Price",
        xaxis_rangeslider_visible=False,
        template='plotly_dark',
        height=600,
        hovermode='x unified'
    )
    
    return fig

def plot_trend_analysis(df, threshold=None, title="Technical Analysis"):
    """Plot comprehensive trend analysis"""
    fig = go.Figure(data=[go.Candlestick(
        x=df['open_time'],
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        increasing_line_color='#26a69a',
        decreasing_line_color='#ef5350',
        name='Price'
    )])

    if 'resistance' in df.columns:
        fig.add_trace(go.Scatter(
            x=df['open_time'], y=df['resistance'], mode='lines',
            line=dict(color='rgba(255, 220, 100, 0.8)', width=2),
            name='Local Resistance'
        ))

    if 'support' in df.columns:
        fig.add_trace(go.Scatter(
            x=df['open_time'], y=df['support'], mode='lines',
            line=dict(color='rgba(255, 220, 100, 0.8)', width=2),
            name='Local Support'
        ))

    if 'resistance_global' in df.columns:
        fig.add_trace(go.Scatter(
            x=df['open_time'], y=df['resistance_global'], mode='lines',
            line=dict(color='#ff6b6b', width=3),
            name='Global Resistance'
        ))

    if 'support_global' in df.columns:
        fig.add_trace(go.Scatter(
            x=df['open_time'], y=df['support_global'], mode='lines',
            line=dict(color='#4ecdc4', width=3),
            name='Global Support'
        ))

    if threshold is not None:
        for seuil in threshold:
            fig.add_hline(
                y=seuil[0],
                line=dict(color='#7FDBFF', dash='dash', width=1.5),
                opacity=0.6,
                annotation_text=f'Level: {seuil[0]:.2f}',
                annotation_position='right'
            )

    fig.update_layout(
        title=title,
        xaxis_title="Time",
        yaxis_title="Price",
        xaxis_rangeslider_visible=False,
        template='plotly_dark',
        height=700,
        hovermode='x unified',
        showlegend=True,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )
    
    return fig

def main():
    if "alpha_vantage_api_key" not in st.session_state:
        st.session_state["alpha_vantage_api_key"] = ""

    st.title("📈 Stock Market Technical Analysis Platform")
    st.markdown("### Advanced Trend Detection & Support/Resistance Analysis")
    st.markdown("---")

    with st.sidebar:
        st.header("⚙️ Configuration")

        st.subheader("Data Source")
        data_mode = st.radio(
            "Choose Input Method",
            ["Fetch via API", "Upload CSV"],
            help="Use API providers for live data or upload your own CSV as a fallback."
        )

        if data_mode == "Fetch via API":
            st.subheader("API Configuration")
            alpha_api_key = st.text_input(
                "Alpha Vantage API Key",
                type="password",
                help="Enter your Alpha Vantage API key to enable the Alpha Vantage data provider.",
                key="alpha_vantage_api_key"
            )
            data_provider_options = ["Alpha Vantage", "Yahoo Finance"]
            provider_index = 0 if alpha_api_key else 1
            data_provider = st.radio(
                "Select Data Provider",
                data_provider_options,
                index=provider_index,
                help="Alpha Vantage requires an API key and offers up to 5 calls/minute on the free tier."
            )
            st.caption("Alpha Vantage free tier limits: 5 API calls/minute, 500 calls/day.")
        else:
            alpha_api_key = ""
            data_provider = None
            uploaded_csv = st.file_uploader(
                "Upload OHLC CSV",
                type=["csv"],
                help="Required columns: date/time plus open, high, low, close. Volume is optional."
            )

        st.subheader("Stock Selection")
        symbol = st.text_input(
            "Enter Stock Symbol",
            value="BNB-USD",
            help="Enter a valid Yahoo Finance ticker (e.g., BNB-USD, BTC-USD, AAPL, TSLA)"
        )

        
        st.subheader("Time Period")
        period_options = {
            "1 Month": "1mo", "3 Months": "3mo", "6 Months": "6mo",
            "1 Year": "1y", "2 Years": "2y", "5 Years": "5y", "Max": "max"
        }
        period = st.selectbox("Select Period", list(period_options.keys()), index=3)
        
        st.subheader("Time Interval")
        interval_options = {
            "1 Hour": "1h", "4 Hours": "4h", "1 Day": "1d",
            "1 Week": "1wk", "1 Month": "1mo"
        }
        interval = st.selectbox("Select Interval", list(interval_options.keys()), index=0)
        
        st.markdown("---")
        
        st.subheader("Analysis Parameters")
        
        moving_avg_period = st.slider(
            "Moving Average Period (hours)",
            min_value=50, max_value=500, value=200, step=50,
            help="Period for calculating moving averages"
        )
        
        learning_rate = st.slider(
            "Peak Detection Sensitivity",
            min_value=0.05, max_value=0.50, value=0.15, step=0.05,
            help="Lower values detect more peaks"
        )
        
        num_psychological_levels = st.slider(
            "Number of Psychological Levels",
            min_value=3, max_value=15, value=10, step=1
        )
        
        st.markdown("---")
        
        st.subheader("Display Options")
        show_local_trend = st.checkbox("Show Local Trend", value=True)
        show_global_trend = st.checkbox("Show Global Trend", value=True)
        show_psychological = st.checkbox("Show Psychological Levels", value=True)
        
        st.markdown("---")
        
        fetch_button = st.button("🔄 Fetch & Analyze", type="primary", use_container_width=True)

    if fetch_button:
        if data_mode == "Upload CSV":
            if "uploaded_csv" not in locals() or uploaded_csv is None:
                st.error("❌ Please upload a CSV file to proceed.")
                return

            with st.spinner("Loading uploaded CSV data..."):
                try:
                    df = load_uploaded_csv(uploaded_csv)
                    df = _filter_period(df, period_options[period])
                except ValueError as err:
                    st.error(f"❌ {err}")
                    return

            st.success(f"✅ Loaded {len(df)} rows from uploaded CSV")
        else:
            provider_key = "alpha" if data_provider == "Alpha Vantage" else "yfinance"
            with st.spinner(f"Fetching data for {symbol} via {data_provider}..."):
                try:
                    if provider_key == "alpha":
                        if not alpha_api_key:
                            raise ValueError("Please provide an Alpha Vantage API key or switch to Yahoo Finance.")
                        df = fetch_stock_data_alpha_vantage(
                            symbol,
                            interval_options[interval],
                            period_options[period],
                            alpha_api_key
                        )
                    else:
                        df = fetch_stock_data_yfinance(
                            symbol,
                            interval_options[interval],
                            period_options[period]
                        )
                except ValueError as err:
                    st.error(f"❌ {err}")
                    return
                except Exception as err:
                    st.error(f"❌ Unexpected error while fetching data: {err}")
                    return

            if df is None or df.empty:
                st.error("❌ Failed to fetch data. Please check the symbol and try again.")
                return

            st.success(
                f"✅ {data_provider} returned {len(df)} data points for {symbol}"
            )

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Current Price", f"${df['Close'].iloc[-1]:.2f}")

        with col2:
            if len(df) >= 2:
                price_change = df['Close'].iloc[-1] - df['Close'].iloc[-2]
                price_change_pct = (price_change / df['Close'].iloc[-2]) * 100
                st.metric("Previous Close Change", f"${price_change:.2f}", f"{price_change_pct:.2f}%")
            else:
                st.metric("Previous Close Change", "N/A", "0.00%")

        with col3:
            st.metric("High", f"${df['High'].max():.2f}")

        with col4:
            st.metric("Low", f"${df['Low'].min():.2f}")

        st.markdown("---")

        st.subheader("📊 Price Chart")
        basic_fig = plot_candlesticks(df, f"{symbol} - {interval} Interval")
        st.plotly_chart(basic_fig, use_container_width=True)

        st.markdown("---")

        try:
            with st.spinner("Performing technical analysis..."):
                df['periode'] = pd.to_datetime(df['open_time']).dt.floor(f'{moving_avg_period}H')
                moyenne_mobile = df.groupby('periode')['Open'].mean()
                min_mobile = df.groupby('periode')['Low'].min()
                max_mobile = df.groupby('periode')['High'].max()

                analysis_df = df.copy()

                if show_local_trend:
                    try:
                        moyenne, max_trend, min_trend, frame, index = find_trend(
                            moyenne_mobile, max_mobile, min_mobile
                        )

                        a_resistance, b_resistance, new_max_mobile = fit_resistance_from_maxima(max_trend)
                        a_support, b_support, new_min_mobile = fit_support_from_minimum(min_trend)

                        analysis_df['resistance'] = define_resistance(new_max_mobile, analysis_df)
                        analysis_df['resistance'] = analysis_df['resistance'].replace(0.0, np.nan)

                        analysis_df['support'] = define_support(new_min_mobile, analysis_df)
                        analysis_df['support'] = analysis_df['support'].replace(0.0, np.nan)

                        st.success("✅ Local trend lines detected")
                    except Exception as e:
                        st.warning(f"⚠️ Could not detect local trends: {str(e)}")

                if show_global_trend:
                    try:
                        resistance_global, support_global, max_peaks = global_trend(
                            analysis_df, learning_rate
                        )

                        analysis_df['resistance_global'] = resistance_global
                        analysis_df['resistance_global'] = analysis_df['resistance_global'].replace(0.0, np.nan)

                        analysis_df['support_global'] = support_global
                        analysis_df['support_global'] = analysis_df['support_global'].replace(0.0, np.nan)

                        st.success("✅ Global trend lines detected")
                    except Exception as e:
                        st.warning(f"⚠️ Could not detect global trends: {str(e)}")

                psychological_levels = None
                if show_psychological:
                    try:
                        psychological_levels = find_psychological_levels(
                            analysis_df, num_psychological_levels, cutting=15000
                        )
                        st.success(f"✅ {len(psychological_levels)} psychological levels detected")
                    except Exception as e:
                        st.warning(f"⚠️ Could not detect psychological levels: {str(e)}")

                st.subheader("🎯 Technical Analysis")
                analysis_fig = plot_trend_analysis(
                    analysis_df, threshold=psychological_levels,
                    title=f"{symbol} - Complete Technical Analysis"
                )
                st.plotly_chart(analysis_fig, use_container_width=True)

                st.markdown("---")
                st.subheader("📋 Analysis Summary")

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("#### 🔴 Resistance Levels")
                    if 'resistance' in analysis_df.columns:
                        local_resistance = analysis_df['resistance'].dropna()
                        if not local_resistance.empty:
                            st.write(f"**Local Resistance:** ${local_resistance.iloc[-1]:.2f}")

                    if 'resistance_global' in analysis_df.columns:
                        global_resistance = analysis_df['resistance_global'].dropna()
                        if not global_resistance.empty:
                            st.write(f"**Global Resistance:** ${global_resistance.iloc[-1]:.2f}")

                with col2:
                    st.markdown("#### 🔵 Support Levels")
                    if 'support' in analysis_df.columns:
                        local_support = analysis_df['support'].dropna()
                        if not local_support.empty:
                            st.write(f"**Local Support:** ${local_support.iloc[-1]:.2f}")

                    if 'support_global' in analysis_df.columns:
                        global_support = analysis_df['support_global'].dropna()
                        if not global_support.empty:
                            st.write(f"**Global Support:** ${global_support.iloc[-1]:.2f}")

                if psychological_levels:
                    st.markdown("#### 🎯 Key Psychological Levels")
                    psych_df = pd.DataFrame(psychological_levels, columns=['Price Level', 'Touch Count'])
                    psych_df['Price Level'] = psych_df['Price Level'].apply(lambda x: f"${x:.2f}")
                    st.dataframe(psych_df, use_container_width=True, hide_index=True)

                st.markdown("---")
                st.subheader("💾 Download Data")
                csv = analysis_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Analysis Data (CSV)",
                    data=csv,
                    file_name=f"{symbol}_analysis_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )

        except Exception as e:
            st.error(f"❌ Analysis error: {str(e)}")
    
    else:
        st.info("👈 Configure your analysis parameters in the sidebar and click 'Fetch & Analyze' to begin.")
        
        st.markdown("---")
        st.subheader("📚 About This Application")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            #### Features
            - **Real-time Data**: Fetch live market data via Yahoo Finance API
            - **Local Trend Detection**: Identify short-term support and resistance
            - **Global Trend Analysis**: Detect major trend lines across the dataset
            - **Psychological Levels**: Find key price levels with high touch frequency
            - **Interactive Charts**: Zoom, pan, and explore data with Plotly
            """)
        
        with col2:
            st.markdown("""
            #### Supported Assets
            - Cryptocurrencies (BTC-USD, ETH-USD, BNB-USD, etc.)
            - Stocks (AAPL, TSLA, GOOGL, etc.)
            - Forex pairs (EURUSD=X, GBPUSD=X, etc.)
            - Indices (^GSPC, ^DJI, ^IXIC, etc.)
            - Commodities (GC=F, CL=F, etc.)
            """)
    
    st.markdown("---")
    st.markdown(
        '<div class="footer">Developed by <strong>Vimal Dhama</strong> | '
        'Stock Market Technical Analysis Platform © 2025</div>',
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
