import matplotlib.pyplot as plt
import pandas as pd 
import os

 
files_map = {
    'rdf_H_O_[H1r_O1o].csv': 'Water (O-H)',
    'rdf_H_C2H3O2_[H1r_CHOo].csv': 'Acetic Acid (O-H)',
    'rdf_H_C3H3N2_[H1r_CHNo].csv': 'Imidazole (N-H)' 
}

output_filename = 'rdf_covalent_comparison.png' 
plt.figure(figsize=(10, 6))
files_found = False
 
for filename, label in files_map.items():
    if os.path.exists(filename):
        try:
            # TRAVIS RDFs use semicolons and # for comments
            df = pd.read_csv(filename, sep=';', comment='#')
            df.columns = df.columns.str.strip()
              
            # Col 0 is Distance, Col 1 is g(r)
            x_col = df.columns[0]
            y_col = df.columns[1]
             
            plt.plot(df[x_col], df[y_col], linewidth=2, label=label)
            print(f" -> Plotted: {filename}") 
            files_found = True
            
        except Exception as e:
            print(f" -> Error reading {filename}: {e}")
    else:
        # # Fallback: Check for files starting with the name (ignoring extension issues)
        # found_partial = False 
        # base_name = filename.replace('.csv', '')
        # for f in os.listdir('.'):
        #     if f.startswith(base_name) and f.endswith('.csv'):
        #         try:
        #             df = pd.read_csv(f, sep=';', comment='#')
        #             df.columns = df.columns.str.strip()
        #             plt.plot(df.iloc[:, 0], df.iloc[:, 1], linewidth=2, label=label)
        #             print(f" -> Found match: {f} (for {label})")
        #             found_partial = True
        #             files_found = True
        #             break
        #         except:
        #             pass 
        
        # if not found_partial:
        #     print(f" -> Warning: File not found: {filename}")
        print(f"Error: File not found: {filename}")

if files_found: 
    plt.xlabel('Distance (pm)', fontsize=14) 
    plt.ylabel('g(r)', fontsize=14) 
    plt.title('MACE - Radial Distribution Functions', fontsize=16)
       
    # Set limit to 300 pm to focus on the bond and first shell
    plt.xlim(0, 350)
    plt.grid(True, linestyle='--', alpha=0.5) 
    plt.legend(fontsize=12)
    plt.tight_layout()
    
    plt.savefig(output_filename, dpi=1200)
    print(f"\nPlot saved as: {output_filename}")
else:
    print("\nError: No valid CSV files found.")
  


