# Assessing significance
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
    ../Data/injections.json \
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