set -e

python ./model_psds.py \
    --tdi-generation $tdi_gen

python ./model_psds.py \
    --tdi-generation $tdi_gen \
    --low-freq-relaxation

for fileout in `ls model_*_TDI*_*imistic.txt` ; do
  gzip -f $fileout
done

