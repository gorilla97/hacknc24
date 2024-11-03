import pandas as pd
from app.services.stock_data_loader import fetch_combined_data
from app.services.neo4j_setup import Neo4jConnection
from app.core.config import settings

# Initialize Neo4j connection
neo4j_conn = Neo4jConnection()

def load_tickers_from_csv(file_path: str):
    df = pd.read_csv(file_path)
    return df["ticker"].tolist()

def create_stock_node(ticker: str, data: dict):
    # Create the Sector node if it doesn't exist
    sector_query = """
    MERGE (s:Sector {name: $sector})
    RETURN s
    """
    neo4j_conn.execute_query(sector_query, {"sector": data["sector"]})

    # Create the Company node and relate it to the Sector
    company_query = """
    MERGE (c:Company {ticker: $ticker, name: $name})
    MERGE (c)-[:BELONGS_TO]->(s:Sector {name: $sector})
    SET c.volatility = $volatility,
        c.is_estimated_volatility = $is_estimated_volatility,
        c.pe_ratio = $pe_ratio,
        c.market_cap = $market_cap,
        c.beta = $beta
    """
    neo4j_conn.execute_query(company_query, {
        "ticker": ticker,
        "name": data["name"],
        "sector": data["sector"],
        "volatility": data["volatility"],
        "is_estimated_volatility": data["is_estimated_volatility"],
        "pe_ratio": data["pe_ratio"],
        "market_cap": data["market_cap"],
        "beta": data["beta"]
    })

def main():
    tickers = load_tickers_from_csv("tickers.csv")
    
    for ticker in tickers:
        try:
            print(f"Fetching data for {ticker}...")
            data = fetch_combined_data(ticker)
            print(f"Inserting data for {ticker} into Neo4j...")
            create_stock_node(ticker, data)
            print(f"Successfully inserted data for {ticker}.")
        except Exception as e:
            print(f"Failed to fetch or insert data for {ticker}: {e}")

if __name__ == "__main__":
    main()