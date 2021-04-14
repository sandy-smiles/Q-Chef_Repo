################################################################################
# Q-Chef Server
# Authors: Q-Chef Backend Programmers
# Updated: 20200621

import time
import json
import csv
import random

import datetime

from app import app, auth_app
from flask import make_response, request, jsonify, render_template, redirect, url_for, send_file, abort
from flask_cors import CORS, cross_origin
from firebase_admin import auth

from func import *
from actions import *
from ratings import *
from reviews import *

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
  'pickedRecipes': {'latest': -1}
}

user_groups = [0, 1]

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
def index():
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
  return send_file('Participant Information Statement - App Store.pdf', attachment_filename='Participant Information Statement - App Store.pdf')

################################################################################
# Returns the participant information statement for the Q-Chef surveys
@app.route('/info_survey')
@cross_origin()
def info_survey():
  return send_file('Participant Information Statement - Survey.pdf', attachment_filename='Participant Information Statement - Survey.pdf')

################################################################################
# Before Request Functions
################################################################################
def before_request_func():
  def get_i_data():
    debug(f'[get_i_data - INFO]: Starting.')
    if 'i_data' not in g:
      data = {}
      with open('./data/qchef_ingredients.json', 'r') as f:
        data = json.load(f)
      g.i_data = data
      return g.i_data

  def get_is_data():
    debug(f'[get_is_data - INFO]: Starting.')
    if 'is_data' not in g:
      data = {}
      with open('./data/qchef_ingredient_subclusters.json', 'r') as f:
        data = json.load(f)
      g.is_data = data
      return g.is_data

  def get_ic_data():
    debug(f'[get_ic_data - INFO]: Starting.')
    if 'ic_data' not in g:
      data = {}
      with open('./data/qchef_ingredient_clusters.json', 'r') as f:
        data = json.load(f)
      g.ic_data = data
      return g.ic_data

  def get_r_data():
    debug(f'[get_r_data - INFO]: Starting.')
    if 'r_data' not in g:
      data = {}
      with open('./data/qchef_recipes.json', 'r') as f:
        data = json.load(f)
      g.r_data = data
      return g.r_data

  def get_surp_data():
    debug(f'[get_surp_data - INFO]: Starting.')
    if 'surp_data' not in g:
      data = {}
      with open('./data/qchef_recipe_surprises.csv', 'r') as f:
        reader = csv.reader(f)
        for row in reader:
          rid = row[0].split("_")[-1]
          if len(rid)<5:
            rid = "0"+rid
          data[rid] = {"surprise_100": float(row[1]), "surprise_95": float(row[2]), "surprise_90": float(row[3]), "surprise_50": float(row[4])}
      g.surp_data = data
      return g.surp_data

  def get_nov_data():
    debug(f'[get_nov_data - INFO]: Starting.')
    if 'nov_data' not in g:
      data = {}
      with open('./data/qchef_recipe_novelties.csv', 'r') as f:
        reader = csv.reader(f)
        for row in reader:
          rid = row[0].split("_")[-1]
          if len(rid)<5:
            rid = "0"+rid
          data[rid] = {"novelty_100": float(row[1]), "novelty_95": float(row[2]), "novelty_90": float(row[3]), "novelty_50": float(row[4])}
      g.nov_data = data
      return g.nov_data

  def get_neighbours_data():
    debug(f'[get_neghbours_data - INFO]: Starting.')
    if "neighbours" not in g:
      with open('./data/qchef_ingredient_cluster_neighbours.csv') as test_neighbours_file:
          neighbours_data = list(csv.DictReader(test_neighbours_file))
      g.neighbours = neighbours_data
      debug(f'[get_neghbours_data - INFO]: {g.neighbours}')

  get_i_data()
  get_is_data()
  get_ic_data()
  get_r_data()
  get_surp_data()
  get_nov_data()
  get_neighbours_data()

################################################################################
# Authentication
################################################################################
# Returns (request_data, user_id, err)
def authentication(request, server_settings):
  request_data = json.loads(request.data)
  id_token = ''
  user_id = None
  err = ''

  requ = f'[auth - REQUEST | {request.url}]: request.method = {request.method}'
  debug(requ)
  requ = f'[auth - REQUEST | {request.url}]: request.data = {request_data}'
  debug(requ)
  requ = f'[auth - REQUEST | {request.url}]: request.headers = {request.headers}'
  debug(requ)

  if request.method == 'GET':
    return request_data, user_id, err

  #request.method == 'POST':
  # Using manual override?
  try:
    if request_data['manualID']:
      user_id = request_data['userID']
      return request_data, user_id, err
  except:
    # Allow there to be no manual override of ID
    pass

  return authCookies(request_data)

