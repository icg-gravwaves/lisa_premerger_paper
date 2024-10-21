"""
Script to calculate optimal SNR for defined injections
"""
import numpy as np
import logging
import argparse
import json


import pycbc
from pycbc.types import MultiDetOptionAction
import pycbc.psd
import pycbc.fft
import pycbc.types
import pycbc.waveform
import pycbc.strain.strain
import pycbc.noise

from pycbc.psd.lisa_pre_merger import generate_pre_merger_psds
import sys
sys.path.append("..")
from utils import get_optimal_snr

parser = argparse.ArgumentParser()
parser.add_argument('--injections-file', required=True)
parser.add_argument('--injection-number', required=True)
parser.add_argument('--psd-files', required=True,
                    action=MultiDetOptionAction,
                    help="PSD files for each channel (A, E), to be "
                        "supplied as channel:value pairs")
parser.add_argument('--days-before-merger', type=float, nargs='+')
parser.add_argument('--f-lower', type=float, default=1e-7)
parser.add_argument('--f-lower-search', type=float, default=1e-6)
parser.add_argument('--label', required=True)
parser.add_argument('--kernel-length', type=int, default=17280)
parser.add_argument('--data-length', type=int, default=2592000)
parser.add_argument('--sample-rate', type=float, default=0.2)

args = parser.parse_args()


#############################
# Generate the necessary PSDs
#############################
print(f"Injection {args.injection_number}, {args.label}")

pycbc.init_logging(True)
logging.info(f"Injection {args.injection_number}, {args.label}")

waveform_params_shared = {
    't_obs_start':args.data_length, # This is setting the data length.
    'f_lower':args.f_lower_search,
    'low-frequency-cutoff': 0.000001, # Why this *and* f_lower??? Don't think this one is used at all.
    'f_final': args.sample_rate / 2,
    'delta_f': 1 / args.data_length,
    'tdi':'1.5',
    't_offset': 7365189.431698299,
    'approximant': 'BBHX_PhenomD',
    'cutoff_deltat': 0,
}

# Note that this is a local copy of http://gitlab.sr.bham.ac.uk/hannahm/low_latency_search/blob/master/injections/injections.json
with open(args.injections_file, 'r') as inj_file:
    injections = json.load(inj_file)

waveform_params = injections[args.injection_number]
waveform_params.update(waveform_params_shared)

# Make these command line options?
delta_t = 1. / args.sample_rate
dlen = args.data_length

length = int(dlen * args.sample_rate)

lisa_a_zero_phase_kern = generate_pre_merger_psds(
    psd_file=args.psd_files['A'],
    duration=args.data_length,
    sample_rate=args.sample_rate,
    kernel_length=args.kernel_length
)

lisa_e_zero_phase_kern = generate_pre_merger_psds(
    psd_file=args.psd_files['E'],
    duration=args.data_length,
    sample_rate=args.sample_rate,
    kernel_length=args.kernel_length
)

psds_for_whitening = {
    'LISA_A': lisa_a_zero_phase_kern['FD'],
    'LISA_E': lisa_e_zero_phase_kern['FD'],
}

all_times = list(np.logspace(-1, 1.3010299956639813, num=150))
all_times += args.days_before_merger
all_times = sorted(all_times)


for time_before_days in all_times:
    time_before = int(time_before_days * 86400)

    snr_val = get_optimal_snr(
        waveform_params,
        psds_for_whitening,
        time_before,
        window_length=17280,
        delta_t=1. /  args.sample_rate,
        kernel_length=args.kernel_length,
    )
    print(time_before_days, time_before, (snr_val[0]**2 + snr_val[1]**2)**0.5)
