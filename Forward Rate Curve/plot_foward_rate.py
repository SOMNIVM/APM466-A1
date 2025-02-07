import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Load the dataset
file_path = "forward_curve.csv"
df = pd.read_csv(file_path)

# Convert Date column to datetime format
df["Date"] = pd.to_datetime(df["Date"])

# Extract forward rate columns (ignoring the "Date" column)
forward_columns = [col for col in df.columns if "Forward Rate" in col]

# Set up the plot
plt.figure(figsize=(10, 6))

# Iterate over unique dates and plot **only original points**
for i, date in enumerate(df["Date"].unique()):
    daily_data = df[df["Date"] == date]

    # Extract forward rates for this date
    forward_rates = daily_data[forward_columns].values.flatten()  # Convert to 1D array
    maturities = list(range(1, len(forward_rates) + 1))  # Create x-axis as 1,2,3,4 (1-n forward)

    # Plot the original forward rate data points only (no interpolation)
    plt.plot(maturities, forward_rates * 100, label=date.date(), marker='o', linestyle='-', alpha=0.8)

# Formatting the plot
plt.title("1-n Forward Curve Over Time")
plt.xlabel("n (Years)")
plt.ylabel("1-n Forward Rate (%)")
plt.legend(title="Date", bbox_to_anchor=(1, 1), loc='upper left', fontsize=7)
plt.grid(True)

# Show the plot
plt.show()
