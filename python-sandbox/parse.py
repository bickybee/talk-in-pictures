'''
Module for parsing text with NLP, outputting relevant icons.
'''
from typing import List, Dict
from flask import json
import time
import spacy
import inflect
import requests
from requests_oauthlib import OAuth1
import os
import nltk
from concreteness import *

# Setup
nlp = spacy.load('en')
inf = inflect.engine()

# Stuff for APIs
# The Noun Project:
noun_project_api_key = os.environ.get("NOUN_PROJECT_API_KEY") # in the shell, $ export NOUN_PROJECT_API_KEY=key
noun_project_api_secret = os.environ.get("NOUN_PROJECT_API_SECRET") # in the shell, $ export NOUN_PROJECT_API_SECRET=secret 
ENDPOINT_BASE = "http://api.thenounproject.com/icons/"
ENDPOINT_PARAMS = "?limit_to_public_domain=1&limit=10"
# Bing:
auth = OAuth1(noun_project_api_key, noun_project_api_secret)
bing_key = os.environ.get("BING_KEY2")
bing_url = "https://api.cognitive.microsoft.com/bing/v7.0/images/search"

# Which API? (default is noun project)
NOUN_PROJECT_API = 0
BING_API = 1

class ImageManager:

    def __init__(self):
        self.concreteness_analyser = WordConcretenessAnalyser()
        print("loaded concreteness ratings")
        self.cached_images = {}
        self.all_phrases = []
        self.current_phrase = []
        self.current_phrase_num = -1
        self.num_requests = 0
        self.api = 0
        
    def set_api(self, api: str) -> None:
        if api == "photo":
            self.api = BING_API
        elif api == "icon":
            self.api = NOUN_PROJECT_API

    def parse_request(self, data: Dict) -> List[Dict[str, str]]:

        self.current_phrase = self.parse_sentence(data["input"])
        phrase_num = data["phrase_num"]

        # Either push new phrase
        if phrase_num > self.current_phrase_num:
            self.all_phrases.append(self.current_phrase)
            self.current_phrase_num = phrase_num
        
        # Or update current phrase
        else:
            self.all_phrases[phrase_num] = self.current_phrase

        return self.current_phrase

    def parse_sentence(self, sentence: str) -> List[Dict[str, str]]:
        analyzed = nlp(sentence)
        new_phrase = []
        # Compare against current phrase so far to see what's changed
        # Avoid unnecessary parses of words we already have
        for i in range(len(analyzed)):
            if i < len(self.current_phrase):
                if analyzed[i].text == self.current_phrase[i]['word']:
                    new_phrase.append(self.current_phrase[i])
                    continue
            new_phrase.append(self.parse_token(analyzed[i]))

        return new_phrase

    def parse_token(self, token) -> Dict[str, str]:
        # Default: no image
        img = ""
        keyword = token.text
        # We are only fetching icon images for nouns and verbs...
        if self.concreteness_analyser.is_concrete_enough(keyword):

            # If we've fetched the icon for this keyword before, grab it from our cache dict
            if keyword in self.cached_images:
                img = self.cached_images[keyword]["url"]

            # Otherwise, call the API to get an img
            else:
                if self.api == NOUN_PROJECT_API:
                    img = self.image_from_noun_project(keyword)
                elif self.api == BING_API:
                    img = self.image_from_bing(keyword)
                # How many requests are we making lol
                self.num_requests += 1
                print(self.num_requests)

        # Return our resultss
        icon = {"word": token.text, "keyword": keyword, "img": img}
        return icon
    
    def get_image_list(self, keyword: str) -> List[str]:
        if keyword in self.cached_images:
            return self.cached_images[keyword]["all_urls"]
        
        return []

    def image_from_noun_project(self, keyword: str) -> str:
        img = ""

        try:
            response = requests.get(ENDPOINT_BASE + keyword + ENDPOINT_PARAMS, auth=auth)

            if response.status_code == 200:
                data = json.loads(response.content)
                icons = data["icons"]
                img = icons[0]['preview_url']
                # Cache it so we don't need to look it up again!
                self.cached_images[keyword] = {
                    "url": img,
                    "all_urls": [icon['preview_url'] for icon in icons]
                }

        except:
            print("RESPONSE ERROR: noun project API keys likely not set properly")

        return img

    def image_from_bing(self, keyword) -> str:
        img = ""

        try:
            headers = {"Ocp-Apim-Subscription-Key" : bing_key}
            params  = {"q": keyword, "count": 10, "license": "public", "imageType": "photo"}
            response = requests.get(bing_url, headers=headers, params=params)
            search_results = response.json()

            if response.status_code == 200:
                search_results = response.json()
                images = search_results["value"]
                img = images[0]["contentUrl"]
                # Cache it so we don't need to look it up again!
                self.cached_images[keyword] = {
                    "url": img,
                    "all_urls": [image['contentUrl'] for image in images]
                }

        except:
            print("RESPONSE ERROR: bing API keys likely not set properly")

        return img

'''
Would eventually like to use some kind of class but for now it's a bit slower than just converting straight to JSON
'''

'''
class Icon:
    def __init__(self, word, keyword, img, occurence):
        self.word = word
        self.keyword = keyword
        self.img = img
        self.occurence = occurence

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
'''