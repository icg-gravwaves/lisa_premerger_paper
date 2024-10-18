"""
This is a script to run the search analysis using a file as input
"""

import h5py
import copy
import json
import argparse
import logging
from tqdm import tqdm

import pycbc
import pycbc.types
from pycbc.types import MultiDetOptionAction
from pycbc.psd.lisa_pre_merger import generate_pre_merger_psds
from pycbc.waveform.pre_merger_waveform import (
    pre_process_data_lisa_pre_merger,
)
from utils import (
    get_snr_from_series,
    get_optimal_snr,
    get_snr_point,
    plot_best_waveform
)

parser = argparse.ArgumentParser()
parser.add_argument('--injections-file', required=True)
parser.add_argument('--injection-number', required=True)
parser.add_argument(
    '--psd-files',
    required=True,
    action=MultiDetOptionAction,
    help=(
        "PSD files for each channel (A, E), to be "
        "supplied as channel:value pairs"
    )
)
parser.add_argument('--bank-file', required=True)
parser.add_argument('--data-file', required=True)
parser.add_argument('--data-file-zero-noise')
parser.add_argument('--days-before-merger', type=float, required=True)
parser.add_argument('--label', required=True)
parser.add_argument('--kernel-length', type=int, default=17280)
parser.add_argument('--data-length', type=int, default=2592000)
parser.add_argument('--f-lower', type=float, default=1e-6)
parser.add_argument('--sample-rate', type=float, default=0.2)
parser.add_argument("--plot-best-waveform", action='store_true')
parser.add_argument('--reduce-bank-factor', type=int,
                    help="Reduce the bank by a factor of this number, "
                         "useful for performing the search quickly in testing"
                         "Default: don't do this")

args = parser.parse_args()

#############################
# Generate the necessary PSDs
#############################
print(
    f"Injection {args.injection_number}, "
    f"{args.days_before_merger} days before "
    f"merger, {args.label}"
)

pycbc.init_logging(True)

# Make these command line options?
length = int(args.data_length * args.sample_rate)
flen = length // 2 + 1

waveform_params_shared = {
    't_obs_start': args.data_length, # This is setting the data length.
    'f_lower': args.f_lower,
    'low-frequency-cutoff': 0.000001, 
    'f_final': args.sample_rate / 2,
    'delta_f': 1 / args.data_length,
    'tdi': '1.5',
    't_offset': 0,
    'cutoff_deltat': 0,
}

with open(args.injections_file, 'r') as inj_file:
    injections = json.load(inj_file)

waveform_params = injections[args.injection_number]
waveform_params.update(waveform_params_shared)

logging.info("Got waveform")

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

logging.info("Generated PSD objects")

time_before = 86400 * args.days_before_merger

cutoff_time=time_before
search_time=86400
window_length=17280

filter_waveform = copy.deepcopy(waveform_params)
filter_waveform.update({
    'approximant': 'BBHX_PhenomD',
    'mode_array':[(2,2)],
})

lisa_a_zero_phase_kern_pycbc_fd = psds_for_whitening['LISA_A']
lisa_e_zero_phase_kern_pycbc_fd = psds_for_whitening['LISA_E']


print('Noiseless data')

snr = get_optimal_snr(
    filter_waveform,
    psds_for_whitening,
    cutoff_time=cutoff_time,
    window_length=window_length,
    delta_t=1./args.sample_rate,
    kernel_length=args.kernel_length,
)
print(
    f"With exact template, optimal (noiseless) SNR is "
    f"{(snr[0]**2 + snr[1]**2)**0.5}"
)

print('Noisy data')
data = {}
data_zero = {}
data_noise = {}
for channel in ['LISA_A', 'LISA_E']:
    data[channel] = pycbc.types.timeseries.load_timeseries(
        args.data_file,
        group=f"/{channel}",
    )
    if args.data_file_zero_noise is not None:
        data_zero[channel] = pycbc.types.timeseries.load_timeseries(
            args.data_file_zero_noise,
            group=f"/{channel}",
        )
        data_noise[channel] = data[channel] - data_zero[channel]

# Pre-process the data for the get_snr_from_series function
# which does not do this

data_label = {
    "from file": data,
    "zero noise": data_zero,
    "noise-only (signal subtracted)": data_noise,
}

