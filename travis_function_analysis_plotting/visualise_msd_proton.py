import matplotlib.pyplot as plt
import pandas as pd


file_msd = 'msd_H_#2.csv'       # The raw trajectory.
file_fit = 'msd_H_#2_fit.csv'   # The linear regression line.

# TRAVIS MSD csv files usually use semicolons.
def load_msd_data(filepath):
    try:
        df = pd.read_csv(
            filepath, 
            sep=';', 
            comment='#', 
            header=None, 
            names=['Time', 'MSD', 'StdDev'] # Columns: Time, Value, StdDev.
        )
        return df
    except FileNotFoundError:
        print(f"Error: Could not find {filepath}")
        return None

df_msd = load_msd_data(file_msd)
df_fit = load_msd_data(file_fit)

if df_msd is not None:
    plt.figure(figsize=(8, 6), dpi=150)

    # Plot raw MSD.
    plt.plot(df_msd['Time'], df_msd['MSD'], 
             label='Mean Square Displacement', 
             color='#2ca02c', linewidth=2, alpha=0.8)

    # Plot linear fit (if available).
    if df_fit is not None:
        plt.plot(df_fit['Time'], df_fit['MSD'], 
                 label='Linear Regression (Fit)', 
                 color='black', linestyle='--', linewidth=1.5)

    # Formatting.
    plt.title('Mean Square Displacement (MSD) - Proton')
    plt.xlabel('Time $t$ (ps)')
    plt.ylabel('MSD ($pm^2$)')
    
    plt.fill_between(df_msd['Time'], df_msd['MSD'], alpha=0.1, color='#2ca02c')

    plt.grid(True, linestyle=':', alpha=0.6)
    plt.legend()
    plt.tight_layout()
    plt.savefig('msd_visualisation')
    plt.close()
