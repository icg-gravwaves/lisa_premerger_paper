set -e

# This is a shell script to run the calculation which goes into
# the plot for sensitive distance as a function of mass given
# time-before-merger and different PSDs

# Note that if you want to parallelize this calculation, it is
# possible using the --parallelize-range argument to
# sensitive_time_distance.py, and then recombining the output
# ready for the plotting notebook, but we do not do so here.

shared_args="""
  --mass-range 1e5 5e9 \
  --log-mass-spacing \
  --n-mass-points 100 \
  --n-sky-points 200 \
  --times 0 3600 43200 86400 345600 604800 1209600 \
"""

python ./sensitive_time_distance.py \
  $shared_args \
  --psd-file \
    ../PSD_Files/model_AE_TDI1_SMOOTH_optimistic.txt.gz \
  --output-file sensitive_distance_optimistic.hdf

python ./sensitive_time_distance.py \
  $shared_args \
  --psd-file \
    ../PSD_Files/model_AE_TDI1_SMOOTH_CUT_optimistic.txt.gz \
  --output-file sensitive_distance_cutoff.hdf

python ./sensitive_time_distance.py \
  $shared_args \
  --psd-file \
    ../PSD_Files/model_AE_TDI1_SMOOTH_pessimistic.txt.gz \
  --output-file sensitive_distance_pessimistic.hdf
