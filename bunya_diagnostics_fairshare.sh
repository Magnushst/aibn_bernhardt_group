#!/bin/bash

# ==========================================
# Bunya User Diagnostic Script
# ==========================================
USER=$(whoami)
echo "------------------------------------------------"
echo " DIAGNOSTIC REPORT FOR: $USER"
echo " Date: $(date)"
echo "------------------------------------------------"

# 1. STORAGE QUOTAS (Specific to Bunya)
echo -e "\n[1] STORAGE QUOTAS (Home & Scratch)"
if command -v rquota &> /dev/null; then
    rquota
else
    echo " 'rquota' command not found. Using standard quota check:"
    /usr/lpp/mmfs/bin/mmlsquota -u $USER --block-size auto
fi

# 2. CURRENT JOBS & PENDING REASONS
echo -e "\n[2] ACTIVE JOBS"
echo "ID        PARTITION    NAME        STATUS   TIME    NODES   REASON"
squeue -u $USER -o "%.10i %.10P %.12j %.8T %.8M %.6D %R"

echo -e "\n[3] WHY ARE MY JOBS PENDING?"
# Loop through pending jobs to get detailed reasons
PENDING_JOBS=$(squeue -u $USER --state=PD -h -o %i)

if [ -z "$PENDING_JOBS" ]; then
    echo "  > You have no pending jobs."
else
    for job in $PENDING_JOBS; do
        echo "  > Job $job:"
        # Extract the exact reason from scontrol
        REASON=$(scontrol show job $job | grep -o "Reason=.*" | cut -d ' ' -f 1)
        echo "    $REASON"

        # Check for QOS limits (MaxCPUs, MaxJobs, etc.)
        if [[ "$REASON" == *"QOS"* ]] || [[ "$REASON" == *"Assoc"* ]]; then
             echo "    (!) You hit a usage limit. Check 'QOS Configuration' below."
        fi

        # Check for Partition availability
        PARTITION=$(scontrol show job $job | grep -o "Partition=.*" | cut -d ' ' -f 1 | cut -d= -f2)
        echo "    Partition: $PARTITION"
    done
fi

# 3. FAIRSHARE SCORE (Priority)
echo -e "\n[4] FAIRSHARE SCORE (Priority)"
echo "  > A score of 1.0 is high. A score near 0.0 means you have used a lot recently."
sshare -U $USER -o User,Account,RawShares,NormShares,FairShare

# 4. PARTITION STATUS (Node Availability)
echo -e "\n[5] PARTITION AVAILABILITY (Idle GPUs/Nodes)"
# Shows idle nodes in GPU partitions
sinfo -p gpu_cuda -o "%15P %10a %12l %10D %6t %10N" | head -n 1
sinfo -p gpu_cuda -o "%15P %10a %12l %10D %6t %10N" | grep "idle"

echo -e "\n------------------------------------------------"
echo "Done."

