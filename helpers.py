import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from bs4 import BeautifulSoup
import requests

cred = credentials.Certificate("mercari-bot-337508-ed622aca8fd4.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
collection_ref = db.collection("searches")

headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15"}

def add_new_search(title, url):
    fields = dict()
    fields["url"] = url
    fields["listings"] = list(retrieve_listings(url))
    collection_ref.document(title).set(fields)    

    print("created new document for: " + title)

def retrieve_listings(url):
    soup = BeautifulSoup(requests.get(url, headers=headers).text, "html.parser")

    search_results = soup.find("div", {"data-testid" : "SearchResults"}).find("div").find("div").find_all("div", recursive=False)

    listings = set()
    for search_result in search_results:
        _id = search_result.find("a").find("div")["data-productid"]
        listings.add(_id)

    return listings
