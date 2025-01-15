import csv
import os
import requests

# Define the relative path to the CSV file and the directory to save the XML files
csv_file_path = 'edgar_filings/combined_filings.csv'
output_dir = 'edgar_filings/xml_files'

# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Function to download and save XML files
def download_xml_files(csv_file_path, output_dir):
    headers = {'User-Agent': 'Alexander Kokiauri akokiauri.ieu2022@student.ie.edu'}
    
    with open(csv_file_path, mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            xml_url = row['xml_url']
            ticker = row['Ticker']
            accession_number = row['accessionNumber']
            
            # Define the filename and path to save the XML file
            filename = f"{ticker}_{accession_number}.xml"
            file_path = os.path.join(output_dir, filename)
            
            # Download the XML file
            response = requests.get(xml_url, headers=headers)
            if response.status_code == 200:
                with open(file_path, 'wb') as file:
                    file.write(response.content)
                print(f"Downloaded and saved: {filename}")
            else:
                print(f"Failed to download: {xml_url}")

# Run the function to download and save XML files
download_xml_files(csv_file_path, output_dir)