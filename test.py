import  RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(21, GPIO.OUT)
GPIO.setup(12, GPIO.OUT)
GPIO.setup(16, GPIO.OUT)
GPIO.output(16, GPIO.HIGH)
GPIO.output(21, GPIO.HIGH)
GPIO.output(12, GPIO.HIGH)
import requests
import face_recognition
import cv2
import time
import json
import picamera
import numpy as np
from PIL import Image
from datetime import datetime, timedelta
import os
import io
auth_token='775f99089e161eb3fe19f2ff8f76a765f204c59a'
header = {'Authorization': 'Token ' + auth_token}

camera = picamera.PiCamera()
camera.resolution = (320, 240)
frame = np.empty((240,320,3),dtype=np.uint8)
GPIO.output(12, GPIO.LOW)
GPIO.output(16, GPIO.LOW)
GPIO.output(21, GPIO.LOW)
time.sleep(0.2)
while True:
	r = requests.post("http://192.168.0.107:80/api/active/devices/", headers=header, data={'device': "000001"})
	print(r.text)
	json_data = json.loads(r.text)
	GPIO.output(12, GPIO.LOW)
	if json_data['success']=="YES":
		break
	else:
		time.sleep(1)
		GPIO.output(12, GPIO.HIGH)
		time.sleep(1)
for i in range(5):
	GPIO.output(16, GPIO.HIGH)
	GPIO.output(21, GPIO.HIGH)
	GPIO.output(12, GPIO.HIGH)
	time.sleep(0.2)
	GPIO.output(12, GPIO.LOW)
	GPIO.output(16, GPIO.LOW)
	GPIO.output(21, GPIO.LOW)
	time.sleep(0.2)

error_counter = 0
while True:
	try:
		#print("frame creation")
		camera.capture(frame, format="rgb", use_video_port=True)
		face_locations = face_recognition.face_locations(frame)
		face_encodings = face_recognition.face_encodings(frame, face_locations)
		if face_locations: 
			GPIO.output(16, GPIO.HIGH)
			image = Image.fromarray(frame)
			#print("image creation")
			imgByteArr = io.BytesIO()
			image.save(imgByteArr, format='jpeg')
			imgByteArr = imgByteArr.getvalue()
			#print("pre request")
			r = requests.post("http://192.168.0.107:80/api/facerec/", headers=header, data={'idn':'000001'}, files={'photo': imgByteArr})		
			#print(r.text)
			json_data = json.loads(r.text)
			if json_data['success']=="YES": 
				GPIO.output(16, GPIO.LOW)
				GPIO.output(21, GPIO.HIGH)
				r = requests.post("http://192.168.0.107:80/api/checks/", 
					headers=header, 
					files={'photo': imgByteArr}, 
					data={'worker':json_data['worker'], 
						'device':'000001',
						'datetime':str(datetime.now())})
				print(r.text)
			else:
				GPIO.output(16, GPIO.LOW)
				GPIO.output(12, GPIO.HIGH)
				r = requests.post("http://192.168.0.107:80/api/checks/", 
					headers=header, 
					files={'photo': imgByteArr}, 
					data={'worker':None,  
						'device':'000001',
						'datetime':str(datetime.now())})
			#print("last print")
			GPIO.output(21, GPIO.LOW)
			GPIO.output(12, GPIO.LOW)
		error_counter = 0
	except KeyboardInterrupt:
		GPIO.output(21, GPIO.LOW)
		GPIO.output(12, GPIO.LOW)
		GPIO.output(16, GPIO.LOW)
		break
	except:
		error_counter +=1
		GPIO.output(21, GPIO.HIGH)
		GPIO.output(12, GPIO.HIGH)
		GPIO.output(16, GPIO.HIGH)
		time.sleep(2)
		GPIO.output(21, GPIO.LOW)
		GPIO.output(12, GPIO.LOW)
		GPIO.output(16, GPIO.LOW)
		if error_counter>8: 
			os.system("reboot")
