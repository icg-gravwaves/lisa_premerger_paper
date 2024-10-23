#!/usr/bin/env python
"""Script to merge the results from the parameter estimation runs."""
import argparse
import h5py
import numpy as np
import pathlib
import yaml

def get_parser():
    parser = argparse.ArgumentParser(description="Merge results from parameter estimation runs.")
    parser.add_argument('--result-mapping', type=str, required=True, help='Path to the result mapping file.')
    parser.add_argument('--validate-only', action='store_true', help='Flag to validate the merged results.')
    parser.add_argument("--output-dir", type=str, default=".", help="Path to the output directory.")
    return parser


def get_nessai_posterior(path, subdir="outdir_nessai"):
    path = pathlib.Path(path) / subdir
    result_file = path / "result.hdf5"
    if not result_file.exists():
        print(f"File does not exist: {result_file}")
        return np.empty(0)
    with h5py.File(result_file, "r") as f:
        posterior = f["posterior_samples"][:]
    return posterior


def merge_results(result_mapping, output_dir):
    output_dir = pathlib.Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    for inj, results in result_mapping.items():
        for psd, psd_results in results.items():
            with h5py.File(f"{output_dir}/{inj.replace(' ', '_')}_merged.hdf", "a") as f:
                if psd not in f:
                    f.create_group(psd)
                for time, path in psd_results.items():
                    base_path = pathlib.Path(path.absolute())
                    path = next(base_path.glob('outdir_inj*'))
                    posterior = get_nessai_posterior(path)
                    if posterior.size == 0:
                        continue
                    f[psd].create_dataset(time, data=posterior)

def validate_path(path):
    path = pathlib.Path(path).absolute()
    valid = path.exists()
    if path.is_dir():
        hdf_files = list(path.glob('**/*.hdf'))
        valid &= bool(hdf_files)
    else:
        valid = False
    return valid


def validate_inputs(result_mapping: dict):
    """Validate the inputs mapping file"""
    all_valid = True
    for inj, results in result_mapping.items():
        for psd, psd_results in results.items():
            for time, path in psd_results.items():
                valid = validate_path(path) 
                all_valid &= valid
                if not valid:
                    print(f"Result does not exist for injection {inj}, psd {psd}, at time {time}")
    return all_valid
    

if __name__ == "__main__":
    args = get_parser().parse_args()

    with open(args.result_mapping, "r") as f:
        result_mapping = yaml.safe_load(f)

    validate_inputs(result_mapping)
    if args.validate_only:
        exit(0)
    merge_results(result_mapping, output_dir=args.output_dir)