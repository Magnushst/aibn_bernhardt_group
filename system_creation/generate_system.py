import numpy as np
import random
from ase import Atoms
from ase.build import molecule
from ase.io import write
from ase.geometry import get_distances


# Calculated for approx 1.0 g/mL density:
# Mass ~ 30,830 u. Volume needed ~ 51,200 A^3. Cube root ~ 37.13 A.
SIDE_LENGTH = 37.2  
FILENAME = 'water_acetic_imidazole_mix.xyz'

N_WATER = 1000
N_ACETIC = 100
N_IMIDAZOLE = 100
TOTAL_MOLS = N_WATER + N_ACETIC + N_IMIDAZOLE
MIN_DISTANCE = 1.5   # Minimum allowed distance (Angstroms).

print(f'Generating system: {N_WATER} Water, {N_ACETIC} Acetic, {N_IMIDAZOLE} Imidazole')
print(f'Box Size: {SIDE_LENGTH} A (Target Density ~ 1.0 g/mL)')


def build_imidazole():
    """Manually constructs Imidazole (C3H4N2)"""
    # Coordinates from standard geometry (approximate, planar).
    # N1-C2-N3-C4-C5 ring.
    atoms = Atoms(
        symbols='NCNCCHHHH',
        positions=[
            [ 1.065, -0.407,  0.000], # N1 (Protonated site usually).
            [ 0.177, -1.450,  0.000], # C2
            [-1.025, -0.916,  0.000], # N3
            [-0.916,  0.456,  0.000], # C4
            [ 0.402,  0.771,  0.000], # C5
            [ 2.067, -0.528,  0.000], # H on N1
            [ 0.457, -2.496,  0.000], # H on C2
            [-1.831,  1.028,  0.000], # H on C4
            [ 0.865,  1.745,  0.000], # H on C5
        ]
    )
    return atoms

def build_acetic_acid():
    """Manually constructs Acetic Acid (CH3COOH)"""
    # Fallback if ASE molecule('CH3COOH') fails
    atoms = Atoms(
        symbols='CCOHHHH',
        positions=[
            [ 0.000,  0.000,  0.000], # C (Methyl)
            [ 1.500,  0.000,  0.000], # C (Carboxyl)
            [ 2.100,  1.200,  0.000], # O (Double bond)
            [ 2.100, -1.100,  0.000], # O (Hydroxyl)
            [-0.350,  0.900,  0.300], # H (Methyl)
            [-0.350, -0.900,  0.300], # H (Methyl)
            [-0.350,  0.000, -1.000], # H (Methyl)
            [ 3.050, -1.000,  0.000], # H (Hydroxyl)
        ]
    )
    return atoms


atoms = Atoms(pbc=True, cell=[SIDE_LENGTH, SIDE_LENGTH, SIDE_LENGTH])

mol_list = []
print("Building molecule list...")

# WATER
for _ in range(N_WATER):
    mol_list.append(molecule('H2O'))

# Try ASE standard first, fallback to manual if missing
try:
    proto_acetic = molecule('CH3COOH')
except:
    proto_acetic = build_acetic_acid()

for _ in range(N_ACETIC):
    mol_list.append(proto_acetic.copy())

proto_imidazole = build_imidazole()

for _ in range(N_IMIDAZOLE):
    mol_list.append(proto_imidazole.copy())

# Shuffle for random mixture
random.shuffle(mol_list)

n_grid = 11  # 11x11x11 = 1331 slots
step = SIDE_LENGTH / n_grid
offset = step / 2.0

print("Placing molecules on 11x11x11 grid with SAFETY CHECK...")
count = 0

for x in range(n_grid):
    for y in range(n_grid):
        for z in range(n_grid):
            if count >= len(mol_list): break
            
            mol_base = mol_list[count]
            
            # Try up to 500 rotations to find a non-overlapping configuration
            # NECESSARY because grid step (3.38 A) < Mol Size (~4.5 A)
            placed_safely = False
            
            for attempt in range(500):
                mol = mol_base.copy()
                mol.center() # Reset to local origin
                
                # Rotate
                mol.rotate(np.random.rand() * 360, 'x')
                mol.rotate(np.random.rand() * 360, 'y')
                mol.rotate(np.random.rand() * 360, 'z')
                
                # Translate to Grid + Jitter.
                jitter = (np.random.rand(3) - 0.5) * 0.4
                pos = [x*step + offset, y*step + offset, z*step + offset]
                mol.translate(pos + jitter)
                
                # CHECK OVERLAPS:
                # If this is the first molecule, it's always safe.
                if len(atoms) == 0:
                    placed_safely = True
                    atoms.extend(mol)
                    break
                
                # Calculate distances to ALL existing atoms using PBC.
                # Only need the distance array (index 1 from get_distances).
                dists = get_distances(mol.get_positions(), atoms.get_positions(), 
                                      cell=atoms.cell, pbc=atoms.pbc)[1]
                
                # If the smallest distance is safe, place it.
                if np.min(dists) > MIN_DISTANCE:
                    placed_safely = True
                    atoms.extend(mol)
                    break
            
            if placed_safely:
                count += 1
                if count % 100 == 0:
                    print(f"Placed {count} molecules...")
            else:
                # If we fail 500 times, the grid is too tight here.
                # We skip this grid slot and hope the next one works (we have ~130 spares).
                print(f"Warning: Grid slot ({x},{y},{z}) too crowded. Skipping.")
                # We do NOT increment count, so we try this molecule again in the next slot.

            
        if count >= len(mol_list): break
    if count >= len(mol_list): break

if count < len(mol_list):
    print(f"CRITICAL WARNING: Only placed {count} / {len(mol_list)} molecules.")
    print("The density is too high for this grid generation method.")
    exit(1)  
else:
    print(f"Placed {count} molecules successfully with NO OVERLAPS.")
    write(FILENAME, atoms)
    print(f"Saved to {FILENAME}")
    
