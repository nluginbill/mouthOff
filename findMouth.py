import requests
import re
import face_recognition
import json
import shutil
from pathlib import Path
from bs4 import BeautifulSoup
import os
from csv import DictWriter, DictReader

from academyQuery import retrieveListOfAAN


def storeListOfActorFaces():
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
	with open("actorFaces.csv") as file:
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
