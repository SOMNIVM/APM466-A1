import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def compute_forward_rates(semi_rates):
    """
    Compute 1-year forward rates from semi-annual spot rates.

    :param semi_rates: List of semi-annual spot rates.
    :return: List of 1-year forward rates.
    """
    indices = [1, 2, 3, 4, 5]  # The semi_annual spot rate of the 1-5 years
    forward_rates = []
    for n in range(2, 6):  # Computing f(1,1) to f(1,4)
        forward_rate = (((1 + semi_rates[n - 1]) ** (2 * (n))) /
                        ((1 + semi_rates[0]) ** (2 * 1))) ** (1 / (2 * (n - 1))) - 1
        forward_rates.append(forward_rate)

    return forward_rates


# Load the bootstrapped spot rates dataset
file_path = r"C:/Users/17764/PycharmProjects/APM466-A1/Spot Curve/bootstrapped_spot_rates.csv"
bond_df = pd.read_csv(file_path)

# Convert date columns to datetime format
bond_df["Maturity Date"] = pd.to_datetime(bond_df["Maturity Date"], errors='coerce')
bond_df["Date"] = pd.to_datetime(bond_df["Date"], errors='coerce')

# Ensure correct sorting: by maturity date
bond_df_sorted = bond_df.sort_values(by=["Maturity Date"], ascending=[True])

# Prepare storage for forward rate results
forward_rate_results = []
forward_maturities = [1, 2, 3, 4, 5]

for date in bond_df_sorted["Date"].unique():

    # Extract the "Spot Rate" column
    daily_bond_data = bond_df_sorted[bond_df_sorted["Date"] == date]
    spot_rates = daily_bond_data["Spot Rate"].values  # Extract spot rates as an array

    # Compute semi-annual rates by averaging every two consecutive spot rates
    semi_annual_rates = [(spot_rates[i] + spot_rates[i + 1]) / 2 for i in range(len(spot_rates) - 1)]

    # Compute forward rates
    forward_rates = compute_forward_rates(semi_annual_rates)

    # Store results
    forward_rate_results.append([date] + forward_rates)

# Convert results to DataFrame
forward_rates_df = pd.DataFrame(forward_rate_results, columns=["Date"] + [f"1Y-{n}Y Forward Rate"
                                                                          for n in range(2, 6)])
forward_rates_df = forward_rates_df.sort_values(by=["Date"], ascending=[True])

# Save to CSV
forward_rates_df.to_csv("forward_curve.csv", index=False)
print("Forward curve saved to forward_curve.csv")
