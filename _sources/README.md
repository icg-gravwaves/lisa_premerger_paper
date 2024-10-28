# Premerger Observation and Characterization of Super-Massive Black Hole Binaries

This is the data release for the paper "Premerger observation and characterization of super-massive black hole binaries", which can be found [here](https://www.youtube.com/watch?v=dQw4w9WgXcQ). We release the data behind each of the figures and the code and configuration files that were used to produce each of them. We also demonstrate the steps needed to reproduce the search and parameter estimation using our code.

FIXME: sort a docker image somewhere (zenodo?) once code is finalised

## Reproducing our analysis
In the data release, we discuss the different parts of the analysis and how they were performed

We provide an outline of the commands used to submit the jobs.
Exact commands are not given as these will depend on your computing setup.

Our analysis was mainly performed using a combination of the [SCIAMA supercomputer](https://sciama.icg.port.ac.uk/) at the University of Portsmouth, and the [HAWK supercomputer](https://ligo.gravity.cf.ac.uk/guide/) at the University of Cardiff.

### Reproducing the analysis environment
As always with python, software dependencies will change in the coming years, and this code may be incompatible with future releases of any dependency.

This paper was generated using a fork of PyCBC at https://github.com/icg-gravwaves/pycbc/tree/lisa-pre-merger. This was forked from PyCBC at cd0e16a.

We plan to have a docker image, but we also provide an environment file here so that if the user wants to use our work as a basis for development, that is possible.

The conda environment is defined in a [yaml file](install_reqs.yml), which can be used for the analysis:

```
conda env create -f install_reqs.yml
```

Make sure you have activated the environment using `conda activate env_lisa_premerger`

# Overview of the Data Release

To navigate the data release, see the table of contents on the left hand side of all pages.

## Generating PSDs

The section [Generating PSDs](./PSD_Files/README.md), we show how the various PSDs are defined and generated in our analysis.

This corresponds to Sections IIA and IIIB of the paper.

Figures 1, 3 4 and 5 are generated as in [the given notebook](./PSD_Files/PSD_filter_images.ipynb).

## Observable Distance

The next [section](./Sensitive_Distance_Plot/README.md), corresponds to Section IIB of the paper, and [the notebook](./Sensitive_Distance_Plot/plot_sensitive_distance.ipynb) generates the plots for Figure 2.

## Generating Injections and Data for Search and Parameter Estimation
In [this section](./Data/README.md), we supply the codes to [define injections](./Data/make_injections.ipynb), and describe how to build the datasets which are utilised later in the Search (IV) and Parameter Estimation (V) sections of the paper

This is described at the start of Section IV.

The [data files](./Data/data_files/) we used are also provided in the git repo.

## Searching for Pre-merger Signals
[Here](./Search/README.md), we provide an overview of the analysis used to demonstrate ability to identify pre-merger signals in LISA, Section IV.

The different parts of this are described in the various subsections, including:
- [Optimal SNR Calculation](./Search/Optimal_SNR/README.md), used to produce the lines on Figure 6.
- [Template Bank Generation](./Search/Template_Banks/README.md), described in section IIIA.
- [The Search for Injected Signals](./Search/Signal_Runs/README.md), used to produce the Points in Figure 6.
- [The Search on noise data only](./Search/Significance_Runs/README.md), used to produce Figure 7 and the greyed-out region in Figure 6.

We describe how the results are collected into a single json file for each PSD, which are supplied [here](./Search/), and [a notebook](./Search/plot_search_results.ipynb) to plot Figures 6 and 7 from these.

## Parameter Estimation of Pre-merger signals

In [the final section](./Parameter_Estimation/README.md), we describe the parameter estimation describe in Section V of the paper

We describe this in several subsections:
- The automated combination of [configuration files](./Parameter_Estimation/Config_Files/README.md)
- [Running the parameter estimation](./Parameter_Estimation/Running_Analyses/README.md) stage, including combining results
- In order to generate skymap-related plots in [Figure 10](./Parameter_Estimation/skymap_plots.ipynb), we must convert the PE results into skymaps, detailed [here](./Parameter_Estimation/Making_Skymaps/README.md)

The plots in Figures 8 and 9 are detailed in [this notebook](./Parameter_Estimation/mass_tc_plots.ipynb), and Figure 10 is in [this notebook](./Parameter_Estimation/skymap_plots.ipynb).