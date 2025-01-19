import pandas as pd
import os
import sys
from tickers_ciks import tickers_ciks  # Import the ticker and CIK mapping

def process_ticker(ticker):
    # Define the folder containing the CSVs for each ticker
    filings_folder = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'CSV', 'raw')

    # Create an empty DataFrame to combine all filings
    combined_df = pd.DataFrame()

    # Get the CIK for the given ticker
    cik = tickers_ciks.get(ticker.upper())
    if not cik:
        print(f"Ticker {ticker} not found in tickers_ciks.")
        return

    csv_file_path = os.path.join(filings_folder, f"{ticker}_form_4_filings.csv")

    # Check if the file exists before attempting to load it
    if os.path.exists(csv_file_path):
        # Load the CSV file
        filings_df = pd.read_csv(csv_file_path)

        # Add the ticker and CIK to the DataFrame for identification
        filings_df['Ticker'] = ticker
        filings_df['CIK'] = cik

        # Construct the URL for each filing
        filings_df['accessionNumber'] = filings_df['accessionNumber'].str.replace("-", "")
        filings_df['xml_url'] = filings_df.apply(
            lambda row: f"https://www.sec.gov/Archives/edgar/data/{row['CIK']}/{row['accessionNumber']}/{row['primaryDocument']}",
            axis=1
        )

        # Append to the combined DataFrame
        combined_df = pd.concat([combined_df, filings_df], ignore_index=True)
    else:
        print(f"CSV file for {ticker} not found at {csv_file_path}")

    # Define the output file path
    output_file_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'CSV', 'combined', 'filings.csv')

    # Save the combined DataFrame with URLs to a new CSV for further processing
    combined_df.to_csv(output_file_path, columns=['Ticker', 'CIK', 'accessionNumber', 'xml_url'], index=False)

    print(f"Combined CIK, filings data, and URLs saved to '{output_file_path}'.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python read_csv.py <ticker>")
        sys.exit(1)

    ticker = sys.argv[1]
    process_ticker(ticker)