################################################################################
# Returns (request_data, user_id, err)
def authCookies(request_data):
  session_cookie = ''
  user_id = None
  err = ''

  try:
    # Extract the firebase token from the HTTP header
    
    session_cookie = request.headers['Authorization'].replace('Bearer ','')
  except:
    err = f'No "session" cookie information given.'
    # else return an error
    return request_data, user_id, err

  # Verify the cookie while checking if the cookie is revoked by
  # passing check_revoked=True.
  try:
    # Validate the cookie
    decoded_cookie = auth.verify_session_cookie(session_cookie, app=auth_app, check_revoked=True)
    # Token is valid and not revoked.
    user_id = decoded_cookie['uid']
    request_data['userID'] = user_id
  except Exception as e:
    err = f'Unable to authenticate the user, err = {e}'

  # else return an error
  return request_data, user_id, err

################################################################################
# Session URLs
################################################################################
# onboarding_ingredient_rating [POST]
# POST: Returns a user's Firebase session cookie.
# - Input:
#   - (json)
# - Output:
#   - (string) error
@app.route('/session_login', methods=['POST'])
@cross_origin()
def session_login():
  debug(f'[session_login - INFO]: Starting.')
  # Get the ID token sent by the client
  id_token = request.json['idToken']
  # Set session expiration to 5 days.
  expires_in = datetime.timedelta(days=14)
  
  session_cookie = auth.create_session_cookie(id_token, app=auth_app, expires_in=expires_in)
  response = jsonify({'status': 'success', 'token': session_cookie})
  return response


################################################################################
# Extend Session
################################################################################
# onboarding_ingredient_rating [POST]
# POST: Returns a user's Firebase session cookie.
# - Input:
#   - (json)
# - Output:
#   - (string) error
@app.route('/extend_session', methods=['POST'])
@cross_origin()
def extend_session():
  debug(f'[extend_session - INFO]: Starting.')
  func_name = 'extend_session'
  # Attempt to grab server settings document
  server_settings, err = getServerSettings()
  if err:
    err = f"[{func_name} - ERROR]: Unable to retrieve settings, err = {err}."
  
    return err, 500

  request_data, user_id, err = authentication(request, server_settings)
  debug(f"[{func_name} - DATA]: request_data: {request_data}")
  if err:
    err = f"[{func_name} - ERROR]: Authentication error, err = {err}"
  
    return err, 500

  custom_token = auth.create_custom_token(user_id)
 
  response = jsonify({'status': 'success', 'customtoken': custom_token.decode("utf-8") })
  return response


################################################################################
# Server API Helper Functions
################################################################################
# Obtains the server settings document from the database.
# server_settings, err = getServerSettings()
def getServerSettings():
  func_name = "getServerSettings"
  doc_ref, doc, err = retrieveDocument('server', 'settings')
  if err:
    err = f"[{func_name} - ERROR]: Unable to retrieve server settings, err = {err}"
    debug(err)
    return None, err
  return doc.to_dict(), err

#-------------------------------------------------------------------------------
# Obtains the user's document.
# If create_flag is set, then if document is not available,
# then they are created.
# user_doc_ref, user_doc, err = getUserDocument(user_id)
def getUserDocument(user_id, server_settings, create_flag=False):
  func_name = "getUserDocument"
  user_doc_ref, user_doc, err = retrieveDocument('users', user_id, create_flag)
  if err:
    err = f"[{func_name} - WARN]: Unable to retrieve document for {user_id}, err = {err}\nCreating documents now..."
    debug(err)

    if not create_flag:
      return None, None, err
    
    user_doc_ref, user_doc, err = createUserProfile(user_id, server_settings)
  
  return user_doc_ref, user_doc, err  

   


