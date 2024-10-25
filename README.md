# Premerger observation and characterization of super-massive black hole binaries

This is the data release for the paper "Premerger observation and characterization of super-massive black hole binaries", which can be found [here](https://www.youtube.com/watch?v=dQw4w9WgXcQ). We release the data behind each of the figures and the code and configuration files that were used to produce each of them. We also demonstrate the steps needed to reproduce the search and parameter estimation using our code.

As always python, software dependencies will change in the coming years, and this code may be incompatible with future releases of any dependency. This paper was generated using a fork of PyCBC at https://github.com/icg-gravwaves/pycbc/tree/lisa-pre-merger. This was forked from PyCBC at cd0e16a.

FIXME: sort a docker image somewhere (zenodo?) once code is finalised

## Reproducing our figures
Figure 2 (a and b) can be reproduced using [this ipython notebook](Sensitive_Distance_Plot/plot_sensitive_distance.ipynb)

Figures 1, 3, 4 and 5 can be reproduced using [this notebook](PSD_Files/PSD_filter_images.ipynb)

Figures 6 and 7 can be made using [this notebook](Search/plot_search_results.ipynb)

Figures 8, 9, 10, 11 .....

## Reproducing our analysis
Here we discuss each of the parts of the analysis presented in the paper, and how each part can be reproduced.

We provide (FIXME: not yet in all cases) a subset of the commands used to submit the jobs.

Our analysis was mainly performed using a combination of the [SCIAMA supercomputer](https://sciama.icg.port.ac.uk/) at the University of Portsmouth, and the [HAWK supercomputer](https://ligo.gravity.cf.ac.uk/guide/) at the University of Cardiff.

### Reproducing the analysis environment
We plan to have a docker image, but we also provide an environment file here so that if the user wants to use our work as a basis for development, that is possible.

The conda environment is defined in a [yaml file](install_reqs.yml), which can be used for the analysis:

```
conda env create -f install_reqs.yml
```

Make sure you have activated the environment using `conda activate env_lisa_premerger`


The following sections show the process we used to generate and analyse data for the Search and Parameter Estimation analyses.