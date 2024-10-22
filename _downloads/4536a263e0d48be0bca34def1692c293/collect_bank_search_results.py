"""
Collect SNRs at different time-before-merger for each injection and PSD type
"""

import argparse
import json
import logging
import numpy as np

from pycbc.events import trigger_fits as trstats

from pycbc import init_logging
init_logging(1)

parser = argparse.ArgumentParser()
parser.add_argument('--data-run-log-files', nargs='+', required=True)
parser.add_argument('--nosignal-run-log-files', nargs='+', required=True)
parser.add_argument('--optimal-snr-files', nargs='+', required=True)
parser.add_argument('--output-file')
args = parser.parse_args()

times_before_merger = [0.5, 1, 4, 7, 14]
results = {
    inj_no: {
        'snr': [0] * 5,
        'ifar': [0] * 5,
    } for inj_no in range(5)
}
results.update({
    'alpha': [0] * 5,
    'alpha_err': [0] * 5,
    'rate_above': [0] * 5,
    'fit_threshold': [0] * 5,
})

psd_type = None
for lf in args.data_run_log_files:
    # Which injection is this?
    with open(lf, 'r') as log_file:
        log_file_lines = log_file.readlines()
    # There will be a line like this that we want:
    # Injection [I], [N] days before merger, cutoff, SNR [some float]
    result_line = [
        l for l in log_file_lines
        if l.startswith('Injection') and
        'SNR' in l
    ]
    if not len(result_line):
        # No result line - possible issue, but just carry on for now
        continue
    psd_type_new = result_line[0].split(',')[-2].strip()
    if psd_type is not None and not psd_type_new == psd_type:
        logging.error(
            "Files are not all the same psd type, got %s and %s",
            psd_type,
            psd_type_new
        )
        raise RuntimeError
    elif psd_type is None:
        # First time
        psd_type = psd_type_new
    inj_number = int(result_line[0].split(',')[0].split()[-1])
    days_before = float(result_line[0].split(',')[1].split()[0])
    idx_days = times_before_merger.index(days_before)
    snr = float(result_line[0].split()[-1])

    results[inj_number]['snr'][idx_days] = snr

if psd_type is None:
    raise RuntimeError("No results")
results['psd_type'] = psd_type
if args.nosignal_run_log_files is None:
    args.nosignal_run_log_files = []

results['nonoise'] = {i: [] for i in times_before_merger}
for rf in args.nosignal_run_log_files:
    with open(rf, 'r') as rffp:
        # No-noise SNR results are the last line
        all_lines = rffp.readlines()

    snrs_nonoise_line = all_lines[-1].strip()
    define_line = [
        l.strip()
        for l in all_lines
        if 'days before merger' in l
    ][0]
    psd_type_new = define_line.split(',')[-1].strip()
    if not psd_type_new == psd_type:
        logging.error(
            "Files are not all the same psd type, got %s and %s",
            psd_type,
            psd_type_new
        )
        raise RuntimeError

    days_before = float(define_line.split()[0])
    idx_days = times_before_merger.index(days_before)
    if not snrs_nonoise_line.startswith('['):
        continue
    snrs_nonoise = [float(snr) for snr in snrs_nonoise_line.strip('[]').split(',')]

    results['nonoise'][times_before_merger[idx_days]] = snrs_nonoise
    # Work out the SNR where we would get FAR of 10 per day
    # Each event contributes one hour times the number of repeats
    # So the ten per day SNR will be in position 10 * (n_repeats * time per search),
    # which is 83 for 200 repeats of a one hour search
    snr_sort = np.argsort(snrs_nonoise)
    ten_per_day_idx = int(10 * (len(snrs_nonoise) / 24))
    fit_threshold = snrs_nonoise[snr_sort[-ten_per_day_idx]]
    alpha, sig_alpha = trstats.fit_above_thresh(
        'exponential',
        snrs_nonoise,
        fit_threshold,
    )
    rate_above = np.count_nonzero(
        np.array(snrs_nonoise) > fit_threshold
    ) / (len(snrs_nonoise) / 24) #  One hour searched around the merger for each noise realisation
    results['alpha'][idx_days] = alpha
    results['alpha_err'][idx_days] = sig_alpha
    results['rate_above'][idx_days] = rate_above
    results['fit_threshold'][idx_days] = fit_threshold
    for inj_number in range(5):
        far = trstats.cum_fit(
            'exponential',
            [results[inj_number]['snr'][idx_days]],
            alpha,
            fit_threshold
        )[0] * rate_above
        ifar = 1 / far
        results[inj_number]['ifar'][idx_days] = min(ifar, 100 * 365.25)

for rf in args.optimal_snr_files:
    with open(rf, 'r') as result_file:
        result_lines = result_file.readlines()
    inj_line = [
        rl.strip().split() for rl in result_lines
        if rl.startswith('Injection')
    ][0]
    inj_no = int(inj_line[1].strip(','))
    psd_type_new = inj_line[2]
    if not psd_type_new == psd_type:
        # psd types don't match; this could be the cutoff which
        # needs translating, if not, skip
        if not(psd_type_new == 'CUT_optimistic' and psd_type == 'cutoff'):
            continue
    opt_snr_all = np.array([
        np.array(rl.strip().split())[[0, -1]]
        for rl in result_lines
        if not rl.startswith('No')
        and not rl.startswith('Injection')
    ], dtype=float)
    results[inj_no]['optimal_snr_all'] = list(opt_snr_all[:,1])
    results[inj_no]['optimal_snr_all_time'] = list(opt_snr_all[:,0])
    # Also find the optimal SNR values defined at the times before merger
    opt_snr_results = np.array([
        float(rl.strip().split()[-1])
        for rl in result_lines
        if not rl.startswith('No')
        and not rl.startswith('Injection')
        and float(rl.split()[0]) in times_before_merger
    ], dtype=float)
    results[inj_no]['optimal_snr'] = list(opt_snr_results)

with open(args.output_file, 'w') as fout:
    json.dump(results, fout)

