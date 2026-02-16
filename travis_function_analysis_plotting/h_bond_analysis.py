import matplotlib.pyplot as plt
import pandas as pd
import os



files_to_plot = {
    'dacf_O_H_d[O1r_H1o]_r125-251_int_acfless_correq.csv': 'Water (O-H)',
    'dacf_C2H3O2_H_d[CHOr_H1o]_r131-217_int_acfless_correq.csv': 'Acetic Acid (O-H)',
    'dacf_C3H3N2_H_d[CHNr_H1o]_r131-232_int_acfless_correq.csv': 'Imidazole (N-H)'
}

output_filename = 'hbond_lifetimes_analysis_200k_10.png'


plt.figure(figsize=(10, 6))
for filename, label in files_to_plot.items():
    if os.path.exists(filename):
        try:
            # TRAVIS CSVs use semicolons. 
            # We use comment='#' to skip the metadata header lines.
            df = pd.read_csv(filename, sep=';', comment='#')
            
            # Clean up column names
            df.columns = df.columns.str.strip()
            
            # Usually Col 0 is Time, Col 1 is the ACF
            time_col = df.columns[0]
            acf_col = df.columns[1]
            
            plt.plot(df[time_col], df[acf_col], linewidth=2.0, label=label)
            print(f"Successfully plotted: {filename}")
            
        except Exception as e:
            print(f"Error reading {filename}: {e}")
    else:
        print(f"Warning: File not found: {filename}")


plt.xlabel('Time (ps)', fontsize=14)
plt.ylabel('Bond Survival Probability', fontsize=14)
plt.title('MACE - Hydrogen Bond Stability', fontsize=16)

plt.ylim(-0.05, 1.05)
plt.xlim(0, 80)
plt.grid(True, linestyle='--', alpha=0.5)
plt.legend(fontsize=12)
plt.tight_layout()
plt.savefig(output_filename, dpi=1200)
print(f"\nPlot saved as: {output_filename}")
