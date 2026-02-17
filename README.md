# README aibn_bernhardt_group

Molecular Modelling of Proton Transport in Aqueous Electrolytes
This repository contains the scripts, environment configurations, and analysis results for benchmarking four state-of-the-art Machine Learning Potentials (MLPs): AIMNet2, MACE, Orb, and SevenNet. The project evaluates their performance in modelling proton transport within aqueous electrolytes, specifically focusing on mixtures of Water, Acetic Acid, and Imidazole.


### Repository Structure
/mlp_models_and_results\
The core of the project, containing the implementation and data for each model.

/Model Subfolders (aimnet2, mace, orb, seven_net):\
*_prod_run.py: The ASE-based production script for the Molecular Dynamics

/simulation.env_*.yml: The Conda environment file required to run the specific model.

/results:\
Organised by analysis type, timestep count, and saving interval (e.g., 09.02_200ksteps_interval10_msd).\
Analyses include:\
RDF: Radial Distribution Functions to determine coordination numbers.\
MSD: Mean Squared Displacement to calculate diffusion coefficients.\
Bond Analysis: Covalent and Hydrogen bond lifetime analyses.

resume_interupted_prod_run.py: A robust restart script designed to truncate corrupt frames from interrupted .xyz files and resume simulations on HPC systems.

/system_creation\
Contains the generation scripts used to build the initial molecular mixture (1000 Water, 100 Acetic Acid, 100 Imidazole) with specific box lengths (37.2 Å) and periodic boundary conditions.

/travis_function_analysis_plotting\
Scripts used for post-processing trajectories via TRAVIS and generating the comparative plots for RDF, MSD, and bond lifetimes.



### HPC Diagnostic Scripts
Tools specifically developed for the Bunya HPC environment:\
bunya_diagnostics_fairshare.sh & check_resources.sh: Scripts to monitor user fairshare, job priority, and current resource usage.\
check_available_gpu.py: A Python tool to find free or under-utilised GPUs in the gpu_cuda partition to improve job backfill efficiency.



### Usage
To reproduce a simulation:\
Navigate to the desired model folder in /mlp_models_and_results.\
Create the environment: conda env create -f env_[model].yml.\
Run the production script: python [model]_prod_run.py.\
Use the restart script if the job hits a walltime limit or crashes due to memory fragmentation.




Repository Structure
/mlp_models_and_results
This directory serves as the core of the project, containing the implementation details and raw data for each evaluated model.

Model Subfolders (aimnet2, mace, orb, seven_net)
Each subfolder follows a standardised structure:

[model]_prod_run.py
The ASE-based (Atomic Simulation Environment) production script used to execute the Molecular Dynamics simulations.

env_[model].yml
The Conda environment file containing the specific dependencies and versions required to run the MLP.

results/
Contains various subdirectories organised by analysis type, date, timestep count, and saving interval. Examples include:

05.02_200ksteps_interval10_hbond_bond_analysis

05.02_200ksteps_interval10_rdf

09.02_200ksteps_interval10_msd

200ksteps_interval10_covalent_bond_analysis

Support Scripts
resume_interupted_prod_run.py
A utility script designed for HPC environments. It includes a repair function that scans .xyz files for corrupt or half-written frames caused by job timeouts or crashes. It truncates the file to the last valid frame before resuming the simulation to ensure data integrity.

/system_creation
This directory contains the scripts used to generate the initial simulation box.

The system consists of 1200 molecules in total.

The simulation box is defined with a length of 37.2 Å.

Periodic boundary conditions (PBC) are applied to simulate a bulk liquid environment.

/travis_function_analysis_plotting
This directory contains scripts for post-processing and visualising the simulation data.

Trajectory Analysis: Utilises TRAVIS (Trajectory Analyser and Visualiser) to process raw .xyz files.

Post-processing: Scripts to convert trajectory data into LAMMPS unwrapped formats for further analysis.

Visualisation: Python-based plotting scripts for generating Radial Distribution Function (RDF), Mean Squared Displacement (MSD), and bond survival probability graphs.

HPC Diagnostic Scripts
A collection of tools specifically developed to optimise workflow and resource management on the Bunya HPC cluster:

bunya_diagnostics_fairshare.sh
Monitors user fairshare and job priority to estimate wait times.

check_resources.sh
Reports current CPU, memory, and disk quota usage.

check_available_gpu.py
A Python-based tool that queries the gpu_cuda partition to identify free or under-utilised GPUs, assisting in manual job backfilling.
