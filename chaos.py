import sys
import os
import subprocess
import pandas as pd

# Add the data_processing directory to the system path
data_processing_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'SEC', 'scripts', 'data_processing'))
sys.path.append(data_processing_path)

from tickers_ciks import tickers_ciks
from csv_extractor import fetch_edgar_data, save_filings_to_csv

def aggregate_csv_data(root_dir, output_file):
    # List to store each CSV file's data
    data_frames = []
    
    # Walk through all subdirectories in the root directory
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith(".csv"):
                file_path = os.path.join(dirpath, filename)
                
                # Read the CSV file
                try:
                    df = pd.read_csv(file_path)
                    data_frames.append(df)  # Append the DataFrame
                except Exception as e:
                    print(f"Could not read {file_path}: {e}")

    # Check if we have any data to aggregate
    if not data_frames:
        print("No CSV files found to aggregate.")
        return
    
    # Concatenate all DataFrames side by side
    try:
        aggregate_df = pd.concat(data_frames, axis=1)
    except Exception as e:
        print(f"Error during concatenation: {e}")
        return

    # Save the aggregated DataFrame to the output file
    try:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        aggregate_df.to_csv(output_file, index=False)
        print(f"Aggregated data saved to {output_file}")
    except Exception as e:
        print(f"Could not save aggregated data: {e}")

def main():
    # Get the stock symbol and query from the user
    stock_symbol = input("Enter the stock symbol: ")
    query = input("Enter the search query: ")

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

    # Additional functionality from input.py
    # Define paths to the YouTube script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    youtube_script = os.path.join(base_dir, "APIs", "youtube_api", "youtubeAPI.py")

    # Check if the YouTube script exists
    if not os.path.exists(youtube_script):
        print(f"Error: {youtube_script} not found.")
        return

    # Run the YouTube script
    youtube_process = subprocess.Popen(
        [python_interpreter, youtube_script, query],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Wait for the YouTube script to complete
    youtube_stdout, youtube_stderr = youtube_process.communicate()

    # Print the output from the YouTube script
    print("\n--- YouTube API Output ---")
    print(youtube_stdout.decode())
    if youtube_stderr:
        print("\nErrors:")
        print(youtube_stderr.decode())

    # Aggregate CSV files
    print("\nAggregating CSV files...")
    root_dir = os.path.join(base_dir, "data")  # Directory containing CSV files
    output_file = os.path.join(base_dir, "aggregated_data.csv")  # Output file path
    aggregate_csv_data(root_dir, output_file)

    # Call sentimentAnalysisV6.py to perform sentiment analysis
    sentiment_analysis_script = os.path.join(base_dir, "test", "sentimentAnalysisV6.py")
    subprocess.run([python_interpreter, sentiment_analysis_script])

if __name__ == "__main__":
    main()