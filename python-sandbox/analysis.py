from typing import List
from flask import json
import time
import spacy
import inflect
import requests
from requests_oauthlib import OAuth1
import os
import nltk

# setup
nlp = spacy.load('en')
inf = inflect.engine()

# auth for the noun project API
noun_project_api_key = os.environ.get("NOUN_PROJECT_API_KEY") # in the shell, $ export NOUN_PROJECT_API_KEY=key
noun_project_api_secret = os.environ.get("NOUN_PROJECT_API_SECRET") # in the shell, $ export NOUN_PROJECT_API_SECRET=secret 
auth = OAuth1(noun_project_api_key, noun_project_api_secret)

# some convenient strings for the API...
ENDPOINT_BASE = "http://api.thenounproject.com/icons/"
ENDPOINT_PARAMS = "?limit_to_public_domain=1&limit=1"

class Icon:
    def __init__(self, word, keyword, img, timestamp):
        self.word = word
        self.keyword = keyword
        self.img = img
        self.timestamp = timestamp


def sentence_to_icons(sentence: str) -> List[Icon]:
    analyzed = nlp(sentence)
    new_icons = []
    for token in analyzed:
        icon = token_to_icon(token)
        if icon:
            new_icons.append(icon)
    return new_icons

def token_to_icon(token) -> Icon: # how to type-hint spacy.Token?
    img = ""
    keyword = token.text

    if token.tag_ == "NNS":
        keyword = inf.singular_noun(token.text)

    try:
        response = requests.get(ENDPOINT_BASE + token.text + ENDPOINT_PARAMS, auth=auth)

        # Found image:
        if response.status_code == 200:
            data = json.loads(response.content)
            img = data['icons'][0]['preview_url']

    except:
        print("RESPONSE ERROR: noun project API keys likely not set properly")

    return Icon(token.text, keyword, img, time.time())
