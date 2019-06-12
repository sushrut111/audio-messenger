import reed as rs
import audio_generator as gen
import array
import argparse
import pyaudio
import wave
R = rs.RSCodec(10)
BASE_FREQ = 1000
STEP = 30
HS_START = 10000
HS_STOP = 10500
MSGLEN = 8 #message of MSGLEN characters will be sent in one go

def encode_byte(x):
	return BASE_FREQ + x*STEP

def modulate(msg):
	encoded = R.encode(msg)
	ba = bytearray(encoded)
	sendarr = []
	sendarr.append(HS_START)
	for onebyte in ba:
		sendarr.append(encode_byte(onebyte))
	sendarr.append(HS_STOP)
	return sendarr

def demodulate(recarr):
	print recarr
	recarr = recarr[1:]
	recarr = recarr[:-1]
	rec = [(f-BASE_FREQ)/STEP for f in recarr]
	msg = ''.join(chr(i) for i in rec)
	return bytearray(msg)

def play_audio(filename):
	print "Transmitting..."
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
	print SEND

def transmit_wrapper(fullmessage):	
	message_array = split2len(fullmessage,MSGLEN)
	msgs_length = len(message_array)

	#First transmit the number of transmissions for receiver to know how long to receive for single message
	transmit(str(msgs_length)) 

	# Start transmitting message array
	for message in message_array:
		transmit(message)

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("message", help="Enter the message to be sent!")
	args = parser.parse_args()
	message = args.message
	transmit_wrapper(message)

if __name__ == '__main__':

	main()
