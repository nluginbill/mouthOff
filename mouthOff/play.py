import urllib.parse

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app
)
from werkzeug.exceptions import abort
from csv import DictReader
from os import getcwd
from os.path import exists

from mouthOff.auth import login_required
from mouthOff.db import get_db

bp = Blueprint('play', __name__)

@bp.route('/')
def index():
    import random

    while True:
        celeb = random.choice(retrieveListOfActors())
        celeb['imgpath'] = f'img/{celeb["filename"]}'
        celeb['imgpath_mouth'] = f'img/cropped{celeb["filename"]}'
        print(celeb['imgpath_mouth'])
        # img_src = urllib.parse.unquote(celeb['imgpath_mouth'])
        # celeb['imgpath_mouth'] = img_src
        print(exists(getcwd() + "/mouthOff" + url_for('static', filename=celeb['imgpath_mouth'])))

        if exists(getcwd() + "/mouthOff" + url_for('static', filename=celeb['imgpath_mouth'])):
            return render_template('play/index.html', celeb=celeb)


def retrieveListOfActors():
    listOfActors = list()
    with current_app.open_resource('../instance/actors.csv', 'rt') as file:
        csv_reader = DictReader(file)
        for i, row in enumerate(csv_reader):
            actor = dict()
            if i > 0:
                actor["name"] = row["name"]
                actor["filename"] = row["filename"]
                # weed out the lists that got added to the csv
                filter_list = ["list of", "academy", "screen "]
                if actor["filename"][:8].lower() not in filter_list:
                    listOfActors.append(actor)
    return listOfActors
