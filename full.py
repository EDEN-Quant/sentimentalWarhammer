import sys
import os
import subprocess

# Add the data_processing directory to the system path
data_processing_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'SEC', 'scripts', 'data_processing'))
sys.path.append(data_processing_path)

from tickers_ciks import tickers_ciks
from csv_extractor import fetch_edgar_data, save_filings_to_csv

def main(stock_symbol):
    # Get the CIK for the given stock symbol
    cik = tickers_ciks.get(stock_symbol.upper())
    if not cik:
        print(f"Stock symbol {stock_symbol} not found in tickers_ciks.")
        return

    # Fetch the EDGAR data for the given CIK
    form_4_df = fetch_edgar_data(cik)

    if not form_4_df.empty:
        # Save the DataFrame to a CSV file named after the stock symbol
        save_filings_to_csv(stock_symbol, form_4_df)
    else:
        print(f"No filings found for {stock_symbol}")

    # Call read_csv.py to process the saved CSV files
    read_csv_script = os.path.join(data_processing_path, 'read_csv.py')
    python_interpreter = sys.executable  # Get the path to the current Python interpreter
    subprocess.run([python_interpreter, read_csv_script, stock_symbol])

    # Call xml_extractor.py to download and save XML files
    xml_extractor_script = os.path.join(data_processing_path, 'xml_extractor.py')
    subprocess.run([python_interpreter, xml_extractor_script])

    # Call read_xml.py to process the downloaded XML files
    read_xml_script = os.path.join(data_processing_path, 'read_xml.py')
    subprocess.run([python_interpreter, read_xml_script, stock_symbol])

    # Call Summarize.py to generate the summary CSV
    summarize_script = os.path.join(data_processing_path, 'Summarize.py')
    subprocess.run([python_interpreter, summarize_script, stock_symbol])

if __name__ == "__main__":
    # Hardcode the stock symbol for testing
    stock_symbol = "BBW"
    main(stock_symbol)