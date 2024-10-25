# Data for Search and Parameter Estimation

We supply the data here which was used for search and parameter estimation analyses.

## Injections

We set the injections according to the desired behaviour of the signals.

We see in the [notebook](make_injections.ipynb), that the masses, spins, time offset from merger to the end of the data, and distance are set manually.

All other parameters are set randomly according to the distributions defined in Table I of the paper.

## Generating data
Data is generated using `generate_data.py` with different arguments.

For convenience, the `Makefile` in this directory contains rules to generate the three sets of data used in the paper:

- `optimistic`: optimistic PSD
- `pessimistic`: pessimistic PSD
- `cut`: optimistic PSD with a cut at `1e-4`

In all three cases, zero noise data is also generated.

The shared settings are defined in `base_data.ini`.

Run `python generate_data.py --help` to see configuration options.

> ⚠️ Different versions of `numpy` may provide different states to the random number generator [as detailed here](https://numpy.org/neps/nep-0019-rng-policy.html), even with the same seed. As a result, you may see slightly different results if generating your own files.

**Example usage**

Run `make optimistic` and data will generated in `data_optimistic_psd`, run `make generate_data` or just `make` to generate all the data.
