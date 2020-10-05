import audio_generator as gen
import array
import argparse
import pyaudio
import wave
from shared_rs import coder
from constants import *


def encode_byte(x):
	''' This function encodes the frequency of the audio.
	BASE_FREQ and STEP_HZ are constants defined in constants.py '''
	return BASE_FREQ + x*STEP_HZ

def modulate(msg):
	''' The parameter of the function is first encoded to utf-8 and then 
	every byte in the bytearray is encoded using the encode_byte function. ''' 
	encoded = coder.encode(msg)
	ba = bytearray(encoded, 'utf-8')
	sendarr = []
	sendarr.append(HS_START)
	for onebyte in ba:
		sendarr.append(encode_byte(onebyte))
	sendarr.append(HS_STOP)
	return sendarr

def play_audio(filename):
	''' The audio is played using pyaudio.Pyaudio.open() where the wave file of the audio
	 is input as read-binary. '''

	print("Transmitting...")
	chunk = 1024  

	f = wave.open(filename,"rb")  
	# instantiation of Pyaudio
	# this sets up the  portaudio system
	p = pyaudio.PyAudio()  

	# stream is opened
	stream = p.open(format = p.get_format_from_width(f.getsampwidth()),  
	                channels = f.getnchannels(),  
	                rate = f.getframerate(),  
	                output = True)
	# reading data in frames, the size of chunk variable
	data = f.readframes(chunk)

	''' stream.write() is used to play audio by writing audio data into the stream
	    stream.stop_stream() is used to pause the recording
	    stream.close() is used to terminate the stream
	    p.terminate() is used to terminate the portaudio session  '''  
	while data:  
	    stream.write(data)  
	    data = f.readframes(chunk)  
	stream.stop_stream()  
	stream.close()  
	p.terminate()   

def split2len(s, n):
    ''' This function splits the parameter s into groups of size n '''
    def _f(s, n):
        while s:
            yield s[:n]
            s = s[n:]
    return list(_f(s, n))

def transmit(message):
	''' The message is modulated and played '''
	SEND = modulate(message)
	file = gen.write_file(SEND)	
	play_audio(file)
	print(SEND)

def transmit_wrapper(fullmessage):
	# fullmessage is split into packets of size MSGLEN	
	message_array = split2len(fullmessage,MSGLEN)
	msgs_length = len(message_array)
	# length of list message_array is used to define the input for transmit function
	initiate_handshake = str(msgs_length) + START_MSG
	transmit(initiate_handshake)
	# Start transmitting message array
	for message in message_array:
		transmit(message)
	transmit(END_MSG)

def main():
	parser = argparse.ArgumentParser()
	# add_argument fills ArgumentParser with information about program arguments
	parser.add_argument("message", help="Enter the message to be sent!")
	args = parser.parse_args()
	message = args.message
	transmit_wrapper(message)

if __name__ == '__main__':

	main()
