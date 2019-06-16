import  RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(21, GPIO.OUT)
GPIO.setup(12, GPIO.OUT)
GPIO.setup(16, GPIO.OUT)
GPIO.output(16, GPIO.HIGH)
GPIO.output(21, GPIO.HIGH)
GPIO.output(12, GPIO.HIGH)
import picamera
import requests
import face_recognition
import cv2
import time
import json
import numpy as np
from PIL import Image
from datetime import datetime, timedelta
import os
import io
import imutils
auth_token='4783cfba6b6e7a1bf30bcef75cc965f585375c7d'
header = {'Authorization': 'Token ' + auth_token}

camera = picamera.PiCamera()
camera.resolution = (320, 240)
frame = np.empty((240,320,3),dtype=np.uint8)
counter = 0
firstFrame = None
counter = 0 
counter_2 = 0
counter_3 = 0
movement_time_1 = datetime.now()
movement_time_2 = datetime.now()
Movement_B = False
time.sleep(10)
GPIO.output(12, GPIO.LOW)
GPIO.output(16, GPIO.LOW)
GPIO.output(21, GPIO.LOW)
error_counter=0
time.sleep(0.2)
while True:
#	try:
		r = requests.post("https://www.kora.work/api/active/devices/",
							headers=header,
							data={'device': "000001"})
		json_data = json.loads(r.text)
		print(r.text)
		GPIO.output(12, GPIO.LOW)
		if json_data['success']=="YES":
			break
		else:
			time.sleep(1)
			GPIO.output(12, GPIO.HIGH)
			time.sleep(1)
#	except KeyboardInterrupt:
#		GPIO.output(21, GPIO.LOW)
#		GPIO.output(12, GPIO.LOW)
#		GPIO.output(16, GPIO.LOW)
#		break
#	except:
#		error_counter +=1
#		GPIO.output(21, GPIO.HIGH)
#		GPIO.output(12, GPIO.HIGH)
#		GPIO.output(16, GPIO.HIGH)
#		time.sleep(2)
#		GPIO.output(21, GPIO.LOW)
#		GPIO.output(12, GPIO.LOW)
#		GPIO.output(16, GPIO.LOW)
#		if error_counter>8: 
#			os.system("reboot")

for i in range(5):
	GPIO.output(16, GPIO.HIGH)
	GPIO.output(21, GPIO.HIGH)
	GPIO.output(12, GPIO.HIGH)
	time.sleep(0.2)
	GPIO.output(12, GPIO.LOW)
	GPIO.output(16, GPIO.LOW)
	GPIO.output(21, GPIO.LOW)
	time.sleep(0.2)
while True:
	try:
		camera.capture(frame, format="rgb", use_video_port=True)
		face_locations = face_recognition.face_locations(frame)
		face_encodings = face_recognition.face_encodings(frame, face_locations)
		if face_locations:
			GPIO.output(16, GPIO.HIGH)
			image = Image.fromarray(frame)
			imgByteArr = io.BytesIO()
			image.save(imgByteArr, format='jpeg')
			imgByteArr = imgByteArr.getvalue()
			r = requests.post("https://www.kora.work/api/facerec/", 
								headers=header, 
								data={'device':'000001'}, 
								files={'photo': imgByteArr})
			json_data = json.loads(r.text)
			if json_data['success']=="YES": 
				GPIO.output(16, GPIO.LOW)
				GPIO.output(21, GPIO.HIGH)
				r = requests.post("https://www.kora.work/api/checks/", 
								headers=header, 
								files={'photo': imgByteArr}, 
								data={'worker':json_data['worker'], 
									'device':'000001',
									'datetime':str(datetime.now())})
				print(r.text)
			else:
				GPIO.output(16, GPIO.LOW)
				GPIO.output(12, GPIO.HIGH)
				r = requests.post("https://www.kora.work/api/checks/", 
					headers=header, 
					files={'photo': imgByteArr}, 
					data={'worker':None,  
						'device':'000001',
						'datetime':str(datetime.now())})
			GPIO.output(21, GPIO.LOW)
			GPIO.output(12, GPIO.LOW)
		Movement_B = False
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		gray = cv2.GaussianBlur(gray, (21, 21), 0)
		if counter_2 == 0: 
			firstFrame = gray
			counter_2 = 1
		if counter == 20:
			firstFrame = gray
			counter = 0
		frameDelta = cv2.absdiff(firstFrame, gray)
		thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
		thresh = cv2.dilate(thresh, None, iterations=2)
		cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
								cv2.CHAIN_APPROX_SIMPLE)
		cnts = imutils.grab_contours(cnts)
		for c in cnts:
			movement_time_2 = datetime.now()
			if cv2.contourArea(c) < 500:
				continue
			Movement_B = True
		if Movement_B:
			if movement_time_2 > (movement_time_1+timedelta(minutes = 10)):
				r = requests.post("https://www.kora.work/api/nomotions/", 
								headers=header, 
								data={'device':"000001",
										'start_datetime': str(movement_time_1), 
										'finish_datetime': str(movement_time_2)
										})
				movement_time_1 = datetime.now()
			else: 
				movement_time_1 = datetime.now()
		if datetime.now() > (movement_time_1+timedelta(minutes = 60)):
			r = requests.post("https://www.kora.work/api/nomotions/", 
							headers=header, 
							data={'device':'000001',
									'start_datetime': str(movement_time_1), 
									'finish_datetime': str(datetime.now())
									})
			movement_time_1 = datetime.now()
		counter +=1
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
