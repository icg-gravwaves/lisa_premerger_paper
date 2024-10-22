# Generating the PSD files used in our analyses

In order to demonstrate the different performance of the search under different assumptions about the low-frequency performance of the detector, we perform our analyses on three different PSD models.

These PSDs have optimistic, pessimistic, and no performance below $10^{-4}$ Hz respectively

We show here how the PSDs for these models are generated.

## Running the model PSD generation scripts

To run the model PSD generation, we run the following:

```
python ./model_psds.py \
    --tdi-generation 1

python ./model_psds.py \
    --tdi-generation 1 \
    --low-freq-relaxation
```

We zip the files for adding to the repository

## Plotting the PSDs and applying conditioning

In [the python notebook](PSD_filter_images), we plot the PSDs, and show the conditioning we need to apply to turn them into the zero-phase whitening kernel.