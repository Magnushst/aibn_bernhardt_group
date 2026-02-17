# README: aibn_bernhardt_group

## Molecular Modelling of Proton Transport in Aqueous Electrolytes

This repository contains scripts, environment configurations, and analysis results for benchmarking four state-of-the-art Machine Learning Potentials (MLPs) — AIMNet2, MACE, Orb, and SevenNet. 

The project focuses on modelling proton transport within aqueous electrolytes, specifically investigating a mixture consisting of 1000 Water, 100 Acetic Acid, and 100 Imidazole molecules. The primary objective is to evaluate how diverse architectural approaches to atomic interactions (such as local vs. non-local message passing and explicit vs. implicit charge modelling) affect the prediction of chemical reactivity and physical transport dynamics.

---

## Repository Structure

### /mlp_models_and_results
This directory serves as the core of the project, containing the implementation details, environments, and raw data for each evaluated MLP.

* **Model Subfolders (`/aimnet2`, `/mace`, `/orb`, `/seven_net`):** \
  Each model has its own dedicated directory containing the following standard structure:
  * `[model]_prod_run.py`: The ASE-based (Atomic Simulation Environment) production script used to execute the Molecular Dynamics simulations.
  * `env_[model].yml`: The Conda environment file containing the specific dependencies and versions required to run that specific MLP.
  * `/results`: A sub-directory containing the output data, organised by analysis type, date, timestep count, and saving interval. Examples include:
    * `05.02_200ksteps_interval10_hbond_bond_analysis`
    * `05.02_200ksteps_interval10_rdf`
    * `09.02_200ksteps_interval10_msd`
    * `200ksteps_interval10_covalent_bond_analysis`

* **resume_interupted_prod_run.py:**
  A robust utility script designed for High-Performance Computing (HPC) environments. It includes a repair function that scans `.xyz` trajectory files for corrupt or half-written frames (often caused by job timeouts or walltime limits), truncates the file to the last valid frame, and safely resumes the simulation.

### /system_creation \
This directory contains the Python scripts used to generate the initial simulation box.
* Builds the molecular mixture (1000 Water, 100 Acetic Acid, 100 Imidazole).
* Configures the simulation box with a specified length of 37.2 Å.
* Applies Periodic Boundary Conditions (PBC) to simulate a continuous bulk liquid environment.

### /travis_function_analysis_plotting
This directory contains all scripts required for post-processing and visualising the simulation data.
* Scripts to interface with TRAVIS (Trajectory Analyser and Visualiser) to process raw `.xyz` files.
* Python plotting scripts to generate comparative graphs for:
  * Radial Distribution Functions (RDF) to determine coordination numbers.
  * Mean Squared Displacement (MSD) to calculate diffusion coefficients.
  * Hydrogen and Covalent bond lifetime probability analyses.

---

## HPC Diagnostic Scripts

A collection of Bash and Python scripts specifically developed to optimise workflow, resource management, and job backfilling on the Bunya HPC cluster.

* **`bunya_diagnostics_fairshare.sh`:** \
  Monitors user fairshare metrics and job priority to help estimate scheduler wait times.
* **`check_resources.sh`:** \
  Reports the current CPU, memory, and disk quota usage for the user.