data_f_dict = {}
for lbl, data_dict in data_label.items():
    if data_dict == {}:
        continue
    data_dict = pre_process_data_lisa_pre_merger(
        data_dict,
        sample_rate=args.sample_rate,
        psds_for_whitening=psds_for_whitening,
        window_length=window_length,
        cutoff_time=cutoff_time,
        forward_zeroes=args.kernel_length,
    )

    data_A_f = data_dict['LISA_A'].to_frequencyseries()
    data_E_f = data_dict['LISA_E'].to_frequencyseries()

    data_f_dict[lbl] = {
        'LISA_A': data_A_f,
        'LISA_E': data_E_f
    }

    snr = get_snr_point(
        filter_waveform,
        data_f_dict[lbl],
        psds_for_whitening,
        cutoff_time=cutoff_time,
        window_length=window_length,
        delta_t=1. / args.sample_rate,
        kernel_length=args.kernel_length,
    )

    print(
        f"With exact template, data {lbl}, MF SNR (point) is {snr[0]}, {snr[1]}, "
        f"{(snr[0]**2 + snr[1]**2)**0.5}"
    )

    snr, _, _ = get_snr_from_series(
        filter_waveform,
        data_f_dict[lbl],
        psds_for_whitening,
        window_length=window_length,
        cutoff_time=cutoff_time,
        kernel_length=args.kernel_length,
        search_time=search_time,
        delta_t=1. / args.sample_rate,
    )

    print(
        f"With exact template, data {lbl} MF SNR (maximum) is {snr[0]}, {snr[1]}, "
        f"{(snr[0]**2 + snr[1]**2)**0.5}"
    )

data_f = data_f_dict['from file']

print(f"Beginning filtering with bank {args.bank_file}")
max_snrsq = 0
snr_vals = "Problem - no SNRs found > 0"
with h5py.File(args.bank_file, 'r') as bank_file:
    for idx in tqdm(range(len(bank_file['mass1'])), disable=False):

        if args.reduce_bank_factor is not None and idx % args.reduce_bank_factor:
                # For testing: reduce the bank size by this factor to make the search quicker
                continue
        bank_wf = copy.deepcopy(waveform_params_shared)
        bank_wf['approximant'] = 'BBHX_PhenomD'
        bank_wf['mode_array'] = [(2,2)]
        # Update waveform params to use the ones from the file
        bank_wf['tc'] = args.data_length
        bank_wf['mass1'] = bank_file['mass1'][idx]
        bank_wf['mass2'] = bank_file['mass2'][idx]
        bank_wf['inclination'] = bank_file['inclination'][idx]
        bank_wf['polarization'] = bank_file['polarization'][idx]
        bank_wf['spin1z'] = bank_file['spin1z'][idx]
        bank_wf['spin2z'] = bank_file['spin2z'][idx]
        #bank_wf['coa_phase'] = hfile['coa_phase'][idx]
        bank_wf['eclipticlatitude'] = bank_file['eclipticlatitude'][idx]
        bank_wf['eclipticlongitude'] = bank_file['eclipticlongitude'][idx]
    
        snr, iidx, times = get_snr_from_series(
            bank_wf,
            data_f,
            psds_for_whitening,
            window_length=window_length,
            cutoff_time=cutoff_time,
            kernel_length=args.kernel_length,
            search_time=search_time,
            delta_t=1. / args.sample_rate,
        )

        snr_qs = snr[0] ** 2 + snr[1] ** 2
        if snr_qs > max_snrsq:
            max_snrsq = snr_qs
            snr_vals = [idx, snr, max_snrsq ** 0.5, iidx, times, copy.deepcopy(bank_wf)]


print(
    f'Injection {args.injection_number}, '
    f'{args.days_before_merger} days before merger, '
    f'{args.label}, SNR {snr_vals[2]}'
)
print(snr_vals)

# The following is all for testing, so we exit here
if args.plot_best_waveform:
    plot_best_waveform(
        snr_vals,
        data_f,
        psds_for_whitening,
        time_before,
        window_length,
        search_time,
        args.kernel_length,
        delta_t=1. / args.sample_rate,
        label=args.label
    )
logging.info('Done!')
