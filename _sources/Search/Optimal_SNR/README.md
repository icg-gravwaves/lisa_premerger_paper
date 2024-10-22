# Optimal SNR calculation

To calculate the expected SNR for a particular signal without worry about particular noise realisations, we calculate the optimal SNR.

The optimal SNR is the matched filter of the signal with itself, i.e. what would we expect from a perfectly matching template (optimal) in typical noise.

$$
\rho_{opt} = 4 \int_{f_{min}}^\infty \frac{|\tilde{h}(f)|^2}{S_n(f)} \textrm{d} f
$$

Where $\tilde{h}(f)$ is the signal, $S_n(f)$ is the single-sided noise density, and $f_{min}$ is the start frequency we consider. For the optimistic and pessimistic PSDs, we use $f_{min}=10^{-6}$ Hz, and for the cutoff PSD we use $f_{min}=10^{-4}$ Hz.

## Calculation process
We provide the code [optimal_snr.py](optimal_snr.py) to perform the calculation, and call this using [optimal_snr.sh](optimal_snr.sh). The results are stored as text files (not given), and these are collated into search results files using the collect_bank_results [python code](../collect_bank_search_results.py) and [shell scipt](../collect_bank_search_results.sh) to produce json files for each PSD (e.g. [search_run_cutoff.json](../search_run_cutoff.json))

## Plotting
To plot the optimal SNR (as well as the data file analysis results), [this notebook](plot_optimal_snr.ipynb) shows how the plot for Figure 6 of the paper is made.