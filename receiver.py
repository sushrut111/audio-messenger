from shared_rs import coder
import numpy as np
import pyaudio
from constants import *

library = 'pyaudio'

def dominant(frame_rate, chunk):
    """
    Calculate the fast fourier transform to get the dominant frequency
    """
    w = np.fft.fft(chunk)
    freqs = np.fft.fftfreq(len(chunk))

    peak_coeff = np.argmax(np.abs(w))
    peak_freq = freqs[peak_coeff]
    return abs(peak_freq * frame_rate) # in Hz

def match(freq1, freq2):
    """
    Due to noise considerations, consider frequencies with difference
    less than 20Hz as equal.
    """
    return abs(freq1 - freq2) < 20

def extract_packet(freqs):
    """
    Take out the valid frequencies from the received signals
    """
    freqs = freqs[::2]
    bit_chunks = [int(f) for f in freqs if f>1000 and f<10000]
    return bit_chunks

def demodulate(recarr):
    """
    Demodulate the modulated received message
    :param recarr: This is list of frequencies
    :returns : bytearray that can be decoded with rs decoder
    """
    rec = [(f-START_HZ)/STEP_HZ for f in recarr]
    rec = [int(x) if (0 <= x and 256 > x) else 0 for x in rec]
    return bytearray(rec)

class Message(object):
    """docstring for Message"""
    def __init__(self,msgs_len):
        super(Message, self).__init__()
        self.message = ""
        self.msgs_len = msgs_len
        self.print_warning = False

    def add_message(self, msg):
        """
        The message comes in chunks, keep appending incoming chunks to form 
        the complete messae
        :param msg str: The message received.
        """
        if(msg == ''):
            pass
        else:
            self.message = self.message + msg
        
        self.msgs_len = self.msgs_len - 1
        if self.msgs_len == 0:
            self.show_message()
            if self.print_warning:
                print("A part of message was lost due to noise!")
    
    def show_message(self):
        """
        Method to print the message on the terminal
        """
        design = "#########"
        for i in range(len(self.message)):
            design += "#"
        print(design)
        print("Message: " + self.message)
        print(design)

def listen_all(frame_rate=SAMPLING_RATE, interval=FREQ_DURATION):
    """
    Method to start listening with pyaudio library.
    """
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
    """
    The method to keep the mic open for listening.
    :param micdata: mic object
    """

    # Get the mic from the micdata object
    mic = micdata[0]

    # Identify the mic's frames per buffer
    frames_per_buffer = micdata[1]

    # Flag to know whether reception has started
    in_packet = False

    # This will hold the package that is currently being received
    packet = []
    print("Listening...")

    # Part of receiving protocol. This will be set to True when reception starts
    msg_started = False
    messages = ""
    messages_len = 0
    while True:
        # Keep looping
        data = mic.read(frames_per_buffer)
        chunk = np.frombuffer(data, dtype=np.int16)

        # Find the dominant frequency.
        dom = dominant(SAMPLING_RATE, chunk)

        if in_packet and match(dom, HANDSHAKE_END_HZ):
            # Check if reception is completed and process the packet
            # if reception has been ended
            

            byte_stream = extract_packet(packet)
            encoded_msg = demodulate(byte_stream).decode('utf-8')
            try:
                this_msg, _ = coder.decode(encoded_msg)
            except Exception as e:
                this_msg = ''
                print(e)
            
            
            
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
            # Append incoming frequencies as this is in the packet
            packet.append(dom)

        elif match(dom, HANDSHAKE_START_HZ):
            # Handshake start received, get ready to receive packet
            in_packet = True


if __name__ == '__main__':
    # Entry point

    # Obtain the microphone to listen from
    micdata = get_mic()

    # Enter into the infinite loop to listen to the signals
    start_listening(micdata)