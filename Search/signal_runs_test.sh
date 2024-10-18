#!/bin/bash

injection_number=2
time_before=14
psd=pessimistic
data_dir=data_pessimistic_psd
# f_lower should be 1e-4 for cutoff, 1e-6 for pessimistic or optimistic
f_lower=1e-6

shared_args="""
  --injections-file \
    ../Injections/injections.json \
  --injection-number \
    $injection_number \
  --days-before-merger \
    $time_before \
  --reduce-bank-factor 25 \
  --plot-best-waveform \
"""
data_file_dir=../Data/data_files/${data_dir}

python ./data_runs.py \
  $shared_args \
  --psd-file \
    ../PSD_Files/model_AE_TDI1_SMOOTH_${psd}.txt \
  --label ${psd} \
  --f-lower ${f_lower} \
  --bank-file \
    ../Template_Banks/lisa_ew_${time_before}_day_${psd}.hdf \
  --data-file \
    $data_file_dir/signal_${injection_number}.hdf \
  --data-file-zero-noise \
    $data_file_dir/signal_zero_noise_${injection_number}.hdf