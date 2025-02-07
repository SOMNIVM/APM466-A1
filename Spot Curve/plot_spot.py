import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from scipy.interpolate import interp1d

# Load the dataset
file_path = "bootstrapped_spot_rates.csv"
df = pd.read_csv(file_path)

# Convert dates to datetime format
df["Date"] = pd.to_datetime(df["Date"])
df["Maturity Date"] = pd.to_datetime(df["Maturity Date"])

# Compute maturity in years
df["Maturity (Years)"] = (df["Maturity Date"] - df["Date"]).dt.days / 365

# Set up the plot
plt.figure(figsize=(10, 6))

# Iterate over unique dates and plot **only original points**
for date in df["Date"].unique():
    daily_data = df[df["Date"] == date]

    # Sort by maturity
    daily_data = daily_data.sort_values("Maturity (Years)")

    # Extract x (maturities) and y (spot rates)
    maturities = daily_data["Maturity (Years)"].values
    spot_rates = daily_data["Spot Rate"].values

    # Plot the original data points only (no interpolation)
    plt.plot(maturities, spot_rates * 100, label=date.date(), marker='o', linestyle='-', alpha=0.8)

# Formatting the plot
plt.title("Bootstrapped Yield Curve (Spot Curve) Over Time (No Interpolation)")
plt.xlabel("Maturity (Years)")
plt.ylabel("Spot Rate (%)")
plt.legend(title="Date", bbox_to_anchor=(1, 1), loc='upper left', fontsize=7)
plt.grid(True)

# Show the plot
plt.show()
