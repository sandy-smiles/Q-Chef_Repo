import cred
import taste_pref
import surprise_models

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

# API surprise - returns json list of recipes that are predicted to surprise a given userid
# TODO(kazjon@): Return a list of 10 surprising recipes.
@app.route('/surp/<id>')
def surp(id):
    err = checkID(id)
    if err:
        return f'Unable to find user {id}. Unable to return a list of surprising recipes. err = {err}'

    userSurprising = {10: "Chicken and vanilla wrap", 8: "Beeswax gnocchi", 4: "Salmon and steak", 42: "Roti canai ice cream"}
    userRecipes = {} # TODO(kazjon@): grab dict of recipes not already reviewed by user from db
    allowedRecipes = userRecipes.keys()

    ratings = []
    for recipe_id in allowedRecipes:
        ratings.append((recipe_id,surprise_models.surpRecipe(id,recipe_id)))
    picks = [x[0] for x in sorted(ratings)][:10]

    return jsonify(picks)

######## Server Activation ########
if __name__ == "__main__":
# Start the web server!
app.run(port=8888, debug=True)
