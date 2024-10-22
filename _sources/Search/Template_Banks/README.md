# Template banks generation

For generating the banks, we use a stochastic placement algorithm.

## Modifying `pycbc_brute_bank`
The stochastic placement code is in `pycbc_brute_bank`; as this code is designed for ground-based detectors with a single detector or averaged PSD, we use [a modified version](./pycbc_brute_bank) in order to use multiple channels.

The primary modification to this code is that we calculate the match as the sum of squares of matches in each of the A and E channels, weighted by the sensitive distance of the waveforms in each channel.

$$
m  = \sqrt{\frac{m_A^2 \sigma_A^2 + m_E^2 \sigma_E^2}{\sigma_A^2 + \sigma_E^2}}
$$

## Generating the template banks

To generate the banks, we use the following command.

```
for time_before in 0.5 1 4 7 14 ; do
  for type in optimistic pessimistic CUT_optimistic ; do

    echo "$time_before days before merger, $type psd"
    ./pycbc_brute_bank \
      --verbose \
      --minimal-match 0.97 \
      --tolerance .05 \
      --buffer-length 2592000 \
      --sample-rate .2 \
      --approximant BBHX_PhenomD \
      --tau0-threshold 100000 \
      --tau0-crawl 20000000 \
      --tau0-start 0 \
      --tau0-end  20000000 \
      --tau0-cutoff-frequency 0.0001 \
      --input-config config.ini \
      --seed 1 \
      --output-file lisa_ew_${time_before}_day_${type}.hdf \
      --time-before `echo "60 * 60 * 24 * $time_before" | bc` \
      --psd-file ../../PSD_Files/model_AE_TDI1_SMOOTH_${type}.txt.gz \
      --low-frequency-cutoff .000001
    done
done
```

We split this using a scheduler, but the script runs relatively quickly, so this is not necessarily needed.