# Searching for injected signals
To search for the signals, we remove data from the end of the file, and then pre-condition the data according to the zero-phase whitening kernel.
Then for each template we:
1. calculate the SNR series by matched filtering the template with the data
2. find the maximum with a search window of the end of the data in one channel
3. find the maximum within a small coincidence window in the other channel and combine these to get a combined SNR
4. repeat steps 2 and 3 above with the channels swapped, and use whichever combined SNR is highest.

The template with the highest combined SNR over the bank is then considered *the* SNR of the signal.

This is done in [signal_runs.py](signal_runs.py).

Command line arguments are possible for testing, particularly 
- `--data-file-zero-noise`, which will subtract zero-noise file and calculate SNR from that - this will not affect the bank filtering
- `--plot-best-waveform` will plot the best-fitting waveform in the frequency and time domains, as well as the SNR time series for the best-fitting waveform
- `--reduce-bank-factor` will skip indices in the loop over waveforms which are not an integer multiple of this number. This is useful to run the search quickly

To run the data file analyses, the following command is used

For saving results for later use, redirect the stdout to a text file. Suggested filename is `output/search_run_${psd}_${injection_number}_${time_before}.out`.

```
injection_number=2
time_before=14
psd=pessimistic
data_dir=data_pessimistic_psd
# f_lower should be 1e-4 for cutoff, 1e-6 for pessimistic or optimistic
f_lower=1e-6

data_file_dir=../Data/data_files/${data_dir}

python ./data_runs.py \
  --injections-file \
    ../Injections/injections.json \
  --injection-number \
    $injection_number \
  --days-before-merger \
    $time_before \
  --psd-file \
    ../PSD_Files/model_AE_TDI1_SMOOTH_${psd}.txt \
  --label ${psd} \
  --f-lower ${f_lower} \
  --bank-file \
    ../Template_Banks/lisa_ew_${time_before}_day_${psd}.hdf \
  --data-file \
    $data_file_dir/signal_${injection_number}.hdf \
```

The stdout should be redirected to a text file, we recommend `output/signal_run_${psd}_${time_before}_${injection_number}.out`