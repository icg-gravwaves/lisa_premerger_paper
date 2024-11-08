# Running analyses

To run the analyses, we use [PyCBC Inference](https://pycbc.org/pycbc/latest/html/inference.html). This should be run for each injection and time IDs.

For example, we set environment variables:
- INJ_ID to the injection we want
- TIME_ID to the time we are considering (see the following table)
- PSD to `cut`, `optimistic` or `pessimistic` depending on the PSD we want
- CONFIG_PATH to point to the [configs subdirectory](Config_Files) located in this repo.
- OUTDIR to be the output directory for this specific analysis, we suggest `outdir_injection${INJ_ID}_time${TIME_ID}_${PSD}_psd`

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

For use downstream, we want the results files to be merged. To do this, we run

```bash
python merge_results.py --result-mapping results.yml --output-dir results/
```

> ⚠️ The [results yaml](results.yml) provided is a guide, please update it to use your configurations.

We have provided the merged files in the repo.