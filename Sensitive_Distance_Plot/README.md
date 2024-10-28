# Observable Distance Plot

Here we find the observable distance calculation and plotting scripts.

We produce these plots by calculating the distance at which a signal would have optimal signal-to-noise ratio of 10 for different times-before-merger and different.

## Frequency cutoff as a proxy for time-before-merger
As this figure is used in the motivation part of the paper, we do not use the novel method in Sec III for the time-before-merger cutoff in this figure.
Instead we calculate the time-frequency evolution of the waveform using pycbc's `get_inspiral_tf` function, and the `SPAtmplt` waveform; which we expect to be valid during this inspiral stage of the signal.
We interpolate the frequency for the required time-before-merger and then use this as the high-frequency cutoff in the optimal SNR calculation.

## Sky averaged observable distance
As the observable distance varies over the sky in a way, we perform this calculation at many points (our plots in the paper use 200) over the sky and average these.

To keep this averaging consistent for the different PSDs, and if we use parallelization, we use the same random seed for every mass and time point where this is calculated. As a result the sky points will remain consistent.

## How to recreate the figure

To run this, we use the command

```
python ./sensitive_time_distance.py \
  --mass-range 1e5 5e9 \
  --log-mass-spacing \
  --n-mass-points 100 \
  --n-sky-points 200 \
  --times 0 3600 43200 86400 345600 604800 1209600 \
  --psd-file \
    ../PSD_Files/model_AE_TDI1_SMOOTH_optimistic.txt.gz \
  --output-file sensitive_distance_optimistic.hdf
```
for each of the optimistic, pessimistic and cutoff PSDs.
We do not recommend running these directly on the command line, as they can take many hours.

From this the files `sensitive_time_distance_cutoff.hdf` `sensitive_time_distance_optimistic.hdf` and `sensitive_time_distance_pessimistic.hdf` are produced, which we supply as part of this data release.

To plot these, we can use the [`plot_sensitive_distance.ipynb` notebook](./plot_sensitive_distance.ipynb).
