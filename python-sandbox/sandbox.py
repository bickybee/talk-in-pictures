import os
import spacy
import requests
from requests_oauthlib import OAuth1
from flask import Flask, json, render_template, jsonify, request, session
from flask_socketio import emit, SocketIO
import wave
import uuid

from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types

from analysis import *

# setup
nlp = spacy.load('en')
app = Flask(__name__)
socketio = SocketIO(app)

language_code = 'en-US'  # a BCP-47 language tag
# Audio recording parameters
RATE = 16000 # should grab this from an http get (audiocontext)
CHUNK = int(RATE / 10)  # 100ms

client = speech.SpeechClient()
config = types.RecognitionConfig(
    encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
    sample_rate_hertz=RATE,
    language_code=language_code)
streaming_config = types.StreamingRecognitionConfig(
    config=config,
    interim_results=True)

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
    # icon_list = sentence_to_icons(data["input"])
    # retval = {"tokens":[icon.__dict__ for icon in icon_list]}

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

# From Miguel Grinberg's SocketIO-Examples
# https://github.com/miguelgrinberg/socketio-examples/tree/master/audio
@socketio.on('start-recording')
def start_recording(options):
    """Start recording audio from the client."""
    id = uuid.uuid4().hex  # server-side filename
    session['wavename'] = id + '.wav'
    wf = wave.open(session['wavename'], 'wb')
    wf.setnchannels(options.get('numChannels', 1))
    wf.setsampwidth(options.get('bps', 16) // 8)
    wf.setframerate(options.get('fps', 44100))
    session['wavefile'] = wf

    ########################
    # Temporary pseudocode #
    ########################
    # Pass the file to the Google Speech API
    # Parse output from the API
    # Generate icons using output received
    # Use emit('add-transcription', <data>) to update the client

@socketio.on('write-audio')
def write_audio(data):
    """Write a chunk of audio from the client."""
    session['wavefile'].writeframes(data)

@socketio.on('end-recording')
def end_recording():
    """Stop recording audio from the client."""
    emit('add-transcription', "hello")
    session['wavefile'].close()
    del session['wavefile']
    del session['wavename']