def createUserProfile(user_id, server_settings):
  # else create_flag: # Create the new documents
    # known only 2 groups
  debug(f'begin create user profile')
  num_group_0 = server_settings['groupNum']['0']
  num_group_1 = server_settings['groupNum']['1']
  if num_group_0 == num_group_1:
    int_user_group = random.choice(user_groups)
  else:
    if num_group_0 > num_group_1:
      int_user_group = 1
    else:
      int_user_group = 0
  userStartingDoc['group'] = int_user_group
  
  err = createDocument('users', user_id, userStartingDoc)

  if err:
    err = f"[{func_name} - ERROR]: Unable to create user document for {user_id}, err = {err}"
    debug(err)
    return None, None, err
    # user document creation successful, update server settings
  server_settings['groupNum'][str(int_user_group)] += 1
  err = updateDocument('server', 'settings', server_settings)
  if err:
    err = f"[{func_name} - ERROR]: Unable to server settings document, err = {err}"
    debug(err)
    return None, None, err

  err = createDocument('actions', user_id, {})
  if err:
    err = f"[{func_name} - ERROR]: Unable to create action document for {user_id}, err = {err}"
    debug(err)
    return None, None, err
  err = createDocument('reviews', user_id, {})
  if err:
    err = f"[{func_name} - ERROR]: Unable to create review document for {user_id}, err = {err}"
    debug(err)
    return None, None, err

  user_doc_ref, user_doc, err = getUserDocument(user_id, server_settings)
  
  return user_doc_ref, user_doc, err  
 

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
def onboarding_ingredient_rating():
  func_name = "onboarding_ingredient_rating"
  debug(f"[{func_name} - INFO]: Starting.")
  if request.method == 'POST':
    debug(f"[{func_name} - INFO]: POST request")

    # Attempt to grab server settings document
    server_settings, err = getServerSettings()
    if err:
      err = f"[{func_name} - ERROR]: Unable to retrieve settings, err = {err}."
      debug(err)
      return err, 500

    request_data, user_id, err = authentication(request, server_settings)
    debug(f"[{func_name} - DATA]: request_data: {request_data}")
    if err:
      err = f"[{func_name} - ERROR]: Authentication error, err = {err}"
      debug(err)
      return err, 500
    # Run any functions that need to be done before the rest of the request
    before_request_func()

    # Attempt to grab user's document
    user_doc_ref, user_doc, err = getUserDocument(user_id, server_settings, create_flag=True)
    if err:
      err = f"[{func_name} - ERROR]: Unable to retrieve document for {user_id}, err = {err}."
      debug(err)
      return err, 500
    user_dict = user_doc.to_dict()
    user_dict['user_id'] = user_id

    # Update user's document with ingredient ratings
    rating_types = ['taste', 'familiarity']
    err = updateIngredientClusterRatings(request_data, rating_types)
    if err:
      err = f"[{func_name} - ERROR]: Unable to update ingredient ratings, err = {err}"
      debug(err)
      return err, 500

    # Return json of test recipes that a user should liked
    onboarding_recipes2, err = getRecipes(user_dict, server_settings)
    if err:
      err = f"[{func_name} - ERROR]: Unable to find any recipes for user {user_id}, err = {err}"
      debug(err)
      return err, 500
    return jsonify(onboarding_recipes2)

  debug(f"[{func_name} - INFO]: GET request")
  # Attempt to grab onboarding recipes list.
  doc_ref, doc, err = retrieveDocument('onboarding', 'ingredients')
  if err:
    err = f"[{func_name} - ERROR]: Unable to retrieve ingredients for onboarding, err = {err}"
    debug(err)
    return err, 500

  onboarding_ingredients = {}
  doc_dict = doc.to_dict()
