set -e

for psd in CUT_optimistic optimistic pessimistic ; do
  for injection_number in {0..4} ; do

  if [ $psd == CUT_optimistic ]  ; then
    f_lower_search=1e-4
  else
    f_lower_search=1e-6
  fi

  shared_args="""
      --injections-file \
      ../../Injections/injections.json \
    --injection-number $injection_number \
    --psd-files \
      ../../PSD_Files/model_AE_TDI1_SMOOTH_${psd}.txt \
    --days-before-merger 0.5 1 4 7 14 \
    --f-lower-search \
      $f_lower_search \
    --label $psd
  """

  python optimal_snr.py \
    $shared_args > output/optimal_snr_${psd}_${injection_number}.out

  done
done
