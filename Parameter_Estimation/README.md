# Parameter Estimation

This directory contains an example parameter estimation configuration.

## Configs

General configs for the runs are stored in `configs`

### Generating ini files for each analysis

The ini files for each injection can be generated using the `Makefile` in configs.

```bash
make create_ini_files
```

> 📝 This will not overwrite existing files. You can run `make clean_ini_files` to remove the existing files.

> ⚠️ This randomly sets the observing time such that the merger will be between 12 and 24 hours before the end of data. This is seeded but different numpy versions may result in different times. The final ini files will be uploaded to ensure the results can be reproduced.

## Running analyses

To run the analyses, we use [PyCBC Inference](https://pycbc.org/pycbc/latest/html/inference.html). This should be run for each injection and time IDs.

For example, we set environment variables:
- INJ_ID to the injection we want
- TIME_ID to the time we are considering (see the following table)
- PSD to `cut`, `optimistic` or `pessimistic` depending on the PSD we want
- CONFIG_PATH to point to the [configs subdirectory](configs) located in Parameter_Estimation in this repo.
- OUTDIR to be the output directory for this specific analysis, we suggest `analyses/outdir_injection${INJ_ID}_time${TIME_ID}_${PSD}_psd`

| Time ID | Time before merger (days) |
| --- | --- |
| 1 | 14 |
| 2 | 7 |
| 3 | 4 |
| 4 | 1 |
| 5 | 0.5 |

```
pycbc_inference \
  --config-files \
    ${CONFIG_PATH}/injections/${PSD}_psd/injection${INJ_ID}.ini \
    ${CONFIG_PATH}/model.ini \
    ${CONFIG_PATH}/PhenomHM.ini \
    ${CONFIG_PATH}/nessai_mcmc.ini \
    ${CONFIG_PATH}/time${TIME_ID}.ini \
    ${CONFIG_PATH}/injection${INJ_ID}_priors.ini \
  --output-file ${OUTDIR}/nessai_PhenomHM.hdf \
  --nprocesses 64 \
  --force \
  --verbose
```

> 📝 Some options may need tweaking based on your computing setup, particularly `--nprocesses`

## Conventions

We use the convention that the mass ratio is defined to be less than one, such that `q=m2/m1`. This is different to the default in PyCBC Inference and, as such, the parameter is labelled `mass_ratio` rather than `q` in the config files.

## Producing merged result files

```bash
python merge_results.py --result-mapping results.yml --output-dir analyses/
```

## Generating sky maps

> 📝 The sky maps are generated using a different environment that is specified in `skymap_env.yml`. Once installed, this can be activated using `conda activate pycbc-pre-merger-skymap`. See the [conda documentation](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-from-an-environment-yml-file) for how to create a conda environment from a YAML file.

Generating the sky maps requires the merged result files, for details see [this section](#producing-merged-result-files).
Once these have been generated, the sky map files for a given injection and PSD are produced by running the following command:

```bash
python produce_skymaps.py --result-dir results/ --output-dir results/skymaps/ --injection-id <id> --psd <psd> --jobs 8 --trials 4
```

where `<id>` and `<psd>` should be set accordingly.

**Note:** this will sky runs with existing sky maps.

Alternatively, the `iterate_skymaps.sh` script can be used to iterate over all the results for a single PSD:

```bash
bash iterate_skymaps.sh <psd>
```

where `<psd>` can be one of `{optimistic, pessimistic, cut}`.
