import torch, os
import numpy as np
from ase import units
from ase.io import read, write, iread
from ase.md.npt import NPT
from ase.optimize import LBFGS
from ase.md.velocitydistribution import MaxwellBoltzmannDistribution, Stationary
from ase.geometry import cell_to_cellpar, cellpar_to_cell

from sevenn.calculator import SevenNetCalculator
# from aimnet.calculators import AIMNet2ASE
# from orb_models.forcefield import pretrained
# from orb_models.forcefield.calculator import ORBCalculator
# from mace.calculators import mace_mp 


INPUT_FILE = '../water_acetic_imidazole_mix.xyz'
TEMP_TARGET = 330
STEPS_EQUIL = 100000
STEPS_PROD = 1000000
BOX_LENGTH = 37.2  
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
VERSION = 'v8_2mill_interval_10'  # NOTE: PLACEHOLDER TO MARK/NAME OUTSPUTS (i.e., a suffix)
INTERVAL = 10                     # NOTE: Interval to save production analysis in.
MODEL = 'sevennet'                # NOTE: Placeholder for model name (does not acutally change loaded model, just for file naming).

try:
    atoms = read(INPUT_FILE)
    atoms.set_cell([BOX_LENGTH, BOX_LENGTH, BOX_LENGTH])
    atoms.set_pbc(True)
    atoms.center()
    print(f'Loaded {len(atoms)} atoms.')
except FileNotFoundError:
    print(f'Error: {INPUT_FILE} not found. Run generate_system.py first.')
    exit()

TRAJ_FILE = f'{MODEL}_proton_sim_{INTERVAL}.xyz'
OUTPUT_LMP_WRAPPED = f'{MODEL}__proton_sim_{INTERVAL}.lmp'
OUTPUT_LMP_UNWRAPPED = f'{MODEL}__analysis_unwrapped_{INTERVAL}.lmp'


def count_frames_xyz(filename):
    count = 0
    CHUNK_SIZE = 16 * 1024 * 1024 
    pattern = b'Lattice='
    with open(filename, 'rb') as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk: break
            count += chunk.count(pattern)
    return count

try:
    if not os.path.exists(TRAJ_FILE):
        print(f'Error: {TRAJ_FILE} not found.')
        # Add logic here to start fresh if file missing?
        exit()

    atoms = read(TRAJ_FILE, index=-1)
    frames_done = count_frames_xyz(TRAJ_FILE)
    steps_done = frames_done * 10
    steps_remaining = STEPS_PROD - steps_done
    
    print(f'Steps remaining: {steps_remaining}')
    if steps_remaining <= 0:
        print('Simulation finished.')
    else:
        atoms.calc = SevenNetCalculator(model='sevennet-0', device=DEVICE)

        print(f'\nRestarting NVT Production ({steps_remaining} steps)')
        dyn_prod = NPT(atoms, timestep=1.0*units.fs, temperature_K=TEMP_TARGET, externalstress=0, pfactor=None, ttime=100*units.fs)

        def write_frame():
            write(TRAJ_FILE, atoms, format='extxyz', append=True)

        def print_status(dyn, current_step_offset):
            pe = atoms.get_potential_energy()
            total_step = current_step_offset + dyn.nsteps
            print(f'Prod Step {total_step}: Temp={atoms.get_temperature():.1f}K, PE={pe:.1f} eV')

        dyn_prod.attach(lambda: print_status(dyn_prod, steps_done), interval=1000) # Print status rarely
        dyn_prod.attach(write_frame, interval=INTERVAL) # Write frames (10fs)

        dyn_prod.run(steps_remaining)
        print('Production finished.')

except Exception as e:
    print(f'Error during simulation: {e}')
    exit()


print(f'\nConverting to LAMMPS')
try:
    with open(OUTPUT_LMP_WRAPPED, 'w') as f:
        # Use iread to prevent memory crash
        for i, frame in enumerate(iread(TRAJ_FILE)):
            cp = cell_to_cellpar(frame.cell)
            frame.set_cell(cellpar_to_cell(cp), scale_atoms=True)
            frame.wrap() # Wrap atoms into box

            c = frame.cell
            pos = frame.get_positions()
            
            f.write(f'ITEM: TIMESTEP\n{i}\nITEM: NUMBER OF ATOMS\n{len(frame)}\n')
            f.write('ITEM: BOX BOUNDS pp pp pp\n')
            f.write(f'0.000000 {c[0,0]:.6f}\n')
            f.write(f'0.000000 {c[1,1]:.6f}\n')
            f.write(f'0.000000 {c[2,2]:.6f}\n')
            
            f.write('ITEM: ATOMS id element x y z\n')
            for j, sym in enumerate(frame.get_chemical_symbols()):
                f.write(f'{j+1} {sym} {pos[j,0]:.4f} {pos[j,1]:.4f} {pos[j,2]:.4f}\n')
    print(f'Done. Saved {OUTPUT_LMP_WRAPPED}')
except Exception as e:
    print(f'Error writing wrapped lammps: {e}')


print(f'Exporting UNWRAPPED coordinates for TRAVIS')
try:
    with open(OUTPUT_LMP_UNWRAPPED, 'w') as f:
        for i, frame in enumerate(iread(TRAJ_FILE)):
            
            cp = cell_to_cellpar(frame.cell)
            frame.set_cell(cellpar_to_cell(cp), scale_atoms=True)

            # Do NOT wrap. Drift is needed for diffusion.
            pos = frame.get_positions()
            box = np.diag(frame.cell)
            symbols = frame.get_chemical_symbols()
            f.write(f'ITEM: TIMESTEP\n{i}\nITEM: NUMBER OF ATOMS\n{len(frame)}\n')
            f.write('ITEM: BOX BOUNDS pp pp pp\n')
            f.write(f'0.000000 {box[0]:.6f}\n')
            f.write(f'0.000000 {box[1]:.6f}\n')
            f.write(f'0.000000 {box[2]:.6f}\n')
            
            f.write('ITEM: ATOMS id element xu yu zu\n')
            for j, sym in enumerate(symbols):
                f.write(f'{j+1} {sym} {pos[j,0]:.4f} {pos[j,1]:.4f} {pos[j,2]:.4f}\n')

    print(f'\nSaved to {OUTPUT_LMP_UNWRAPPED}')

except Exception as e:
    print(f'\nError writing unwrapped lammps: {e}')

