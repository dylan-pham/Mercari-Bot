import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
import time

cred = credentials.Certificate("mercari-bot-337508-0a00be491377.json")
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
    browser = webdriver.Safari()
    browser.get(url)
    time.sleep(3)

    soup = BeautifulSoup(browser.page_source, "html.parser")

    search_results = soup.find("div", {"data-testid" : "SearchResults"}).find("div").find("div").find_all("div", recursive=False)

    listings = set()
    for search_result in search_results:
        _id = search_result.find("a").find("div")["data-productid"]
        listings.add(_id)

    return listings

add_new_search("Airpods Pro", "https://www.mercari.com/search/?categoryIds=1593&itemConditions=1-2&itemStatuses=1&keyword=AirPods%20pro&maxPrice=10000&minPrice=3500&sortBy=2")

# print(len(retrieve_listings("https://www.mercari.com/search/?brandIds=319&customFacets%5BModel%5D=AirPods%20Pro&itemConditions=1-2&itemStatuses=1&keyword=airpods&maxPrice=10000&minPrice=5000&searchId=249995205&sortBy=2")))