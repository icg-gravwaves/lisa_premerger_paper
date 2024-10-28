# Generating sky maps

PAGE UNDER CONSTRUCTION


> 📝 The sky maps are generated using a different environment that is specified in `skymap_env.yml`. Once installed, this can be activated using `conda activate pycbc-pre-merger-skymap`. See the [conda documentation](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-from-an-environment-yml-file) for how to create a conda environment from a YAML file.

Generating the sky maps requires the merged result files, for details see [this section](#producing-merged-result-files).
Once these have been generated, the sky map files for a given injection and PSD are produced by running the following command:

```bash
python produce_skymaps.py \
  --result-dir ../Running_Analyses/results/ \
  --output-dir results/ \
  -injection-id <id> \
  --psd <psd> \
  --jobs 8 \
  --trials 4
```

where `<id>` and `<psd>` should be set accordingly.
`<psd>` can be one of `{optimistic, pessimistic, cut}` and `<id>` can take any number in the range `{0..4}`.
