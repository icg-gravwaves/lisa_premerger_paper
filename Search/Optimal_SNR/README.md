# Optimal SNR calculation

To calculate the expected SNR for a particular signal without worry about particular noise realisations, we calculate the optimal SNR.

The optimal SNR is the matched filter of the signal with itself, i.e. what would we expect from a perfectly matching template (optimal) in typical noise.

$$
\rho_{opt} = 4 \int_{f_{min}}^\infty \frac{|\tilde{h}(f)|^2}{S_n(f)} \textrm{d} f
$$

Where $\tilde{h}(f)$ is the signal, $S_n(f)$ is the single-sided noise density, and $f_{min}$ is the start frequency we consider. For the optimistic and pessimistic PSDs, we use $f_{min}=10^{-6}$ Hz, and for the cutoff PSD we use $f_{min}=10^{-4}$ Hz.

## Calculation process
We provide the code [optimal_snr.py](optimal_snr.py) to perform the calculation, the command to run this is.
```
for psd in CUT_optimistic optimistic pessimistic ; do
  for injection_number in {0..4} ; do

  if [ $psd == CUT_optimistic ]  ; then
    f_lower_search=1e-4
  else
    f_lower_search=1e-6
  fi

  python optimal_snr.py \
      --injections-file \
      ../../Data/injections.json \
    --injection-number $injection_number \
    --psd-files \
      ../../PSD_Files/model_AE_TDI1_SMOOTH_${psd}.txt \
    --days-before-merger 0.5 1 4 7 14 \
    --f-lower-search \
      $f_lower_search \
    --label $psd

  done
done
```

To store results, we redirect stdout to text files (not given in this repo) called `output/optimal_snr_${psd}_${injection_number}.out`, and these are collated into search results files using the collect_bank_results [python code](../collect_bank_search_results.py) and to produce json files for each PSD (e.g. [search_run_cutoff.json](../search_run_cutoff.json))

## Plotting
To plot the optimal SNR (as well as other analysis results), [this notebook](../plot_search_results.ipynb) shows how the plot for Figure 6 of the paper is made.