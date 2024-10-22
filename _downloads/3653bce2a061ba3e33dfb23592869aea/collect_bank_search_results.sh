for psd_type in optimistic cutoff pessimistic ; do
  python collect_bank_search_results.py \
    --output-file \
      search_run_${psd_type}.json \
    --data-run-log-files \
      output/search_run_${psd_type}_*.out \
    --nosignal-run-log-files \
      output/nosignal_run_${psd_type}_*.out \
    --optimal-snr-files \
      Optimal_SNR/output/optimal_snr_${psd_type}_*.out \

done
