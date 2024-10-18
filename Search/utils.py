import numpy as np
import copy
from tqdm import tqdm
import h5py

import pycbc
import pycbc.psd
import pycbc.fft
import pycbc.types
import pycbc.waveform
import pycbc.strain.strain
import pycbc.noise
import pycbc.pnutils
import pycbc.filter
from pycbc.waveform.pre_merger_waveform import (
    generate_data_lisa_pre_merger,
    generate_waveform_lisa_pre_merger,
    pre_process_data_lisa_pre_merger,
)


####################################################
# Function to get SNR given data and wform params
####################################################
def get_snr_series(
        params,
        data_f,
        psds_for_whitening,
        window_length,
        cutoff_time,
        kernel_length,
        delta_t=5
    ):

    waveforms = generate_waveform_lisa_pre_merger(
        params,
        psds_for_whitening,
        sample_rate=1./delta_t,
        window_length=window_length,
        cutoff_time=cutoff_time,
        forward_zeroes=kernel_length,
    )

    snr_A = pycbc.filter.matched_filter(
        waveforms['LISA_A'],
        data_f['LISA_A'],
    )
    snr_E = pycbc.filter.matched_filter(
        waveforms['LISA_E'],
        data_f['LISA_E'],
    )

    return abs(snr_A), abs(snr_E)


