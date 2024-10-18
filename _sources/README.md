# Premerger observation and characterization of super-massive black hole binaries

This is the data release for the paper "Premerger observation and characterization of super-massive black hole binaries", which can be found [here](https://www.youtube.com/watch?v=dQw4w9WgXcQ). We release the data behind each of the figures and the code and configuration files that were used to produce each of them. We also demonstrate the steps needed to reproduce the search and parameter estimation using our code.

As always python, software dependencies will change in the coming years, and this code may be incompatible with future releases of any dependency. This paper was generated using a fork of PyCBC at https://github.com/icg-gravwaves/pycbc/tree/lisa-pre-merger. This was forked from PyCBC at cd0e16a.

FIXME: sort a docker image somewhere (zenodo?) once code is finalised

## Reproducing our figures
Figure 2 (a and b) can be reproduced using [this ipython notebook](./Sensitive_Distance_Plot/plot_sensitive_distance.html)

Figures 1, 3, 4 and 5 can be reproduced using [this notebook](./PSD_files/PSD_filter_images.html)

Figures 6, 7, 8, 9, 10, 11 .....

## Reproducing our analysis
Here we discuss each of the parts of the analysis presented in the paper, and how each part can be reproduced.

### Reproducing the analysis environment
We plan to have a docker image, but we also provide instructions here so that if the user wants to use our work as a basis for development, that is possible

We have provided a [yaml file](./install_reqs.yml), which can be used to create a conda environment for the analysis:

```
conda env create -f install_reqs.yml
```

Make sure you have activated the environment using `conda activate env_lisa_premerger`

This will use the latest possible version of PyCBC, however we need some changes to to main code. So we will install a particular version of PyCBC. To get this, run

```
git clone git@github.com:icg-gravwaves/pycbc.git
cd pycbc
git branch lisa-pre-merger
pip install .
```
## Generating supplied files with injections
The search and parameter estimation are run on the same files to ensure consistency.
In order to generate these files, we use the process detailed in [Data](./Data).

## Searching for SMBHB signals pre-merger
In [Search](./Search)

### Generating the template bank
The bank generation is detailed in [Template Banks](.Search/Template_Banks)



### Running searches on generated noise without injections

### Running parameter estimation on injections
