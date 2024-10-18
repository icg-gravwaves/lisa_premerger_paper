# Generating the PSD files used in our analyses

In order to demonstrate the different performance of the search under different assumptions about the low-frequency performance of the detector, we perform our analyses on three different PSD models.

These PSDs have optimistic, pessimistic, and no performance below $10^{-4}$ Hz respectively

We show here how the PSDs for these models are generated.

In [the python notebook](PSD_filter_images.ipynb), we plot the PSDs, and show the conditioning we need to apply to turn them into the zero-phase whitening kernel.