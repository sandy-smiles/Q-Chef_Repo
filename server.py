import cred
import taste_pref 

import random as rand
from flask import Flask, request, jsonify

# Create a web server
app = Flask(__name__)

######## API URLs ########
# API index - shows when people visit the home page
@app.route('/')
def home():
    return 'Hello!\nYou have reached the backend API for Q-Chef.'

# API about - page about contacts that might be needed?
@app.route('/about')
def about():
    return 'Q-Chef is ...'

# API hello - ID validator?
@app.route('/<id>')
def hello(id):
    return f'Hello user {id}. Welcome to Q-Chef!'

# API pref - returns json list of recipes
# TODO(kbona@): Return a list of 10 pref recipes.
@app.route('/pref/<id>')
def pref(id):
    err = checkID(id)
    if err:
        return f'Unable to find user {id}. Unable to return a list of preferenced recipes. err = {err}'

    userPreferenced = {10: "Chicken Wrap", 8: "Gnocchi", 4: "Salmon Steak", 42: "Roti Canai"}
    userRecipes = {} # grab dict of user's recipes not rated from db
    allowedRecipes = userRecipes.keys()
    picked = -1 # index not allowed.

    """
        for i in range(10):
            while picked != -1: # tolerance > choice:
                picked = rand.Random(allowedRecipes)
                allowedRecipes.remove(picked)
            userPreferenced[picked] = userRecipes[picked]
            picked = -1 # TODO(kbona@): Remove once finalised while loop logic.
    """

    return jsonify(userPreferenced)

######## Server Activation ########
if __name__ == "__main__":
# Start the web server!
app.run(port=8888, debug=True)
