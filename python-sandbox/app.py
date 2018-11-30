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

@app.route("/images/<keyword>", methods=['GET'])
def get_images(keyword):
    """
    Handles a GET request, returning a JSON object that lists up to 10 image urls for <keyword>
    (IMPORTANT!! <keyword> NOT just <word>-- cuz we may have a different "keyword" if the original "word" is plural)
    Body of response is in the format:

        {
            "images": [<url1>, <url2>, <url3>...]
        }

    """
    images = image_manager.get_image_list(keyword)
    retval = {"images": images}

    # Set up response
    res = app.response_class(
        response=json.dumps(retval),
        status=200,
        mimetype='application/json'
    )

    return res

@app.route("/image/<keyword>", methods=['PUT'])
def set_image(keyword):
    """
    Handles a PUT request, setting the image for <keyword> to a new <url>
    Request body is in the format:

        {
            "img": <url>
        }

    Only returns a response status code!
    """
    status = 200
    data = request.get_json()
    img = data["img"]
    success = image_manager.set_image(keyword, img)
    if not success:
        status = 204

    retval = {"img": data["img"]}
    res = app.response_class(
        response=json.dumps(retval), # send it back? lol
        status=status,
        mimetype='application/json'
    )

    return res

@app.route("/phrases", methods=['GET'])
def get_phrases():
    """
    Handles a GET request, returning a JSON object that contains a list of all phrases (which are lists of word-keyword-image dicts)

        {
            "phrases": [
                [
                    {
                        "word": "<token>",
                        "keyword: "<keyword>",
                        "img": "<url>" (or "" if no image found)

                    },
                    {
                        ...
                    }
                ],
                [
                    ...
                ]
            ]
        }

    """
    retval = {"phrases": image_manager.all_phrases}

    res = app.response_class(
        response=json.dumps(retval),
        status=200,
        mimetype='application/json'
    )

    return res


@app.route("/phrases/<index>", methods=['PUT', 'GET'])
def get_set_phrase(index):

    ind = int(index)

    if request.method == "GET":
        """
        Handles a GET request, returns a response containing the <index>-th phrase (as a list of dicts)

            {
                "phrase": 
                    [
                        {
                            "word": "<word>",
                            "keyword: "<keyword>",
                            "img": "<url>" (or "" if no image found)

                        },
                        {
                            ...
                        }
                    ]
            }

        """

        # If the given index exists in the phrase-list, return the phrase
        if ind < len(image_manager.all_phrases):
            retval = {"phrase": image_manager.all_phrases[ind]}
            res = app.response_class(
                response=json.dumps(retval),
                status=200,
                mimetype='application/json'
            )
            return res
        
        # Else, error!
        else:
            res = app.response_class(
                status=404,
                mimetype='application/json'
            )
            return res

    if request.method == "PUT":
        """
        Handle a PUT request whose body is in the format:

            {
                "input": "<sentence>"
            }

        Creates OR modifies the <index>-th phrase, returns it with the response format:

            {
                "phrase": 
                    [
                        {
                            "word": "<word>",
                            "keyword: "<keyword>",
                            "img": "<url>" (or "" if no image found)

                        },
                        {
                            ...
                        }
                    ],
                "index": <index>
            }

        """

        # Handle body
        data = request.get_json()
        parsed = image_manager.parse_request(data["input"], ind)
        index = image_manager.get_current_phrase_index()
        retval = {
            "phrase": parsed,
            "index": index
        }

        # Set up response
        res = app.response_class(
            response=json.dumps(retval),
            status=200,
            mimetype='application/json'
        )

        return res

@app.route("/end", methods=['POST'])
def end_recording():
    image_manager.update_phrase_count()

    res = app.response_class(
            status=200,
            mimetype='application/json'
    )

    return res

if __name__ == "__main__":
    if len(sys.argv) > 1:
        image_manager.set_api(sys.argv[1])
    app.run()