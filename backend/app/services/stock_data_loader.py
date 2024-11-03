import yfinance as yf
import numpy as np
import pandas as pd
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
FMP_API_KEY = os.environ.get("FMP_API_KEY")

def fetch_yahoo_data(ticker: str) -> dict:
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1y")
    info = stock.info
    
    # Basic stock information
    name = info.get("longName", ticker)
    sector = info.get("sector", "Unknown")
    
    return {
        "name": name,
        "sector": sector,
        "historical_data": hist
    }

def calculate_volatility(hist_data: pd.DataFrame, period: int = 30, fallback_period: int = 10) -> dict:
    # Calculate daily returns
    hist_data['returns'] = hist_data['Close'].pct_change()
    
    # Calculate volatility based on available data
    if len(hist_data['returns'].dropna()) >= period:
        rolling_volatility = hist_data['returns'].rolling(window=period).std()
        annualized_volatility = rolling_volatility.iloc[-1] * np.sqrt(252)
        return {"volatility": annualized_volatility, "is_estimated": False}
    
    # Fallback if insufficient data for primary period
    if len(hist_data['returns'].dropna()) >= fallback_period:
        rolling_volatility = hist_data['returns'].rolling(window=fallback_period).std()
        annualized_volatility = rolling_volatility.iloc[-1] * np.sqrt(252)
        return {"volatility": annualized_volatility, "is_estimated": True}
    
    # Return zero volatility if no data is available
    return {"volatility": 0.0, "is_estimated": True}

def fetch_fmp_data(ticker: str) -> dict:
    url = f'https://financialmodelingprep.com/api/v3/profile/{ticker}?apikey={FMP_API_KEY}'
    response = requests.get(url)
    data = response.json()
    
    if data and isinstance(data, list):
        profile = data[0]
        pe_ratio = profile.get("pe")
        market_cap = profile.get("mktCap")
        beta = profile.get("beta")
        
        return {
            "pe_ratio": pe_ratio,
            "market_cap": market_cap,
            "beta": beta
        }
    return {
        "pe_ratio": None,
        "market_cap": None,
        "beta": None
    }

def fetch_combined_data(ticker: str) -> dict:
    # Fetch Yahoo Finance data (price and sector info)
    yahoo_data = fetch_yahoo_data(ticker)
    hist_data = yahoo_data["historical_data"]
    
    # Calculate volatility based on Yahoo Finance historical data
    volatility_data = calculate_volatility(hist_data)
    
    # Fetch FMP data (financial metrics)
    fmp_data = fetch_fmp_data(ticker)
    
    # Combine all data
    combined_data = {
        "name": yahoo_data["name"],
        "ticker": ticker,
        "sector": yahoo_data["sector"],
        "volatility": volatility_data["volatility"],
        "is_estimated_volatility": volatility_data["is_estimated"],
        "pe_ratio": fmp_data["pe_ratio"],
        "market_cap": fmp_data["market_cap"],
        "beta": fmp_data["beta"]
    }
    
    return combined_data