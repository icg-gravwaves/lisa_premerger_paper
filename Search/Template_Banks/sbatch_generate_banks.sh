#!/bin/bash

# Configure the resources needed to run my job, e.g.

# job name (default: name of script file)
#SBATCH --job-name=lisa_premerger_bank
# resource limits: cores, max. wall clock time during which job can be running
# and maximum memory (RAM) the job needs during run time:
#SBATCH --ntasks=3
#SBATCH --time=48:00:00
#SBATCH --mem=16G
# This array is used for setting the different
# times-before-merger
#SBATCH --array=0-4
# define log files for output on stdout and stderr
#SBATCH --output=output/generate_template_banks_all_out
#SBATCH --error=output/generate_template_banks_all_err
# choose system/queue for job submission
#SBATCH --partition=sciama2.q
#SBATCH --cpus-per-task 4

# set up the software environment to run your job in ; this will
# change depending on your setup

shared_args="""    --verbose \
    --minimal-match 0.97 \
    --tolerance .05 \
    --buffer-length 2592000 \
    --sample-rate .2 \
    --approximant BBHX_PhenomD \
    --tau0-threshold 100000 \
    --tau0-crawl 20000000 \
    --tau0-start 0 \
    --tau0-end  20000000 \
    --tau0-cutoff-frequency 0.0001 \
    --input-config config.ini \
    --seed 1 \
"""

times_before=(0.5 1 4 7 14)
# Note that here we have used the slurm array to
# parallelize the jobs
time_before=${times_before[$SLURM_ARRAY_TASK_ID]}
# We could further parallelize using slurm over the
# different PSDs, but this was sufficient on our cluster 

for type in optimistic pessimistic CUT_optimistic ; do

  echo "$time_before days before merger"
  srun ./pycbc_brute_bank \
    $shared_args \
    --output-file lisa_ew_${time_before}_day_${type}.hdf \
    --time-before `echo "60 * 60 * 24 * $time_before" | bc` \
    --psd-file ../../PSD_Files/model_AE_TDI1_SMOOTH_${type}.txt.gz \
    --low-frequency-cutoff .000001
done

