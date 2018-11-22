from flask import Flask, json, render_template, jsonify, request, session
from flask_session import Session
from parse import *

app = Flask(__name__)
# # Should I be using sessions to store state?
# app.secret_key = 'super secret key'
# app.config['SESSION_TYPE'] = 'filesystem'
# Session(app)
icon_manager = IconManager()

@app.route("/")
def home():
    return render_template('index.html')

@app.route('/set/')
def set():
    session['key'] = 'value'
    return 'ok'

@app.route('/get/')
def get():
    return session.get('key', 'not set')

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
    parsed = icon_manager.parse_request(data)
    retval = {"tokens": parsed}

    # Set up response
    res = app.response_class(
        response=json.dumps(retval),
        status=200,
        mimetype='application/json'
    )

    return res