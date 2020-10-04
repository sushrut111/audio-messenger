import reed as rs
import numpy as np
import pyaudio
from constants import *

library = ''

try:
    import alsaaudio
except Exception as e:
    library = 'pyaudio'
else:
    library = 'alsaaudio'
    

R = rs.RSCodec(10)

def dominant(frame_rate, chunk):
    w = np.fft.fft(chunk)
    freqs = np.fft.fftfreq(len(chunk))

    peak_coeff = np.argmax(np.abs(w))
    peak_freq = freqs[peak_coeff]
    return abs(peak_freq * frame_rate) # in Hz

def match(freq1, freq2):
    return abs(freq1 - freq2) < 20

def extract_packet(freqs):
    freqs = freqs[::2]
    bit_chunks = [int(f) for f in freqs if f>1000 and f<10000]
    return bit_chunks

def returnchar(c):
    c = int(c)
    if c<256 and c>=0 :
        return chr(c)
    else :
        if c<0:
            return chr(0)
        return chr(255)

def demodulate(recarr):
    rec = [(f-START_HZ)/STEP_HZ for f in recarr]
    msg = ''.join(returnchar(i) for i in rec)
    return bytearray(msg, 'utf-8')

class Message(object):
    """docstring for Message"""
    def __init__(self,msgs_len):
        super(Message, self).__init__()
        self.message = ""
        self.msgs_len = msgs_len
        self.print_warning = False

    def add_message(self,msg):
        if(msg == ''):
            pass
        else:
            self.message = self.message + msg
        
        self.msgs_len = self.msgs_len - 1
        if self.msgs_len == 0:
            self.show_message()
            if self.print_warning:
                print("A part of messages were lost due to noise!")
    
    def show_message(self):
        design = "#########"
        for i in range(len(self.message)):
            design += "#"
        print(design)
        print("Message: " + self.message)
        print(design)
def listen_all(frame_rate=SAMPLING_RATE, interval=FREQ_DURATION):
    frames_per_buffer = int(round((interval / 2) * frame_rate))
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = frame_rate
    RECORD_SECONDS = 5
    WAVE_OUTPUT_FILENAME = "output.wav"

    p = pyaudio.PyAudio()

    mic = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=frames_per_buffer)
    return (mic,frames_per_buffer)

def listen_linux(frame_rate=SAMPLING_RATE, interval=FREQ_DURATION):
    mic = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NORMAL)
    mic.setchannels(1)
    mic.setrate(frame_rate)
    mic.setformat(alsaaudio.PCM_FORMAT_S16_LE)
    num_frames = int(round((interval / 2) * frame_rate))
    mic.setperiodsize(num_frames)
    return (mic,frames_per_buffer)
    
def get_mic():
    if library == "alsaaudio":
        return listen_linux()
    else:
        return listen_all()

def start_listening(micdata):
    mic = micdata[0]
    frames_per_buffer = micdata[1]
    in_packet = False
    packet = []
    print("Listening...")
    msg_started = False
    messages = ""
    messages_len = 0
    while True:
        data = mic.read(frames_per_buffer)
        chunk = np.fromstring(data, dtype=np.int16)
        dom = dominant(SAMPLING_RATE, chunk)
        if in_packet and match(dom, HANDSHAKE_END_HZ):
            ############## decode block ###############
            byte_stream = extract_packet(packet)
            encoded_msg = demodulate(byte_stream)
            try:
                this_msg = R.decode(encoded_msg)
            except Exception as e:
                this_msg = ''
                print(e)
            ###########################################
            ############## synthesis block ############
            if START_MSG in this_msg:
                print("Reception started")
                msgs_len = int(this_msg.split('{')[0])
                msg_started = True
                message_holder = Message(msgs_len)
            elif END_MSG in this_msg:
                msg_started = False
                print("Listening...")
            else:
                print("Received : "+this_msg)
                print("Please wait for reception to complete!")
                print("======================================")
                if msg_started:
                    message_holder.add_message(this_msg)

            packet = []
            in_packet = False

        elif in_packet:
            packet.append(dom)
        elif match(dom, HANDSHAKE_START_HZ):
            in_packet = True


if __name__ == '__main__':
    micdata = get_mic()
    start_listening(micdata)