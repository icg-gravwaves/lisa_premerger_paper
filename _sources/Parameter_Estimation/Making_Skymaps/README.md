# Generating sky maps

Generating the sky maps requires the merged result files, for details see [this section](../Running_Analyses/README.md).
Once these have been generated, the sky map files for a given injection and PSD are produced by running the following command:

```bash
python produce_skymaps.py \
  --result-dir ../Running_Analyses/results/ \
  --output-dir . \
  --injection-id <id> \
  --psd <psd> \
  --jobs 8 \
  --trials 4
```

where `<id>` and `<psd>` should be set accordingly.
`<psd>` can be one of `{optimistic, pessimistic, cut}` and `<id>` can take any number in the range `{0..4}`.

This will generate fits files (gzipped), which we have provided in the repo.

In the next notebook, we see how the skymap plots are generated.