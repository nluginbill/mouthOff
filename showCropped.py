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
			print(celebFace)
			face = ast.literal_eval(celebFace["facelandmarks"][1:-1])
			filename = url.split("/")[-1][5::]
			path = f"{Path(__file__).parent}/temp/"
			img = path + filename
			

			img = Image.open(BytesIO(imgReq.content))
			box = (int(face["chin"][2][0]), int(face["chin"][2][1]), int(face["chin"][14][0]), int(face["chin"][8][1]))
			croppedImg = img.crop(box)
			croppedImg.show()

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

			# img = Image.open(BytesIO(imgReq.content))
			# box = (face[""])
			# croppedImg = img.crop()
			# img.show()


showCropped(retrieveListOfActorFaces())