#!/usr/bin/env python
"""Script to generate the injection ini files.

This also randomly sets the observation times.
"""
import argparse
import json
import os
import numpy as np
from pathlib import Path
from pycbc.workflow.configuration import WorkflowConfigParser


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--injection-file", type=str, help="Path to the JSON file with injections"
    )
    parser.add_argument(
        "--f-lower-file",
        type=str,
        help="Path to JSON file with f_lower for each injection",
    )
    parser.add_argument(
        "--psd-file",
        type=str,
        help="Path to the PSD ini file to use",
    )
    parser.add_argument(
        "--data-files",
        required=True,
        type=str,
        help="Path to directory containing the data files",
    )
    parser.add_argument(
        "--data-files-label",
        required=True,
        type=str,
        help="Label for the data files in the data files directory.",
    )
    parser.add_argument(
        "--outdir", type=str, help="Directory for saving ini files"
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing files if present"
    )
    parser.add_argument(
        "--config-path",
        type=str,
        help="Path to config files",
        default="configs"
    )
    parser.add_argument("--seed", type=int, default=1234)
    return parser


def main():
    args = get_parser().parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    rng = np.random.default_rng(args.seed)

    print(f"Reading injection data from: {args.injection_file}")
    with open(args.injection_file, "r") as f:
        injection_dict = json.load(f)

    print(f"Reading f_lower data from: {args.f_lower_file}")
    with open(args.f_lower_file, "r") as f:
        f_lower_dict = json.load(f)

    configs = [
        f"{args.config_path}/base_priors.ini",
        f"{args.config_path}/model.ini",
        f"{args.psd_file}",
    ]
    for inj_id, parameter_dict in injection_dict.items():
        config = WorkflowConfigParser(configFiles=configs)
        config.remove_section("environment")

        # Add injection params
        if not config.has_section("model"):
            config.add_section("model")

        # Specify the path to the data
        config["model"]["data_file"] = str(Path(os.path.join(
            args.data_files,
            f"{args.data_files_label}_{inj_id}.hdf",
        )).absolute())

        # Update the path to the PSD to use the absolute path
        config["model"]["psd_file"] = str(Path(os.path.join(
            config["model"]["psd_file"]
        )).absolute())

        tc = float(parameter_dict["tc"])
        t_from_end = float(parameter_dict["additional_end_data"])
        # Set t_obs_start to match tlen
        t_obs_start = float(config["model"]["tlen"])
        start_gps_time = float(t_from_end + tc) - t_obs_start

        if not config.has_section("prior-tc"):
            config.add_section("prior-tc")

        # Set the tc prior. Has 1 hour width around tc with a random offset
        # so that the true value is not centred.
        tc_offset = rng.integers(low=-900, high=900)
        config["prior-tc"]["min-tc"] = str(int(tc) - 3600 + tc_offset)
        config["prior-tc"]["max-tc"] = str(int(tc) + 3600 + tc_offset)

        # Add f-lower
        if not config.has_section("static_params"):
            config.add_section("static_params")
        if inj_id in f_lower_dict:
            print(f"Overriding f_lower value for {inj_id}")
            config["static_params"]["f_lower"] = str(f_lower_dict[inj_id])
        config["static_params"]["t_obs_start"] = str(t_obs_start)
        config["static_params"]["start_gps_time"] = str(start_gps_time)

        # Write the ini file
        filename = f"{args.outdir}/injection{inj_id}.ini"
        if os.path.exists(filename) and not args.overwrite:
            raise RuntimeError("File already exists!")
        with open(filename, "w") as config_file:
            config.write(config_file)


if __name__ == "__main__":
    main()
