# csc2526-project

## Online usage

Click the mic to turn it on, talk to see your words turn into pictures. Click on icons to have the option to "clarify" the selected image. 

Works in Chrome.

## Setup

To set up the project, install all dependencies using:

```
pipenv install
```

Create a .env file with the following:

```
FLASK_APP=app.py
NOUN_PROJECT_API_KEY=[your-API-key]
NOUN_PROJECT_API_SECRET=[your-API-secret]
```

Now you can run the project with Flask.

```
pipenv run flask run
```
