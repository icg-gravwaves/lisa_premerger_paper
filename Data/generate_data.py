#!/usr/bin/env python
import argparse
import json
import os


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--configs", type=str, nargs="+", help="The config files to load"
    )
    parser.add_argument(
        "--injections-file",
        type=str,
        required=True,
        help="Path to the JSON files with the injection parameters"
    )
    parser.add_argument(
        "--outdir",
        type=str,
        default=os.getcwd(),
        help="Output directory. If not specified, defaults to the current directory",
    )
    parser.add_argument(
        "--label",
        type=str,
        default="signal",
        help=(
            "Label to use for the filenames. "
            "Files will be named <label>_<inj_id>.hdf. "
            "Default label is 'signal'."
        )
    )
    parser.add_argument(
        "--zero-noise",
        action="store_true",
        help="If true, generate zero-noise data."
    )
    return parser


def main(args):

    import pycbc.psd
    from pycbc.waveform.pre_merger_waveform import (
        generate_data_lisa_pre_merger
    )
    from pycbc.distributions import read_params_from_config
    from pycbc.workflow.configuration import WorkflowConfigParser


    print("Loading config")
    config = WorkflowConfigParser(configFiles=args.configs)
    _, static_params = read_params_from_config(config)

    # Convert inputs
    psd_file = config.get("data", "psd_file")
    sample_rate = float(config.get("data", "sample_rate"))
    safe_tlen = float(config.get("data", "safe_tlen"))
    tlen = float(config.get("data", "tlen"))
    zero_noise = args.zero_noise
    seed = int(config.get("data", "seed"))

    print("Generating PSDs")
    # Generate PSDs for simulating the noise
    length = int(safe_tlen * sample_rate)
    flen = length // 2 + 1

    # Assume A & E PSDs are the same
    psd = pycbc.psd.from_txt(
        psd_file, flen, 1./safe_tlen, 1./safe_tlen, is_asd_file=False
    )
    psds_for_datagen = {}
    psds_for_datagen['LISA_A'] = psd
    psds_for_datagen['LISA_E'] = psd.copy()

    with open(args.injections_file, "r") as f:
        injection_params = json.load(f)

    os.makedirs(args.outdir, exist_ok=True)

    if "f_lower" not in static_params:
        raise RuntimeError("Must specify 'f_lower'")

    print(f"Generating data with seed={seed}")
    for key, params in injection_params.items():

        print(f"Generating data for injection {key}")
        params.update(static_params)

        print(f"Specified safe duration: {safe_tlen}")
        # Generate a longer waveform that can then be cut to the desired length
        # after it has been generated. This makes sure all the modes are
        # present for the full length of the data.
        params["t_obs_start"] = safe_tlen
        print(f"Duration after truncation: {tlen}")

        filename = os.path.join(args.outdir, f"{args.label}_{key}.hdf")

        print(f"Zero noise={zero_noise}") 

        data = generate_data_lisa_pre_merger(
            params,
            psds_for_datagen=psds_for_datagen,
            seed=seed + int(key),
            sample_rate=sample_rate,
            zero_noise=zero_noise,
            duration=tlen,
        )

        # Make sure that the difference between tc and start time is less than
        # the duration.
        if (params["tc"] - data["LISA_A"].start_time) >  tlen:
            raise RuntimeError("Something went horribly wrong!")
 
        for key, ts in data.items():
            # Save the data to /ifo
            ts.save(
                filename,
                group=f"/{key}",
            )
            

if __name__ == "__main__":
    args = get_parser().parse_args()
    main(args)
