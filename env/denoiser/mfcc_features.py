from python_speech_features import *
import numpy as np
import librosa
from scipy.io import wavfile
import sys


def get_mfcc_feature(filename):
    '''
    Use Python_Speech_Features package to calculate the mfcc feature.

    :param filename: path of the input audio.
    :return: mfcc feature of the input audio.
    '''

    fs, signal = wavfile.read(filename)  # 音频采样率,音频数据numpy数组

    if len(signal.shape) != 1:  # if not mono sound
        signal = signal[:, 0]  # choose left channel

    mfcc_feature = mfcc(signal, samplerate=fs,numcep=13, winlen=0.025, winstep=0.01,nfilt=26, nfft=512, lowfreq=0, highfreq=None, preemph=0.97)
    d_mfcc_feat = delta(mfcc_feature, 1)
    d_mfcc_feat2 = delta(mfcc_feature, 2)

    if len(mfcc_feature) == 0:
        print("ERROR.. failed to extract mfcc feature", file=sys.stderr)

    # mfcc_feature = np.hstack((mfcc_feature, d_mfcc_feat, d_mfcc_feat2))
    return mfcc_feature


def lib_mfcc_feature(filename, delta=2):
    '''
    Use Librosa package to calculate the mfcc feature.

    :param filename: path of the input audio.
    :param delta: take the delta times derivatives, default=2.
    :return: mfcc feature of the input audio.
    '''

    x, sample_rate = librosa.load(filename)
    # mfcc = librosa.feature.mfcc(y=x, sr=sample_rate, n_mfcc=39)
    # mfcc_delta = librosa.feature.delta(mfcc, delta=delta)   # 若设置mode ='nearest'会损失精度
    # return mfcc_delta.T
    # mfcc = librosa.feature.mfcc(y=x, sr=sample_rate, n_mfcc=20)
    mfcc = librosa.feature.mfcc(y=x, sr=sample_rate, n_mfcc=13)
    return mfcc.T
