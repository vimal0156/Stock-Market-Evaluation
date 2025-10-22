# 📖 Usage Guide - Stock Market Technical Analysis Platform

## Table of Contents

1. [Installation](#installation)
2. [Running the Application](#running-the-application)
3. [Using the Interface](#using-the-interface)
4. [Understanding the Analysis](#understanding-the-analysis)
5. [Troubleshooting](#troubleshooting)
6. [Examples](#examples)

---

## Installation

### Step 1: Install Python

Ensure you have Python 3.10 or higher installed on your system.

```bash
python --version
```

### Step 2: Install Dependencies

Navigate to the project directory and install required packages:

```bash
cd "Stock market evaluation"
pip install -r requirements.txt
```

**Required Packages:**

- streamlit==1.31.0
- pandas==2.1.4
- numpy==1.26.3
- plotly==5.18.0
- scipy==1.11.4
- yfinance==0.2.36
- matplotlib==3.8.2
- scikit-learn==1.4.0

---

## Running the Application

### Start the Streamlit Server

```bash
streamlit run app.py
```

The application will automatically open in your default web browser at `http://localhost:8501`

### Alternative: Specify Port

```bash
streamlit run app.py --server.port 8502
```

---

## Using the Interface

### 1. Sidebar Configuration

#### Stock Selection
- **Input Field**: Enter any valid Yahoo Finance ticker symbol
- **Examples**: 
  - Crypto: `BNB-USD`, `BTC-USD`, `ETH-USD`
  - Stocks: `AAPL`, `TSLA`, `GOOGL`, `MSFT`
  - Forex: `EURUSD=X`, `GBPUSD=X`
  - Indices: `^GSPC`, `^DJI`, `^IXIC`

#### Time Period

Choose the historical data range:
- **1 Month**: Recent short-term analysis
- **3 Months**: Quarterly trends
- **6 Months**: Medium-term patterns
- **1 Year**: Annual analysis (recommended)
- **2 Years**: Long-term trends
- **5 Years**: Extended historical view
- **Max**: All available data

#### Time Interval

Select the candlestick interval:
- **1 Hour**: Intraday trading (requires recent period)
- **4 Hours**: Short-term swing trading
- **1 Day**: Daily analysis (most common)
- **1 Week**: Weekly trends
- **1 Month**: Long-term investing

#### Analysis Parameters

**Moving Average Period (50-500 hours)**
- Controls the window for trend detection
- Lower values: More sensitive to short-term changes
- Higher values: Smoother, longer-term trends
- **Recommended**: 200 hours for balanced analysis

**Peak Detection Sensitivity (0.05-0.50)**
- Determines how prominent a peak must be to be detected
- Lower values: Detect more peaks (more trend lines)
- Higher values: Detect fewer, more significant peaks
- **Recommended**: 0.15 for balanced detection

**Number of Psychological Levels (3-15)**
- How many key price levels to identify
- More levels: Detailed analysis
- Fewer levels: Focus on most significant zones
- **Recommended**: 10 levels

#### Display Options

Toggle visualization layers:
- ☑️ **Show Local Trend**: Short-term support/resistance
- ☑️ **Show Global Trend**: Major long-term trend lines
- ☑️ **Show Psychological Levels**: Key price zones

### 2. Main Dashboard

#### Metrics Panel

After fetching data, view key statistics:
- **Current Price**: Latest closing price
- **24h Change**: Price change and percentage
- **High**: Maximum price in the period
- **Low**: Minimum price in the period

#### Price Chart

Basic candlestick visualization:
- **Green candles**: Price increased (bullish)
- **Red candles**: Price decreased (bearish)
- **Interactive**: Zoom, pan, hover for details

#### Technical Analysis Chart

Comprehensive analysis with overlays:
- **Yellow lines**: Local support/resistance
- **Red line**: Global resistance
- **Cyan line**: Global support
- **Dashed cyan lines**: Psychological levels

#### Analysis Summary

Detailed breakdown of detected levels:
- **Resistance Levels**: Price ceilings
- **Support Levels**: Price floors
- **Psychological Levels**: High-frequency touch points

#### Download Data

Export analysis results as CSV for further processing.

### 3. Uploading CSV Data (Fallback Mode)

If APIs are unavailable or you prefer offline data:

- Switch the **Data Source** radio to `Upload CSV` in the sidebar.
- Provide a CSV containing at least these columns (case-insensitive):
  - Time column (`open_time`, `datetime`, `date`, or `timestamp`)
  - `open`, `high`, `low`, `close`
  - Optional: `volume`
- The app automatically parses, sorts, and filters the uploaded dataset.
- All downstream analytics, charts, and downloads operate the same as with API data.

---

## Understanding the Analysis

### Local Trend Lines

**What they are:**
- Short-term support and resistance based on recent price action
- Calculated using moving averages and peak detection

**How to interpret:**
- **Local Resistance** (upper line): Price may struggle to break above
- **Local Support** (lower line): Price may find buying pressure

**Trading implications:**
- Consider selling near local resistance
- Consider buying near local support
- Breakouts above/below indicate trend changes

### Global Trend Lines

**What they are:**
- Major trend lines spanning the entire dataset
- Identified by scoring all possible peak combinations

**How to interpret:**
- **Global Resistance**: Long-term ceiling, strong selling pressure
- **Global Support**: Long-term floor, strong buying pressure

**Trading implications:**
- Breaking global resistance = strong bullish signal
- Breaking global support = strong bearish signal
- Respect these levels for position sizing

### Psychological Levels

**What they are:**
- Price zones where the market has repeatedly interacted
- Often round numbers or historically significant prices

**How to interpret:**
- High touch count = strong psychological significance
- Price tends to pause or reverse at these levels

**Trading implications:**
- Set take-profit orders near psychological levels
- Watch for breakout confirmations
- Use as reference points for stop-losses

---

## Troubleshooting

### Common Issues

#### 1. "Failed to fetch data"

**Causes:**
- Invalid ticker symbol
- No data available for the selected period/interval
- Internet connection issues
- Yahoo Finance API temporarily unavailable

**Solutions:**
- Verify ticker symbol on Yahoo Finance website
- Try a different time period or interval
- Check internet connection
- Wait and retry later

#### 2. "Could not detect local trends"

**Causes:**
- Insufficient data points
- Moving average period too large
- Highly volatile or irregular price action

**Solutions:**
- Increase the time period
- Reduce moving average period
- Try a different interval

#### 3. "Could not detect global trends"

**Causes:**
- Not enough significant peaks
- Peak detection sensitivity too high

**Solutions:**
- Lower the peak detection sensitivity
- Increase the time period
- Try a different asset with more volatility

#### 4. "Could not detect psychological levels"

**Causes:**
- Insufficient price data
- Extremely volatile or trending market

**Solutions:**
- Increase the time period
- Reduce the number of requested levels
- Try a different interval

### Performance Issues

**Slow loading:**
- Reduce the time period
- Use larger intervals (daily instead of hourly)
- Close other browser tabs

**Memory errors:**
- Reduce the number of psychological levels
- Use shorter time periods
- Restart the application

---

## Examples

### Example 1: Bitcoin Daily Analysis

**Configuration:**
- Symbol: `BTC-USD`
- Period: `1 Year`
- Interval: `1 Day`
- Moving Average: `200`
- Sensitivity: `0.15`
- Psychological Levels: `10`

**Expected Results:**
- Clear global trend lines showing bull/bear markets
- Multiple psychological levels at round numbers ($20k, $30k, etc.)
- Local trends showing recent consolidation patterns

### Example 2: Apple Stock Weekly Analysis

**Configuration:**
- Symbol: `AAPL`
- Period: `2 Years`
- Interval: `1 Week`
- Moving Average: `150`
- Sensitivity: `0.20`
- Psychological Levels: `8`

**Expected Results:**
- Long-term trend lines showing stock trajectory
- Support levels at previous consolidation zones
- Resistance at all-time highs

### Example 3: BNB Intraday Trading

**Configuration:**
- Symbol: `BNB-USD`
- Period: `1 Month`
- Interval: `1 Hour`
- Moving Average: `100`
- Sensitivity: `0.10`
- Psychological Levels: `12`

**Expected Results:**
- Detailed short-term support/resistance
- Multiple local trends for day trading
- Frequent psychological levels for scalping

---

## Best Practices

### For Day Trading
- Use 1-hour or 4-hour intervals
- Focus on local trends
- Monitor psychological levels closely
- Update analysis multiple times per day

### For Swing Trading
- Use daily intervals
- Balance local and global trends
- Set alerts at key levels
- Review analysis weekly

### For Long-Term Investing
- Use weekly or monthly intervals
- Focus on global trends
- Identify major support zones for entry
- Review analysis monthly

---

## Tips for Success

1. **Combine with other indicators**: Use this analysis alongside volume, RSI, MACD
2. **Confirm breakouts**: Wait for price to close above/below levels
3. **Use stop-losses**: Place stops below support or above resistance
4. **Consider market context**: Factor in news, events, and overall market sentiment
5. **Backtest strategies**: Use historical data to validate your approach
6. **Risk management**: Never risk more than 1-2% per trade
7. **Regular updates**: Refresh analysis as new data becomes available

---

## Advanced Features

### Data Export
Download CSV files containing:
- OHLC data
- Calculated trend lines
- Support/resistance levels
- Timestamps

Use exported data for:
- Backtesting strategies
- Custom analysis in Excel/Python
- Record keeping and journaling

### Custom Analysis
Modify `utils.py` to:
- Adjust scoring algorithms
- Add custom indicators
- Change tolerance levels
- Implement new detection methods

---

## Support & Resources

### Getting Help
- Review this guide thoroughly
- Check the main README.md for technical details
- Examine the Jupyter notebook for algorithm explanations
- Test with known assets (BTC-USD, AAPL) first

### Learning Resources
- **Technical Analysis**: Study candlestick patterns, support/resistance
- **Python**: Learn Pandas, NumPy for data analysis
- **Streamlit**: Explore Streamlit documentation for customization
- **Finance**: Understand market dynamics and trading psychology

---

**Developed by Vimal Dhama**

*Last Updated: October 2025*
