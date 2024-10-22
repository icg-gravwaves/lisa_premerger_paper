# Searching for pre-merger signals

## Generating a template bank
In [Template Banks](Template_Banks/README.md), we provide the details on how template banks were generated, as well as the template banks themselves.

## Searching for injected signals
In [Signal_Runs](Signal_Runs/README.md), we describe how to 

## Assessing significance
In order to assess significance, we run the search described above repeatedly over Gaussian noise and obtain a distribution, which we interpolate/extrapolate to get an estimate of the false alarm rate of the signal.

This is described in [Significance_Runs](Significance_Runs/README.md).

## Collecting results

To collect results in order to plot the results in Figure 6, run the following:

```
for psd_type in optimistic cutoff pessimistic ; do
  python collect_bank_search_results.py \
    --output-file \
      search_run_${psd_type}.json \
    --data-run-log-files \
      Signal_Runs/output/search_run_${psd_type}_*.out \
    --nosignal-run-log-files \
      Significance_Runs/output/nosignal_run_${psd_type}_*.out \
    --optimal-snr-files \
      Optimal_SNR/output/optimal_snr_${psd_type}_*.out \

done

```