def get_snr_from_series(
        params,
        data_f,
        psds_for_whitening,
        window_length,
        cutoff_time,
        kernel_length,
        search_time,
        delta_t=5
    ):

    snr_A, snr_E = get_snr_series(
        params,
        data_f,
        psds_for_whitening,
        window_length,
        cutoff_time,
        kernel_length,
        delta_t=delta_t
    )

    if search_time is None:
        search_indices = len(snr_A)
    else:
        search_indices = int(search_time//delta_t)
    start_idx = len(snr_A) - search_indices
    search_slice = slice(start_idx, len(snr_A))
    
    #snrsq_series = (snr_A ** 2 + snr_E ** 2)
    #amax = np.argmax(snrsq_series[search_slice])
    #idx_everywhere = start_idx + amax

    #snr = (snr_A[idx_everywhere], snr_E[idx_everywhere])
    #time = idx_everywhere*snr_A._delta_t + float(snr_A._epoch)
    #return snr, idx_everywhere, time

    amax_A = np.argmax(
        abs(snr_A.data[search_slice])
    )
    #print(amax_A)
    #print(abs(snr_A[amax_A]))

    mineval = max(amax_A - 20, 0)
    maxeval = min(amax_A + 20, search_indices)

    amax_E = np.argmax(
        abs(snr_E.data[search_slice][mineval:maxeval])
    )
    amax_E = amax_E + mineval
    snr = (
        (snr_A.data[search_slice][amax_A]),
        (snr_E.data[search_slice][amax_E])
    )
    snr_sq = abs(snr[0]**2 + snr[1]**2)

    amax2_E = np.argmax(
        abs(snr_E.data[search_slice])
    )
    minaval = max(amax2_E - 20, 0)
    maxaval = min(amax2_E + 20, search_indices)
    amax2_A = np.argmax(
        abs(snr_A.data[search_slice][minaval:maxaval])
    )
    amax2_A = amax2_A + minaval
    snr2 = (
        (snr_A.data[search_slice][amax2_A]),
        (snr_E.data[search_slice][amax2_E])
    )
    snr2_sq = abs(snr2[0]**2 + snr2[1]**2)
    if snr2_sq > snr_sq:
        snr = snr2
        amax_A = amax2_A
        amax_E = amax2_E

    # NOTE to Gareth: TimeSeries should have a get_sample_time method
    #                 sample_times is not quick if you only want one point!

    #print(snr)
    #print((snr[0] ** 2 + snr[1] ** 2) ** 0.5)
    A_time = (start_idx + amax_A)*snr_A._delta_t + float(snr_A._epoch)
    E_time = (start_idx + amax_E)*snr_E._delta_t + float(snr_E._epoch)
    return snr, (start_idx + amax_A, start_idx + amax_E), (A_time, E_time)

def get_snr_point(
        params,
        data,
        psds_for_whitening,
        window_length,
        cutoff_time,
        kernel_length,
        delta_t=5,
    ):

    snr_A, snr_E = get_snr_series(
        params,
        data,
        psds_for_whitening,
        window_length,
        cutoff_time,
        kernel_length,
        delta_t=delta_t
    )

    return abs(snr_A[0]), abs(snr_E[0])

################################
# Function to perform filtering
#################################
def filter_some_waveforms(
        waveform_params,
        psds_for_datagen,
        psds_for_whitening,
        time_before,
        tmpltbank,
        kernel_length,
        nosignal=False,
        random_seed=137,
        delta_t=5,
        search_time=3600,
        window_length=17280,
        reduce_bank_factor=None,
        label='Label',
        plot_best_wf=False,
    ):
    generation_waveform = copy.deepcopy(waveform_params)
    generation_waveform.update({
        'approximant': 'BBHX_PhenomHM'
    })
    filter_waveform = copy.deepcopy(waveform_params)
    filter_waveform.update({
        'approximant': 'BBHX_PhenomD',
        'mode_array':[(2,2)],
    })

    print(f"Time before {time_before}")

    data = generate_data_lisa_pre_merger(
        generation_waveform,
        psds_for_datagen,
        sample_rate=1. / delta_t,
        seed=random_seed,
        no_signal=nosignal,
    )
    data = pre_process_data_lisa_pre_merger(
        data,
        sample_rate=1. / delta_t,
        psds_for_whitening=psds_for_whitening,
        window_length=window_length,
        cutoff_time=time_before,
        forward_zeroes=kernel_length,
    )

    data_A_f = data['LISA_A'].to_frequencyseries()
    data_E_f = data['LISA_E'].to_frequencyseries()

    if not nosignal:
        data_nn = generate_data_lisa_pre_merger(
            generation_waveform,
            psds_for_datagen,
            sample_rate=1./delta_t,
            no_signal=nosignal,
            zero_noise=True
        )
        data_nn = pre_process_data_lisa_pre_merger(
            data_nn,
            sample_rate=1./delta_t,
            psds_for_whitening=psds_for_whitening,
            window_length=window_length,
            cutoff_time=time_before,
            forward_zeroes=kernel_length,
        )
        data_A_f_nn = data_nn['LISA_A'].to_frequencyseries()
        data_E_f_nn = data_nn['LISA_E'].to_frequencyseries()

        snr, _, _ = get_snr_from_series(
            filter_waveform,
            {'LISA_A': data_A_f_nn, 'LISA_E': data_E_f_nn},
            psds_for_whitening,
            window_length,
            time_before,
            kernel_length,
            search_time,
            delta_t=delta_t,
        )
        print(
            f"With no-higher-modes template, optimal (noiseless) SNR is {snr[0]}, {snr[1]}, "
            f"{(snr[0]**2 + snr[1]**2)**0.5}"
        )

        snr, _, _ = get_snr_from_series(
            filter_waveform,
            {'LISA_A': data_A_f, 'LISA_E': data_E_f},
            psds_for_whitening,
            window_length,
            time_before,
            kernel_length,
            search_time,
            delta_t=delta_t,
        )
        print(
            f"With no-higher-modes template, MF SNR is {snr[0]}, {snr[1]}, "
            f"{(snr[0]**2 + snr[1]**2)**0.5}"
        )

    # Reverse engineer the time-length of the data
    data_length = (len(data_A_f) - 1) * 2 * delta_t
    print(f"Beginning filtering with bank {tmpltbank}")
    max_snr = 0
    snr_vals = "Problem - no SNRs found > 0"
    with h5py.File(tmpltbank, 'r') as bank_file:
        for idx in range(len(bank_file['mass1'])):
            if reduce_bank_factor is not None and idx % reduce_bank_factor:
                # For testing: reduce the bank size by this factor to make the search quicker
                continue
            params = copy.deepcopy(filter_waveform)
            params['tc'] = data_length
            params['mass1'] = bank_file['mass1'][idx]
            params['mass2'] = bank_file['mass2'][idx]
            params['inclination'] = bank_file['inclination'][idx]
            params['polarization'] = bank_file['polarization'][idx]
            params['spin1z'] = bank_file['spin1z'][idx]
            params['spin2z'] = bank_file['spin2z'][idx]
            #params['coa_phase'] = bank_file['coa_phase'][idx]
            params['eclipticlatitude'] = bank_file['eclipticlatitude'][idx]
            params['eclipticlongitude'] = bank_file['eclipticlongitude'][idx]

            snr, iidx, times = get_snr_from_series(
                params,
                {'LISA_A': data_A_f, 'LISA_E': data_E_f},
                psds_for_whitening,
                window_length,
                time_before,
                kernel_length,
                search_time,
                delta_t=delta_t,
            )
            snr_qs = snr[0]**2 + snr[1]**2
            if snr_qs > max_snr:
                max_snr = snr_qs
                snr_vals = [idx, snr, max_snr**0.5, iidx, times, copy.deepcopy(params)]


    if plot_best_wf:
        plot_best_waveform(
            snr_vals,
            {'LISA_A': data_A_f, 'LISA_E': data_E_f},
            psds_for_whitening,
            time_before,
            window_length,
            search_time,
            kernel_length,
            delta_t=delta_t,
            label=f'{label}_{random_seed}'
        )
    return snr_vals

def get_optimal_snr(
        waveform_params,
        psds_for_whitening,
        cutoff_time,
        window_length=17280,
        delta_t=5,
        kernel_length=17280,
    ):

    waveforms = generate_waveform_lisa_pre_merger(
        waveform_params,
        psds_for_whitening,
        sample_rate=1. / delta_t,
        window_length=window_length,
        cutoff_time=cutoff_time,
        forward_zeroes=kernel_length,
    )

    snr = get_snr_point(
        waveform_params,
        waveforms,
        psds_for_whitening,
        window_length,
        cutoff_time,
        kernel_length,
    )

    return snr

def get_optimal_snr_freq_cut(
        waveform_params,
        psds_for_datagen,
        cutoff_time,
        delta_t=5.,
        f_lower=1e-7,
        delta_f=1e-7,
    ):
    """
    A function to get the optimal SNR using a frequency
    cut rather than the FIR filter and cutting method.
    This is approximate and a useful sanity check
    """
    if cutoff_time == 0:
        end_freq = 1 / (2 * delta_t)
    else:
        # Approximate a time cut by working out
        # the time-frequency track and interpolating
        # the frequency cut based off that
        track_t, track_f = pycbc.pnutils.get_inspiral_tf(
            0,
            waveform_params['mass1'],
            waveform_params['mass2'],
            0,
            0,
            f_lower,
            approximant='SPAtmplt'
        )
        end_freq = np.interp(
            -cutoff_time,
            track_t,
            track_f,
        )
        if end_freq < (f_lower + 2 * delta_f):
            # This frequency / time before merger is too low
            # frequency, and won't give sensible results
            return np.nan

    wf = pycbc.waveform.get_fd_det_waveform(
        **waveform_params,
        ifos=['LISA_A','LISA_E'],
        f_final=end_freq,
    )

    sig = {}
    for channel in ['A','E']:
        chan = f'LISA_{channel}'
        cut_psd = psds_for_datagen[chan][:len(wf[chan])]
        sig[channel] = pycbc.filter.sigma(
            wf[chan],
            cut_psd,
            low_frequency_cutoff=f_lower,
            high_frequency_cutoff=end_freq
        )

    return sig['A'], sig['E']

def plot_best_waveform(
    snr_vals,
    data_f,
    psds_for_whitening,
    time_before,
    window_length,
    search_time,
    kernel_length,
    delta_t=5,
    label='Label'
):

    snr = get_optimal_snr(
        snr_vals[5],
        psds_for_whitening,
        cutoff_time=time_before,
        window_length=window_length,
        delta_t=delta_t,
        kernel_length=kernel_length,
    )

    data_length = (len(data_f['LISA_A']) - 1) * 2 * delta_t

    print(
        f"With found template, optimal SNR is {snr[0]}, {snr[1]}, "
        f"{(snr[0]**2 + snr[1]**2)**0.5}"
    )

    waveforms = generate_waveform_lisa_pre_merger(
            snr_vals[5],
            psds_for_whitening,
            sample_rate=1. / delta_t,
            window_length=window_length,
            cutoff_time=time_before,
            forward_zeroes=kernel_length,
    )

    from matplotlib import pyplot as plt

    fig, ax = plt.subplots(1)
    for channel in ['LISA_A', 'LISA_E']:
        ax.plot(
            data_f[channel].sample_frequencies,
            data_f[channel],
            alpha=0.5,
            label=f'{channel} data'
        )
        ax.plot(
            waveforms[channel].sample_frequencies,
            abs(waveforms[channel]),
            alpha=0.5,
            label=f'{channel} waveform'
        )
    if label == 'cutoff':
        ax.axvspan(
            0, 1e-4,
            color='red',
            alpha=0.25,
            zorder=-100
        )
    ax.loglog()
    ax.grid()
    ax.set_xlim(1e-6, 1e-1)

    ax.legend()
    ax.set_xlabel('Frequency, Hz')
    ax.set_title(f'Template {snr_vals[0]}, {time_before / 86400} days before merger, {label} psd')
    fig.savefig(f'bestwf_freq_{label}.png')

    wv_time = {k: v.to_timeseries() for k, v in waveforms.items()}

    fig, (ax0, ax1, ax2, ax3) = plt.subplots(
        1, 4, figsize=(16,4)
    )

    for ax in [ax0, ax1, ax2, ax3]:
        for channel in ['LISA_A', 'LISA_E']:
            ax.plot(
                wv_time[channel].sample_times,
                wv_time[channel].real(),
                alpha=0.5,
                label=channel
            )
        ax.grid()
        ax.set_yscale('symlog', linthresh=1e-5)

    ax0.set_xlim(
        0,
        kernel_length * delta_t,
    )
    ax1.set_xlim(
        kernel_length * delta_t,
        kernel_length * delta_t + window_length,
    )
    ax2.set_xlim(
        kernel_length * delta_t,
        data_length - time_before,
    )
    ax3.set_xlim(
        data_length - time_before,
        data_length
    )

    for ax in [ax0, ax1, ax2, ax3]:
        ax.axvspan(
            kernel_length * delta_t + window_length,
            data_length - time_before,
            color='g',
            zorder=-100,
            alpha=0.25
        )
        ax.axvspan(
            data_length - time_before,
            data_length,
            color='r',
            zorder=-100,
            alpha=0.25
        )
        ax.axvspan(
            0,
            kernel_length * delta_t,
            color='r',
            zorder=-100,
            alpha=0.25
        )
        ax.axvspan(
            kernel_length * delta_t,
            kernel_length * delta_t + window_length,
            color='y',
            zorder=-100,
            alpha=0.25
        )

    ax0.set_xlabel('Zeroed start')
    ax1.set_xlabel('Tapered Waveform start')
    ax2.set_xlabel('Full Waveform')
    ax3.set_xlabel('Zeroed End')
    fig.suptitle(f'Template {snr_vals[0]}, {time_before / 86400} days before merger, {label} psd')

    fig.savefig(f'bestwf_time_{label}.png')


    fig, ax = plt.subplots(1)

    series_out = get_snr_series(
        snr_vals[5],
        data_f,
        psds_for_whitening,
        window_length,
        time_before,
        kernel_length,
        delta_t=delta_t
    )

    ax.plot(
        series_out[1].sample_times - series_out[1].sample_times[-1],
        (series_out[0] ** 2 + series_out[1] ** 2) ** 0.5,
        c='k',
        label='Sum squared'
    )
    ax.plot(
        series_out[1].sample_times - series_out[1].sample_times[-1],
        series_out[0],
        c='r',
        label='LISA_A'
    )
    ax.plot(
        series_out[1].sample_times - series_out[1].sample_times[-1],
        series_out[1],
        c='b',
        label='LISA_E'
    )
    ax.plot(
        series_out[1].sample_times - series_out[1].sample_times[0],
        (series_out[0] ** 2 + series_out[1] ** 2) ** 0.5,
        c='k',
        linestyle=':',
    )
    ax.plot(
        series_out[1].sample_times - series_out[1].sample_times[0],
        series_out[0],
        c='r',
        linestyle=':',
    )
    ax.plot(
        series_out[1].sample_times - series_out[1].sample_times[0],
        series_out[1],
        c='b',
        linestyle=':',
    )

    snr_best, _, times = get_snr_from_series(
        snr_vals[5],
        data_f,
        psds_for_whitening,
        window_length,
        time_before,
        kernel_length,
        delta_t=delta_t,
        search_time=search_time
    )

    ax.scatter(
        times[0] - series_out[1].sample_times[-1],
        snr_best[0],
        marker='x',
        color='r',
        zorder=100
    )
    ax.scatter(
        times[0] - series_out[1].sample_times[-1],
        snr_best[1],
        marker='x',
        color='b',
        zorder=100
    )
    ax.scatter(
        sum(times) / 2 - series_out[1].sample_times[-1],
        (snr_best[0] ** 2 + snr_best[1] ** 2) ** 0.5,
        marker='x',
        color='k',
        zorder=100
    )

    ax.axvspan(
        -search_time,
        0,
        color='g',
        zorder=-100,
        alpha=0.25
    )

    ax.set_xlim(
        left=-search_time*2.5,
        right=search_time*0.25
    )
    ax.grid(zorder=-50)
    ax.legend()
    ax.set_xlabel('Time from merger')
    ax.set_ylabel('SNR')
    ax.set_title(f'Template {snr_vals[0]}, {time_before / 86400} days before merger, {label} psd')
    fig.savefig(f'bestwf_snr_series_{label}.png')