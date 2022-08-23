import time

import requests
import face_recognition
import shutil
from pathlib import Path
from csv import DictWriter, DictReader
from urllib import request as ul_req
from PIL import ImageFile, Image
import ssl
import ast

from academyQuery import getListOfAcademyAwardNominees


def storeListOfActorFaces():
	celebs = getListOfAcademyAwardNominees()
	with open("actorFaces.csv", "w", newline="") as file:
		headers = ["pageid", "name", "facelandmarks"]
		csv_writer = DictWriter(file, fieldnames=headers)
		csv_writer.writeheader()
		listOfActors = findMouths(celebs)
		for actor in listOfActors:
			csv_writer.writerow({
				"pageid": actor["pageid"],
				"name": actor["name"],
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
				actor["facelandmarks"] = row["facelandmarks"]
				listOfActors.append(actor)
	return listOfActors


def getMouthCoords(celeb):

	box = tuple()
	face = ast.literal_eval(celeb["facelandmarks"][1:-1])
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
		box = {'top': int(face[closestFace]["chin"][2][0]), 'right': int(face[closestFace]["chin"][2][1]), 'bottom':
									int(face[closestFace]["chin"][14][0]), 'left': int(face[closestFace]["chin"][8][1])}

	return box


def retrieveMouthImg(celeb):
	S = requests.Session()
	URL = "https://en.wikipedia.org/w/api.php"
	headers = {'User-Agent': 'MouthOffbot/0.1 (nluginbill@gmail.com)'}
	PARAMS = {
		"action": "query",
		"format": "json",
		"titles": celeb["name"],
		"prop": "pageimages|pageterms",
		"piprop": "original",
		"formatversion": "2"
	}

	R = S.get(url=URL, params=PARAMS, headers=headers)
	DATA = R.json()
	imgurl = None

	try:
		imgurl = DATA['query']['pages'][0]['original']['source']
	except KeyError:
		return

	# workaround ssl certificate error when using urlopen
	ssl._create_default_https_context = ssl._create_unverified_context

	# get the size of the image so it can be cropped appropriately
	img_file = ul_req.urlopen(imgurl)
	size = img_file.headers.get("content-length")
	if size:
		size = int(size)
	p = ImageFile.Parser()
	while True:
		data = img_file.read(1024)
		if not data:
			break
		p.feed(data)
		if p.image:
			return imgurl, p.image.size
			break
	file.close()
	return imgurl

def findMouths(celebs):
	S = requests.Session()
	celebsFaceLandmarks = list()
	for celeb in celebs:
		URL = "https://en.wikipedia.org/w/api.php"
		headers = {'User-Agent': 'MouthOffbot/0.1 (nluginbill@gmail.com)'}
		PARAMS = {
			"action": "query",
			"format": "json",
			"titles": celeb["name"],
			"prop": "pageimages|pageterms",
			"piprop": "original",
			"formatversion": "2",
			"maxlag": "1"
		}

		R = S.get(url=URL, params=PARAMS, headers=headers)
		DATA = R.json()
		imgurl = None
		try:
			imgurl = DATA['query']['pages'][0]['original']['source']
		except:
			print(celeb)


		if imgurl:
			# added the strip without testing
			filename = imgurl.split("/")[-1].strip("()")

			imgReq = S.get(imgurl, stream=True)
			if imgReq.status_code == 200:
				imgReq.raw.decode_content = True

				path = f"{Path(__file__).parent}/static/img/"
				img = path + filename
				with open(img, 'wb') as f:
					shutil.copyfileobj(imgReq.raw, f)

				print('Image successfully downloaded: ', filename)

				faceImg = face_recognition.load_image_file(img)
				face_landmarks_list = face_recognition.face_landmarks(faceImg)
				face = face_landmarks_list
				img = Image.open(img)
				box = tuple()
				# if there are two faces in a picture, face will actually be a tuple of faces. If there is one face, it will be dict.
				if type(face) is dict:
					box = (int(face["chin"][2][0]), int(face["chin"][2][1]), int(face["chin"][14][0]), int(face["chin"][8][1]))
				if face:
					# this conditional is for the tuples, for multiple faces. it finds the biggest/closest face and assigns the crop box based
					# on the closest face
					closestFace = None
					biggestFace = 0
					for i, f in enumerate(face):
						if f["chin"][16][0] - f["chin"][0][0] > biggestFace:
							biggestFace = f["chin"][16][0] - f["chin"][0][0]
							closestFace = i
					box = (int(face[closestFace]["chin"][2][0]), int(face[closestFace]["chin"][2][1]),
						   int(face[closestFace]["chin"][14][0]), int(face[closestFace]["chin"][8][1]))
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
					location = path + "cropped" + filename
					finalImage.save(location)

				celeb["facelandmarks"] = face_landmarks_list
				celebsFaceLandmarks.append(celeb)
		# downloading images, takes a long timer to keep api server happy
		time.sleep(4)
	return celebsFaceLandmarks

if __name__ == "__main__":
	findMouths(getListOfAcademyAwardNominees())