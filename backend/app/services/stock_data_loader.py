from app.services.neo4j_setup import neo4j_conn
from typing import Dict
import requests
import pandas as pd
import numpy as np

def create_stock_node(ticker: str, name: str, sector: str, metrics: Dict[str, float]):
    sector_query = """
    MERGE (s:Sector {name: $sector})
    RETURN s
    """
    neo4j_conn.execute_query(sector_query, {"sector": sector})

    stock_query = """
    MERGE (c:Company {ticker: $ticker, name: $name})
    MERGE (c)-[:BELONGS_TO]->(:Sector {name: $sector})
    """
    neo4j_conn.execute_query(stock_query, {"ticker": ticker, "name": name, "sector": sector})

    for metric, value in metrics.items():
        metric_query = """
        MERGE (m:Metric {type: $metric, value: $value})
        MERGE (c:Company {ticker: $ticker})-[:HAS_METRIC]->(m)
        """
        neo4j_conn.execute_query(metric_query, {"ticker": ticker, "metric": metric, "value": value})

def fetch_stock_data(ticker: str) -> Dict:
    api_key = 'YOUR_ALPHA_VANTAGE_API_KEY'
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={ticker}&apikey="MZM0C6YX1861U15C'
    response = requests.get(url).json()
    

    metrics = {
        "volatility": 0.1, 
        "earnings_growth": 0.2,
    }
    return {
        "name": "Apple Inc.",
        "ticker": ticker,
        "sector": "Technology",
        "metrics": metrics
    }

def load_stock_to_db(ticker: str):
    stock_data = fetch_stock_data(ticker)
    create_stock_node(
        ticker=stock_data["ticker"],
        name=stock_data["name"],
        sector=stock_data["sector"],
        metrics=stock_data["metrics"]
    )

def fetch_daily_data(ticker: str, api_key: str) -> pd.DataFrame:
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={ticker}&apikey={api_key}'
    response = requests.get(url).json()
    
    daily_data = response.get("Time Series (Daily)", {})
    prices = {date: float(values["5. adjusted close"]) for date, values in daily_data.items()}
    
    df = pd.DataFrame.from_dict(prices, orient='index', columns=['adjusted_close'])
    df.index = pd.to_datetime(df.index)
    df.sort_index(inplace=True)
    return df

def calculate_volatility(df: pd.DataFrame, period: int = 30) -> float:
    df['returns'] = df['adjusted_close'].pct_change()
    rolling_volatility = df['returns'].rolling(window=period).std()
    annualized_volatility = rolling_volatility.iloc[-1] * np.sqrt(252)
    return annualized_volatility

def calculate_moving_averages(df: pd.DataFrame, short_period: int = 50, long_period: int = 200):
    df[f'SMA_{short_period}'] = df['adjusted_close'].rolling(window=short_period).mean()
    df[f'SMA_{long_period}'] = df['adjusted_close'].rolling(window=long_period).mean()
    return df

def fetch_earnings_data(ticker: str, api_key: str) -> dict:
    url = f'https://www.alphavantage.co/query?function=EARNINGS&symbol={ticker}&apikey={api_key}'
    response = requests.get(url).json()
    
    earnings_data = response.get("annualEarnings", [])
    if len(earnings_data) >= 2:
        current_eps = float(earnings_data[0]["reportedEPS"])
        previous_eps = float(earnings_data[1]["reportedEPS"])
        eps_growth = (current_eps - previous_eps) / previous_eps if previous_eps != 0 else None
    else:
        eps_growth = None

    return {"eps_growth": eps_growth}

def fetch_fundamental_data(ticker: str, api_key: str) -> dict:
    url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={api_key}'
    response = requests.get(url).json()
    
    pe_ratio = float(response.get("PERatio", 0))
    beta = float(response.get("Beta", 0))
    dividend_yield = float(response.get("DividendYield", 0))
    peg_ratio = float(response.get("PEGRatio", 0))
    market_cap = float(response.get("MarketCapitalization", 0))

    return {
        "pe_ratio": pe_ratio,
        "beta": beta,
        "dividend_yield": dividend_yield,
        "peg_ratio": peg_ratio,
        "market_cap": market_cap
    }

def fetch_sector_performance(api_key: str) -> dict:
    url = f'https://www.alphavantage.co/query?function=SECTOR&apikey={api_key}'
    response = requests.get(url).json()

    # Extract performance metrics over different periods
    sector_performance = {
        "1_day": response.get("Rank A: Real-Time Performance"),
        "5_day": response.get("Rank B: 1 Day Performance"),
        "1_month": response.get("Rank C: 5 Day Performance"),
        "3_month": response.get("Rank D: 1 Month Performance")
    }
    return sector_performance

def fetch_all_metrics(ticker: str, api_key: str) -> dict:
    daily_data = fetch_daily_data(ticker, api_key)
    volatility = calculate_volatility(daily_data)
    moving_averages = calculate_moving_averages(daily_data)

    earnings_data = fetch_earnings_data(ticker, api_key)
    fundamental_data = fetch_fundamental_data(ticker, api_key)
    sector_performance = fetch_sector_performance(api_key)

    return {
        "ticker": ticker,
        "volatility": volatility,
        "moving_averages": moving_averages[['SMA_50', 'SMA_200']].iloc[-1].to_dict(),
        "eps_growth": earnings_data["eps_growth"],
        **fundamental_data,
        "sector_performance": sector_performance
    }