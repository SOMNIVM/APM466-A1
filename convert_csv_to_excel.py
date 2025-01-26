import openpyxl
import pandas as pd

# Input and output file paths
csv_file = "bond_data.csv"  # Replace with your CSV file name
excel_file = "bond_data.xlsx"  # Replace with desired Excel file name

# Read the CSV file
df = pd.read_csv(csv_file)

# Save to Excel
df.to_excel(excel_file, index=False)

print(f"File successfully converted to {excel_file}")
