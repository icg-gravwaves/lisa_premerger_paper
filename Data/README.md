# Data for Search and Parameter Estimation

We supply the data here which was used for search and parameter estimation analyses.

Data is generated using `generate_data.py` with different arguments.

## Generating data
For convenience, the `Makefile` in this directory contains rules to generate the three sets of data used in the paper:

- `optimistic`: optimistic PSD
- `pessimistic`: pessimistic PSD
- `cut`: optimistic PSD with a cut at `1e-4`

In all three cases, zero noise data is also generated.

The shared settings are defined in `base_data.ini`.

Run `python generate_data.py --help` to see configuration options.

> :warning: Different versions of `numpy` may provide different states to the random number generator [as detailed here](https://numpy.org/neps/nep-0019-rng-policy.html), even with the same seed. As a result, you may see slightly different results if generating your own files.

**Example usage**

Run `make optimistic` and data will generated in `data_optimistic_psd`, run `make generate_data` or just `make` to generate all the data.
