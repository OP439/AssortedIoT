import serial
import time

ser = serial.Serial("/dev/ttyUSB0", 115200)

ser.write(str.encode("M84 ;\r\n"))


ser.write(str.encode("M105 ;\r"))
time.sleep(1)
while True:
	line = ser.readline()
	if not line.strip():  # evaluates to true when an "empty" line is received
		var = raw_input()
		if var:
			ser.write(var)
	else:
		print(line)
