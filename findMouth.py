# first download the picture
# then find the mouth (tip of nose? chin?)
# then delete the picture

import requests
import re
import face_recognition
import json
import shutil
from pathlib import Path
from bs4 import BeautifulSoup
import os 

import academyQuery


def findMouths(celebs):
	S = requests.Session()
	celebsFaceLandmarks = list()
	for celeb in celebs:
		# https://en.wikipedia.org/wiki/Anthony_Hopkins#/media/File:AnthonyHopkins10TIFF.jpg
		first_name = celeb["name"].split()[0]
		last_name = celeb["name"].split()[1]
		url = f"https://en.wikipedia.org/wiki/{first_name}_{last_name}#/media/File:{celeb['picurl']}"
		filename = url.split("/")[-1][5::]
		R = S.get(url)
		soup = BeautifulSoup(R.content, "html.parser")
		if soup.find("meta", {"property": "og:image"}):
			imgurl = soup.find("meta", {"property": "og:image"})["content"]
			imgReq = S.get(imgurl, stream=True)
			face_landmarks_list = list()
			if imgReq.status_code == 200:
				imgReq.raw.decode_content = True

				path = f"{Path(__file__).parent}/temp/"
				img = path + filename
				with open(img, 'wb') as f:
					shutil.copyfileobj(imgReq.raw, f)

				print('Image sucessfully Downloaded: ', filename)

				faceImg = face_recognition.load_image_file(img)
				face_landmarks_list = face_recognition.face_landmarks(faceImg)

				celeb["facelandmarks"] = face_landmarks_list
				celebsFaceLandmarks.append(celeb)
				os.remove(img)
	return celebsFaceLandmarks


celebs = academyQuery.retrieveListOfAAN()
print(findMouths(celebs))


def testFuckWithImg():

	# Load the jpg file into a numpy array
	image = face_recognition.load_image_file("biden.jpg")

	# Find all facial features in all the faces in the image
	face_landmarks_list = face_recognition.face_landmarks(image)

	pil_image = Image.fromarray(image)
	for face_landmarks in face_landmarks_list:
		d = ImageDraw.Draw(pil_image, 'RGBA')

		# Make the eyebrows into a nightmare
		d.polygon(face_landmarks['left_eyebrow'], fill=(68, 54, 39, 128))
		d.polygon(face_landmarks['right_eyebrow'], fill=(68, 54, 39, 128))
		d.line(face_landmarks['left_eyebrow'], fill=(68, 54, 39, 150), width=5)
		d.line(face_landmarks['right_eyebrow'],
			   fill=(68, 54, 39, 150), width=5)

		# Gloss the lips
		d.polygon(face_landmarks['top_lip'], fill=(150, 0, 0, 128))
		d.polygon(face_landmarks['bottom_lip'], fill=(150, 0, 0, 128))
		d.line(face_landmarks['top_lip'], fill=(150, 0, 0, 64), width=8)
		d.line(face_landmarks['bottom_lip'], fill=(150, 0, 0, 64), width=8)

		# Sparkle the eyes
		d.polygon(face_landmarks['left_eye'], fill=(255, 255, 255, 30))
		d.polygon(face_landmarks['right_eye'], fill=(255, 255, 255, 30))

		# Apply some eyeliner
		d.line(face_landmarks['left_eye'] +
			   [face_landmarks['left_eye'][0]], fill=(0, 0, 0, 110), width=6)
		d.line(face_landmarks['right_eye'] +
			   [face_landmarks['right_eye'][0]], fill=(0, 0, 0, 110), width=6)

		pil_image.show()
