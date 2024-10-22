# Searching for pre-merger signals

## Generating a template bank
In [Template Banks](Template_Banks/README.md), we provide the details on how template banks were generated, as well as the template banks themselves.

## Searching for injected signals
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
  --data-file-zero-noise \
    $data_file_dir/signal_zero_noise_${injection_number}.hdf
```

## Assessing significance
In order to assess significance, we run the search described above repeatedly over Gaussian noise and obtain a distribution, which we interpolate/extrapolate to get an estimate of the false alarm rate of the signal.

For this, we run [nosignal_runs.py](nosignal_runs.py), which repeatedly generates Gaussian data, conditions it and calculates the maximum SNR from a template bank analysis as described above.

An example of running this is given below:

```
injection_number=4
time_before=7
label=pessimistic
f_lower=1e-6

python ./nosignal_runs.py \
  --injections-file \
    ../Injections/injections.json \
  --days-before-merger \
    $time_before \
  --psd-file \
    ../PSD_Files/model_AE_TDI1_SMOOTH_${label}.txt \
  --label ${label} \
  --f-lower ${f_lower} \
  --repeats 15 \
  --bank-file \
    Template_Banks/lisa_ew_${time_before}_day_${label}.hdf \
```

Similarly to `signal_runs.py`, it is possible to supply testing options `--reduce-bank-factor` and `--plot-best-waveform`.

For the paper, we used `--repeats 200` - this code then takes a long time, so using a job scheduler is recommended.

Again, the stdout should be redirected to a text file, we recommend `output/nosignal_run_${label}_${time_before}_${injection_number}.out`

## Collecting results

To collect results in order to plot the results in Figure 6, run the following:

```
for psd_type in optimistic cutoff pessimistic ; do
  python collect_bank_search_results.py \
    --output-file \
      search_run_${psd_type}.json \
    --data-run-log-files \
      output/search_run_${psd_type}_*.out \
    --nosignal-run-log-files \
      output/nosignal_run_${psd_type}_*.out \
    --optimal-snr-files \
      Optimal_SNR/output/optimal_snr_${psd_type}_*.out \

done

```