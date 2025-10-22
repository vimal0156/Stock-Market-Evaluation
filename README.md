# 📈 Stock Market Technical Analysis Platform

A professional, production-ready **Streamlit web application** for advanced technical analysis of financial markets. This platform automatically detects trend lines, support/resistance levels, and psychological price zones using sophisticated algorithms and real-time market data.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.31.0-FF4B4B.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🌟 Features

### Real-Time Data Integration
- **Dual Data Providers**: Alpha Vantage (API key required) or Yahoo Finance
- **Yahoo Finance API Integration**: Fetch live market data for any supported asset
- **Multi-Asset Support**: Cryptocurrencies, stocks, forex, indices, and commodities
- **Flexible Time Frames**: 1-hour to monthly intervals with customizable periods
- **CSV Upload Fallback**: Import your own OHLC datasets when APIs are unavailable

### Advanced Technical Analysis
- **Local Trend Detection**: Identifies short-term support and resistance based on moving averages and peak detection
- **Global Trend Analysis**: Detects major trend lines across the entire dataset using advanced scoring algorithms
- **Psychological Level Detection**: Finds key price levels with high touch frequency using variance-based algorithms
- **Peak Detection**: Automated identification of significant price peaks and troughs

### Professional Visualization
- **Interactive Candlestick Charts**: Built with Plotly for smooth, responsive interactions
- **Multi-Layer Analysis**: Overlay local trends, global trends, and psychological levels
- **Dark Theme UI**: Modern, professional interface optimized for extended use
- **Real-Time Metrics**: Live price updates, 24h changes, and key statistics

### User Experience
- **Intuitive Sidebar Controls**: Easy configuration of all analysis parameters
- **Responsive Design**: Optimized for desktop and tablet viewing
- **Data Export**: Download analysis results as CSV files
- **Error Handling**: Graceful handling of API failures and edge cases

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- pip package manager

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd "Stock market evaluation"
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the Streamlit application**
```bash
streamlit run app.py
```

4. **Access the application**
Open your browser and navigate to `http://localhost:8501`

