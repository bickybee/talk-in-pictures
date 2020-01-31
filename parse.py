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
import webcolors

# Setup
#import en_core_web_sm
#nlp = en_core_web_sm.load()
nlp = spacy.load('models/en_core_web_sm')
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

KEYWORD_BLACKLIST = ["what", "do", "can", "it", "i", "a", "or"]

# Color image site:
COLOR_IMG_STR = "https://www.colorhexa.com/{}.png"


class ImageManager:
    """
    This class needs a more suitable name...
    Holds onto and manages all the phrase-to-image info!
    """

    def __init__(self):
        self.concreteness_analyser = WordConcretenessAnalyser()
        self.images = {}
        self.phrases = []
        self.current_phrase = []
        self.current_phrase_index = -1
        self.num_requests = 0 # For debugging
        self.api = 0
        self.phrase_count = 0
        
    def set_api(self, api: str) -> None:
        """
        Which image-search API will we use? This is called at start-up with a command line argument
        """
        
        if api == "photo":
            self.api = BING_API
        elif api == "icon":
            self.api = NOUN_PROJECT_API

    def update_phrase_count(self) -> None:
        print("NUM RECORDINGS")
        self.phrase_count = len(self.phrases)
        print (self.phrase_count)

    def get_current_phrase_index(self) -> int:
        return self.current_phrase_index

    # Parse a request!
    def parse_request(self, phrase: str, num: int) -> List[Dict[str, str]]:

        index = num + self.phrase_count

        self.current_phrase = self.parse_sentence(phrase)

        # Either push new phrase
        if index > self.current_phrase_index:
            self.phrases.append(self.current_phrase)
            self.current_phrase_index = index
        
        # Or update current phrase
        else:
            self.phrases[index] = self.current_phrase

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
        print(token.pos_)

        # If plural noun, use singular as our keyword
        if token.tag_ == "NNS":
            keyword = inf.singular_noun(token.text)

        # If color, return a color
        color_img = self.image_from_color(keyword)
        if color_img is not "":
            img = color_img

        # Only try to visualize word if it is concrete enough
        # if self.concreteness_analyser.is_concrete_enough(keyword) and (keyword not in KEYWORD_BLACKLIST):
        elif (token.pos_ == "VERB" or token.pos_ == "NOUN" or self.concreteness_analyser.is_concrete_enough(keyword)) and (keyword not in KEYWORD_BLACKLIST):
        
            # If we've fetched the image for this keyword before, grab it from our cache dict
            if keyword in self.images:
                img = self.images[keyword]["url"] 

            # Otherwise, call the API to get an image
            else:
                if self.api == NOUN_PROJECT_API:
                    img = self.image_from_noun_project(keyword)
                    print(img)
                elif self.api == BING_API:
                    img = self.image_from_bing(keyword)
                # How many requests are we making lol
                self.num_requests += 1
                print(self.num_requests)

        # Return our results

        icon = {"word": token.text, "keyword": keyword, "img": img}
        return icon

    # For when the primary image of a word is updated, make sure to update the image url in all our phrases
    def update_all_phrases(self) -> List[Dict[str, str]]:
        for phrase in self.phrases:
            for word in phrase:
                if word["keyword"] in self.images:
                    updated_img_url = self.images[word["keyword"]]["url"]
                    word["img"] = updated_img_url
    
    # Get a list of up to 10 images for the keyword
    def get_image_list(self, keyword: str) -> List[str]:
        if keyword in self.images:
            return self.images[keyword]["all_urls"]
        
        return []
    
    # Set the primary image url for a keyword to the url at INDEX in that keyword's image list
    def set_image(self, keyword: str, url: str) -> bool:
        if keyword in self.images:
            self.images[keyword]["url"] = url
            self.update_all_phrases()
            return True
        
        return False

    # Return url of the first image from The Noun Project API
    # Also creates an entry in our image cache, including up to 10 images
    def image_from_noun_project(self, keyword: str) -> str:
        img = ""

        try:
            response = requests.get(ENDPOINT_BASE + keyword + ENDPOINT_PARAMS, auth=auth)
            print(response.status_code)
            if response.status_code == 200:
                data = json.loads(response.content)
                icons = data["icons"]
                img = icons[0]['preview_url']
                # Cache it so we don't need to look it up again!
                self.images[keyword] = {
                    "url": img,
                    "all_urls": [icon['preview_url'] for icon in icons]
                }

        except:
            print("RESPONSE ERROR: noun project API keys likely not set properly")

        return img

    # Return url of the first image from Bing's image search API
    # Also creates an entry in our image cache, including up to 10 images
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
                self.images[keyword] = {
                    "url": img,
                    "all_urls": [image['contentUrl'] for image in images]
                }

        except:
            print("RESPONSE ERROR: bing API keys likely not set properly")

        return img

    def image_from_color(self, keyword) -> str:
        if keyword in webcolors.CSS3_NAMES_TO_HEX:
            hex_color_code = webcolors.CSS3_NAMES_TO_HEX[keyword].strip("#")
            return COLOR_IMG_STR.format(hex_color_code)
        return ""
