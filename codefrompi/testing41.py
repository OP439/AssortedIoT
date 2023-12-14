from picamera2 import Picamera2, Preview
from libcamera import controls
import time
import serial
import boto3
import paho.mqtt.client as mqtt



#init stuff

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    #client.subscribe("$SYS/#")
    client.subscribe('takepicture')
    client.subscribe('toggleheater')
    client.subscribe('rotateprinter')

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))






picam2 = Picamera2()
camera_config = picam2.create_preview_configuration({"size": (4608, 2592)})
picam2.configure(camera_config)
picam2.set_controls({"AfMode": controls.AfModeEnum.Manual, "LensPosition": 10.0})

s3 = boto3.resource("s3")
BUCKET = "oppiphotos"


ser = serial.Serial("/dev/ttyUSB0", 115200)
spaceheaterstatus = 0
rotateprintervar = 0



#stuff that runs over and over

def takepicture(client, userdata, msg):
	timeunix = time.time_ns()
	#originally -2 -> needs to change in case the operations happen at different nanoseconds
	timeunix = str(timeunix)[:-5]#need to remove last two characters for node red
	#print(timeunix)
	picam2.start()
	#print(timeunix)
	time.sleep(2)
	#print(timeunix)
	picam2.capture_file(f"{timeunix}.jpg")
	#print(timeunix)

	s3.Bucket(BUCKET).upload_file(f"{timeunix}.jpg", f"dump/file/{timeunix}.jpg", ExtraArgs={'ContentType': "image/jpeg"})
	client.publish('takepictureack', payload=timeunix)
	print(timeunix)
	print('pciture taken and added to bucket')
	print(str(client)+str(userdata)+str(msg.payload))
	
def toggleheater(client, userdata, msg):
	global spaceheaterstatus
	print("toggleheater callback")
	ser.write(str.encode("G91 ;\r\n"))
	ser.write(str.encode("G0 Y40 ;\r\n"))#one rotation
	spaceheaterstatus = not spaceheaterstatus #boolean on off
	print(int(spaceheaterstatus))#convert from true to 1
	client.publish('toggleheaterack', payload=int(spaceheaterstatus))
	
def rotateprinterfn(client, userdata, msg):
	global rotateprintervar
	print("rotateprinter callback")
	ser.write(str.encode("G91 ;\r\n"))
	ser.write(str.encode("G0 X15 ;\r\n"))#full rotation is about 95
	rotateprintervar += 1 #increment counter to show number of rotations
	print(rotateprintervar)
	client.publish('rotateprinterack', payload=rotateprintervar)


client = mqtt.Client()
client.on_connect = on_connect
client.message_callback_add("takepicture", takepicture)
client.message_callback_add("toggleheater", toggleheater)
client.message_callback_add("rotateprinter", rotateprinterfn)
client.on_message = on_message #final statement if not caught by earlier block

client.connect("oppi1.local", 1883, 60)

client.loop_forever()



