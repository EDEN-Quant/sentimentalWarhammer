import os
import csv
from bs4 import BeautifulSoup
from tickers_ciks import tickers_ciks  # Import tickers_ciks

# Define paths
base_dir = os.path.dirname(__file__)
xml_dir = os.path.join(base_dir, '..', '..', 'data', 'XML', 'raw')
output_csv = os.path.join(base_dir, '..', '..', 'data', 'form4transactions', 'form4_data.csv')

def extract_form4_data(html_file):
    """
    Extracts Table I transactions from the given Form 4 (HTML/XML).
    Returns a list of dictionaries, each dict representing one transaction row.
    """
    # Derive company_name from filename (e.g. "apple_123.xml" => "apple")
    base_name = os.path.splitext(os.path.basename(html_file))[0]
    company_name = base_name.split('_')[0]  # Split at underscore and take the first part

    with open(html_file, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')
    
    # Relationship to issuer (sometimes 'CEO', 'CFO', etc.)
    relationship_to_issuer = ''
    # Search with a partial text approach
    relationship_section = soup.find('span', class_='MedSmallFormText',
                                     text=lambda t: t and 'relationship of reporting person' in t.lower())
    if relationship_section:
        parent_td = relationship_section.find_parent('td')
        # Often the job title is in a <td style="color: blue"> or near "Officer (give title below)"
        officer_title_td = parent_td.find('td', style=lambda s: s and 'color: blue' in s)
        if officer_title_td:
            relationship_to_issuer = officer_title_td.get_text(strip=True)
        else:
            # fallback: you might look for the <tr> containing "Officer (give title below)"
            # and read the next cell.  This is just a fallback approach:
            officer_tr = parent_td.find(lambda tag: tag.name == 'tr' and 'Officer (give title below)' in tag.get_text())
            if officer_tr:
                next_td = officer_tr.find_next_sibling('tr')
                if next_td:
                    relationship_to_issuer = next_td.get_text(strip=True)

    # Now parse Table I
    transactions = []
    table1_header = soup.find('th', class_='FormTextC',
                              text=lambda t: t and 'Table I' in t)
    if table1_header:
        table1 = table1_header.find_parent('table')
        if table1:
            tbody = table1.find('tbody')
            if tbody:
                rows = tbody.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    # Typically we expect ~11 columns. We need at least 9 for our fields:
                    if len(cells) >= 9:
                        # columns:
                        #   0 - Title of Security
                        #   1 - Transaction Date
                        #   2 - Deemed Execution Date
                        #   3 - Transaction Code
                        #   4 - V? (sometimes blank)
                        #   5 - Amount Transacted
                        #   6 - A or D
                        #   7 - Price
                        #   8 - Shares Owned After
                        title_of_security = cells[0].get_text(strip=True)
                        transaction_date = cells[1].get_text(strip=True)
                        transaction_code = cells[3].get_text(strip=True)
                        transaction_shares = cells[5].get_text(strip=True)
                        acquired_or_disposed = cells[6].get_text(strip=True)
                        raw_price = cells[7].get_text(strip=True)
                        # Clean price: remove $ and footnotes
                        if raw_price:
                            raw_price = raw_price.replace('$', '')
                            if '(' in raw_price:
                                raw_price = raw_price.split('(')[0].strip()
                        shares_owned_after = cells[8].get_text(strip=True)

                        row_data = {
                            'company_name': company_name,
                            'relationship_to_issuer': relationship_to_issuer,
                            'title_of_security': title_of_security,
                            'transaction_date': transaction_date,
                            'transaction_code': transaction_code,
                            'acquired_or_disposed': acquired_or_disposed,
                            'transaction_shares': transaction_shares,
                            'transaction_price': raw_price,
                            'shares_owned_after': shares_owned_after,
                        }
                        # Optionally skip if row is blank or footnotes
                        # e.g., if transaction_date == '' and transaction_code == '', skip
                        # But for now, let's just append
                        transactions.append(row_data)
    return transactions

def save_form4_data_to_csv(xml_dir, output_csv):
    """
    Reads all .xml from xml_dir, extracts the relevant columns, and writes them to CSV.
    """
    fieldnames = [
        'company_name',
        'relationship_to_issuer',
        'title_of_security',
        'transaction_date',
        'transaction_code',
        'acquired_or_disposed',
        'transaction_shares',
        'transaction_price',
        'shares_owned_after',
    ]

    with open(output_csv, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for xml_file in os.listdir(xml_dir):
            if xml_file.endswith('.xml'):
                # Check if the file starts with any of the symbols in tickers_ciks
                if any(xml_file.startswith(symbol) for symbol in tickers_ciks.keys()):
                    xml_path = os.path.join(xml_dir, xml_file)
                    all_transactions = extract_form4_data(xml_path)
                    if all_transactions:
                        for tx in all_transactions:
                            writer.writerow(tx)
                    print(f"Processed {xml_file} with {len(all_transactions)} transaction(s).")

# Finally, run the extraction
if __name__ == '__main__':
    save_form4_data_to_csv(xml_dir, output_csv)