#  for ingredient_id in doc_dict['ingredient_ids']:
#    ingredient_info, err = getIngredientInformation(ingredient_id)
#    if err:
#      err = f'[onboarding_recipe_rating - ERROR]: Unable to retrieve ingredient {ingredient_id} for onboarding, err = {err}'
#      debug(err)
#      continue
#    onboarding_ingredients[ingredient_id] = ingredient_info

  return jsonify(doc_dict)

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
  func_name = "onboarding_recipe_rating"
  debug(f"[{func_name} - INFO]: Starting.")
  if request.method == 'POST':
    debug(f"[{func_name} - INFO]: POST request")

    # Attempt to grab server settings document
    server_settings, err = getServerSettings()
    if err:
      err = f"[{func_name} - ERROR]: Unable to retrieve settings, err = {err}."
      debug(err)
      return err, 500

    request_data, user_id, err = authentication(request, server_settings)
    debug(f"[{func_name} - DATA]: request_data: {request_data}")
    if err:
      err = f"[{func_name} - ERROR]: Authentication error, err = {err}"
      debug(err)
      return err, 500
    # Run any functions that need to be done before the rest of the request
    before_request_func()
 
    # Attempt to grab user's document
    user_doc_ref, user_doc, err = getUserDocument(user_id, server_settings, create_flag=True)
    if err:
      err = f"[{func_name} - ERROR]: Unable to retrieve document for {user_id}, err = {err}."
      debug(err)
      return err, 500

    # Update user's document with recipe ratings
    rating_types = ['taste', 'familiarity', 'surprise']
    err = updateRecipeRatings(request_data, rating_types)
    if err:
      err = f"[{func_name} - ERROR]: Unable to update recipe ratings, err = {err}"
      debug(err)
      return err, 500

    return ''

  debug(f"[{func_name} - INFO]: GET request")
  # Attempt to grab onboarding recipes list.
  doc_ref, doc, err = retrieveDocument('onboarding', 'recipes')
  if err:
    err = f"[{func_name} - ERROR]: Unable to retrieve recipes for onboarding, err = {err}"
    debug(err)
    return err, 500

  doc_dict = doc.to_dict()
  return jsonify(doc_dict)

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
  func_name = "validation_recipe_rating"
  debug(f"[{func_name} - INFO]: Starting.")
  if request.method == 'POST':
    debug(f"[{func_name} - INFO]: POST request")

    # Attempt to grab server settings document
    server_settings, err = getServerSettings()
    if err:
      err = f"[{func_name} - ERROR]: Unable to retrieve settings, err = {err}."
      debug(err)
      return err, 500

    request_data, user_id, err = authentication(request, server_settings)
    debug(f"[{func_name} - DATA]: request_data: {request_data}")
    if err:
      err = f"[{func_name} - ERROR]: Authentication error, err = {err}"
      debug(err)
      return err, 500
    # Run any functions that need to be done before the rest of the request
    before_request_func()

    # Update user's document with recipe ratings
    rating_types = ['taste', 'familiarity', 'surprise']
    err = updateRecipeRatings(request_data, rating_types)
    if err:
      err = f"[{func_name} - ERROR]: Unable to update recipe ratings, err = {err}"
      debug(err)
      return err, 500
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
  func_name = "get_meal_plan_selection"
  debug(f"[{func_name} - INFO]: Starting.")
  if request.method == 'POST':
    debug(f"[{func_name} - INFO]: POST request")

    # Attempt to grab server settings document
    server_settings, err = getServerSettings()
    if err:
      err = f"[{func_name} - ERROR]: Unable to retrieve settings, err = {err}."
      debug(err)
      return err, 500

    request_data, user_id, err = authentication(request, server_settings)
    debug(f"[{func_name} - DATA]: request_data: {request_data}")
    if err:
      err = f"[{func_name} - ERROR]: Authentication error, err = {err}"
      debug(err)
      return err, 500
    # Run any functions that need to be done before the rest of the request
    before_request_func()

    # Attempt to grab user's document
    user_doc_ref, user_doc, err = getUserDocument(user_id, server_settings)
    if err:
      err = f"[{func_name} - ERROR]: Unable to retrieve document for {user_id}, err = {err}."
      debug(err)
      return err, 500
    user_dict = user_doc.to_dict()
    user_dict['user_id'] = user_id

    #num_wanted_recipes = request_data['number_of_recipes']
    num_wanted_recipes = recipesReturned
    # Update user's document with ingredient ratings
    # Return json of test recipes that a user should liked

    # Return json of test recipes that a user should liked
    ret_recipes, err = getRecipes(user_dict, server_settings)
    if err:
      err = f"[{func_name} - ERROR]: Unable to find any recipes for user {user_id}, err = {err}"
      debug(err)
      return err, 500
    return jsonify(ret_recipes)

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
  func_name = "save_meal_plan"
  debug(f"[{func_name} - INFO]: Starting.")
  if request.method == 'POST':
    debug(f"[{func_name} - INFO]: POST request")

    # Attempt to grab server settings document
    server_settings, err = getServerSettings()
    if err:
      err = f"[{func_name} - ERROR]: Unable to retrieve settings, err = {err}."
      debug(err)
      return err, 500

    request_data, user_id, err = authentication(request, server_settings)
    debug(f"[{func_name} - DATA]: request_data: {request_data}")
    if err:
      err = f"[{func_name} - ERROR]: Authentication error, err = {err}"
      debug(err)
      return err, 500
    # Run any functions that need to be done before the rest of the request
    before_request_func()

    # Attempt to grab user's document
    user_doc_ref, user_doc, err = getUserDocument(user_id, server_settings)
    if err:
      err = f"[{func_name} - ERROR]: Unable to retrieve document for {user_id}, err = {err}."
      debug(err)
      return err, 500
    user_dict = user_doc.to_dict()
    user_dict['user_id'] = user_id

    if 'pickedRecipes' in user_dict:
      pickedRecipes = user_dict['pickedRecipes']
    else:
      pickedRecipes = {'latest':-1}
    pickedRecipes['latest'] += 1
    pickedRecipes[str(pickedRecipes['latest'])] = request_data['picked']
    updateData = {'pickedRecipes': pickedRecipes}
    err = updateDocument('users', user_id, updateData)
    if err:
      err = f"[{func_name} - ERROR]: Unable to update the data {updateData} for user {user_id}, err = {err}"
      debug(err)
      return err, 500

    err = updateActionLog(request_data)
    if err:
      err = f"[{func_name} - ERROR]: Unable to update recipe(s) action log, err = {err}"
      debug(err)
      return err, 500
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
  func_name = "retrieve_meal_plan"
  debug(f"[{func_name} - INFO]: Starting.")
  if request.method == 'POST':
    debug(f"[{func_name} - INFO]: POST request")

    # Attempt to grab server settings document
    server_settings, err = getServerSettings()
    if err:
      err = f"[{func_name} - ERROR]: Unable to retrieve settings, err = {err}."
      debug(err)
      return err, 500

    request_data, user_id, err = authentication(request, server_settings)
    debug(f"[{func_name} - DATA]: request_data: {request_data}")
    if err:
      err = f"[{func_name} - ERROR]: Authentication error, err = {err}"
      debug(err)
      return err, 500
    # Run any functions that need to be done before the rest of the request
    before_request_func()

    # Attempt to grab user's document
    user_doc_ref, user_doc, err = getUserDocument(user_id, server_settings)
    if err:
      err = f"[{func_name} - ERROR]: Unable to retrieve document for {user_id}, err = {err}."
      debug(err)
      return err, 500
    user_dict = user_doc.to_dict()
    user_dict['user_id'] = user_id

    # Grab the recipe information to be returned in the json
    pickedRecipes = user_dict['pickedRecipes']
    latest = pickedRecipes['latest']
    if latest == -1:
      err = f"[{func_name} - ERROR]: {user_id} has not selected any recipes."
      debug(err)
      return err,500
    recipe_info = {}
    recipe_ids = pickedRecipes[str(pickedRecipes['latest'])]
    for recipe_id in recipe_ids:
      # Get the recipe information
      recipeInfo, err = getRecipeInformation(recipe_id)
      if err:
        err = f"[{func_name} - ERROR]: Unable to get recipe {recipe_id} information, err = {err}"
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
  func_name = "review_recipe"
  debug(f"[{func_name} - INFO]: Starting.")
  if request.method == 'POST':
    debug(f"[{func_name} - INFO]: POST request")

    # Attempt to grab server settings document
    server_settings, err = getServerSettings()
    if err:
      err = f"[{func_name} - ERROR]: Unable to retrieve settings, err = {err}."
      debug(err)
      return err, 500

    request_data, user_id, err = authentication(request, server_settings)
    debug(f"[{func_name} - DATA]: request_data: {request_data}")
    if err:
      err = f"[{func_name} - ERROR]: Authentication error, err = {err}"
      debug(err)
      return err, 500
    # Run any functions that need to be done before the rest of the request
    before_request_func()

    # Update user's document with recipe ratings
    rating_types = ['taste', 'familiarity']
    err = updateRecipeRatings(request_data, rating_types)
    if err:
      err = f"[{func_name} - ERROR]: Unable to update recipe(s) ratings, err = {err}"
      debug(err)
      return err, 500

    err = updateRecipeReviews(request_data)
    if err:
      err = f"[{func_name} - ERROR]: Unable to update recipe(s) review, err = {err}"
      debug(err)
      return err, 500
    return ""

