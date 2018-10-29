import os
import spacy
import requests
from requests_oauthlib import OAuth1
from flask import Flask, json

# setup
nlp = spacy.load('en')
app = Flask(__name__)

# auth for the noun project API
noun_project_api_key = os.environ.get("NOUN_PROJECT_API_KEY") # in the shell, $ export NOUN_PROJECT_API_KEY=key
noun_project_api_secret = os.environ.get("NOUN_PROJECT_API_SECRET") # in the shell, $ export NOUN_PROJECT_API_SECRET=secret 
auth = OAuth1(noun_project_api_key, noun_project_api_secret)

# some convenient strings for the API...
ENDPOINT_BASE = "http://api.thenounproject.com/icons/"
ENDPOINT_PARAMS = "?limit_to_public_domain=1&limit=1"

# default route
@app.route("/")
def hello():
    return "Hello world! :-)"

# sentence -> icons!
# delimit sentence with dashes instead of spaces
@app.route("/parse/<string:sentence>")
def parse(sentence):
    sentence = sentence.replace("-", " ")
    analyzed = nlp(sentence)
    # append an icon for every noun found
    icon_str = ""
    for word in analyzed:
        print (word.text + " " + word.tag_)
        if word.tag_ == "NN": # only handling non-plural nouns right now
            response = requests.get(ENDPOINT_BASE + word.text + ENDPOINT_PARAMS, auth=auth)
            if response.status_code == 200: # if we successfully find an icon...
                data = json.loads(response.content)
                # append icon image to return string (since there's no front-end lol)
                icon_str += "<img src=\'" + data['icons'][0]['preview_url'] + "\'>"

    return icon_str