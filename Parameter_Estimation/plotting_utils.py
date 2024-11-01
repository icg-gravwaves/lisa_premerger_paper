"""General plotting utilities."""
import numpy as np


def generate_all_params(samples, return_array=False):
    from nessai.livepoint import live_points_to_dict, dict_to_live_points
    import pycbc.conversions

    # This is lazy but simple
    if isinstance(samples, np.ndarray):
        samples = live_points_to_dict(samples)

    if "mchirp" in samples:
        key = "q" if "q" in samples else "mass_ratio"
        samples["mass1"] = pycbc.conversions.mass1_from_mchirp_q(
            samples["mchirp"], samples[key]
        )
        samples["mass2"] = pycbc.conversions.mass2_from_mchirp_q(
            samples["mchirp"], samples[key]
        )
    elif "mass1" in samples and "mchrip" not in samples:
        samples["mchirp"] = pycbc.conversions.mchirp_from_mass1_mass2(samples["mass1"], samples["mass2"])
        samples["mass_ratio"] = 1 / pycbc.conversions.q_from_mass1_mass2(samples["mass1"], samples["mass2"])
    try:
        samples["chi_eff"] = pycbc.conversions.chi_eff(
            samples["mass1"], samples["mass2"], samples["spin1z"], samples["spin2z"]
        )
    except KeyError:
        print("Could not generate chi_eff")
        pass
    if "comoving_volume" in samples:
        samples["distance"] = pycbc.cosmology.distance_from_comoving_volume(samples["comoving_volume"])
        samples["redshift"] = pycbc.cosmology.redshift_from_comoving_volume(samples["comoving_volume"])
    if "distance" in samples:
        samples["redshift"] = pycbc.cosmology.redshift(samples["distance"])
    if "additional_end_data" in samples:
        samples["cutoff_deltat"] = -samples["additional_end_data"]
    if return_array:
        return dict_to_live_points(samples, non_sampling_parameters=False)
    else:
        return samples


def get_times_array(times):
    return np.array([times_lookup[t] for t in times])


def get_priors(config_file, parameter):
    import configparser
    priors = {}
    for i in range(5):
        config = configparser.ConfigParser()
        config.read([config_file])
        x_min = float(config.get(f"prior-{parameter}", f"min-{parameter}"))
        x_max = float(config.get(f"prior-{parameter}", f"max-{parameter}"))
        priors[i] = np.array([x_min, x_max])
    return priors

times_lookup = {
    "time 1": 14,
    "time 2": 7,
    "time 3": 4,
    "time 4": 1,
    "time 5": 0.5,
}

psd_ls = {
    "optimistic": "-",
    "pessimistic": "--",
    "cut": ":",
}
psd_markers = {
    "optimistic": "^",
    "pessimistic": "v",
    "cut": "x"
}

psd_labels = {
    "optimistic": "Optimistic",
    "pessimistic": "Pessimistic",
    "cut": "Hard cut",
}

psd_colours = {
    "optimistic": "C0",
    "pessimistic": "C2",
    "cut": "C1",
}

parameter_labels = {
    "mchirp": r"$\mathcal{M}\;[\text{M}_{\odot}]$",
    "mass_ratio": r"$q$",
    "tc": r"$t_\text{c}\;[s]$",
    "inclination": r"$\iota$",
    "spin1z": r"$\chi_1$",
    "spin2z": r"$\chi_2$",
}