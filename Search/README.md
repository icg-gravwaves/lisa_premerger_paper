# Searching for pre-merger signals

## Generating a template bank
In [Template Banks](Template_Banks), we provide the details on how template banks were generated, as well as the template banks themselves.

## Searching for injected signals
To search for the signals, we remove data from the end of the file, and then pre-condition the data according to the zero-phase whitening kernel.
Then for each template we:
1. calculate the SNR series by matched filtering the template with the data
2. find the maximum with a search window of the end of the data in one channel
3. find the maximum within a small coincidence window in the other channel and combine these to get a combined SNR
4. repeat steps 2 and 3 above with the channels swapped, and use whichever combined SNR is highest.

The template with the highest combined SNR over the bank is then considered *the* SNR of the signal.

Command line arguments are possible for testing, particularly 
- `--data-file-zero-noise`, which will subtract zero-noise file and calculate SNR from that - this will not affect the bank filtering
- `--plot-best-waveform` will plot the best-fitting waveform in the frequency and time domains, as well as the SNR time series for the best-fitting waveform
- `--reduce-bank-factor` will skip indices in the loop over waveforms which are not an integer multiple of this number. This is useful to run the search quickly

An example using these options is supplied as [signal_runs_test.sh](signal_runs_test.sh)

## Assessing significance
In order to assess significance, we run the search described above repeatedly over Gaussian noise and obtain a distribution, which we interpolate/extrapolate to get an estimate of the false alarm rate of the signal.

For this, we run [nosignal_runs.py](nosignal_runs.py), which repeatedly generates Gaussian data, conditions it and calculates the maximum SNR during a 