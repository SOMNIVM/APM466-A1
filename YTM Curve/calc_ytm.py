
import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta



def generate_coupon_dates(maturity_day, current_day):
    """
    Generate a list of coupon dates every 6 months from maturity_day backward until current_day.

    Parameters:
    - maturity_day (datetime): The final maturity date.
    - current_day (datetime): The current date.

    Returns:
    - List of coupon payment dates in descending order.
    """
    coupon_dates = []
    date = maturity_day

    while date > current_day:
        coupon_dates.append(date)
        date -= relativedelta(months=6)  # Move back 6 months

    return list(reversed(coupon_dates)) if coupon_dates else [maturity_day]


def generate_time_periods(maturity_day, current_day):
    """
    Generate an array of time periods in increments of -0.5 year, starting from end_period until the
    current date, where end_period is the days between maturity_day and the current date.
    date.
    """
    # Generate coupon dates
    coupon_dates = generate_coupon_dates(maturity_day, current_day)

    # Find the nearest future coupon date
    future_coupons = [date for date in coupon_dates if date >= current_day]
    if not future_coupons:
        raise ValueError("No future coupon dates or final payment date available.")

    nearest_coupon = min(future_coupons)  # Next coupon date after current_day

    # Define first_period as the difference between maturity and nearest coupon
    first_period = (nearest_coupon - current_day).days / 365

    # Define end_period as the difference between maturity and current day
    end_period = (maturity_day - current_day).days / 365

    if first_period != end_period:
        # Generate time periods with increments of 0.5, +0.1 to avoid rounding issue
        time_periods = np.arange(first_period, end_period + 0.1, 0.5)
    else:
        time_periods = np.array([first_period])
    # print(time_periods)
    return time_periods


def bond_price(y, coupon, interval, face=100):
    """
    Compute the bond price given a yield to maturity (y),
    coupon rate, time to maturity (in years), and face value.
    Assumes semi-annual compounding.
    """
    N = len(interval)
    price_calc = sum((coupon / 2) / ((1 + y / 2) ** i) for i in range(1, N+1))
    price_calc += face / ((1 + y / 2) ** N)
    return price_calc


def bond_ytm(price, coupon, interval, face=100):
    """
    Find the yield to maturity (YTM) by searching for the yield
    that equates bond price to present value of future cash flows.
    Uses a brute-force search with linear interpolation.
    """
    y_candidates = np.linspace(0.0, 0.20, 2001)  # Search for YTM between 0% and 20%
    prices = [bond_price(y, coupon, interval, face) for y in y_candidates]

    for i in range(len(prices) - 1):
        if (prices[i] - price) * (prices[i+1] - price) < 0:  # Detect price crossing
            # Linear interpolation to refine YTM
            return y_candidates[i] + (y_candidates[i+1] - y_candidates[i]) * (price - prices[i]) / (prices[i+1] - prices[i])

    return None  # Return None if no YTM found


# Load bond dataset
bond_data_path = "../Data Extract/bond_selection.csv"
bond_df = pd.read_csv(bond_data_path)

# Convert date columns to datetime format
bond_df["Maturity Date"] = pd.to_datetime(bond_df["Maturity Date"], errors='coerce')
bond_df["Date"] = pd.to_datetime(bond_df["Date"], errors='coerce')

# Compute maturity in years
bond_df["Maturity (Years)"] = (bond_df["Maturity Date"] - bond_df["Date"]).dt.days / 365

# Ensure correct sorting: by maturity date
bond_df_sorted = bond_df.sort_values(by=["Maturity Date"], ascending=[True])

# Compute YTM for each bond
ytm_results = []

# Iterate over each unique date to compute ytm
for date in bond_df_sorted["Date"].unique():
    daily_bond_data = bond_df_sorted[bond_df_sorted["Date"] == date]

    ytm_results = []
    for _, row in bond_df_sorted.iterrows():
        price = row["Close"]
        coupon = row["Coupon Rate"] * 100  # convert into coupon payment
        maturity_day = row["Maturity Date"]
        current_day = row["Date"]
        interval = generate_time_periods(maturity_day, current_day)

        # Compute ytm
        ytm = bond_ytm(price, coupon, interval)

        ytm_results.append([row["Name"], row["ISIN"], row["Date"], row["Maturity Date"], ytm])


# Convert results to DataFrame and save
ytm_df = pd.DataFrame(ytm_results, columns=["Bond Name", "ISIN", "Date", "Maturity Date", "YTM"])
ytm_df.to_csv("ytm.csv", index=False)

print("Corrected ytm saved to ytm.csv")
