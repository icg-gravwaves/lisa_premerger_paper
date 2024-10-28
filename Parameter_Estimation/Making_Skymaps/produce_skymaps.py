#!/usr/bin/env python
"""Script to produce skymap fits files from the posterior samples.

Note: this requires having ligo.skymap installed.
"""
import argparse
import pathlib

from astropy import units as u
import h5py
from ligo.skymap.io import write_sky_map
from ligo.skymap import moc, io, postprocess
from ligo.skymap.kde import Clustered2DSkyKDE
import numpy as np
import numpy.lib.recfunctions as rfn

sr_to_deg2 = u.sr.to(u.deg**2)


def get_parser():
    parser = argparse.ArgumentParser(description="Produce skymaps from posterior samples.")
    parser.add_argument("--result-dir", type=str, required=True, help="Path to the result directory.")
    parser.add_argument("--output-dir", type=str, required=True, help="Path to the output directory.")
    parser.add_argument("--injection-id", type=int, required=True, help="Injection ID.")
    parser.add_argument("--psd", type=str, required=True, help="PSD used for the run.")
    parser.add_argument("--trials", type=int, default=1, help="Number of trials for ligo.skymap")
    parser.add_argument("--jobs", type=int, default=1, help="Number of jobs for ligo.skymap")
    return parser


def process_skymap(posterior_samples, /, outdir, psd, time, trials=1, jobs=1, top_nside=16, overwrite=False):
    path = pathlib.Path(outdir) / psd
    path.mkdir(exist_ok=True)
    fits_file = path / f"sky_map_time_{time}.fits.gz"

    if not fits_file.exists() or overwrite:
        loc_samples = rfn.structured_to_unstructured(posterior_samples[["eclipticlongitude", "eclipticlatitude"]])
        skypost = Clustered2DSkyKDE(loc_samples, trials=trials, jobs=jobs)
        hpmap = skypost.as_healpix(top_nside=top_nside)
        write_sky_map(fits_file, hpmap, nest=True)
    else:
        print("Sky map already exists!")
    return fits_file


def compute_skymap_area(fits_file, levels):
    """
    Compute the area of the sky map at the given credible levels.

    Based on the code from ligo.skymap.tools.ligo_skymap_plot.py.
    """
    skymap = io.fits.read_sky_map(fits_file, moc=True)
    dA = moc.uniq2pixarea(skymap['UNIQ'])
    dP = skymap['PROBDENSITY'] * dA
    dP = skymap['PROBDENSITY'] * dA
    cls = 100 * postprocess.find_greedy_credible_levels(dP, skymap['PROBDENSITY'])
    i = np.flipud(np.argsort(skymap['PROBDENSITY']))
    area = np.interp(levels, cls[i], np.cumsum(dA[i]), left=0, right=4 * np.pi)
    return area * sr_to_deg2


def main():

    args = get_parser().parse_args()
    result_file = pathlib.Path(args.result_dir) / f"injection_{args.injection_id}_merged.hdf"
    outdir = pathlib.Path(args.output_dir) / f"injection_{args.injection_id}"
    outdir.mkdir(exist_ok=True, parents=True)

    for time in range(1, 6):
        try:
            with h5py.File(result_file, "r") as f:
                posterior_samples = f[args.psd][f"time {time}"][:]
        except KeyError:
            print(f"Posterior samples do not exist for {args.psd} at time {time}")
            continue
        fits_file = process_skymap(
            posterior_samples,
            outdir,
            args.psd,
            time,
            jobs=args.jobs,
            trials=args.trials,
        )
        print(f"Saved fits file: {fits_file}")

if __name__ == "__main__":
    main()
