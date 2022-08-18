from bs4 import BeautifulSoup
import requests
import os
from twilio.rest import Client
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import time
from selenium import webdriver

cred = credentials.Certificate("mercari-bot-337508-0a00be491377.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
collection_ref = db.collection("searches")

account_sid = os.environ['TWILIO_ACCOUNT_SID']
twilio_phone_number = os.environ['TWILIO_PHONE_NUMBER']
my_phone_number = os.environ['MY_PHONE_NUMBER']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
client = Client(account_sid, auth_token)

headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15"}

def send_sms_notif(product_details):
    title = product_details[0]
    price = product_details[2]
    link = product_details[1]

    body = title + " " + price + "\n\nhttps://mercari.com" + link
    message = client.messages \
        .create(
            body=body,
            from_=twilio_phone_number,
            to=my_phone_number
         )

def get_new_listings(doc):
    browser = webdriver.Safari()
    browser.get("https://www.mercari.com/search/?keyword=iphone")
    time.sleep(3)

    soup = BeautifulSoup(browser.page_source, "html.parser")
    search_results = soup.find("div", {"data-testid" : "SearchResults"}).find("div").find("div").find_all("div", recursive=False)

    product_details = dict()
    current_listings = set()
    for search_result in search_results:
        title = search_result.find("a").find("div").find_all("div")[1].find("div").find("div")
        link = search_result.find("a")["href"]
        price = search_result.find("a").find("div").find_all("div", recursive=False)[1].find_all("div", recursive=False)[1].find("p").find("span").text
        _id = search_result.find("a").find("div")["data-productid"]

        product_details[_id] = (title, link, price)
        current_listings.add(_id)

    # updating database with most recent set of listings
    collection_ref.document(doc.id).update({"listings": current_listings})

    new_listings = current_listings - set(doc.get("listings"))
    return new_listings, product_details

def notif_new_listings(new_listings, product_details):
    for product_id in new_listings:
        send_sms_notif(product_details[product_id])

def main():
    for doc in collection_ref.stream():
        new_listings, product_details = get_new_listings(doc)
        print(new_listings)
        # notif_new_listings(new_listings, product_details)

    print("ran")

while True:
    main()

    # check for new listings every half hour
    time.sleep(1800)