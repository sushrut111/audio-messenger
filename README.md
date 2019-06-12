# audio-messenger

Transfer texts between two python supported devices with speaker and mic. 
The message to be sent, modulates frequency of sine wave in audible range.
The message is encoded in the form of audio signals in this way and the signals are stored in .wav file.
When the .wav file is played and decoder is listening, message is decoded and displayed. This is something similar to audio QR.

# Installation:
  `pip install -r requirements.txt`

# How to use:
  - On one machine run main.py with `python main.py {message}` 
  - On another machine where message is to be received, run decoder.py with `python decoder.py`
  - The decoder file is infinite loop which keeps listeing continuosly. When main.py transmits audio decoder catches and decodes the message. Avoid noisy surroundings and keep the two devices close.
  
# How this works:
  - The message string is converted into bytestring and is fed to reed-solomon encoder which is error correctig encoding scheme. The encoder returns the encoded message. 
  - The with the interger values of characters of message, a sine wave is modulated. I am using base frequency (BASE_FREQ) of 1000Hz. And a STEP of 30 is used to modulation.
  The frequency corresponding to a particular ith character is calculated as :
  ```
  Fmsg[i] = BASE_FREQ + STEP * (message[i])
  ```
 
  - The encoded message array is prepended with a start frequency (HANDSHAKE) to let the receiver know that message started. The for similar purpose end frequency is appended to the message array.
  ```
  HS_START = 10000Hz
  HZ_STOP = 10500Hz
  ```
  
 - Now with this frequency array, a sine wave of duration 100ms is constructed for each frequency value.
 
 ```
 RATE = 44100 # Sampling rate
 t = np.linspace(0,0.1,RATE/10)
 # t contains the points at which values of sine are calculated. Thus we have RATE/10 i.e. 4410 samples in 100ms
 signal = np.sin(2*np.pi*Fmsg[i]*t)
 # this is the signal corresponding to one frequency.
 ```
- Similarly, signals for all the frequencies are calculated. The `signal` variable contains 4410 samples of sine wave of that particular frequency. As each frequency is played for 100ms, the total audio duration will be 100ms * the number of characters in reed-solomon encoded message. All the calculated samples are written in a .wav file and then the file is played back as transmission.

- The transmitted signal is recieved by the decoder. Decoder detects the HANDSHAKE_START (HS_START) frequency and starts noting down the subsequent receptions.

- When decoder recieves HS_STOP frequency, reception stops, the noted frequencies are filtered to remove frequencies which don't lie in out frequency range (Eg. Any frequency below 1000Hz)

- The original message code is calculated from each recieved frequency using:

```
message[i] = (Fmsg[i]-BASE_FREQ)/STEP
```
- The message array now contains reed-solomon encoded code with possible errors. The array is then fed to reed-solomon decoder which returns the decoded message if error correction is possible.


Inspired by: https://github.com/rraval/pied-piper
