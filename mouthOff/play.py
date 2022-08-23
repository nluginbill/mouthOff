from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app
)
from werkzeug.exceptions import abort
from csv import DictReader
from os import getcwd
from os.path import exists

from mouthOff.auth import login_required
from mouthOff.db import get_db
from mouthOff.findMouth import retrieveMouthImg, getMouthCoords

bp = Blueprint('play', __name__)

@bp.route('/')
def index():
    import random

    while True:
        celeb = random.choice(retrieveListOfActorFaces())
        celeb['imgpath'] = f'img/{celeb["picurl"]}'
        celeb['imgpath_mouth'] = f'img/cropped{celeb["picurl"]}'
        # print(url_for('static', filename=celeb['imgpath_mouth']))
        # print(getcwd())
        # print(getcwd() + "/mouthOff/" + celeb['imgpath_mouth'])
        # print(exists((getcwd() + "/mouthOff/" + celeb['imgpath_mouth']).strip()))
        # print(getcwd() + "/mouthOff" + url_for('static', filename=celeb['imgpath_mouth']))
        # print(exists(getcwd() + "/mouthOff" + url_for('static', filename=celeb['imgpath_mouth'])))

        print(celeb['imgpath_mouth'])


        if exists(getcwd() + "/mouthOff" + url_for('static', filename=celeb['imgpath_mouth'])):
            return render_template('play/index.html', celeb=celeb)





def retrieveListOfActorFaces():
    listOfActors = list()
    with current_app.open_resource('../instance/actorFaces.csv', 'rt') as file:
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