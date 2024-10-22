import json
import argparse
import logging
from tqdm import tqdm


import pycbc
import pycbc.psd
import pycbc.fft
import pycbc.types
import pycbc.waveform
import pycbc.strain.strain
import pycbc.noise
from pycbc.types import MultiDetOptionAction

from pycbc.psd.lisa_pre_merger import generate_pre_merger_psds
from utils import filter_some_waveforms

parser = argparse.ArgumentParser()
parser.add_argument('--injections-file', required=True, help="Only needed so that the generate_data function doesn't break")
parser.add_argument('--psd-files', required=True,
                    action=MultiDetOptionAction,
                    help="PSD files for each channel (A, E), to be "
                         "supplied as channel:value pairs")
parser.add_argument('--bank-file', required=True)
parser.add_argument('--days-before-merger', type=float, required=True)
parser.add_argument('--f-lower', type=float, default=1e-6)
parser.add_argument('--label', required=True)
parser.add_argument('--kernel-length', type=int, default=17280)
parser.add_argument('--data-length', type=int, default=2592000)
parser.add_argument('--sample-rate', type=float, default=0.2)
parser.add_argument('--search-time', type=float, default=3600)
parser.add_argument('--reduce-bank-factor', type=int,
                    help="Reduce the bank by a factor of this number, "
                         "useful for performing the search quickly in testing"
                         "Default: don't do this")
parser.add_argument('--repeats', type=int, default=100)
parser.add_argument('--plot-best-waveform', action='store_true', help="Plot the best waveform from the bank - use in testing, default dont do this")

args = parser.parse_args()

#############################
# Generate the necessary PSDs
#############################
print(f"{args.days_before_merger} days before merger, {args.label}")

pycbc.init_logging(True)

# Make these command line options?
delta_t = 1. / args.sample_rate
dlen = args.data_length

length = int(dlen * args.sample_rate)
flen = length // 2 + 1

##########################
# Waveform 1
##########################

waveform_params_shared = {
    't_obs_start':dlen, # This is setting the data length.
    'f_lower': args.f_lower,
    'low-frequency-cutoff': 0.000001, # Why this *and* f_lower??? Don't think this one is used at all.
    'f_final': args.sample_rate / 2,
    'delta_f': 1 / dlen,
    'tdi':'1.5',
    't_offset': 0,
    'approximant': 'BBHX_PhenomD',
    'mode_array':[(2,2)],
    'cutoff_deltat': 0,
}

# Note that this is a local copy of http://gitlab.sr.bham.ac.uk/hannahm/low_latency_search/blob/master/injections/injections.json
with open(args.injections_file, 'r') as inj_file:
    injections = json.load(inj_file)
waveform_params = injections['0']

lisa_a_zero_phase_kern = generate_pre_merger_psds(
    psd_file=args.psd_files['A'],
    duration=dlen,
    sample_rate=args.sample_rate,
    kernel_length=args.kernel_length
)

lisa_e_zero_phase_kern = generate_pre_merger_psds(
    psd_file=args.psd_files['E'],
    duration=dlen,
    sample_rate=args.sample_rate,
    kernel_length=args.kernel_length
)

LISA_A_PSD = pycbc.psd.from_txt(
    args.psd_files['A'],
    flen,
    1./dlen,
    5e-6,
    is_asd_file=False
)

LISA_E_PSD = pycbc.psd.from_txt(
    args.psd_files['E'],
    flen,
    1./dlen,
    5e-6,
    is_asd_file=False
)

psds_for_whitening = {
    'LISA_A': lisa_a_zero_phase_kern['FD'],
    'LISA_E': lisa_e_zero_phase_kern['FD'],
}
psds_for_datagen = {
    'LISA_A': LISA_A_PSD,
    'LISA_E': LISA_E_PSD,
}

logging.info("Generated PSD objects")

waveform_params.update(waveform_params_shared)

time_before = 86400 * args.days_before_merger
tmpltbank = args.bank_file

all_snrs = []
logging.info("Performing no-signal runs")
print(f"No-signal runs")
for i in tqdm(range(args.repeats)):
    snr_vals = filter_some_waveforms(
        waveform_params, # tc is defined here
        psds_for_datagen,
        psds_for_whitening,
        time_before,
        tmpltbank,
        args.kernel_length,
        nosignal=True,
        random_seed=i*100,
        delta_t=delta_t,
        search_time=args.search_time,
        reduce_bank_factor=args.reduce_bank_factor,
        label=args.label,
        plot_best_wf=args.plot_best_waveform
    )

    all_snrs.append(snr_vals[2])
print(all_snrs)
logging.info('Done!')
