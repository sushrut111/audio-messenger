import reed as rs
import gen
import array

R = rs.RSCodec(10)
BASE_FREQ = 1000
STEP = 30
HS_START = 10000
HS_STOP = 10500

def encode_byte(x):
	return BASE_FREQ + x*STEP

def modulate(msg):
	encoded = R.encode(msg)
	ba = bytearray(encoded)
	for i in ba:
		print i
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

SEND = modulate("9403039900")
file = gen.write_file(SEND)
print SEND
encode_msg = demodulate(gen.read_file(file))
decoded_msg = R.decode(encode_msg)
print decoded_msg
# print SEND

