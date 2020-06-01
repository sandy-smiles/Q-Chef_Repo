################################################################################
# Q-Chef Server
# Authors: Q-Chef Backend Programmers
# Updated: 20200418
################################################################################
# Imports and application creation
################################################################################
import os
import json
import requests
from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS, cross_origin

# Create a web server
app = Flask(__name__)

################################################################################
# Constants
################################################################################
documentationUrl = "https://www.docs.google.com/document/d/1iNerEqPo3D_fMmJwdRgAc42P3XKh6JzDNiu1Xo1z5hc/edit?usp=sharing"

backendIndexUrl = "https://q-chef-test.herokuapp.com"

listDelimiter = ";"

collectionIDs = ['users',
                 'recipes',
                 'ingredients',
                 'ingredient_clusters',
                 'ingredient_subclusters',
                 'onboarding']

userStartingDoc = {
  'i_taste' : {},
  'is_taste': {},
  'ic_taste': {},
  'r_taste' : {},
  'i_familiarity' : {},
  'is_familiarity': {},
  'ic_familiarity': {},
  'r_familiarity' : {},
  'pickedRecipes': []
}

relativeIngredientsFilePath = "./tmp_ingredients"
relativeRecipesFolderPath = "./tmp_recipes"

################################################################################
# Debugging
################################################################################
DEBUG = True
WARN = True
INFO = True
DATA = True
HELP = True

def debug(fString):
  if DEBUG and 'ERROR' in fString:
    print(fString)
    return

  if DEBUG and WARN and 'WARNING' in fString:
    print(fString)
    return

  if DEBUG and INFO and 'INFO' in fString:
    print(fString)
    return

  if DEBUG and DATA and 'DATA' in fString:
    print(fString)
    return

  if DEBUG and HELP and 'HELP' in fString:
    print(fString)
    return

################################################################################
# Helper Functions
################################################################################
# getExampleIngredients - Input: Number of ingredients, Output: Dictionary
def getExampleIngredients(n):
  ingredients = {}
  with open(relativeIngredientsFilePath, 'r') as f:
    for line in f:
      ingredient_id, ingredient_name = line.strip().split(listDelimiter)
      ingredients[ingredient_id] = ingredient_name

  if n == -1:
    n = len(ingredients.keys())

  r = {}
  for i, ingredient_id in enumerate(ingredients.keys()):
    if i > n:
      break
    r[ingredient_id] = ingredients[ingredient_id]

  return r

################################################################################
# getExampleRecipes - Input: Number of recipes, Output: Dictionary
def getExampleRecipes(n):
  recipe_ids = []
  for rootFolder, directories, fileNames in os.walk(relativeRecipesFolderPath):
    fileNames.sort()
    recipe_ids = fileNames
    break
  print(recipe_ids)

  if n == -1:
    n = len(recipe_ids)
    print(f"n = {n}")

  r = {}
  for i, recipe_id in enumerate(recipe_ids):
    print(f"i = {i}, recipe_id = {recipe_id}")
    if i > n:
      print("Breaking... i = {i}, n = {n}")
      break
    fileName = f"{relativeRecipesFolderPath}/{recipe_id}"
    print(f"Attempting to open file {fileName}")
    with open(fileName, 'r') as f:
      print(f"recipe_id = {recipe_id}")
      recipe_dic = json.load(f)
      print(f"recipe_dic = {recipe_dic}")
      r[recipe_id] = recipe_dic

  return r

################################################################################
# API URLs
################################################################################
# API index - shows when people visit the home page
@app.route('/', methods=['GET', 'POST'])
def home():
  debug('[HOME - INFO]: Request for the home page...')
  try:
    debug(f'[HOME - INFO]: Redirecting to index page {backendIndexUrl}.')
    return redirect(backendIndexUrl)
  except:
    return f"[HOME - ERROR]: Something went wrong..."

################################################################################
# Backend End Points URLs
################################################################################
# onboarding_ingredient_rating [GET|POST]
# 1st end point used.
# GET: End point is for obtaining the ingredients for the user to rate
# during on-boarding.
# - Input:
#   - n/a
# - Output:
#   - (json)
# POST: End point is for saving the user's ratings of ingredients
# during on-boarding.
# - Input:
#   - (json)
# - Output:
#   - (string) error
@app.route('/onboarding_ingredient_rating', methods=['GET', 'POST'])
@cross_origin()
def onboarding_ingredient_rating():
  debug(f'[onboarding_ingredient_rating - INFO]: Starting.')
  try:
    if request.method == 'POST':
      debug('[onboarding_ingredient_rating - INFO]: POST request')
      request_data = json.loads(request.data)
      debug(f'[onboarding_ingredient_rating - DATA]: request_data: {request_data}')
      return ''

    debug('[onboarding_ingredient_rating - INFO]: GET request')
    return jsonify(getExampleIngredients(-1))
  except:
    return f"[onboarding_recipe_rating - ERROR]: Something went wrong..."
  return ""