5. **(Optional) Set Alpha Vantage API Key**
   - Create a free account at [Alpha Vantage](https://www.alphavantage.co/)
   - Copy your API key
   - Paste it into the **API Configuration** section in the Streamlit sidebar when running the app

6. **(Optional) Prepare CSV Data**
   - Save OHLC data as a CSV with columns for time, open, high, low, close (volume optional)
   - Use the **Upload CSV** option in the sidebar when running the app

---

## 📂 Project Structure

```
Stock market evaluation/
│
├── app.py                              # Main Streamlit application
├── utils.py                            # Core analysis algorithms and helper functions
├── requirements.txt                    # Python dependencies
├── README.md                           # Project documentation
│
├── Project_Trend_lines.ipynb          # Original Jupyter notebook with detailed analysis
├── BNBUSDT_1h_20171106_20250328.csv   # Sample dataset (BNB/USDT historical data)
│
└── .gitignore                         # Git ignore configuration
```

---

## 🎯 How to Use

### 1. Configure Analysis Parameters

**Stock Selection**
- Enter any valid Yahoo Finance ticker symbol (e.g., `BNB-USD`, `BTC-USD`, `AAPL`, `TSLA`)

**Time Period**
- Choose from 1 month to maximum available history

**Time Interval**
- Select from 1-hour to 1-month intervals

**Analysis Parameters**
- **Moving Average Period**: Controls the trend detection window (50-500 hours)
- **Peak Detection Sensitivity**: Adjusts how many peaks are detected (0.05-0.50)
- **Psychological Levels**: Number of key price levels to identify (3-15)

### 2. Display Options

Toggle visualization layers:
- ✅ Show Local Trend
- ✅ Show Global Trend
- ✅ Show Psychological Levels

### 3. Fetch & Analyze

Click the **"🔄 Fetch & Analyze"** button to:
1. Fetch real-time data from Yahoo Finance
2. Perform comprehensive technical analysis
3. Generate interactive visualizations
4. Display key metrics and insights

### 4. Interpret Results

**Resistance Levels** (Red lines)
- Price levels where upward movement may face selling pressure
- Local resistance: Short-term barriers
- Global resistance: Major long-term barriers

**Support Levels** (Blue/Cyan lines)
- Price levels where downward movement may face buying pressure
- Local support: Short-term floors
- Global support: Major long-term floors

**Psychological Levels** (Dashed cyan lines)
- Price points with historically high touch frequency
- Often represent round numbers or significant price zones

---

## 🔬 Technical Methodology

### Trend Detection Algorithm

1. **Moving Average Calculation**: Compute moving averages over configurable periods
2. **Trend Reversal Detection**: Identify the last reversal in moving average direction
3. **Working Area Delimitation**: Define the analysis window for trend extraction
4. **Support/Resistance Fitting**: Use robust line fitting with tolerance for minor deviations
5. **Scoring System**: Evaluate trend line quality based on touch count and proximity

### Psychological Level Detection

1. **Variance Analysis**: Calculate price variance to determine adaptive thresholds
2. **Touch Frequency**: Count how many candles interact with each price level
3. **Interval Segmentation**: Divide price range into variance-based intervals
4. **Best Candidate Selection**: Choose the most significant level in each interval
5. **Ranking**: Sort and return top N psychological levels

### Global Trend Analysis

1. **Peak Detection**: Use scipy's `find_peaks` with prominence-based filtering
2. **Pairwise Evaluation**: Test all combinations of peaks for potential trend lines
3. **Quality Scoring**: Evaluate each line based on:
   - Number of touches
   - Maximum deviation
   - Trend length
4. **Optimal Selection**: Choose the highest-scoring resistance and support lines

---

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Frontend** | Streamlit | Interactive web interface |
| **Data Source** | yfinance | Real-time market data API |
| **Data Processing** | Pandas, NumPy | Data manipulation and analysis |
| **Visualization** | Plotly | Interactive candlestick charts |
| **Analysis** | SciPy | Peak detection and signal processing |
| **Machine Learning** | scikit-learn | Robust regression (Theil-Sen) |

---

## 📊 Supported Assets

### Cryptocurrencies
- Bitcoin (BTC-USD), Ethereum (ETH-USD), Binance Coin (BNB-USD)
- And 100+ other cryptocurrencies

### Stocks
- Apple (AAPL), Tesla (TSLA), Google (GOOGL), Microsoft (MSFT)
- All major US and international stocks

### Forex Pairs
- EUR/USD (EURUSD=X), GBP/USD (GBPUSD=X), USD/JPY (JPY=X)

### Indices
- S&P 500 (^GSPC), Dow Jones (^DJI), NASDAQ (^IXIC)

### Commodities
- Gold (GC=F), Crude Oil (CL=F), Silver (SI=F)

---

## 🎓 Educational Use

This project is ideal for:
- **Students** learning quantitative finance and technical analysis
- **Traders** seeking automated trend detection tools
- **Developers** building financial analysis applications
- **Researchers** studying market behavior and price patterns

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📸 Screenshots

### Full Dashboard Overview

![Dashboard Overview](Results/API-IMG-1.png)

Showcases the main Streamlit interface with live price metrics, configurable sidebar controls, and the primary candlestick chart displaying market action.

### Technical Analysis Layers

![Technical Analysis Layers](Results/API-IMG-2.png)

Highlights overlaid local and global trend lines, including resistance and support zones detected automatically from the fetched market data.

### Psychological Levels & Insights

![Psychological Levels](Results/API-IMG-3.png)

Demonstrates the psychological level markers with accompanying summary metrics, emphasizing key price zones traders should monitor.

### CSV Upload Configuration

![CSV Upload Configuration](Results/CSV-IMG-1.png)

Displays the fallback input mode where users upload custom OHLC datasets, informing them of required columns before analysis begins.

### CSV Data Parsing Preview

![CSV Data Preview](Results/CSV-IMG-2.png)

Shows the parsed CSV data flowing through the same analytical pipeline, confirming successful ingestion and validation of offline datasets.

### CSV-Based Technical Analysis

![CSV Technical Analysis](Results/CSV-IMG-3.png)

Illustrates technical analysis outputs derived from uploaded data, validating that trend detection and psychological levels work identically in offline scenarios.

> 📌 **Tip:** Screenshots were captured in dark theme for consistency; the UI adapts to your system theme automatically.

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👨‍💻 Author

**Vimal Dhama**

- Technical Analysis Specialist
- Quantitative Finance Enthusiast
- Full-Stack Developer

---

## 🙏 Acknowledgments

- Yahoo Finance for providing free market data API
- Streamlit team for the excellent web framework
- The open-source community for the amazing Python libraries

---

## 📧 Contact & Support

For questions, suggestions, or support:
- Open an issue on GitHub
- Contact: [Your Email]

---

## 🔮 Future Enhancements

- [ ] Machine learning-based trend prediction
- [ ] Multi-timeframe analysis
- [ ] Automated trading signals
- [ ] Portfolio backtesting
- [ ] Custom indicator builder
- [ ] Real-time alerts and notifications
- [ ] Mobile-responsive design
- [ ] Multi-language support

---

**⭐ If you find this project useful, please consider giving it a star!**

---

*Last Updated: October 2025*