################################################################################
# lookup_user_predicted [POST]
# POST: End point returns the predicted ratings that the user has.
# - Input:
#   - (json) {"userID": <user_id>}
# - Output:
#   - (json)
@app.route('/lookup_user_predicted', methods=['POST'])
@cross_origin()
def lookup_user_predicted():
  func_name = "lookup_user_predicted"
  debug(f"[{func_name} - INFO]: Starting.")
  if request.method == 'POST':
    debug(f"[{func_name} - INFO]: POST request")

    # Attempt to grab server settings document
    server_settings, err = getServerSettings()
    if err:
      err = f"[{func_name} - ERROR]: Unable to retrieve settings, err = {err}."
      debug(err)
      return err, 500

    request_data, user_id, err = authentication(request, server_settings)
    debug(f"[{func_name} - DATA]: request_data: {request_data}")
    if err:
      err = f"[{func_name} - ERROR]: Authentication error, err = {err}"
      debug(err)
      return err, 500
    # Run any functions that need to be done before the rest of the request
    before_request_func()

    # Attempt to grab user's document
    user_doc_ref, user_doc, err = getUserDocument(user_id, server_settings)
    if err:
      err = f"[{func_name} - ERROR]: Unable to retrieve document for {user_id}, err = {err}."
      debug(err)
      return err, 500
    user_dict = user_doc.to_dict()

    user_ratings = {}

    # Obtain a list of all rate recipes
    # keys of all recipe taste ratings
    r_ids = request_data['recipe_ids']
    for r_id in r_ids:
      # Change into a string (just in case)
      r_id = str(r_id)
      # Find the ratings
      user_recipe_ratings = {}
      user_recipe_ratings['recipe'] = {
        'familiarity': getRecipeRating(user_dict, r_id, 'familiarity'),
        'surprise': surpRecipe(user_dict, r_id, simpleSurprise=False),
        'taste': getRecipeRating(user_dict, r_id, 'taste'),
      }

      debug(f'[lookup_user_predicted - DATA]: user_recipe_ratings[{r_id}]: {user_recipe_ratings}')

      # Find the ingredients and the user's ratings of them
      user_ingredient_ratings = {}
      i_ids = g.r_data[r_id]["ingredient_ids"]
      for i_id in i_ids:
        # Change into a string (just in case)
        i_id = str(i_id)
        # Find the ratings
        user_ingredient_ratings[i_id] = {
          'familiarity': getIngredientRating(user_dict, i_id, 'familiarity'),
          'surprise': getIngredientRating(user_dict, i_id, 'surprise'),
          'taste': getIngredientRating(user_dict, i_id, 'taste'),
        }

      user_recipe_ratings['ingredient'] = user_ingredient_ratings
      user_ratings[r_id] = user_recipe_ratings

    return jsonify(user_ratings)


