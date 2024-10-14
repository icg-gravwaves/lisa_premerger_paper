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
As the first part of generating this figure, the `sensitive_time_distance.sh` script supplied was run on the [SCIAMA supercomputer](https://sciama.icg.port.ac.uk/). This was slightly modified for use with the Slurm workload manager. From this the files `sensitive_time_distance_cutoff.hdf` `sensitive_time_distance_optimistic.hdf` and `sensitive_time_distance_pessimistic.hdf` are produced.

To plot these, we can use the `plot_sensitive_distance.ipynb` notebook.
In the notebook, the boolean flag `source_frame_masses` is set, which can be utilised to generate Figure 2a or 2b.