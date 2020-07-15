################################################################################
# Q-Chef Server
# Authors: Q-Chef Backend Programmers
# Updated: 20200621

import time
import json

from app import app, config, authentication
from flask import make_response, request, jsonify, render_template, redirect, url_for, session, send_file
from flask_cors import CORS, cross_origin

from func import *
from actions import *
from ratings import *
from reviews import *

################################################################################
# Constants
################################################################################
app.secret_key = config['app-secret_key']

from authlib.integrations.flask_client import OAuth
oauth = OAuth(app)
google_auth = oauth.register(
  name='google',
  client_id=config['client_id'],
  client_secret=config['client_secret'],
  access_token_url='https://accounts.google.com/o/oauth2/token',
  access_token_params=None,
  authorize_url='https://accounts.google.com/o/oauth2/auth',
  authorize_params=None,
  api_base_url='https://www.googleapis.com/oauth2/v1/',
  client_kwargs={'scope': 'openid email'},
)

################################################################################
# Constants
################################################################################
userStartingDoc = {
  'i_taste' : {},
  'is_taste': {},
  'ic_taste': {},
  'r_taste' : {},
  'i_familiarity' : {},
  'is_familiarity': {},
  'ic_familiarity': {},
  'r_familiarity' : {},
  'i_surprise' : {},
  'is_surprise': {},
  'ic_surprise': {},
  'r_surprise' : {},
  'pickedRecipes': []
}

recipesReturned = 10

################################################################################
# API URLs
################################################################################
# API index
# Renders the template index.html
def format_server_time():
  server_time = time.localtime()
  return time.strftime("%I:%M:%S %p", server_time)

@app.route('/')
@authentication
def index():
  # Figure out the session of a user
  user_id = dict(session).get('user_id', None)
  #print(f'session = {session}')

  # Create context for template
  context = {'server_time': format_server_time(), 'authenticated': "False"}
  # Retrieve the information for recipe number: 60372
  # context['recipe'] = getRecipeInformation("60372")
  template = render_template("index.html", context=context)
  response = make_response(template)
  # 'max-age' is for the browser
  # 's-maxage' is for the browser
  # response.headers['Cache-Control'] = 'public, max-age=300, s-maxage=600'
  return response

################################################################################
# Returns the participant information statement for the Q-Chef surveys
@app.route('/info')
@cross_origin()
def info():
  return send_file('Participant Information Statement - Survey.pdf', attachment_filename='Participant Information Statement - Survey.pdf')

################################################################################
# Auth URLs
################################################################################
# Login auth route
@app.route('/login')
def login():
  google_auth = oauth.create_client('google')
  redirect_url = url_for('authorize', _external=True)
  return google_auth.authorize_redirect(redirect_url)

# Authorized route
@app.route('/authorize')
def authorize():
  google_auth = oauth.create_client('google')
  google_token = google_auth.authorize_access_token()
  resp = google_auth.get('userinfo', token=google_token)
  user_info = resp.json()
  #print(f'user_info = {user_info}')
  # Do something with token and profile
  session['user_id'] = user_info['id']
  return redirect('/')

# Logout route
@app.route('/logout')
def logout():
  #print(f'session = {session}')
  for key in list(session.keys()):
    session.pop(key)
  return redirect('/')

################################################################################
# Server API URLs
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
@authentication
def onboarding_ingredient_rating():
  debug(f'[onboarding_ingredient_rating - INFO]: Starting.')
  if request.method == 'POST':
    debug('[onboarding_ingredient_rating - INFO]: POST request')
    request_data = json.loads(request.data)
    debug(f'[onboarding_ingredient_rating - DATA]: request_data: {request_data}')
    user_id =  request_data['userID']

    # Attempt to grab user's document (as this is the first endpoint)
    err = createDocument('users', user_id, userStartingDoc)
    err = createDocument('actions', user_id, {})
    err = createDocument('reviews', user_id, {})
    if err:
      err = f'[onboarding_ingredient_rating - ERROR]: Unable to create document for {user_id}, err = {err}'
      debug(err)
      return err

    # Update user's document with recipe ratings
    rating_types = ['taste', 'familiarity']
    err = updateIngredientClusterRatings(request_data, rating_types)
    if err:
      err = f'[onboarding_recipe_rating - ERROR]: Unable to update ingredient ratings, err = {err}'
      debug(err)
      return err
    return ''

  debug('[onboarding_ingredient_rating - INFO]: GET request')
  # Attempt to grab onboarding recipes list.
  doc_ref, doc, err = retrieveDocument('onboarding', 'ingredients')
  if err:
    err = f'[onboarding_ingredient_rating - ERROR]: Unable to retrieve ingredients for onboarding, err = {err}'
    debug(err)
    return err

  onboarding_ingredients = {}
  doc_dict = doc.to_dict()
  for ingredient_id in doc_dict['ingredient_ids']:
    ingredient_info, err = getIngredientInformation(ingredient_id)
    if err:
      err = f'[onboarding_recipe_rating - ERROR]: Unable to retrieve ingredient {ingredient_id} for onboarding, err = {err}'
      debug(err)
      continue
    onboarding_ingredients[ingredient_id] = ingredient_info

  return jsonify(onboarding_ingredients)

