from struct import pack
from math import sin, pi
import wave
import random
import numpy as np
from scipy.io import wavfile

RATE = 44100
maxVol=2**15-1 #maximum amplitude

def write_file(sendarr):
	'''
	len of arr is number of different frequencies we are sending
	each frequency sustains for 0.1 seconds
	thus the duration of audio will be len(sendarr)*0.1s
	'''
	filename = 'signal_sushrut.wav'
	t = np.linspace(0,0.1,RATE/10)
	signals = []
	wvData = ""
	for asample in sendarr:
		signal = maxVol * np.sin(2*np.pi*asample*t)
		for i in range(RATE/10):
			wvData +=pack('h',signal[i])
	'''
	now we have all the signals written in wavedata variable
	we write it into wav file
	'''
	wv = wave.open(filename, 'w')
	wv.setparams((1, 2, RATE, 0, 'NONE', 'not compressed'))
	wv.writeframes(wvData)
	wv.close()
	return filename

def read_file(filename):
	'''
	We have encoded one frequency per 100ms or 0.1s
	And the sampling rate is 44100. So in 0.1 seconds, we will have 4410 samples.
	'''
	fs, data = wavfile.read(filename)
	total_samples = len(data)
	total_frequencies = total_samples/4410
	frequency_wise_samples = np.split(data,total_frequencies)
	diff_freqs = []
	for onechunk in frequency_wise_samples:	
		fft = np.fft.fft(onechunk)
		freqs = np.fft.fftfreq(len(onechunk))
		peak_coeff = np.argmax(np.abs(fft))
		peak_freq = freqs[peak_coeff]
		diff_freqs.append(abs(int(peak_freq * fs)))
	return diff_freqs

