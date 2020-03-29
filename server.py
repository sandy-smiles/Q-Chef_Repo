##########################################
# Q-Chef Server
# Authors: Q-Chef Backend Programmers
##########################################
import cred
import taste_pref

import random as rand
from flask import Flask, request, jsonify

# Create a web server
app = Flask(__name__)

##########################################
# API URLs
##########################################
# API index - shows when people visit the home page
@app.route('/')
def home():
    return 'Hello!\nYou have reached the backend API for Q-Chef.'

# API about - page about contacts that might be needed?
@app.route('/about')
def about():
    return 'Q-Chef is ...'

# API save diet req - saving the user's dietary requirements
@app.route('/diet_req')
def about():
    requ = request.json
    resp = {}
    resp[user_id] = requ["user_id"]

    return jsonify(info)

##########################################
# Testing URLs
##########################################
# API pref - returns json list of recipes
# TODO(kbona@): Return a list of 10 pref recipes.
@app.route('/pref/<id>')
def taste_preference(id):
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

##########################################
# Server Activation
##########################################
# Start the web server!
if __name__ == "__main__":
    app.run()