################################################################################
# onboarding_recipe_rating [GET|POST]
# 2nd end point used.
# GET: End point is for obtaining the recipes for the user to rate
# during on-boarding.
# - Input:
#   - n/a
# - Output:
#   - (json)
# POST: End point is for saving the user's ratings of recipes
# during on-boarding.
# - Input:
#   - (json)
# - Output:
#   - (string) error
@app.route('/onboarding_recipe_rating', methods=['GET', 'POST'])
@cross_origin()
def onboarding_recipe_rating():
  debug(f'[onboarding_recipe_rating - INFO]: Starting.')
  if request.method == 'POST':
    debug('[onboarding_recipe_rating - INFO]: POST request')
    request_data = json.loads(request.data)
    debug(f'[onboarding_recipe_rating - DATA]: request_data: {request_data}')
    user_id =  request_data['userID']

    # Update user's document with recipe ratings
    rating_types = ['taste', 'familiarity', 'surprise']
    err = updateRecipeRatings(request_data, rating_types)
    if err:
      err = f'[onboarding_recipe_rating - ERROR]: Unable to update recipe ratings, err = {err}'
      debug(err)
      return err

    # Return json of test recipes that a user should liked
    onboarding_recipes2, err = getTasteRecipes(user_id, recipesReturned)
    if err:
      err = f'[onboarding_recipe_rating - ERROR]: Unable to find any recipes for user {user_id}, err = {err}'
      debug(err)
      return err
    return jsonify(onboarding_recipes2)

  debug('[onboarding_recipe_rating - INFO]: GET request')
  # Attempt to grab onboarding recipes list.
  doc_ref, doc, err = retrieveDocument('onboarding', 'recipes')
  if err:
    err = f'[onboarding_recipe_rating - ERROR]: Unable to retrieve recipes for onboarding, err = {err}'
    debug(err)
    return err

  onboarding_recipes = {}
  doc_dict = doc.to_dict()
  for recipe_id in doc_dict['recipe_ids']:
    recipe_info, err = getRecipeInformation(recipe_id)
    if err:
      err = f'[onboarding_recipe_rating - ERROR]: Unable to retrieve recipe {recipe_id} for onboarding, err = {err}'
      debug(err)
      continue
    onboarding_recipes[recipe_id] = recipe_info
  return jsonify(onboarding_recipes)

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
  if request.method == 'POST':
    debug('[validation_recipe_rating - INFO]: POST request')
    request_data = json.loads(request.data)
    debug(f'[validation_recipe_rating - DATA]: request_data: {request_data}')
    user_id =  request_data['userID']

    # Update user's document with recipe ratings
    rating_types = ['taste', 'familiarity', 'surprise']
    err = updateRecipeRatings(request_data, rating_types)
    if err:
      err = f'[onboarding_recipe_rating - ERROR]: Unable to update recipe ratings, err = {err}'
      debug(err)
      return err
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
  if request.method == 'POST':
    debug('[get_meal_plan_selection - INFO]: POST request')
    request_data = json.loads(request.data)
    debug(f'[get_meal_plan_selection - DATA]: request_data: {request_data}')
    user_id =  request_data['userID']
    num_wanted_recipes = request_data['number_of_recipes']

    # Update user's document with ingredient ratings
    # Return json of test recipes that a user should liked
    taste_recipes, err = getTasteRecipes(user_id, num_wanted_recipes)
    if err:
      err = f'[onboarding_recipe_rating - ERROR]: Unable to find any recipes for user {user_id}, err = {err}'
      debug(err)
      return err
    taste_recipes
    return jsonify(taste_recipes)

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
  if request.method == 'POST':
    debug('[save_meal_plan - INFO]: POST request')
    request_data = json.loads(request.data)
    debug(f'[save_meal_plan - DATA]: request_data: {request_data}')
    user_id = request_data['userID']

    updateData = {'pickedRecipes': request_data['picked']}
    err = updateDocument('users', user_id, updateData)
    if err:
      err = f'[save_meal_plan - ERROR]: Unable to update the data {updateData} for user {user_id}, err = {err}'
      debug(err)
      return err

    err = updateActionLog(request_data)
    if err:
      err = f'[save_meal_plan - ERROR]: Unable to update recipe(s) action log, err = {err}'
      debug(err)
      return err
    return ''

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
  if request.method == 'POST':
    debug('[retrieve_meal_plan - INFO]: POST request')
    request_data = json.loads(request.data)
    debug(f'[retrieve_meal_plan - DATA]: request_data: {request_data}')
    user_id = request_data['userID']

    user_doc_ref, user_doc, err = retrieveDocument('users', user_id)
    if err:
      err = f'[retrieve_meal_plan - INFO]: Unable to retrieve the user {user_id} data, err = {err}'
      debug(err)
      return err

    # Grab the recipe information to be returned in the json
    recipe_info = {} 
    recipe_ids = user_doc.to_dict()['pickedRecipes']
    for recipe_id in recipe_ids:
      # Get the recipe information
      recipeInfo, err = getRecipeInformation(recipe_id)
      if err:
        err = f'[retrieve_meal_plan - ERROR]: Unable to get recipe {recipe_id} information, err = {err}'
        debug(err)
        continue
      recipe_info[recipe_id] = recipeInfo

    return jsonify(recipe_info)

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
  if request.method == 'POST':
    debug('[review_recipe - INFO]: POST request')
    request_data = json.loads(request.data)
    debug(f'[review_recipe - DATA]: request_data: {request_data}')
    user_id =  request_data['userID']

    # Update user's document with recipe ratings
    rating_types = ['taste', 'familiarity']
    err = updateRecipeRatings(request_data, rating_types)
    if err:
      err = f'[onboarding_recipe_rating - ERROR]: Unable to update recipe(s) ratings, err = {err}'
      debug(err)
      return err

    err = updateRecipeReviews(request_data)
    if err:
      err = f'[onboarding_recipe_rating - ERROR]: Unable to update recipe(s) review, err = {err}'
      debug(err)
      return err
    return ""
