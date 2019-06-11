import reed as rs
import alsaaudio
import numpy as np

R = rs.RSCodec(10)
HANDSHAKE_START_HZ = 10000
HANDSHAKE_END_HZ = 10500
START_HZ = 1000
STEP_HZ = 30
BITS = 4

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

def demodulate(recarr):
    rec = [(f-START_HZ)/STEP_HZ for f in recarr]
    msg = ''.join(chr(i) for i in rec)
    return bytearray(msg)


def listen_linux(frame_rate=44100, interval=0.1):
    mic = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NORMAL)
    mic.setchannels(1)
    mic.setrate(44100)
    mic.setformat(alsaaudio.PCM_FORMAT_S16_LE)

    num_frames = int(round((interval / 2) * frame_rate))
    mic.setperiodsize(num_frames)

    in_packet = False
    packet = []
    print("Listening...")
    while True:
        l, data = mic.read()
        if not l:
            continue
        chunk = np.fromstring(data, dtype=np.int16)
        dom = dominant(frame_rate, chunk)
        if in_packet and match(dom, HANDSHAKE_END_HZ):
            byte_stream = extract_packet(packet)
            encoded_msg = demodulate(byte_stream)
            try:
                msg = R.decode(encoded_msg)
            except Exception as e:
                msg = ''
                print(e)
            print("Message:"+msg)
            packet = []
            in_packet = False
            print("Listening...")

        elif in_packet:
            packet.append(dom)
        elif match(dom, HANDSHAKE_START_HZ):
            in_packet = True

if __name__ == '__main__':

    listen_linux()
