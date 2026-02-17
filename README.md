# README aibn_bernhardt_group

Molecular Modelling of Proton Transport in Aqueous Electrolytes

This repository contains scripts, environment configurations, and analysis results for benchmarking four state-of-the-art Machine Learning Potentials (MLPs)—AIMNet2, MACE, Orb, and SevenNet—in modelling proton transport within aqueous electrolytes (Water/Acetic Acid/Imidazole mixtures).


### Repository Structure
/mlp_models_and_results
The core of the project, containing the implementation and data for each model.

Model Subfolders (aimnet2, mace, orb, seven_net): 
*_prod_run.py: The ASE-based production script for the Molecular Dynamics 

simulation.env_*.yml: The Conda environment file required to run the specific model.

/results: 
Organised by analysis type, timestep count, and saving interval (e.g., 09.02_200ksteps_interval10_msd). 
Analyses include:
RDF: Radial Distribution Functions to determine coordination numbers.
MSD: Mean Squared Displacement to calculate diffusion coefficients.
Bond Analysis: Covalent and Hydrogen bond lifetime analyses.

resume_interupted_prod_run.py: A robust restart script designed to truncate corrupt frames from interrupted .xyz files and resume simulations on HPC systems.

/system_creation
Contains the generation scripts used to build the initial molecular mixture (1000 Water, 100 Acetic Acid, 100 Imidazole) with specific box lengths (37.2 Å) and periodic boundary conditions.

/travis_function_analysis_plotting
Scripts used for post-processing trajectories via TRAVIS and generating the comparative plots for RDF, MSD, and bond lifetimes.



### HPC Diagnostic Scripts
Tools specifically developed for the Bunya HPC environment:
bunya_diagnostics_fairshare.sh & check_resources.sh: Scripts to monitor user fairshare, job priority, and current resource usage.
check_available_gpu.py: A Python tool to find free or under-utilised GPUs in the gpu_cuda partition to improve job backfill efficiency.



### Usage
To reproduce a simulation:
Navigate to the desired model folder in /mlp_models_and_results.
Create the environment: conda env create -f env_[model].yml.
Run the production script: python [model]_prod_run.py.
Use the restart script if the job hits a walltime limit or crashes due to memory fragmentation.

