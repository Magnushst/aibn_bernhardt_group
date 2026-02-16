import matplotlib.pyplot as plt
import pandas as pd
import os

# --- Configuration ---
# Define the files, labels, and colors for the 4 species
species_list = [
    {
        "file": "msd_H_#2.csv", 
        "label": "Proton (H)", 
        "color": "#d62728"  # Red
    },
    {
        "file": "msd_O_#2.csv", 
        "label": "Water Oxygen (O)", 
        "color": "#1f77b4"  # Blue
    },
    {
        "file": "msd_C3H3N2_CHN.csv", 
        "label": "Imidazole", 
        "color": "#2ca02c"  # Green
    },
    {
        "file": "msd_C2H3O2_CHO.csv", 
        "label": "Acetic Acid", 
        "color": "#ff7f0e"  # Orange
    }
]

def load_msd_data(filepath):
    """Loads TRAVIS MSD csv files (semicolon separated)."""
    if not os.path.exists(filepath):
        print(f"Warning: File '{filepath}' not found. Skipping.")
        return None
        
    try:
        df = pd.read_csv(
            filepath, 
            sep=';', 
            comment='#', 
            header=None, 
            names=['Time', 'MSD', 'StdDev'] 
        )
        return df
    except Exception as e:
        print(f"Error reading '{filepath}': {e}")
        return None


plt.figure(figsize=(10, 7), dpi=150)
# Loop through each species and plot
for item in species_list:
    df = load_msd_data(item["file"])
    
    if df is not None:
        plt.plot(
            df['Time'], 
            df['MSD'], 
            label=item["label"], 
            color=item["color"], 
            linewidth=2.5, 
            alpha=0.9
        )

plt.title('Orb - Diffusion Comparison', fontsize=16, fontweight='bold')
plt.xlabel('Time (ps)', fontsize=14)
plt.ylabel(r'Mean Squared Displacement (pm$^2$)', fontsize=14)

plt.grid(True, which='major', linestyle='--', linewidth=0.7, alpha=0.7)
plt.grid(True, which='minor', linestyle=':', linewidth=0.5, alpha=0.4)
plt.minorticks_on()

plt.legend(fontsize=12, loc='upper left', frameon=True, framealpha=0.9, edgecolor='gray')
plt.tight_layout()

output_filename = 'combined_msd_comparison.png'
plt.savefig(output_filename)
print(f"\nGraph saved to: {output_filename}")
plt.close()
