# Template banks generation

For generating the banks, we use a stochastic placement algorithm.

## Modifying `pycbc_brute_bank`
The stochastic placement code is in `pycbc_brute_bank`; as this code is designed for ground-based detectors with a single detector or averaged PSD, we use [a modified version](./pycbc_brute_bank) in order to use multiple channels.

The primary modification to this code is that we calculate the match as the sum of squares of matches in each of the A and E channels, weighted by the sensitive distance of the waveforms in each channel.

$$
m  = \sqrt{\frac{m_A^2 \sigma_A^2 + m_E^2 \sigma_E^2}{\sigma_A^2 + \sigma_E^2}}
$$

## Generating the template banks
We provide [the slurm batch script](./sbatch_generate_banks.sh) used to generate the banks using `pycbc_brute_bank`.

Note that the software environment will need to be set up within this batch script, but will depend on your environment setup and location

This script can easily be adapted to *not* use a scheduling manager