import numpy as np
import argparse
import pycbc
import pycbc.psd
import pycbc.waveform
import pycbc.filter
from tqdm import tqdm
import h5py

from pycbc.pnutils import get_inspiral_tf

# Some top-level parameters
f_nyquist = 0.01
tlen = 86400 * 40
delta_f = 1. / (tlen * 2) # Note that this is not long enough to represent in the time-domain, but we won't do that!
low_freq_cutoff = max(1e-06, delta_f)
nominal_distance = 2000

parser = argparse.ArgumentParser()
parser.add_argument(
    '--psd-file',
    required=True
)
parser.add_argument(
    '--mass-range',
    nargs=2,
    type=float,
    required=True,
    help="Range of component masses to calculate, min/max"
)
parser.add_argument(
    '--log-mass-spacing',
    action='store_true',
    help="Use a range of masses separated logarithmically. Default linear.")
parser.add_argument(
    '--n-mass-points',
    type=int,
    default=1000,
    help='Number of points to use in mass spacing. Default 1000.'
)
parser.add_argument(
    '--n-sky-points',
    type=int,
    default=1000,
    help='Number of sky points to use to calculate the optimal SNR.'
)
parser.add_argument(
    '--q',
    type=float,
    default=1
)
parser.add_argument(
    '--output-file',
    required=True,
    help="File to output the times, masses and distances for plotting"
)
parser.add_argument(
    '--low-frequency-cutoff',
    type=float,
    default=1e-6,
    help="Low frequency cutoff for calculating SNR, in Hz. Default 1e-6"
)
parser.add_argument(
    '--parallelize-range',
    default='0/1'
)
parser.add_argument(
    '--times',
    nargs='+',
    type=float,
    help="Specific times to calculate, seconds."
)

args = parser.parse_args()

if args.low_frequency_cutoff < delta_f:
    args.low_frequency_cutoff = delta_f

# Open the PSD, load as PyCBC object
psd = pycbc.psd.from_txt(
    args.psd_file,
    int(f_nyquist/delta_f),
    delta_f,
    low_freq_cutoff,
    is_asd_file=False
)

if args.log_mass_spacing:
    masses = np.logspace(
        np.log10(args.mass_range[0]),
        np.log10(args.mass_range[1]),
        args.n_mass_points,
    )
else:
    masses = np.linspace(
        args.mass_range[0],
        args.mass_range[1],
        args.n_mass_points,
    )

times = np.array(args.times)

shared_waveform = {
    'ifos':['LISA_A','LISA_E','LISA_T'],
    'approximant':'BBHX_PhenomD',
    'spin1z':0,
    'spin2z':0,
    'delta_f':delta_f,
    'distance':nominal_distance,
    't_obs_start':tlen,
    'tc':tlen - 86400,
    'f_lower':low_freq_cutoff,
    't_offset':0,
    'tdi': '1.5',
}

def get_sensitive_distance(t, m):
    """
    Get the sensitive distance given the masses
    at the time-before-merger considered
    """
    # Calculate the time-frequency track in order
    # to convert and get the right upper frequency cutoff
    if t == 0:
        freq = f_nyquist
    else:
        track_t, track_f = get_inspiral_tf(
            0, m, m, 0, 0,
            args.low_frequency_cutoff,
            approximant='SPAtmplt'
        )
        freq = np.interp(-t, track_t, track_f)

        if freq < (args.low_frequency_cutoff + 2 * delta_f):
            # This frequency / time before merger is too low
            # frequency, and won't give sensible results
            return np.nan
    
    # Using a standard seed keeps the sky points the same for
    # all points and any repeats
    np.random.seed(24601)
    sum_sigsq = 0
    for _ in range(args.n_sky_points):
        wf = pycbc.waveform.get_fd_det_waveform(
            **shared_waveform,
            mass1=m,
            mass2=m,
            f_final=freq,
            coa_phase=np.random.uniform(0, np.pi * 2),
            inclination=np.arccos(np.random.uniform(0,1)),
            polarization=np.random.uniform(0, np.pi * 2),
            eclipticlatitude=np.arccos(np.random.uniform(0,1)),
            eclipticlongitude=np.random.uniform(0, np.pi * 2),
        )

        for channel in ['A','E']:
            sig = pycbc.filter.sigma(
                wf['LISA_' + channel],
                psd[:len(wf['LISA_' + channel])],
                low_frequency_cutoff=args.low_frequency_cutoff,
                high_frequency_cutoff=freq
            )
            sum_sigsq += sig ** 2

    mean_sigsq = sum_sigsq / args.n_sky_points
    if mean_sigsq > 0:
        dist_out = np.sqrt(mean_sigsq) / 10 * (nominal_distance / 1000)
    else:
        dist_out = np.nan
    
    return dist_out

masses_all, times_all = np.meshgrid(masses, times)

masses_all = masses_all.flatten()
times_all = times_all.flatten()

ids = np.arange(len(masses_all))

part = float(args.parallelize_range.split('/')[0])
pieces = float(args.parallelize_range.split('/')[1])
imin = int(masses_all.size / float(pieces) * part)
imax = int(masses_all.size / float(pieces) * (part + 1))

np.random.seed(0)
np.random.shuffle(ids)
ids = ids[imin:imax]

masses_all = masses_all[ids]
times_all = times_all[ids]

dists = np.zeros_like(times_all)

m_t = list(zip(masses_all, times_all))
for i, (m, t) in enumerate(tqdm(m_t)):

    dists[i] = get_sensitive_distance(t, m)
    continue

with h5py.File(args.output_file, 'w') as out_f:
    out_f['mass'] = masses_all.flatten()
    out_f['time'] = times_all.flatten()
    out_f['distance'] = dists
    out_f.attrs['mass_range'] = args.mass_range
    out_f.attrs['times'] = args.times
