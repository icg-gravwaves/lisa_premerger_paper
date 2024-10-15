
import numpy as np
import argparse
import logging

from scipy.constants import speed_of_light

parser=argparse.ArgumentParser()
parser.add_argument('--tdi-generation', type=int, choices=[1,2], required=True)
parser.add_argument('--low-freq-relaxation', action='store_true',
                    help="Apply test-mass relaxation below 1e-4Hz (pessimistic)")
parser.add_argument('--lower-frequency-limit', type=float, default=1e-7)
parser.add_argument('--frequency-spacing', type=float, default=1e-6)
parser.add_argument('--nyquist-frequency', type=float, default=2)
args = parser.parse_args()

logging.basicConfig(format='%(asctime)s %(levelname)s : %(message)s')
logging.getLogger().setLevel(logging.INFO)

# some constants

# Multiplicative factor for the strain conversion
# https://gitlab.in2p3.fr/lisa-simulation/instrument/-/blob/e83f84d/lisainstrument/instrument.py#L130
central_laser_freq = 2.816E14 

A_oms = 7.9e-12 # m Hz^-0.5
fknee_oms = 2e-3 # Hz

A_tm = 2.4e-15 # m Hz^-0.5 / s^2
fknee_tm = 0.4e-3 # Hz

arm_length = 8.323804616176023 # seconds

if args.low_freq_relaxation:
    f_relax = 1e-4 # Hz
else:
    f_relax = None

# Frequencies to calculate the model at
freqs = np.linspace(
    args.lower_frequency_limit,
    args.nyquist_frequency,
    int((args.nyquist_frequency - args.lower_frequency_limit) / args.frequency_spacing)
)
# convenience parameter
wL = 2 * np.pi * freqs * arm_length

# Conversion to TDI
# TDI transfer functions from https://arxiv.org/pdf/2211.02539.pdf
# Note here we include division by the laser frequency simply because it's an easy place to put it
tdi_common = 4 * np.sin(wL) ** 2
# Unitless

if args.tdi_generation == 2:
    tdi_common *= 4 * np.sin(2 * wL) ** 2
    # Unitless

def psd_oms_hz(A_oms, fknee_oms):
    # Model of the OMS noise
    oms_m = \
        A_oms ** 2 * (1 + (fknee_oms / freqs) ** 4)
    # Units (m^2 / Hz)

    oms_hz = oms_m * \
        (2 * np.pi * freqs * central_laser_freq / speed_of_light) ** 2

    # Units m^2 / Hz * (Hz * Hz / (m s^-1)) ** 2
    # = m^2 * Hz ^ 3 / (m^2 * s^-2)
    # = Hz^3 * s^2 = Hz

    return oms_hz


def psd_tm_hz(A_tm, fknee_tm, f_relax=None):
    # Model of the test mass noise
    tm_acc = \
        A_tm ** 2 * (1 + (fknee_tm / freqs) ** 2)
    # Units m^2 s^-4 Hz^-1

    if f_relax is not None:
        tm_acc *= 1 + (f_relax / freqs) ** 4
        # Unitless

    tm_hz = tm_acc * \
            (2 * central_laser_freq / (2 * np.pi * speed_of_light * freqs)) ** 2

    # m^2 s^-4 Hz^-1 * (Hz / (m s ^-1) / Hz)^2
    # = m^2 s^-4 Hz^-1 m^-2 * s^2
    # = Hz^-1 s^-4 s^2 = Hz^-1 s^-2 = Hz

    return tm_hz

def xyz_model_oms(A_oms, fknee_oms):
    # 2211.02539 Table II Backlink RFI PSD
    oms_transfer = 4 * tdi_common
    # Unitless
    
    return psd_oms_hz(A_oms, fknee_oms) * oms_transfer


def xyz_model_tm(A_tm, fknee_tm, f_relax=1e-4):
    # 2211.02539 Table II backlink TMI PSD
    tm_transfer = \
        tdi_common * (3 + np.cos(2 * wL))
    # Unitless

    return psd_tm_hz(A_tm, fknee_tm, f_relax=f_relax) * tm_transfer


def ae_model_oms(A_oms, fknee_oms):
    # 2211.02539 Table III backlink RFI PSD A&E 
    oms_transfer = \
        2 * tdi_common * (2 + np.cos(wL))
    # Unitless
    
    return psd_oms_hz(A_oms, fknee_oms) * oms_transfer


def ae_model_tm(A_tm, fknee_tm, f_relax=1e-4):
    # 2211.02539 Table III backlink TMI PSD A&E
    tm_transfer = \
        tdi_common * (3 + 2 * np.cos(wL) + np.cos(2 * wL))
    # Unitless

    return psd_tm_hz(A_tm, fknee_tm, f_relax=f_relax) * tm_transfer

def t_model_oms(A_oms, fknee_oms):
    # 2211.02539 Table III PSD T, backlink RFI
    oms_transfer = \
        4 * tdi_common * (1 - np.cos(wL))
    # Unitless
    
    return psd_oms_hz(A_oms, fknee_oms) * oms_transfer


def t_model_tm(A_tm, fknee_tm, f_relax=None):
    # 2211.02539 Table III PSD T, test mass, None
    tm_transfer = \
        8 * tdi_common * np.sin(wL / 2) ** 4
    # Unitless

    return psd_tm_hz(A_tm, fknee_tm, f_relax=f_relax) * tm_transfer



# Combine the models - this is a PSD, so we add them
#logging.info("Calculating XYZ model")
#model_oms_xyz = xyz_model_oms(A_oms, fknee_oms) / central_laser_freq ** 2
#model_tm_xyz = xyz_model_tm(A_tm, fknee_tm, f_relax=f_relax) / central_laser_freq ** 2
#model_tot_xyz = model_oms_xyz + model_tm_xyz

logging.info("Calculating AE model")
model_oms_ae = ae_model_oms(A_oms, fknee_oms) / central_laser_freq ** 2
model_tm_ae = ae_model_tm(A_tm, fknee_tm, f_relax=f_relax) / central_laser_freq ** 2
model_tot_ae = model_oms_ae + model_tm_ae
logging.info("Calculating T model")
model_oms_t = t_model_oms(A_oms, fknee_oms) / central_laser_freq ** 2
model_tm_t = t_model_tm(A_tm, fknee_tm, f_relax=f_relax) / central_laser_freq ** 2
model_tot_t = model_oms_t + model_tm_t 

model_tot = {
#    'XYZ': model_tot_xyz,
    'AE': model_tot_ae,
    'T': model_tot_t,
}

for model in ['AE', 'T']: #, 'XYZ']:
    logging.info("Saving modelled %s PSD", model)
    model_out_filename = f'model_{model}_TDI{args.tdi_generation}'

    if args.low_freq_relaxation:
        model_out_filename += '_pessimistic'
    else:
        model_out_filename += '_optimistic'

    model_out_filename += '.txt'
    logging.info(model_out_filename)

    model_save = np.array([*zip(freqs, model_tot[model])])
    np.savetxt(model_out_filename, model_save)

logging.info("Done")

