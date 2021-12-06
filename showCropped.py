from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import requests
import random
from bs4 import BeautifulSoup
from pathlib import Path
import shutil
import ast

from findMouth import retrieveListOfActorFaces

def showCropped(celebFaces):
	# celebFace = random.choice(celebFaces)
	celebFace = next(x for x in celebFaces if x["name"] == "Walter Brennan")
	# celebFace = next(x for x in celebFaces if x["name"] == "Kim Basinger")

	first_name = celebFace["name"].split()[0]
	last_name = celebFace["name"].split()[1]
	url = f"https://en.wikipedia.org/wiki/{first_name}_{last_name}#/media/File:{celebFace['picurl']}"
	S = requests.Session()
	headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0"}
	R = S.get(url, headers=headers)	
	soup = BeautifulSoup(R.content, "html.parser")
	if soup.find("meta", {"property": "og:image"}):
		imgurl = soup.find("meta", {"property": "og:image"})["content"]
		imgReq = S.get(imgurl, stream=True)
		if imgReq.status_code == 200:
			imgReq.raw.decode_content = True
			face = ast.literal_eval(celebFace["facelandmarks"][1:-1])
			filename = url.split("/")[-1][5::]
			path = f"{Path(__file__).parent}/temp/"
			img = path + filename
			print(celebFace["name"])
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
			croppedImg.show()
			return celebFace
		else:
			print(celebFace["name"])
			print(imgReq.status_code)
			print("html error")
	else:
		print("Image didn't work out")
			

def showLandmarkNumbers(celebFaces):
	celebFace = random.choice(celebFaces)

	first_name = celebFace["name"].split()[0]
	last_name = celebFace["name"].split()[1]
	url = f"https://en.wikipedia.org/wiki/{first_name}_{last_name}#/media/File:{celebFace['picurl']}"
	S = requests.Session()
	R = S.get(url)
	soup = BeautifulSoup(R.content, "html.parser")
	if soup.find("meta", {"property": "og:image"}):
		imgurl = soup.find("meta", {"property": "og:image"})["content"]
		imgReq = S.get(imgurl, stream=True)
		if imgReq.status_code == 200:
			imgReq.raw.decode_content = True
			face = ast.literal_eval(celebFace["facelandmarks"][1:-1])
			filename = url.split("/")[-1][5::]
			path = f"{Path(__file__).parent}/temp/"
			img = path + filename
			with open(img, 'wb') as f:
				shutil.copyfileobj(imgReq.raw, f)
			with Image.open(img) as base:
				txt = Image.new("RGBA", base.size, (255,255,255,0))
				fnt = ImageFont.truetype("Pillow/Tests/fonts/FreeMono.ttf", 40)
				d = ImageDraw.Draw(txt)
				for landmark in face:

					for i, point in enumerate(face[landmark]):
						print(point)
						text = str(i + 1)
						d.text(point, text, font=fnt, fill=(255,255,255,255))
				out = Image.alpha_composite(base, txt)
				out.show()