################################################################################
# lookup_user_saved [POST]
# POST: End point returns the saved ratings that the user has.
# - Input:
#   - (json) {"userID": <user_id>}
# - Output:
#   - (json)
@app.route('/lookup_user_saved', methods=['POST'])
@cross_origin()
def lookup_user_saved():
  func_name = "lookup_user_saved"
  debug(f"[{func_name} - INFO]: Starting.")
  if request.method == 'POST':
    debug(f"[{func_name} - INFO]: POST request")

    # Attempt to grab server settings document
    server_settings, err = getServerSettings()
    if err:
      err = f"[{func_name} - ERROR]: Unable to retrieve settings, err = {err}."
      debug(err)
      return err, 500

    request_data, user_id, err = authentication(request, server_settings)
    debug(f"[{func_name} - DATA]: request_data: {request_data}")
    if err:
      err = f"[{func_name} - ERROR]: Authentication error, err = {err}"
      debug(err)
      return err, 500
    # Run any functions that need to be done before the rest of the request
    before_request_func()

    # Attempt to grab user's document
    user_doc_ref, user_doc, err = getUserDocument(user_id, server_settings)
    if err:
      err = f"[{func_name} - ERROR]: Unable to retrieve document for {user_id}, err = {err}."
      debug(err)
      return err, 500
    user_dict = user_doc.to_dict()

    return jsonify(user_dict)


