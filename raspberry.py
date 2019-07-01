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
from threading import Timer, Thread
import subprocess
auth_token='3f27387c0015b9dba34cf0bc10d1bd936f6d09e8'
header = {'Authorization': 'Token ' + auth_token}
device_idn = "000001"
known_face_encodings = []
known_face_pk = []
sended_face_pk = []
sended_unknown = True
language = 'en'
counter = 0
firstFrame = None
counter = 0
counter_2 = 0
counter_3 = 0
movement_time_1 = datetime.now()
movement_time_2 = datetime.now()
counter_internet=0



def refreshEncodings():
	global known_face_pk
	global known_face_encodings
	while True:
		try:
			r = requests.get("https://www.kora.work/api/devices/"+device_idn+"/encodings/", headers=header)
			break
		except:
			time.sleep(20)
			pass
	json_data = json.loads(r.text)
	known_face_encodings = []
	known_face_pk = []
	for worker in json_data:
		temp = worker['faceEncodings'].split("[")[2].split("]")[0]
		known_face_encoding = np.fromstring(temp, dtype=float, sep=',')
		known_face_encodings.append(known_face_encoding)
		known_face_pk.append(worker['pk'])
	Timer(60, refreshEncodings).start()
refreshEncodings()

def refreshSendedList():
	global sended_face_pk
	global sended_unknown
	sended_unknown = True
	sended_face_pk = []
	Timer(30, refreshSendedList).start()
refreshSendedList()

def checkInternet():
	try:
		r = requests.get("https://www.google.com")
		print("GO")
		if counter_internet==0:
			BashCommand = "cd /home/pi/Documents/korainside/tunnel/; sh start_tunnel.sh"
			output = subprocess.run(BashCommand, shell=True, universal_newlines=True, check=True)
			counter_internet+=1
		Timer(15, checkInternet).start()
	except:
		while True:
			try:
				time.sleep(5)
				r = requests.get("https://www.google.com")
				break
			except:
				print("waiting")
				pass
		BashCommand = "cd /home/pi/Documents/korainside/tunnel/; sh stop_tunnel.sh; sh start_tunnel.sh"
		output = subprocess.run(BashCommand, shell=True, universal_newlines=True, check=True)
		print("GOGOGOGOG")
		Timer(15, checkInternet).start()
checkInternet()

def sendPK(name_index, frame):
	GPIO.output(16, GPIO.LOW)
	GPIO.output(21, GPIO.HIGH)
	global known_face_pk
	image = Image.fromarray(frame)
	imgByteArr = io.BytesIO()
	image.save(imgByteArr, format='jpeg')
	imgByteArr = imgByteArr.getvalue()
	while True:
		try:
			r = requests.post("https://www.kora.work/api/checks/",
				headers=header,
				files={'photo': imgByteArr},
				data={'worker':known_face_pk[name_index],
					'device':device_idn,
					'datetime':str(datetime.now())})
			break
		except:
			time.sleep(20)
			pass
	print(r.text)
	GPIO.output(21, GPIO.LOW)
def sendUnknown(name_index, frame):
	GPIO.output(16, GPIO.LOW)
	GPIO.output(12, GPIO.HIGH)
	image = Image.fromarray(frame)
	imgByteArr = io.BytesIO()
	image.save(imgByteArr, format='jpeg')
	imgByteArr = imgByteArr.getvalue()
	while True:
		try:
			r = requests.post("https://www.kora.work/api/checks/",
				headers=header,
				files={'photo': imgByteArr},
				data={'worker':None,
					'device':device_idn,
					'datetime':str(datetime.now())})
			break
		except:
			time.sleep(20)
			pass
	print(r.text)
	GPIO.output(12, GPIO.LOW)

def sendMovement(time1, time2):
	while True:
		try:
			r = requests.post("https://www.kora.work/api/nomotions/",
						headers=header,
						data={'device':device_idn,
								'start_datetime': time1,
								'finish_datetime': time2
								})
			break
		except:
			time.sleep(20)
			pass
	print(r.text)

def sendActivity():
	while True:
		try:
			r = requests.post("https://www.kora.work/api/status/devices/",
					headers=header,
					data={'device':device_idn,
						'activity': str(datetime.now())})
			break
		except:
			time.sleep(20)
			pass
	print(r.text)

GPIO.output(12, GPIO.LOW)
GPIO.output(16, GPIO.LOW)
GPIO.output(21, GPIO.LOW)
error_counter=0
time.sleep(0.2)
while True:
	try:
		r = requests.post("https://www.kora.work/api/active/devices/",
							headers=header,
							data={'device': device_idn,})
		json_data = json.loads(r.text)
		print(r.text)
		GPIO.output(12, GPIO.LOW)
		if json_data['success']=="YES":
			break
		else:
			time.sleep(1)
			GPIO.output(12, GPIO.HIGH)
			time.sleep(1)
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
		time.sleep(20)
		GPIO.output(21, GPIO.LOW)
		GPIO.output(12, GPIO.LOW)
		GPIO.output(16, GPIO.LOW)
		pass

for i in range(5):
	GPIO.output(16, GPIO.HIGH)
	GPIO.output(21, GPIO.HIGH)
	GPIO.output(12, GPIO.HIGH)
	time.sleep(0.2)
	GPIO.output(12, GPIO.LOW)
	GPIO.output(16, GPIO.LOW)
	GPIO.output(21, GPIO.LOW)
	time.sleep(0.2)

camera = picamera.PiCamera()
camera.resolution = (320, 240)
frame = np.empty((240,320,3),dtype=np.uint8)
while True:
	try:
		camera.capture(frame, format="rgb", use_video_port=True)
		if counter_3 > 30:
			t3 = Thread(target=sendActivity)
			t3.start()
			counter_3 = 0
		face_locations = face_recognition.face_locations(frame)
		if face_locations:
			GPIO.output(16, GPIO.HIGH)
			face_encodings = face_recognition.face_encodings(frame, face_locations)
			for face_encoding in face_encodings:
				matches = face_recognition.face_distance(known_face_encodings, face_encoding)
				name_index = np.argmin(matches)
				if (matches[name_index]<0.5):
					if known_face_pk[name_index] not in sended_face_pk:
						sended_face_pk.append(known_face_pk[name_index])
						t1 = Thread(target=sendPK, args=(name_index, frame))
						t1.start()
				else:
					if sended_unknown:
						sended_unknown = False
						t2 = Thread(target=sendUnknown, args=(name_index, frame))
						t2.start()
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
		print(Movement_B)
		if Movement_B:
			if movement_time_2 > (movement_time_1+timedelta(seconds = 5)):
				t3 = Thread(target=sendMovement, args=(str(movement_time_1), str(datetime.now())))
				t3.start()
				movement_time_1 = datetime.now()
			else:
				movement_time_1 = datetime.now()
		if datetime.now() > (movement_time_1+timedelta(seconds = 10)):
			t3 = Thread(target=sendMovement, args=(str(movement_time_1), str(datetime.now())))
			t3.start()
			movement_time_1 = datetime.now()
		counter +=1
		counter_3+=1
		GPIO.output(16, GPIO.LOW)
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
		time.sleep(20)
		GPIO.output(21, GPIO.LOW)
		GPIO.output(12, GPIO.LOW)
		GPIO.output(16, GPIO.LOW)
		pass
