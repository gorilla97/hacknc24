import pandas as pd
from app.services.stock_data_loader import load_stock_to_db

def load_tickers_from_csv(file_path: str):
    return pd.read_csv(file_path)

def main():
    ticker_data = load_tickers_from_csv("tickers.csv")

    for _, row in ticker_data.iterrows():
        ticker = row['ticker']
        print(f"Loading data for ticker: {ticker}")
        load_stock_to_db(ticker)

if __name__ == "__main__":
    main()