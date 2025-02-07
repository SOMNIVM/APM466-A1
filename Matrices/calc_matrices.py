import numpy as np
import pandas as pd

# Load forward rates dataset
forward_rates_file = (r"C:/Users/17764/PycharmProjects/APM466-A1/Forward Rate Curve/"
                      r"forward_curve.csv")
forward_df = pd.read_csv(forward_rates_file)

# Load YTM dataset
ytm_file = r"C:/Users/17764/PycharmProjects/APM466-A1/YTM Curve/ytm.csv"
ytm_df = pd.read_csv(ytm_file)

# Convert Date columns to datetime format
forward_df["Date"] = pd.to_datetime(forward_df["Date"], errors='coerce')
ytm_df["Date"] = pd.to_datetime(ytm_df["Date"], errors='coerce')

# Ensure sorting by Date and Bond Name for consistency
ytm_df = ytm_df.sort_values(by=["Date", "ISIN"])

# Pivot table: Convert from long format (100 rows) to wide format (10x10 matrix)
ytm_pivot = ytm_df.pivot(index="ISIN", columns="Date", values="YTM")

ytm_array = ytm_pivot.to_numpy()

# Select only the 5 bonds (indices 1, 3, 5, 7, 9)
selected_indices = [1, 3, 5, 7, 9]
ytm_selected = ytm_array[selected_indices,:]  # Shape: (5 bonds x 10 dates)

# Initialize log return matrix (9 times, 5 bonds)
log_ytm_matrix = np.zeros((5, 9))

# Compute log returns for each selected bond
for i in range(5):  # Iterate over 5 selected bonds (columns) 0-4
    for j in range(9):  # Compute log return for 9 time periods (rows) 0-8
        log_ytm_matrix[i, j] = np.log(ytm_selected[i, j+1] / ytm_selected[i, j])

# Compute the covariance matrix of log returns (5 bonds × 5 bonds)
cov_ytm = np.cov(log_ytm_matrix, rowvar=False)
print(cov_ytm)


# Extract only fwd rate
forward_rates_array = np.transpose(forward_df.iloc[:, 1:].to_numpy())  # Convert to NumPy array
log_forward_matrix = np.zeros((5, 9))
for i in range(1, 5):  # from row 1-4
    for j in range(1, 10):  # from column 1-9
        log_forward_matrix[i-1, j-1] = np.log(forward_rates_array[i-1, j]
                                              / forward_rates_array[i-1, j-1])
cov_fwd = np.cov(log_forward_matrix, rowvar=False)
print(cov_fwd)


# Compute eigenvalues and eigenvectors for both covariance matrices
eigvals_yield, eigvecs_yield = np.linalg.eig(cov_ytm)
eigvals_forward, eigvecs_forward = np.linalg.eig(cov_fwd)

# Print results for verification
print("\nEigenvalues of Yield Covariance Matrix:")
print(eigvals_yield)
print("\nEigenvectors of Yield Covariance Matrix:")
print(eigvecs_yield)

print("Eigenvalues of Forward Rate Covariance Matrix:")
print(eigvals_forward)
print("\nEigenvectors of Forward Rate Covariance Matrix:")
print(eigvecs_forward)
