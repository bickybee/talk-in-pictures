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

# Setup
nlp = spacy.load('en')
inf = inflect.engine()

# Auth for the noun project API
noun_project_api_key = os.environ.get("NOUN_PROJECT_API_KEY") # in the shell, $ export NOUN_PROJECT_API_KEY=key
noun_project_api_secret = os.environ.get("NOUN_PROJECT_API_SECRET") # in the shell, $ export NOUN_PROJECT_API_SECRET=secret 
auth = OAuth1(noun_project_api_key, noun_project_api_secret)

# Convenient strings for the API
ENDPOINT_BASE = "http://api.thenounproject.com/icon/"
ENDPOINT_PARAMS = "?limit_to_public_domain=1&limit=1"

class IconManager:

    def __init__(self):
        self.cached_icons = {}
        self.all_phrases = []
        self.current_phrase = []
        self.current_phrase_num = -1
        
    def parse_request(self, data: Dict) -> List[Dict[str, str]]:

        self.current_phrase = self.parse_sentence(data["input"])
        phrase_num = data["phrase_num"]

        # Either push new phrase
        if phrase_num > self.current_phrase_num:
            self.all_phrases.append(self.current_phrase)
            current_phrase_num = phrase_num
        
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

        #return [self.parse_token(token) for token in analyzed]
        # num_new_tokens = len(analyzed) - len(icons.all_phrases)
        # start_index = len(analyzed) - num_new_tokens

        # for i in range(start_index, len(analyzed)):
        #     icons.all_phrases.append(parse_token(analyzed[i]))
        
        #return icons.all_phrases

    def parse_token(self, token) -> Dict[str, str]:
        # Default: no image
        img = ""
        keyword = token.text

        # If word is plural, convert to singular for enhanced keyword search
        if token.tag_ == "NNS":
                keyword = inf.singular_noun(token.text)

        # We are only fetching icon images for nouns and verbs...
        if token.pos_ is "NOUN" or token.pos_ is "VERB":

            # If we've fetched the icon for this keyword before, grab it from our cache dict
            if keyword in self.cached_icons:
                img = self.cached_icons[keyword]

            # Otherwise, call the API to get an img
            else:
                try:
                    response = requests.get(ENDPOINT_BASE + token.text , auth=auth)

                    # Found image:
                    if response.status_code == 200:
                        data = json.loads(response.content)
                        img = data['icon']['preview_url']
                        # Cache it so we don't need to look it up again!
                        self.cached_icons[keyword] = img

                except:
                    print("RESPONSE ERROR: noun project API keys likely not set properly")

        # Return our resultss
        icon = {"word": token.text, "keyword": keyword, "img": img}
        return icon

'''
Would eventually like to use some kind of class but for now it's a bit slower than just converting straight to JSON
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