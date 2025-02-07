
import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta


def generate_coupon_dates(maturity_day, current_day):
    """
    Generate coupon dates every 6 months from maturity_day backward until current_day.

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
    Generate an array of time periods in increments of -0.5, starting from end_period until the
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


def bootstrap_yield_curve(bonds, compounding_frequency=2):
    """
    Bootstraps the spot rate curve using semiannual compounding, ensuring the first period is fractional.

    :param bonds: List of tuples [(price, coupon_rate, maturity_date, current_date)] where:
                  - price is the dirty price of the bond (including accrued interest)
                  - coupon_rate is the annual coupon rate (decimal)
                  - maturity_date is the bond's maturity date
                  - current_date is the date on which the bond price is observed
    :param compounding_frequency: Number of compounding periods per year (default = 2 for semiannual)
    :return: Array of spot rates for each bond
    """
    spot_rates = np.zeros(len(bonds))

    for i, (price, coupon_rate, maturity_date, current_date) in enumerate(sorted(bonds, key=lambda x: x[2])):
        if price <= 0:
            print(f"Warning: Invalid bond price {price}. Skipping bond with maturity {maturity_date}.")
            spot_rates[i] = np.nan  # Assign NaN to invalid calculations
            continue

        # Compute correct time periods for discounting
        time_periods = generate_time_periods(maturity_date, current_date)
        # note time period already equivalent to the t_i in the semi-annual compounding

        # Construct cash flows using semiannual payments
        coupon_payment = coupon_rate * 100  # Coupon payment per year
        cash_flows = np.array([coupon_payment / 2] * (len(time_periods) - 1) +
                              [100 + coupon_payment / 2])
        # i.e. cash_flow is a list of the cash flow of one bond
        # print(cash_flows)

        # First bond (Zero-Coupon Bond first)
        if len(cash_flows) == 1:
            spot_rates[i] = compounding_frequency * (((100 + coupon_payment/2)
                                                      / price) ** (1 / (2 * time_periods[-1])) - 1)
        else:
            # Compute present value of earlier cash flows using previously bootstrapped spot rates
            discounted_cash_flows = sum(
                cash_flows[j] / ((1 + spot_rates[j] / compounding_frequency) **
                                 (2 * time_periods[j])) for j in range(len(cash_flows) - 1))
            # Discount all earlier cash flows


            # Compute the residual amount for the last cash flow
            residual = price - discounted_cash_flows
            if residual <= 0:
                print(f"Warning: Residual for bond with maturity {maturity_date} is too low. Adjusting spot rate calculation.")
                spot_rate = spot_rates[i-1]  # Use previous spot rate as an approximation
            else:
                # Solve for the new spot rate using the final cash flow
                spot_rate = compounding_frequency * (((100 + coupon_payment/2) / residual) ** (1 / (2 * time_periods[-1])) - 1)

            spot_rates[i] = spot_rate

    return spot_rates

# Load bond dataset
bond_data_path = "../Data Extract/bond_selection.csv"
bond_df = pd.read_csv(bond_data_path)

# Convert date columns to datetime format
bond_df["Maturity Date"] = pd.to_datetime(bond_df["Maturity Date"], errors='coerce')
bond_df["Date"] = pd.to_datetime(bond_df["Date"], errors='coerce')

# Ensure correct sorting: by maturity date
bond_df_sorted = bond_df.sort_values(by=["Maturity Date"], ascending=[True])

# Prepare storage for spot rate results
spot_rate_results = []

# Iterate over each unique date to compute spot rates
for date in bond_df_sorted["Date"].unique():
    daily_bond_data = bond_df_sorted[bond_df_sorted["Date"] == date]

    # Prepare bond data for bootstrapping
    bonds = []
    for _, bond in daily_bond_data.iterrows():
        if pd.notna(bond["Maturity Date"]) and pd.notna(bond["Date"]):
            bonds.append((bond["Dirty"], bond["Coupon Rate"], bond["Maturity Date"], bond["Date"]))

    # Compute spot rates using bootstrapping
    if bonds:
        spot_rates = bootstrap_yield_curve(bonds)

        # Store results
        for i, bond in enumerate(daily_bond_data.iterrows()):
            bond_name = bond[1]["Name"]
            coupon_rate = bond[1]["Coupon Rate"]
            close = bond[1]["Close"]
            spot_rate_results.append([bond_name, coupon_rate, date, bond[1]["Maturity Date"], close,
                                      spot_rates[i]])

# Convert results to DataFrame and save
spot_rate_df = pd.DataFrame(spot_rate_results, columns=["Bond Name", "Coupon Rate",
                                                        "Date", "Maturity Date", "Close", "Spot Rate"])
spot_rate_df.to_csv("bootstrapped_spot_rates.csv", index=False)

print("Corrected bootstrapped spot rates saved to bootstrapped_spot_rates.csv")

# Debug Report:
# time_periods are correct
# cash_flow are correct
# bond_df is correct
