import requests
import json
import time
from csv import DictReader, DictWriter
from bs4 import BeautifulSoup


def getListOfSAGAwardedActors():
    S = requests.Session()
    count = 0
    lhcontinue = ""
    actors = []
    while True:
        # get all of the links on the Academy Award Nominations list of actors
        URL = "https://en.wikipedia.org/w/api.php"

        PARAMS = {
            "action": "query",
            "format": "json",
            "prop": "linkshere",
            "continue": "||",
            "titles": "Screen Actors Guild Awards",
            "formatversion": "2",
            "maxlag": "1",
            "lhcontinue": lhcontinue,
        }

        R = S.get(url=URL, params=PARAMS)
        DATA = R.json()
        links = None
        if "query" in DATA:
            links = DATA["query"]["pages"][0]["linkshere"]
        if links:
            for i, link in enumerate(links):
                # if i > 0:
                actor = dict()
                actor["pageid"] = link["pageid"]
                actor["name"] = link["title"]
                actors.append(actor)

            # check if there are any more results, if there are, enter continue code for next page results
            if "batchcomplete" in DATA:
                break
            else:
                lhcontinue = DATA["continue"]["lhcontinue"]
            # keep mediawiki happy
            time.sleep(.5)
    return actors

# returns a list of all Academy Award Nominees
def getListOfAcademyAwardNominees():
    S = requests.Session()
    count = 0
    lhcontinue = ""
    academyActors = []
    while True:
        # get all of the links on the Academy Award Nominations list of actors
        URL = "https://en.wikipedia.org/w/api.php"  

        PARAMS = {
            "action": "query",
            "format": "json",
            "prop": "linkshere",
            "continue": "||",
            "titles": "List of actors with Academy Award nominations",
            "formatversion": "2",
            "maxlag": "1",
            "lhcontinue": lhcontinue,
        }

        R = S.get(url=URL, params=PARAMS)
        DATA = R.json()
        links = None
        if "query" in DATA:    
            links = DATA["query"]["pages"][0]["linkshere"]
        if links:         
            for i, link in enumerate(links):
                # if i > 0:
                actor = dict()
                actor["pageid"] = link["pageid"]
                actor["name"] = link["title"]
                academyActors.append(actor)

            # check if there are any more results, if there are, enter continue code for next page results
            if "batchcomplete" in DATA:
                break
            else:
                lhcontinue = DATA["continue"]["lhcontinue"]
            # keep mediawiki happy
            time.sleep(.5)
    return academyActors



def getEachActorInfo(listOfActors):
    S = requests.Session()
    academyActors = []
    for actor in listOfActors:
        URL = "https://en.wikipedia.org/w/api.php"  

        PARAMS = {
            "action": "parse",
            "format": "json",
            "pageid": actor["pageid"],
            "prop": "categories|images|text",
            "maxlag": "1"
        }

        R = S.get(url=URL, params=PARAMS)
        DATA = R.json()

        print(actor)

        if "parse" in DATA:
            actualActor = False
            soup = BeautifulSoup(DATA["parse"]["text"]["*"], "html.parser")
            if soup.find('th', text="Occupation"):
                if "Actor" or "Actress" in soup.find('th', text="Occupation").parent:
                    actualActor = True
                main_pic = soup.find("td", class_="infobox-image").next_element
                if main_pic.name == 'a' and main_pic['href']:
                    actor['href'] = soup.find("td", class_="infobox-image").next_element['href']
                    actor['picurl'] = actor['href'][11:]
                else:
                    actualActor = False
            if actualActor:
                academyActors.append(actor)

        time.sleep(.5)
    return academyActors

def storeListOfAAN():
    with open("actors.csv", "w", newline="") as file:
        headers = ["pageid", "name", "href", "picurl"]
        csv_writer = DictWriter(file, fieldnames=headers)
        csv_writer.writeheader()
        listOfActors = getEachActorInfo(getListOfAcademyAwardNominees())
        for actor in listOfActors:
            csv_writer.writerow({
                "pageid": actor["pageid"],
                "name": actor["name"],
                "href": actor["href"],
                "picurl": actor["picurl"]
                })

def retrieveListOfAAN():
    listOfActors = list()
    with open("actors.csv") as file:
        csv_reader = DictReader(file)      
        for i, row in enumerate(csv_reader):
            actor = dict()
            if i > 0:
                actor["pageid"] = row["pageid"]
                actor["name"] = row["name"]
                actor["href"] = row["href"]
                actor["picurl"] = row["picurl"]
                listOfActors.append(actor)
        return listOfActors


if __name__ == "__main__":
    getListOfAcademyAwardNominees()