################################################################################
# onboarding_recipe_rating [GET|POST]
# 2nd end point used.
# GET: End point is for obtaining the recipes for the user to rate 
# during on-boarding.
# - Input:
#   - n/a
# - Output:
#   - (json)
# POST: End point is for saving the user's initial ratings of recipes 
# (during onboarding).
# - Input:
#   - (json)
# - Output:
#   - (json)
@app.route('/onboarding_recipe_rating', methods=['GET', 'POST'])
@cross_origin()
def onboarding_recipe_rating():
  debug(f'[onboarding_recipe_rating - INFO]: Starting.')
  try:
    if request.method == 'POST':
      debug('[onboarding_recipe_rating - INFO]: POST request')
      request_data = json.loads(request.data)
      debug(f'[onboarding_recipe_rating - DATA]: request_data: {request_data}')
      return jsonify(getExampleRecipes(-1))

    debug('[onboarding_recipe_rating - INFO]: GET request')
    return jsonify(getExampleRecipes(-1))
  except:
    return f"[onboarding_recipe_rating - ERROR]: Something went wrong..."
  return ""

################################################################################
# validation_recipe_rating [POST]
# POST: End point is for saving the final set of user's reviews of recipes
# given (during onboarding).
# - Input:
#   - (json)
# - Output:
#   - (string) error
@app.route('/validation_recipe_rating', methods=['POST'])
@cross_origin()
def validation_recipe_rating():
  debug(f'[validation_recipe_rating - INFO]: Starting.')
  try:
    if request.method == 'POST':
      debug('[validation_recipe_rating - INFO]: POST request')
      request_data = json.loads(request.data)
      debug(f'[validation_recipe_rating - DATA]: request_data: {request_data}')
  except:
    return f"[validation_recipe_rating - ERROR]: Something went wrong..."
  return ""

################################################################################
# get_meal_plan_selection [POST]
# POST: End point is for saving the user's chosen number of recipes 
# for the week and retrieving the recipes to be picked from.
# Note: This function is fairly involved and may take some time 
# (so there is a wait screen in the app).
# - Input:
#   - (json)
# - Output:
#   - (json)
@app.route('/get_meal_plan_selection', methods=['POST'])
@cross_origin()
def get_meal_plan_selection():
  debug(f'[get_meal_plan_selection - INFO]: Starting.')
  try:
    if request.method == 'POST':
      debug('[get_meal_plan_selection - INFO]: POST request')
      request_data = json.loads(request.data)
      debug(f'[get_meal_plan_selection - DATA]: request_data: {request_data}')

      return jsonify(getExampleRecipes(10))
  except:
    return f"[get_meal_plan_selection - ERROR]: Something went wrong..."
  return ""

################################################################################
# save_meal_plan [POST]
# POST: End point is for saving the user's chosen recipes.
# Note: This function is fairly involved and may take some time 
# (so there is a wait screen in the app).
# - Input:
#   - (json) {"userID": <user_id>, "picked": [<recipe_id>, …, <recipe_id>], "action_log": [(<timestamp_epoch_milliseconds>, <recipe_id>, <action>), … ]}
# - Output:
#   - (string) error
@app.route('/save_meal_plan', methods=['POST'])
@cross_origin()
def save_meal_plan():
  debug(f'[save_meal_plan - INFO]: Starting.')
  try:
    if request.method == 'POST':
      debug('[save_meal_plan - INFO]: POST request')
      request_data = json.loads(request.data)
      debug(f'[save_meal_plan - DATA]: request_data: {request_data}')
  except:
    return f"[save_meal_plan - ERROR]: Something went wrong..."
  return ""

################################################################################
# retrieve_meal_plan [POST]
# POST: End point is for retrieving all info about the user's chosen recipes.
# - Input:
#   - (json) {"userID": <user_id>}
# - Output:
#   - (json)
@app.route('/retrieve_meal_plan', methods=['POST'])
@cross_origin()
def retrieve_meal_plan():
  debug(f'[retrieve_meal_plan - INFO]: Starting.')
  try:
    if request.method == 'POST':
      debug('[retrieve_meal_plan - INFO]: POST request')
      request_data = json.loads(request.data)
      debug(f'[retrieve_meal_plan - DATA]: request_data: {request_data}')
      return jsonify(getExampleRecipes(3))
  except:
    return f"[retrieve_meal_plan - ERROR]: Something went wrong..."
  return ""

################################################################################
# review_recipe [POST]
# POST: End point is for saving the user's reviews of recipes they cooked.
# - Input:
#   - (json) {"userID": <user_id>}
# - Output:
#   - (json)
@app.route('/review_recipe', methods=['POST'])
@cross_origin()
def review_recipe():
  debug(f'[review_recipe - INFO]: Starting.')
  try:
    if request.method == 'POST':
      debug('[review_recipe - INFO]: POST request')
      request_data = json.loads(request.data)
      debug(f'[review_recipe - DATA]: request_data: {request_data}')
  except:
    return f"[review_recipe - ERROR]: Something went wrong..."
  return ""

################################################################################
# Server Activation
################################################################################
# Start the web server!
if __name__ == "__main__":
  app.run(debug=True)