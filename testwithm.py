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
import numpy as np
import base64
import time
import imutils
import json
import picamera
from PIL import Image
from datetime import datetime, timedelta

#import serial
import os
import io
#cmd = 'sudo wvdial &'
#os.system(cmd)
#time.sleep(30)
auth_token='eb39b4bf80482c2070afa94bb6b3cfc43c3000d6'
header = {'Authorization': 'Token ' + auth_token}
#requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':ADH-AES256-SHA384'

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


time.sleep(2)
GPIO.output(12, GPIO.LOW)
GPIO.output(16, GPIO.LOW)
GPIO.output(21, GPIO.LOW)

#error_counter = 0
while True:
	#video_capture = cv2.VideoCapture(0)
	#try:
	#ret, frame = video_capture.read()
	print("frame creation")
	#print("Frame captured----"+str(datetime.now().time()))
	camera.capture(frame, format="rgb", use_video_port=True)
	face_locations = face_recognition.face_locations(frame)
	face_encodings = face_recognition.face_encodings(frame, face_locations)
	if face_locations: 
		GPIO.output(16, GPIO.HIGH)
		#print("Face found----"+str(datetime.now().time()))
		#retval, buffer = cv2.imencode('.jpg', frame)
		#print(type(buffer))
		#jpg_as_text = base64.b64encode(buffer)
		#print("Formated to base64----"+str(datetime.now().time()))
		image = Image.fromarray(frame)
		print("image creation")
		imgByteArr = io.BytesIO()
		image.save(imgByteArr, format='jpeg')
		imgByteArr = imgByteArr.getvalue()
		print("pre request")
		r = requests.post("http://192.168.0.107:80/api/facerec/", headers=header, files={'photo': imgByteArr})		
		print(r.text)
		json_data = json.loads(r.text)
		if json_data['success']=="YES": 
			GPIO.output(16, GPIO.LOW)
			GPIO.output(21, GPIO.HIGH)
			r = requests.post("http://192.168.0.107:80/api/checks/", 
				headers=header, 
				files={'photo': imgByteArr}, 
				data={'user':'1', 
					'worker':json_data['worker'], 
					'device':'1',
					'datetime':str(datetime.now())})
			print(r.text)
		else:
			GPIO.output(16, GPIO.LOW)
			GPIO.output(12, GPIO.HIGH)
			time.sleep(4)
		print("last print")
		GPIO.output(21, GPIO.LOW)
		GPIO.output(12, GPIO.LOW)
		#time.sleep(4)
		

"""
			print("responsed server----"+str(datetime.now().time()))
			json_data = json.loads(r.text)
			if json_data['message'] == "OK": 
				#GPIO.output(16, GPIO.LOW)
				#GPIO.output(21, GPIO.HIGH)
				r = requests.post("http://localhost:8000/facerec/smartcamera/api", data={'message_id':'2',
																					'camera_id':'sdf8a7sda7sd87asd87as87das8d8as87d8asd78a', 
																					'worker':json_data['worker'],
																					'image':jpg_as_text,
																					'geotag':8})
				print(r.text)
				print("second responsed server----"+str(datetime.now().time()))
			elif json_data['message'] == "Not recognized!": 
				GPIO.output(16, GPIO.LOW)
				GPIO.output(12, GPIO.HIGH)
				r = requests.post("http://localhost:8000/facerec/smartcamera/api", data={'message_id':'3',
																					'camera_id':'sdf8a7sda7sd87asd87as87das8d8as87d8asd78a', 
																					'image':jpg_as_text,
																					'geotag':8})
				print(r.text)
#			time.sleep(2)
#			GPIO.output(21, GPIO.LOW)
#			GPIO.output(12, GPIO.LOW)
#			GPIO.output(16, GPIO.LOW)

		print("movement test----"+str(datetime.now().time()))	
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
		print("movement test finished----"+str(datetime.now().time()))
		#print(text)
		if Movement_B:
			if movement_time_2 > (movement_time_1+timedelta(minutes = 30)):
				time.sleep(1)
				r = requests.post("http://localhost:8000/facerec/test/", data={'camera_id':'sdf8a7sda7sd87asd87as87das8d8as87d8asd78a', 
																				'movement_time_1': str(movement_time_1.time()), 
																				'movement_time_2': str(movement_time_2.time()),
																				'geotag':8})
				print(r.text)
				print("movement response----"+str(datetime.now().time()))
				movement_time_1 = datetime.now()
			else: 
				movement_time_1 = datetime.now()
		
		if datetime.now() > (movement_time_1+timedelta(minutes = 60)): 
			r = requests.post("http://localhost:8000/facerec/test/", data={'camera_id':'sdf8a7sda7sd87asd87as87das8d8as87d8asd78a', 
																			'movement_time_1': str(movement_time_1.time()), 
																			'movement_time_2': str(datetime.now().time()),
																			'geotag':8})
			print(r.text)
			movement_time_1 = datetime.now()
	
		
		print("Loop finished----"+str(datetime.now().time()))
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
"""
