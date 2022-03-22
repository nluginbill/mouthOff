import requests
import re
import face_recognition
import json
import shutil
from pathlib import Path
from bs4 import BeautifulSoup
import os
from csv import DictWriter, DictReader
import ast
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

from academyQuery import retrieveListOfAAN


def storeListOfActorFaces(celebs):
	with open("actorFaces.csv", "w", newline="") as file:
		headers = ["pageid", "name", "picurl", "facelandmarks"]
		csv_writer = DictWriter(file, fieldnames=headers)
		csv_writer.writeheader()
		listOfActors = findMouths(celebs)
		for actor in listOfActors:
			csv_writer.writerow({
				"pageid": actor["pageid"],
				"name": actor["name"],
				"picurl": actor["picurl"],
				"facelandmarks": actor["facelandmarks"]
			})

def retrieveListOfActorFaces():
	listOfActors = list()
	with open("../instance/actorFaces.csv") as file:
		csv_reader = DictReader(file)
		for i, row in enumerate(csv_reader):
			actor = dict()
			if i > 0:
				actor["pageid"] = row["pageid"]
				actor["name"] = row["name"]
				actor["picurl"] = row["picurl"]
				actor["facelandmarks"] = row["facelandmarks"]
				listOfActors.append(actor)
	return listOfActors


def gather_images():
	celebs = retrieveListOfAAN()
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
			if imgReq.status_code == 200:
				imgReq.raw.decode_content = True

				path = f"/static/img/"
				img = path + filename
				with open(img, 'wb') as f:
					shutil.copyfileobj(imgReq.raw, f)

				print('Image sucessfully Downloaded: ', filename)


def gather_mouths():
	celebs = retrieveListOfActorFaces()
	for celebFace in celebs:
		print(celebFace["name"])
		first_name = celebFace["name"].split()[0]
		last_name = celebFace["name"].split()[1]
		url = f"https://en.wikipedia.org/wiki/{first_name}_{last_name}#/media/File:{celebFace['picurl']}"
		S = requests.Session()
		headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0"}
		R = S.get(url, headers=headers)
		soup = BeautifulSoup(R.content, "html.parser")
		if soup.find("meta", {"property": "og:image"}):
			imgurl = soup.find("meta", {"property": "og:image"})["content"]
			imgReq = S.get(imgurl, headers=headers, stream=True)
			if imgReq.status_code == 200:
				imgReq.raw.decode_content = True
				# print(celebFace)
				face = ast.literal_eval(celebFace["facelandmarks"][1:-1])
				filename = f'mouth_{url.split("/")[-1][5::]}'
				path = f"static/img/"
				img = Image.open(BytesIO(imgReq.content))
				box = tuple()
				# if there are two faces in a picture, face will actually be a tuple of faces. If there is one face, it will be dict.
				if type(face) is dict:			
					box = (int(face["chin"][2][0]), int(face["chin"][2][1]), int(face["chin"][14][0]), int(face["chin"][8][1]))
				else:
					# this else block is for the tuples, for multiple faces. it finds the biggest/closest face and assigns the crop box based
					# on the closest face
					closestFace = None
					biggestFace = 0
					for i, f in enumerate(face):
						if f["chin"][16][0] - f["chin"][0][0] > biggestFace:
							biggestFace = f["chin"][16][0] - f["chin"][0][0]
							closestFace = i
					box = (int(face[closestFace]["chin"][2][0]), int(face[closestFace]["chin"][2][1]), int(face[closestFace]["chin"][14][0]), int(face[closestFace]["chin"][8][1]))
				croppedImg = img.crop(box)
				resizedImg = None
				if croppedImg.size[0] < 200:
					width, height = croppedImg.size
					ratio = width / height
					resizedImg = croppedImg.resize((200, int(200 / ratio)))
				finalImage = None
				if resizedImg:
					finalImage = resizedImg
				else:
					finalImage = croppedImg
				location = path + filename
				finalImage.save(location)


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

				path = f"{Path(__file__).parent}/img/"
				img = path + filename
				with open(img, 'wb') as f:
					shutil.copyfileobj(imgReq.raw, f)

				print('Image sucessfully Downloaded: ', filename)

				faceImg = face_recognition.load_image_file(img)
				face_landmarks_list = face_recognition.face_landmarks(faceImg)

				celeb["facelandmarks"] = face_landmarks_list
				celebsFaceLandmarks.append(celeb)
	return celebsFaceLandmarks

