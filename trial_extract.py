# This is a trial that aims to test if the extract_data_script works properly for only 1 bond.
import requests
from bs4 import BeautifulSoup
import csv


# Scraper function
def scraper(bond_data_dict, target_dates, output_file):
    # Open CSV file for writing
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write headers
        writer.writerow(
            ["Name", "ISIN", "Coupon Rate", "Issue Date", "Maturity Date", "Date", "Close"])

        # Loop through the bond data dictionary
        for bond_url, url_data in bond_data_dict.items():
            print(f"Processing bond: {bond_url}")

            # Fetch bond details
            response = requests.get(bond_url)
            soup = BeautifulSoup(response.content, "html.parser")

            # Extract Coupon Name
            name_row = soup.find("td", text=lambda t: t and "name" in t.lower())
            name_value = name_row.find_next_sibling("td").text.strip() if name_row else "N/A"

            # Extract ISIN
            isin_row = soup.find("td", text=lambda t: t and "isin" in t.lower())
            isin_value = isin_row.find_next_sibling("td").text.strip() if isin_row else "N/A"

            # Extract Coupon Rate
            coupon_rows = soup.find_all("td", text=lambda t: t and "coupon" in t.lower())
            coupon_value = "N/A"
            if len(coupon_rows) > 1:
                coupon_value_cell = coupon_rows[1].find_next_sibling("td").text.strip()
                coupon_value = float(
                    coupon_value_cell.replace('%', '')) / 100 if coupon_value_cell else "N/A"

            # Extract Issue Date
            issue_row = soup.find("td", text=lambda t: t and "issue date" in t.lower())
            issue_value = issue_row.find_next_sibling("td").text.strip() if issue_row else "N/A"

            # Extract Maturity Date
            maturity_row = soup.find("td", text=lambda t: t and "maturity date" in t.lower())
            maturity_value = maturity_row.find_next_sibling(
                "td").text.strip() if maturity_row else "N/A"

            # Print bond details
            print(
                f"Name: {name_value}, ISIN: {isin_value}, Coupon Rate: {coupon_value}, Issue Date: {issue_value}, Maturity Date: {maturity_value}")

            # Fetch historical prices
            print("\nFetching historical prices...")
            historical_prices = []
            try:
                response = requests.get(url_data)
                data = response.json()
                for entry in data:
                    if entry["Date"] in target_dates:
                        historical_prices.append({"Date": entry["Date"], "Close": entry["Close"]})
                        print(f"Date: {entry['Date']}, Close Price: {entry['Close']}")
            except Exception as e:
                print(f"Error fetching historical prices: {e}")

            # Write bond details and historical prices to CSV
            for price in historical_prices:
                writer.writerow([name_value, isin_value, coupon_value, issue_value, maturity_value,
                                 price["Date"], price["Close"]])

    print(f"Data saved to {output_file}")

# Define Target Dates
target_dates = [
    "2025-01-06 00:00", "2025-01-07 00:00", "2025-01-08 00:00",
    "2025-01-09 00:00", "2025-01-10 00:00", "2025-01-13 00:00",
    "2025-01-14 00:00", "2025-01-15 00:00", "2025-01-16 00:00",
    "2025-01-17 00:00", "2025-01-20 00:00"
]

# Example Dictionary of Bond URLs and Historical Price URLs
bond_data_dict = {
    # These are the bonds maturing within 3 years. There are 24 bonds in total.
    "https://markets.businessinsider.com/bonds/canadacd-bonds_202225-bond-2025-ca135087p246?miRedirects=1":
        "https://markets.businessinsider.com/Ajax/Chart_GetChartData?instrumentType=Bond&tkData=1,120634330,1330,184&from=20241125&to=20250125",
}

# Output CSV file
output_file = "bond_data_trial.csv"

# Run the scraper
scraper(bond_data_dict, target_dates, output_file)
