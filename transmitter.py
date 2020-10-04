import audio_generator as gen
import array
import argparse
import pyaudio
import wave
from shared_rs import coder
from constants import *


def encode_byte(x):
	return BASE_FREQ + x*STEP_HZ

def modulate(msg):
	encoded = coder.encode(msg)
	ba = bytearray(encoded, 'utf-8')
	sendarr = []
	sendarr.append(HS_START)
	for onebyte in ba:
		sendarr.append(encode_byte(onebyte))
	sendarr.append(HS_STOP)
	return sendarr

def play_audio(filename):
	print("Transmitting...")
	chunk = 1024  

	f = wave.open(filename,"rb")  
	p = pyaudio.PyAudio()  
	stream = p.open(format = p.get_format_from_width(f.getsampwidth()),  
	                channels = f.getnchannels(),  
	                rate = f.getframerate(),  
	                output = True)  
	data = f.readframes(chunk)  
	while data:  
	    stream.write(data)  
	    data = f.readframes(chunk)  
	stream.stop_stream()  
	stream.close()  
	p.terminate()   

def split2len(s, n):
    def _f(s, n):
        while s:
            yield s[:n]
            s = s[n:]
    return list(_f(s, n))

def transmit(message):
	SEND = modulate(message)
	file = gen.write_file(SEND)	
	play_audio(file)
	print(SEND)

def transmit_wrapper(fullmessage):	
	message_array = split2len(fullmessage,MSGLEN)
	msgs_length = len(message_array)
	initiate_handshake = str(msgs_length) + START_MSG
	transmit(initiate_handshake)
	# Start transmitting message array
	for message in message_array:
		transmit(message)
	transmit(END_MSG)

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("message", help="Enter the message to be sent!")
	args = parser.parse_args()
	message = args.message
	transmit_wrapper(message)

if __name__ == '__main__':

	main()
