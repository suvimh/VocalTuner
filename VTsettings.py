# VocalTuner Application
# This application analyses the timbre and pitch characteristics of an input sound.
# The purpose of the VocalTuner is to assist vocalists when practicing control over their vocal pitch and timbre
# Developed by Suvi Häärä
# 2021-2022

import pyaudio
from PyQt5 import QtCore

# General settings to setup
f_s = 44100  # sample rate in Hz
WINDOW_SIZE = 4096  # number of data points to read at a given time (must be power of two and larger than sub chunk)
SUB_CHUNK = 3969  # number of data points to create file of same length as test files - 0.2s files
CHANNEL_NUM = 1  # number of channels used
SAMPLE_FORMAT = pyaudio.paInt16  # 16 bit audio
THRESHOLD_PERCENTAGE = 0.02  # percentage of max peak that will determine cut-point for peak bandwidth
K_VALUE = 3  # set k number of neighbours for knn

DEF_TEXT = "color: black; background: none;"  # default text colour setting
DEF_CAP = QtCore.Qt.SquareCap  # default pen cap setting
DEF_JOIN = QtCore.Qt.BevelJoin  # default pen cap join style

# variables for display settings without detected input over threshold
DEF_TIMBRE = 'none'
NO_INPUT = -1
DISPLAY_NONE = ' - '
