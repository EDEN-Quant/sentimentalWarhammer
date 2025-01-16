import os
import csv
from bs4 import BeautifulSoup

# Define the relative paths
base_dir = os.path.dirname(__file__)
xml_dir = os.path.join(base_dir, 'edgar_filings', 'xml_files')
output_csv = os.path.join(base_dir, 'edgar_filings', 'form4_data.csv')

def extract_form4_data(html_file):
    """
    Extracts ALL Table I transactions from the given Form 4 HTML (XML) file.
    Returns a list of dictionaries, each dictionary representing one transaction row.
    """
    with open(html_file, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')
    
    # First, gather "shared" info that applies to the entire Form 4 (filer name, address, etc.)
    reporting_person_name = ''
    reporting_person_address = ''
    relationship_to_issuer = ''
    issuer_name = ''
    ticker_symbol = ''
    # Some forms put the actual transaction date inside Table I or in section "3. Date of Earliest Transaction."
    # We'll rely on the transaction row's date in Table I for that column, so let's collect the "earliest date" only if you need it.
    
    # --- Reporting Person Name & Address ---
    name_section = soup.find('span', class_='MedSmallFormText', text=lambda t: t and 'Name and Address of Reporting Person' in t)
    if name_section:
        parent_td = name_section.find_parent('td')
        if parent_td:
            # 1) Person's name in an <a> tag
            name_tag = parent_td.find('a', href=True)
            if name_tag:
                reporting_person_name = name_tag.get_text(strip=True)

            # 2) Address spans
            address_spans = parent_td.find_all('span', class_='FormData')
            address_parts = [span.get_text(strip=True) for span in address_spans if span.get_text(strip=True)]
            reporting_person_address = ', '.join(address_parts)  # e.g. "ONE APPLE PARK WAY, CUPERTINO, CA, 95014"

    # --- Relationship to Issuer ---
    relationship_section = soup.find('span', class_='MedSmallFormText', text=lambda t: t and 'Relationship of Reporting Person(s)' in t)
    if relationship_section:
        parent_td = relationship_section.find_parent('td')
        # Look for the officer title <td> with style="color: blue"
        officer_title_td = parent_td.find('td', width='35%', style=lambda s: s and 'color: blue' in s)
        if officer_title_td:
            relationship_to_issuer = officer_title_td.get_text(strip=True)

    # --- Issuer Name & Ticker Symbol ---
    issuer_section = soup.find('span', class_='MedSmallFormText', text=lambda t: t and 'Issuer Name' in t)
    if issuer_section:
        parent_td = issuer_section.find_parent('td')
        if parent_td:
            # Issuer name is typically in an <a> tag
            issuer_a = parent_td.find('a', href=True)
            if issuer_a:
                issuer_name = issuer_a.get_text(strip=True)
            # Ticker symbol is in a <span class="FormData">
            ticker_span = parent_td.find('span', class_='FormData')
            if ticker_span:
                ticker_symbol = ticker_span.get_text(strip=True)

    # ----------------------------------------------------------------------
    # Collect ALL Table I Transactions
    # ----------------------------------------------------------------------
    transactions = []
    
    # Locate "Table I - Non-Derivative Securities" by finding its header
    table1_header = soup.find('th', class_='FormTextC', text=lambda t: t and 'Table I' in t)
    if table1_header:
        table1 = table1_header.find_parent('table')
        if table1:
            # The <tbody> has the actual transaction rows
            tbody = table1.find('tbody')
            if tbody:
                # Each <tr> is one transaction row
                rows = tbody.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    # We expect ~11 columns in Table I
                    # They may vary, but usually:
                    #   0) Title of Security
                    #   1) Transaction Date
                    #   2) Deemed Execution Date (sometimes empty)
                    #   3) Transaction Code
                    #   4) Transaction Code "V" (voluntary?)
                    #   5) Amount
                    #   6) (A) or (D)
                    #   7) Price
                    #   8) Amount of Securities Owned After
                    #   9) Ownership Form (D or I)
                    #   10) Nature of Indirect Ownership
                    if len(cells) >= 8:
                        title_of_security = cells[0].get_text(strip=True)
                        transaction_date = cells[1].get_text(strip=True)
                        transaction_code = cells[3].get_text(strip=True)

                        # Amount of securities
                        amount_of_securities = cells[5].get_text(strip=True)

                        # Price (strip out "$" or footnote references)
                        raw_price = cells[7].get_text(strip=True)
                        # e.g. "$207.05(2)" => "207.05"
                        if raw_price:
                            raw_price = raw_price.replace('$', '')
                            # remove any "(...)" footnotes
                            if '(' in raw_price:
                                raw_price = raw_price.split('(')[0].strip()

                        # Build the transaction dict
                        transaction_data = {
                            'reporting_person_name': reporting_person_name,
                            'reporting_person_address': reporting_person_address,
                            'relationship_to_issuer': relationship_to_issuer,
                            'issuer_name': issuer_name,
                            'ticker_symbol': ticker_symbol,
                            'transaction_date': transaction_date,
                            'transaction_code': transaction_code,
                            'title_of_security': title_of_security,
                            'amount_of_securities': amount_of_securities,
                            'price': raw_price or ''
                        }
                        transactions.append(transaction_data)

    return transactions

def save_form4_data_to_csv(xml_dir, output_csv):
    """
    Loops over each .xml file in `xml_dir`, extracts *all* Table I transactions,
    and writes them as rows in `form4_data.csv`.
    """
    fieldnames = [
        'reporting_person_name',
        'reporting_person_address',
        'relationship_to_issuer',
        'issuer_name',
        'ticker_symbol',
        'transaction_date',
        'transaction_code',
        'title_of_security',
        'amount_of_securities',
        'price'
    ]
    
    with open(output_csv, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for xml_file in os.listdir(xml_dir):
            if xml_file.endswith('.xml'):
                xml_path = os.path.join(xml_dir, xml_file)
                # Extract a *list* of transactions
                all_transactions = extract_form4_data(xml_path)
                if not all_transactions:
                    continue
                # Write each transaction as a separate row
                for tx in all_transactions:
                    writer.writerow(tx)
                print(f"Processed {len(all_transactions)} transaction(s) from: {xml_file}")

# Run the function
save_form4_data_to_csv(xml_dir, output_csv)
