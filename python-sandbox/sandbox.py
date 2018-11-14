import os
import spacy
import requests
from requests_oauthlib import OAuth1
from flask import Flask, json, render_template, jsonify, request

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
def home():
    return render_template('index.html')

# Returns a JSON object containing a breakdown of all tokens, mapped
# to icons from the Noun Project (if such an icon exists)

@app.route("/parse", methods=['POST'])
def parse():
    """
    Handle a POST request whose body is in the format:
        {"input": "<sentence>"}

    And return a JSON object mapping each token in the sentence to an
    image URL from the Noun Project.

    Body of response is in the format:
    {
        "tokens: 
            [
                {
                    "word": "<token>",
                    "img": "<url>" (or "" if no image found)
                },
                {
                    ...
                }
            ]
    }
    """

    # Handle body
    data = request.get_json()

    # Perform tagging
    sentence = data["input"]
    analyzed = nlp(sentence)

    # Keep track of word:icon mappings
    retval = {"tokens": []}

    # Find an image for each token, if it exists
    for word in analyzed:
        to_append = {}
        to_append["word"] = word.text
        to_append["img"] = ""

        # print (word.text + " " + word.tag_)

        if word.tag_ == "NN": # only handling non-plural nouns right now
            try:
                response = requests.get(ENDPOINT_BASE + word.text + ENDPOINT_PARAMS, auth=auth)

                # Found image:
                if response.status_code == 200:
                    data = json.loads(response.content)
                    to_append["img"] = data['icons'][0]['preview_url']

            except:
                print("RESPONSE ERROR: noun project API keys likely not set properly")

        retval["tokens"].append(to_append)

    # print(retval)

    # Set up response
    res = app.response_class(
        response=json.dumps(retval),
        status=200,
        mimetype='application/json'
    )

    return res