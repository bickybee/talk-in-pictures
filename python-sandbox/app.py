from flask import Flask, json, render_template, jsonify, request, session
from flask_session import Session
from parse import *
import sys

app = Flask(__name__)
# # Should I be using sessions to store state?
# app.secret_key = 'super secret key'
# app.config['SESSION_TYPE'] = 'filesystem'
# Session(app)
image_manager = ImageManager()

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/images", methods=['GET'])
def images():
    """
    Handle a GET request whose args are in the format:
        /images?word=<string>

    And return a JSON object that lists up to 10 image urls for the given word

    Body of response is in the format:
    {
        "images": [<url1>, <url2>, <url3>...]
    }
    """
    word = request.args.get("word")
    images = image_manager.get_image_list(word)
    retval = {"images": images}

    # Set up response
    res = app.response_class(
        response=json.dumps(retval),
        status=200,
        mimetype='application/json'
    )

    return res


@app.route("/parse", methods=['POST'])
def parse():
    """
    Handle a POST request whose body is in the format:
        {"input": "<sentence>",
        "num_phrase": num}

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
    parsed = image_manager.parse_request(data)
    retval = {"tokens": parsed}

    # Set up response
    res = app.response_class(
        response=json.dumps(retval),
        status=200,
        mimetype='application/json'
    )

    return res

if __name__ == "__main__":
    if len(sys.argv) > 1:
        image_manager.set_api(sys.argv[1])
    app.run()