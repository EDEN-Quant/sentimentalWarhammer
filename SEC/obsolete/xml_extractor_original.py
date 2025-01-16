import os
import requests
import pandas as pd

# Define the folder containing the combined CSV
filings_folder = os.path.join(os.path.dirname(__file__), 'edgar_filings')
combined_csv_path = os.path.join(filings_folder, 'combined_filings.csv')

# Load the combined CSV
combined_df = pd.read_csv(combined_csv_path)

# Create a base folder for storing the XMLs
base_folder = os.path.join(os.path.dirname(__file__), 'edgar_xmls')
os.makedirs(base_folder, exist_ok=True)

# Loop through each row, create subfolders for each company, and download the XMLs
for index, row in combined_df.iterrows():
    ticker = row['Ticker']
    cik = row['CIK']
    accession_number = str(row['accessionNumber'])
    primary_document = row['primaryDocument']  # Get the primary document from the row

    # Construct the XML URL using the CIK, accession number, and primary document
    xml_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_number}/{primary_document}"

    # Create a folder for each company
    company_folder = os.path.join(base_folder, ticker)
    os.makedirs(company_folder, exist_ok=True)

    # Define the filename for the XML
    filename = f"{accession_number}.xml"
    file_path = os.path.join(company_folder, filename)

    # Download the XML file
    response = requests.get(xml_url, headers={'User-Agent': 'Your-Name Your-Email'})
    if response.status_code == 200:
        with open(file_path, 'wb') as file:
            file.write(response.content)
        print(f"Saved XML for {ticker} to {file_path}")
    else:
        print(f"Failed to download XML for {ticker} from {xml_url}. Status code: {response.status_code}")
