import requests
import json
import time
from csv import DictReader, DictWriter
from bs4 import BeautifulSoup

# new and improved get list of nominees, using get html from media wiki
def getListOfAAN():
    S = requests.Session()
    URL = "https://en.wikipedia.org/w/api.php" 
    PARAMS = {
        "action": "parse",
        "format": "json",
        "page": "List of actors with Academy Award nominations",
        "prop": "text",
        "formatversion": "2"
    }
    R = S.get(url=URL, params=PARAMS)
    DATA = R.json()
    soup = BeautifulSoup(DATA["parse"]["text"], "html.parser")
    tableOfActors = soup.find(class_="sortable")
    actorRows = tableOfActors.tbody.find_all('tr')
    actors = list()
    for row in actorRows:
        try:
            row.td.span
        except AttributeError:
            pass
        else:
            actors.append(row.td.span.a.text)
    return actors

def getInfoForActors():
    S = requests.Session()

    listOfActors = getListOfAAN()
    actorInfo = list()
    for actor in listOfActors:
        info = dict()
        URL = "https://en.wikipedia.org/w/api.php" 
        PARAMS = {
            "action": "parse",
            "format": "json",
            "page": actor,
            "prop": "text",
            "formatversion": "2",
            "maxlag": "1"
        }
        R = S.get(url=URL, params=PARAMS)
        DATA = R.json()
        try:
            DATA["parse"]
        except:
            pass
        else:
            soup = BeautifulSoup(DATA["parse"]["text"], "html.parser")
            try:
                image = soup.find(class_="infobox-image").a['href']
            except AttributeError:
                pass
            else:
                trimmedImageURL = image[11:]
                info["name"] = actor
                info["picurl"] = trimmedImageURL
                actorInfo.append(info)
    return actorInfo

def storeListOfAAN():
    with open("actors.csv", "w", newline="") as file:
        headers = ["name", "picurl"]
        csv_writer = DictWriter(file, fieldnames=headers)
        csv_writer.writeheader()
        listOfActors = getInfoForActors()
        for actor in listOfActors:
            csv_writer.writerow({
                "name": actor["name"],
                "picurl": actor["picurl"]
                })

def retrieveListOfAAN():
    listOfActors = list()
    with open("actors.csv") as file:
        csv_reader = DictReader(file)      
        for i, row in enumerate(csv_reader):
            actor = dict()
            if i > 0:
                actor["name"] = row["name"]
                actor["picurl"] = row["picurl"]
                listOfActors.append(actor)
        return listOfActors

# storeListOfAAN()
# returns a list of all Academy Award Nominees
# def getListOfAcademyAwardNominees():
#     S = requests.Session()
#     count = 0
#     lhcontinue = ""
#     academyActors = []
#     while True:
#         # get all of the links on the Academy Award Nominations list of actors
#         URL = "https://en.wikipedia.org/w/api.php"  

#         PARAMS = {
#             "action": "query",
#             "format": "json",
#             "prop": "linkshere",
#             "continue": "||",
#             "titles": "List of actors with Academy Award nominations",
#             "formatversion": "2",
#             "maxlag": "1",
#             "lhcontinue": lhcontinue,
#         }

#         R = S.get(url=URL, params=PARAMS)
#         DATA = R.json()
#         links = None
#         if "query" in DATA:    
#             links = DATA["query"]["pages"][0]["linkshere"]
#         if links:         
#             for i, link in enumerate(links):
#                 # if i > 0:
#                 actor = dict()
#                 actor["pageid"] = link["pageid"]
#                 actor["name"] = link["title"]
#                 academyActors.append(actor)

#             # check if there are any more results, if there are, enter continue code for next page results
#             if "batchcomplete" in DATA:
#                 break
#             else:
#                 lhcontinue = DATA["continue"]["lhcontinue"]
#             # keep mediawiki happy
#             time.sleep(.5)
#     return academyActors

# def getEachActorInfo(listOfActors):
#     S = requests.Session()
#     academyActors = []
#     for actor in listOfActors:
#         URL = "https://en.wikipedia.org/w/api.php"  

#         PARAMS = {
#             "action": "parse",
#             "format": "json",
#             "pageid": actor["pageid"],
#             "prop": "categories|images|text",
#             "maxlag": "1"
#         }

#         R = S.get(url=URL, params=PARAMS)
#         DATA = R.json()
#         if "parse" in DATA:
#             actualActor = False
#             soup = BeautifulSoup(DATA["parse"]["text"]["*"], "html.parser")
#             if soup.find('th', text="Occupation"):
#                 if "Actor" or "Actress" in soup.find('th', text="Occupation").parent:
#                     actualActor = True
#                 if soup.find("td", class_="infobox-image").next_element['href']:                
#                     actor['picurl'] = soup.find("td", class_="infobox-image").next_element['href']
#                     actor['picurl'] = actor['picurl'][11:]
#                 else:
#                     actualActor = False
#             if actualActor:
#                 academyActors.append(actor)

#         time.sleep(.5)
#     return academyActors