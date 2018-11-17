from flask import Flask, json, render_template, jsonify, request, session
from parse import *

app = Flask(__name__)

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
    parsed = parse_sentence(data["input"])
    retval = {"tokens": parsed}

    # Set up response
    res = app.response_class(
        response=json.dumps(retval),
        status=200,
        mimetype='application/json'
    )

    return res