# csc2526-project

### python-sandbox

Using pipenv as a dependency & virtual environment manager.

In the repo, install dependencies using:

```
pipenv install
```

Now you can access the environment shell with all the dependencies (like Flask) ready to go.

```
pipenv shell
```

In order for the spaCy NLP library to work, you need to download some english languages stuff too.
Do so in the shell.

```
python -m spacy download en
```

And now, in the shell, you can run the project with Flask.

```
FLASK_APP=sandbox.py flask run
```

Also, you'll need the API key and secret from Vicky!

Then set them as environment variables in the pipenv shell.
