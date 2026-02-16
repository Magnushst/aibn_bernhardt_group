import torch
import numpy as np
from ase import units
from ase.io import read, write, iread
from ase.md.npt import NPT
from ase.optimize import LBFGS
from sevenn.calculator import SevenNetCalculator
from ase.md.velocitydistribution import MaxwellBoltzmannDistribution, Stationary
from ase.geometry import cell_to_cellpar, cellpar_to_cell



INPUT_FILE = '../water_acetic_imidazole_mix.xyz'
TEMP_TARGET = 330
STEPS_EQUIL = 100000
STEPS_PROD = 2000000
BOX_LENGTH = 37.2  
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
VERSION = '_2mill_interval_10'  # NOTE: PLACEHOLDER TO MARK/NAME OUTSPUTS (i.e., a suffix)
INTERVAL = 10                     # NOTE: Interval to save production analysis in.


try:
    atoms = read(INPUT_FILE)
    atoms.set_cell([BOX_LENGTH, BOX_LENGTH, BOX_LENGTH])
    atoms.set_pbc(True)
    atoms.center()
    print(f'Loaded {len(atoms)} atoms.')
except FileNotFoundError:
    print(f'Error: {INPUT_FILE} not found. Run generate_system.py first.')
    exit()


atoms.calc = SevenNetCalculator(model="sevennet-0", device=DEVICE)
# Use Fmax=0.1 to ensure it stops once atoms are comfortable.
LBFGS(atoms).run(fmax=0.1, steps=50)


print('\nHeating 100K -> 330K')
atoms.set_velocities(np.zeros_like(atoms.get_positions()))
for t in range(100, TEMP_TARGET + 1, 50):
    print(f' -> {t} K')
    MaxwellBoltzmannDistribution(atoms, temperature_K=t)
    Stationary(atoms)
    
    # NVT heating (barostat off).
    # 100fs coupling is safer for bonds.
    NPT(atoms, timestep=1.0*units.fs, temperature_K=t, externalstress=0, pfactor=None, ttime=100*units.fs).run(500)


print(f'\nNVT Equilibration ({STEPS_EQUIL} steps)')
dyn_equil = NPT(atoms, timestep=1.0*units.fs, temperature_K=TEMP_TARGET, externalstress=0, pfactor=None, ttime=100*units.fs)
def print_status(dyn, phase):
    pe = atoms.get_potential_energy()
    print(f'{phase} Step {dyn.nsteps}: Temp={atoms.get_temperature():.1f}K, PE={pe:.1f} eV')
dyn_equil.attach(lambda: print_status(dyn_equil, 'Equil'), interval=INTERVAL)
dyn_equil.run(STEPS_EQUIL)


write('sevennet_equilibrated_{VERSION}.xyz', atoms)  # Checkpoint.


print(f'\nNVT Production ({STEPS_PROD} steps)')
atoms = read('sevennet_equilibrated_{VERSION}.xyz')  # Reload calculator to be safe.
atoms.calc = SevenNetCalculator(model="sevennet-0", device=DEVICE)

dyn_prod = NPT(atoms, timestep=1.0*units.fs, temperature_K=TEMP_TARGET, externalstress=0, pfactor=None, ttime=100*units.fs)
def write_frame():
    write('sevennet_proton_sim_{VERSION}.xyz', atoms, format='extxyz', append=True)
dyn_prod.attach(write_frame, interval=INTERVAL)

def print_status():
    pe = atoms.get_potential_energy()
    print(f'Prod Step {dyn_prod.nsteps}: T={atoms.get_temperature():.1f}K, PE={pe:.1f}')
dyn_prod.attach(print_status, interval=INTERVAL)
dyn_prod.run(STEPS_PROD)


# NOTE: Need unwrapped coords in TRAVIS, so this is the actually import file:
print('Done. Saved sevennet_proton_{VERSION}.lmp')
print('Exporting UNWRAPPED coordinates for TRAVIS')
with open('sevennet_analysis_unwrapped_{VERSION}.lmp', 'w') as f:
    # iread yields one frame at a time, keeping RAM usage low.
    for i, frame in enumerate(iread('sevennet_proton_sim_{VERSION}.xyz')):
        
        cp = cell_to_cellpar(frame.cell)
        frame.set_cell(cellpar_to_cell(cp), scale_atoms=True)

        # Get unwrapped coords.
        # Since we are reading from an MD run XYZ, the positions are naturally drifting (unwrapped). 
        pos = frame.get_positions()
        box = np.diag(frame.cell)
        symbols = frame.get_chemical_symbols()
        
        # Write LAMMPS file (manually written).
        f.write(f'ITEM: TIMESTEP\n{i}\nITEM: NUMBER OF ATOMS\n{len(frame)}\n')
        f.write('ITEM: BOX BOUNDS pp pp pp\n')
        f.write(f'0.000000 {box[0]:.6f}\n')
        f.write(f'0.000000 {box[1]:.6f}\n')
        f.write(f'0.000000 {box[2]:.6f}\n')
        
        # Body (xu yu zu flags for unwrapped coords).
        f.write('ITEM: ATOMS id element xu yu zu\n')
        for j, sym in enumerate(symbols):
            f.write(f'{j+1} {sym} {pos[j,0]:.4f} {pos[j,1]:.4f} {pos[j,2]:.4f}\n')

        # Progress bar.
        if i % 1000 == 0:
            print(f'Converted {i} frames...', end='\r')

print(f"\n\nSUCCESS. Saved to 'sevennet_analysis_unwrapped_{VERSION}.lmp'")
print('(use this file for all Travis analyses.)')
