# VocalTuner Application
# This application analyses the timbre and pitch characteristics of an input sound.
# The purpose of the VocalTuner is to assist vocalists when practicing control over their vocal pitch and timbre
# Developed by Suvi Häärä
# 2021-2022

import numpy as np
import pyaudio
import librosa
import wave
from sklearn.neighbors import KNeighborsClassifier
import VTclass
import VTdata
import VTsettings
import VTsetup


def get_mfccs(file):
    audio_ts, sr = librosa.load(VTsetup.PATH + file)
    mfccs = librosa.feature.mfcc(y=audio_ts, sr=sr, n_mfcc=13)
    return mfccs.reshape(1, -1)


# assigns the input file with timbre labels using sklearn KNN algorithm
def get_timbre_knn(file):
    input_mfcc = get_mfccs(file)
    # knn for colour label
    knn_c = KNeighborsClassifier(n_neighbors=VTsettings.K_VALUE)
    knn_c.fit(VTdata.MY_DATA_VOL.data, VTdata.MY_DATA_COL.target)
    predicted_c = knn_c.predict(input_mfcc)
    # knn for volume label
    knn_v = KNeighborsClassifier(n_neighbors=VTsettings.K_VALUE)
    knn_v.fit(VTdata.MY_DATA_VOL.data, VTdata.MY_DATA_COL.target)
    predicted_v = knn_v.predict(input_mfcc)

    return predicted_c, predicted_v


# finds the start and end of the 1st peak of the fft based on the threshold value
def find_peak_start_end(complex_data_arr, freq_arr):
    magnitudes = abs(complex_data_arr)
    maxm = max(magnitudes)  # find maximum peak value of whole spectrum
    # find the start of peak one based on percentage of maximum peak value
    peak_1_start = next(x for x, val in enumerate(magnitudes) if val > VTsettings.THRESHOLD_PERCENTAGE * maxm)
    i = 0
    # find end of 1st peak
    while True:
        i += 1
        if magnitudes[peak_1_start + i] <= VTsettings.THRESHOLD_PERCENTAGE * maxm:
            peak_1_end = peak_1_start + i
            break
    # find start of 2nd peak using end of 1st peak
    i = 0
    while True:
        if magnitudes[peak_1_end + i] >= VTsettings.THRESHOLD_PERCENTAGE * maxm:
            low_index = peak_1_end + i
            break
        i += 1
    # find end of 2nd peak
    i = 0
    while True:
        if magnitudes[low_index + i] <= VTsettings.THRESHOLD_PERCENTAGE * maxm:
            high_index = low_index + i
            break
        i += 1

    VTclass.Peak.low_freq = freq_arr[low_index]  # using second peak values - no longer using averages
    VTclass.Peak.high_freq = freq_arr[high_index]  # using second peak values - no longer using averages


# open audio stream and record a small chunk for timbre analysis
def audio_in():
    filename = "input_rec.wav"
    # start pyaudio class
    audio = pyaudio.PyAudio()
    # open audio stream using default input device
    stream = audio.open(format=VTsettings.SAMPLE_FORMAT, channels=VTsettings.CHANNEL_NUM, rate=VTsettings.f_s, input=True, frames_per_buffer=VTsettings.WINDOW_SIZE)
    # read data into a numpy array holding a single read of audio data
    data = np.frombuffer(stream.read(VTsettings.WINDOW_SIZE), dtype=np.int16)

    record_data = data[:VTsettings.SUB_CHUNK]
    # close the audio stream
    stream.stop_stream()
    stream.close()

    recording = wave.open(VTsetup.PATH + filename, 'wb')
    recording.setnchannels(VTsettings.CHANNEL_NUM)
    recording.setsampwidth(audio.get_sample_size(VTsettings.SAMPLE_FORMAT))
    recording.setframerate(VTsettings.f_s)
    recording.writeframes(b''.join(record_data))
    recording.close()

    return filename


# open audio stream and find frequency when exceed set amplitude
# adapted and modified from
# Harden, S.W., 2016. Realtime Audio Visualization in python.
# SWHarden.com. Available at:
# https://swharden.com/blog/2016-07-19-realtime-audio-visualization-in-python/
# [Accessed November 10, 2021].
def find_freq():
    # start pyaudio class
    audio = pyaudio.PyAudio()
    # open audio stream using default input device
    stream = audio.open(format=VTsettings.SAMPLE_FORMAT, channels=VTsettings.CHANNEL_NUM, rate=VTsettings.f_s, input=True, frames_per_buffer=VTsettings.WINDOW_SIZE)
    # read data into a numpy array holding a single read of audio data
    data = np.frombuffer(stream.read(VTsettings.WINDOW_SIZE), dtype=np.int16)
    # check data amplitude
    mean_amp = sum(abs(data)) / len(data)
    if mean_amp > 50:
        # smooth the signal by windowing using a Hanning window
        data = data * np.hanning(len(data))
        # take absolute value of fft
        fft = abs(np.fft.fft(data).real)
        # keep only first half of fft output
        fft = fft[:int(len(fft) / 2)]
        # return DFT sample frequencies
        freq_spectrum = np.fft.fftfreq(VTsettings.WINDOW_SIZE, 1.0 / VTsettings.f_s)
        # keep only first half
        freq_spectrum = freq_spectrum[:int(len(freq_spectrum) / 2)]

        # store value of the highest frequency in the attained frequency array
        note_freq = freq_spectrum[np.where(fft == np.max(fft))[0][0]] + 1

        # find vibrato based on input data
        fft = np.fft.fft(data)
        fft_freq = np.fft.fftfreq(len(data))  # calculate frequency values associates with fft bins
        freq_hz = abs(fft_freq * VTsettings.f_s)

        find_peak_start_end(fft, freq_hz)

    else:
        note_freq = VTsettings.NO_INPUT

    # close the audio stream
    stream.stop_stream()
    stream.close()

    return note_freq
