from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app
)
from werkzeug.exceptions import abort
from csv import DictReader

from mouthOff.auth import login_required
from mouthOff.db import get_db

bp = Blueprint('play', __name__)

@bp.route('/')
def index():
    import random
    celeb = random.choice(retrieveListOfActorFaces())
    celeb['imgpath'] = f'img/{celeb["picurl"]}'
    celeb['imgpath_mouth'] = f'img/mouth_{celeb["picurl"]}'
    
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