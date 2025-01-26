import re
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
            name_row = soup.find("td", string=lambda t: t and "name" in t.lower())
            name_value = name_row.find_next_sibling("td").text.strip() if name_row else "N/A"
            name_value = re.sub(r'\s+', ' ', name_value)

            # Extract ISIN
            isin_row = soup.find("td", string=lambda t: t and "isin" in t.lower())
            isin_value = isin_row.find_next_sibling("td").text.strip() if isin_row else "N/A"

            # Extract Coupon Rate
            coupon_rows = soup.find_all("td", string=lambda t: t and "coupon" in t.lower())
            coupon_value = "N/A"
            if len(coupon_rows) > 1:
                coupon_value_cell = coupon_rows[1].find_next_sibling("td").text.strip()
                coupon_value = float(
                    coupon_value_cell.replace('%', '')) / 100 if coupon_value_cell else "N/A"

            # Extract Issue Date
            issue_row = soup.find("td", string=lambda t: t and "issue date" in t.lower())
            issue_value = issue_row.find_next_sibling("td").text.strip() if issue_row else "N/A"

            # Extract Maturity Date
            maturity_row = soup.find("td", string=lambda t: t and "maturity date" in t.lower())
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
    "2025-01-17 00:00"
]

# Example Dictionary of Bond URLs and Historical Price URLs
bond_data_dict = {
    # These are the bonds maturing within 3 years. There are 24 bonds in total.
    "https://markets.businessinsider.com/bonds/canadacd-bonds_202225-bond-2025-ca135087p246?miRedirects=1":
        "https://markets.businessinsider.com/Ajax/Chart_GetChartData?instrumentType=Bond&tkData=1,120634330,1330,184&from=20241125&to=20250125",

    "https://markets.businessinsider.com/bonds/canadacd-bonds_201526-bond-2026-ca135087e679?miRedirects=1":
        "https://markets.businessinsider.com/Ajax/Chart_GetChartData?instrumentType=Bond&tkData=1,28975906,1330,184&from=20241125&to=20250125",

    "https://markets.businessinsider.com/bonds/canadacd-bonds_202225-bond-2025-ca135087n340?miRedirects=1":
        "https://markets.businessinsider.com/Ajax/Chart_GetChartData?instrumentType=Bond&tkData=1,116204014,1330,184&from=20241125&to=20250125",

    "https://markets.businessinsider.com/bonds/canadacd-bonds_201425-bond-2025-ca135087d507?miRedirects=1":
        "https://markets.businessinsider.com/Ajax/Chart_GetChartData?instrumentType=Bond&tkData=1,24795156,1330,184&from=20241125&to=20250125",

    "https://markets.businessinsider.com/bonds/canadacd-bonds_202227-bond-2027-ca135087n837?miRedirects=1":
        "https://markets.businessinsider.com/Ajax/Chart_GetChartData?instrumentType=Bond&tkData=1,119036843,1330,184&from=20241125&to=20250125",

    "https://markets.businessinsider.com/bonds/canadacd-bonds_201627-bond-2027-ca135087f825?miRedirects=1":
        "https://markets.businessinsider.com/Ajax/Chart_GetChartData?instrumentType=Bond&tkData=1,33461441,1330,184&from=20241125&to=20250125",

    "https://markets.businessinsider.com/bonds/canadacd-bonds_201925-bond-2025-ca135087k528?miRedirects=1":
        "https://markets.businessinsider.com/Ajax/Chart_GetChartData?instrumentType=Bond&tkData=1,50546643,1330,184&from=20241125&to=20250125",

    "https://markets.businessinsider.com/bonds/canadacd-bonds_202126-bond-2026-ca135087l930?miRedirects=1":
        "https://markets.businessinsider.com/Ajax/Chart_GetChartData?instrumentType=Bond&tkData=1,111141014,1330,184&from=20241125&to=20250125",

    "https://markets.businessinsider.com/bonds/canadacd-bonds_202026-bond-2026-ca135087l518?miRedirects=1":
        "https://markets.businessinsider.com/Ajax/Chart_GetChartData?instrumentType=Bond&tkData=1,57601476,1330,184&from=20241125&to=20250125",

    "https://markets.businessinsider.com/bonds/canadacd-bonds_202127-bond-2027-ca135087m847?miRedirects=1":
        "https://markets.businessinsider.com/Ajax/Chart_GetChartData?instrumentType=Bond&tkData=1,114329463,1330,184&from=20241125&to=20250125",

    "https://markets.businessinsider.com/bonds/canadacd-bonds_202225-bond-2025-ca135087p659?miRedirects=1":
        "https://markets.businessinsider.com/Ajax/Chart_GetChartData?instrumentType=Bond&tkData=1,122922756,1330,184&from=20241125&to=20250125",

    "https://markets.businessinsider.com/bonds/canadacd-bonds_202025-bond-2025-ca135087k940?miRedirects=1":
        "https://markets.businessinsider.com/Ajax/Chart_GetChartData?instrumentType=Bond&tkData=1,53991397,1330,184&from=20241125&to=20250125",

    "https://markets.businessinsider.com/bonds/canadacd-bonds_202427-bond-2027-ca135087s547?miRedirects=1":
        "https://markets.businessinsider.com/Ajax/Chart_GetChartData?instrumentType=Bond&tkData=1,139591564,1330,184&from=20241125&to=20250125",

    "https://markets.businessinsider.com/bonds/canadacd-bonds_202227-bond-2027-ca135087p733?miRedirects=1":
        "https://markets.businessinsider.com/Ajax/Chart_GetChartData?instrumentType=Bond&tkData=1,123653782,1330,184&from=20241125&to=20250125",

    "https://markets.businessinsider.com/bonds/8_000-canada-government-of-bond-2027-ca135087vw17?miRedirects=1":
        "https://markets.businessinsider.com/Ajax/Chart_GetChartData?instrumentType=Bond&tkData=1,490501,1330,184&from=20241125&to=20250125",

    "https://markets.businessinsider.com/bonds/canadacd-bonds_202326-bond-2026-ca135087r226?miRedirects=1":
        "https://markets.businessinsider.com/Ajax/Chart_GetChartData?instrumentType=Bond&tkData=1,130654501,1330,184&from=20241125&to=20250125",

    "https://markets.businessinsider.com/bonds/canadacd-bonds_202426-bond-2026-ca135087s398?miRedirects=1":
        "https://markets.businessinsider.com/Ajax/Chart_GetChartData?instrumentType=Bond&tkData=1,137893857,13,184&from=20241125&to=20250125",

    "https://markets.businessinsider.com/bonds/canadacd-bonds_202325-bond-2025-ca135087q640?miRedirects=1":
        "https://markets.businessinsider.com/Ajax/Chart_GetChartData?instrumentType=Bond&tkData=1,126861078,1330,184&from=20241125&to=20250125",

    "https://markets.businessinsider.com/bonds/canadacd-bonds_202426-bond-2026-ca135087r556?miRedirects=1":
        "https://markets.businessinsider.com/Ajax/Chart_GetChartData?instrumentType=Bond&tkData=1,132969994,1330,184&from=20241125&to=20250125",

    "https://markets.businessinsider.com/bonds/canadacd-bonds_202326-bond-2026-ca135087p816?miRedirects=1":
        "https://markets.businessinsider.com/Ajax/Chart_GetChartData?instrumentType=Bond&tkData=1,124578091,1330,184&from=20241125&to=20250125",

    "https://markets.businessinsider.com/bonds/canadacd-bonds_202325_sq319-bond-2025-ca135087q319?miRedirects=1":
        "https://markets.businessinsider.com/Ajax/Chart_GetChartData?instrumentType=Bond&tkData=1,125111425,1330,184&from=20241125&to=20250125",

    "https://markets.businessinsider.com/bonds/canadacd-bonds_202325-bond-2025-ca135087q806?miRedirects=1":
        "https://markets.businessinsider.com/Ajax/Chart_GetChartData?instrumentType=Bond&tkData=1,128862182,1330,184&from=20241125&to=20250125",

    "https://markets.businessinsider.com/bonds/9_000-canada-government-of-bond-2025-ca135087vh40?miRedirects=1":
        "https://markets.businessinsider.com/Ajax/Chart_GetChartData?instrumentType=Bond&tkData=1,324796,1330,184&from=20241125&to=20250125",

    "https://markets.businessinsider.com/bonds/canadacd-bonds_202426-bond-2026-ca135087r978?miRedirects=1":
        "https://markets.businessinsider.com/Ajax/Chart_GetChartData?instrumentType=Bond&tkData=1,135402145,1330,184&from=20241125&to=20250125",

    # Below are the bonds maturing in 3-10 years, there are 19 bonds in total
    "https://markets.businessinsider.com/bonds/canadacd-bonds_202131-bond-2031-ca135087n266?miRedirects=1":
        "https://markets.businessinsider.com/Ajax/Chart_GetChartData?instrumentType=Bond&tkData=1,114466942,1330,184&from=20241125&to=20250125",

    "https://markets.businessinsider.com/bonds/canadacd-bonds_202131-bond-2031-ca135087m276?miRedirects=1":
        "https://markets.businessinsider.com/Ajax/Chart_GetChartData?instrumentType=Bond&tkData=1,111293704,1330,184&from=20241125&to=20250125",

    "https://markets.businessinsider.com/bonds/canadacd-bonds_202229-bond-2029-ca135087n670?miRedirects=1":
        "https://markets.businessinsider.com/Ajax/Chart_GetChartData?instrumentType=Bond&tkData=1,117855494,1330,184&from=20241125&to=20250125",

    "https://markets.businessinsider.com/bonds/canadacd-bonds_201728-bond-2028-ca135087h235?miRedirects=1":
        "https://markets.businessinsider.com/Ajax/Chart_GetChartData?instrumentType=Bond&tkData=1,37720230,1330,184&from=20241125&to=20250125",

    "https://markets.businessinsider.com/bonds/canadacd-bonds_202030_series_l443-bond-2030-ca135087l443?miRedirects=1":
        "https://markets.businessinsider.com/Ajax/Chart_GetChartData?instrumentType=Bond&tkData=1,57501684,1330,184&from=20241125&to=20250125",

    "https://markets.businessinsider.com/bonds/canadacd-bonds_201829-bond-2029-ca135087j397?miRedirects=1":
        "https://markets.businessinsider.com/Ajax/Chart_GetChartData?instrumentType=Bond&tkData=1,42965744,1330,184&from=20241125&to=20250125",

    "https://markets.businessinsider.com/bonds/canadacd-bonds_202228-bond-2028-ca135087p576?miRedirects=1":
        "https://markets.businessinsider.com/Ajax/Chart_GetChartData?instrumentType=Bond&tkData=1,122651336,1330,184&from=20241125&to=20250125",

    "https://markets.businessinsider.com/bonds/canadacd-bonds_202232-bond-2032-ca135087p329?miRedirects=1":
        "https://markets.businessinsider.com/Ajax/Chart_GetChartData?instrumentType=Bond&tkData=1,120914999,1330,184&from=20241125&to=20250125",

    "https://markets.businessinsider.com/bonds/canadacd-bonds_202232-bond-2032-ca135087n597?miRedirects=1":
        "https://markets.businessinsider.com/Ajax/Chart_GetChartData?instrumentType=Bond&tkData=1,117606959,1330,184&from=20241125&to=20250125",

    "https://markets.businessinsider.com/bonds/canadacd-bonds_202434-bond-2034-ca135087r713?miRedirects=1":
        "https://markets.businessinsider.com/Ajax/Chart_GetChartData?instrumentType=Bond&tkData=1,133356706,1330,184&from=20241125&to=20250125",

    "https://markets.businessinsider.com/bonds/canadacd-bonds_202333-bond-2033-ca135087q723?miRedirects=1":
        "https://markets.businessinsider.com/Ajax/Chart_GetChartData?instrumentType=Bond&tkData=1,128007448,1330,184&from=20241125&to=20250125",

    "https://markets.businessinsider.com/bonds/canadacd-bonds_202429-bond-2029-ca135087r895?miRedirects=1":
        "https://markets.businessinsider.com/Ajax/Chart_GetChartData?instrumentType=Bond&tkData=1,134387959,1330,184&from=20241125&to=20250125",

    "https://markets.businessinsider.com/bonds/canadacd-bonds_202434-bond-2034-ca135087s216?miRedirects=1":
        "https://markets.businessinsider.com/Ajax/Chart_GetChartData?instrumentType=Bond&tkData=1,136888775,1330,184&from=20241125&to=20250125",

    "https://markets.businessinsider.com/bonds/canadacd-bonds_202430-bond-2030-ca135087s471?miRedirects=1":
        "https://markets.businessinsider.com/Ajax/Chart_GetChartData?instrumentType=Bond&tkData=1,138913105,16,184&from=20241125&to=20250125",

    "https://markets.businessinsider.com/bonds/canadacd-bonds_202334-bond-2034-ca135087r481?miRedirects=1":
        "https://markets.businessinsider.com/Ajax/Chart_GetChartData?instrumentType=Bond&tkData=1,131843886,1330,184&from=20241125&to=20250125",

    "https://markets.businessinsider.com/bonds/5_750-canada-government-of-bond-2029-ca135087wl43?miRedirects=1":
        "https://markets.businessinsider.com/Ajax/Chart_GetChartData?instrumentType=Bond&tkData=1,847359,1330,184&from=20241125&to=20250125",

    "https://markets.businessinsider.com/bonds/canadacd-bonds_202328-bond-2028-ca135087q491?miRedirects=1":
        "https://markets.businessinsider.com/Ajax/Chart_GetChartData?instrumentType=Bond&tkData=1,126528699,1330,184&from=20241125&to=20250125",

    "https://markets.businessinsider.com/bonds/5_750-canada-government-of-bond-2033-ca135087xg49?miRedirects=1":
        "https://markets.businessinsider.com/Ajax/Chart_GetChartData?instrumentType=Bond&tkData=1,1321208,1330,184&from=20241125&to=20250125",

    "https://markets.businessinsider.com/bonds/canadacd-bonds_202329-bond-2029-ca135087q988?miRedirects=1":
        "https://markets.businessinsider.com/Ajax/Chart_GetChartData?instrumentType=Bond&tkData=1,130328741,1330,184&from=20241125&to=20250125",
}

# Output CSV file
output_file = "bond_data.csv"

# Run the scraper
scraper(bond_data_dict, target_dates, output_file)
