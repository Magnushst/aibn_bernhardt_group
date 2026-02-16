#!/bin/bash
#SBATCH --job-name=travis
#SBATCH --output=travis_%j.out
#SBATCH --error=travis_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=48G
#SBATCH --time=02:00:00
#SBATCH --account=a_bernhardt
#SBATCH --partition=general

export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK

module load gcc
export PATH=$PATH:$(pwd)/exe
travis -p aimnet2_analysis_unwrapped_v6_200k_interval_10.lmp -i input_tr.txt

echo "Job completed."

