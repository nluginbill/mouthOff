import requests
import re
import face_recognition
import json
import shutil
import time
from pathlib import Path
from bs4 import BeautifulSoup
import os
from csv import DictWriter, DictReader

from academyQuery import retrieveListOfAAN


def storeListOfActorFaces():
	with open("actorFaces.csv", "w", newline="") as file:
		headers = ["name", "picurl", "facelandmarks"]
		csv_writer = DictWriter(file, fieldnames=headers)
		csv_writer.writeheader()
		listOfActors = findMouths()
		print(len(listOfActors))
		for actor in listOfActors:
			print("yeah I'm writing I'm writing")
			csv_writer.writerow({
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
				actor["name"] = row["name"]
				actor["picurl"] = row["picurl"]
				actor["facelandmarks"] = row["facelandmarks"]
				listOfActors.append(actor)
	return listOfActors


def findMouths():
	S = requests.Session()
	celebsFaceLandmarks = list()
	celebs = retrieveListOfAAN()
	for celeb in celebs:
		# https://en.wikipedia.org/wiki/Anthony_Hopkins#/media/File:AnthonyHopkins10TIFF.jpg
		print(celeb)
		# this is my new solution that I have yet to test. It is supposed to catch names with 
		# 3 words like William H. Macy. Takes a long time to run though, and want to move on,
		# so will test another time.
		celeb_regex = re.compile(r'([a-zA-Z]+)[ -]?([a-zA-Z.]+)?[ -]?([a-zA-Z]+)?')
		match = celeb_regex.search(celeb["name"])
		wikiUrl = match.group(0).replace(' ', '_')
		# these are what I used to get one batch of faces, but you'd have to change the regex back
		# first_name = match.group(1)
		# last_name = match.group(2)
		print(first_name)
		print(last_name)
		# first_name = celeb["name"].split()[0]
		# last_name = celeb["name"].split()[1]
		url = f"https://en.wikipedia.org/wiki/{wikiUrl}#/media/File:{celeb['picurl']}"
		filename = url.split("/")[-1][5::]
		R = S.get(url)
		soup = BeautifulSoup(R.content, "html.parser")
		if soup.find("meta", {"property": "og:image"}):
			imgurl = soup.find("meta", {"property": "og:image"})["content"]
			headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0"}
			imgReq = S.get(imgurl, stream=True, headers=headers)
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
			else:
				print(celeb["name"])
				print(imgReq.status_code)
			time.sleep(.5)
	return celebsFaceLandmarks