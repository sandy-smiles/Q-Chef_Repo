################################################################################
# Q-Chef Server
# Authors: Q-Chef Backend Programmers
# Updated: 20200621

import time
import json

from app import app
from flask import make_response, request, jsonify, render_template, redirect, url_for

from func import *
from taste import *

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
def index():
  # Create context for template
  context = {'server_time': format_server_time(), 'authenticated': "False"}
  # Retrieve the information for recipe number: 60372
  context['recipe'] = getRecipeInformation("60372")
  template = render_template("index.html", context=context)
  response = make_response(template)
  # 'max-age' is for the browser
  # 's-maxage' is for the browser
  # response.headers['Cache-Control'] = 'public, max-age=300, s-maxage=600'
  return response

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
def onboarding_ingredient_rating():
  debug(f'[onboarding_ingredient_rating - INFO]: Starting.')
  if request.method == 'POST':
    debug('[onboarding_ingredient_rating - INFO]: POST request')
    request_data = json.loads(request.data)
    debug(f'[onboarding_ingredient_rating - DATA]: request_data: {request_data}')
    user_id =  request_data['userID']
    # Attempt to grab user's document (as this is the first endpoint)
    err = createDocument('users', user_id, userStartingDoc)
    if err:
      err = f'[onboarding_ingredient_rating - ERROR]: Unable to create document for {user_id}, err = {err}'
      debug(err)
      return err
    # Update user's document with ingredient ratings
    err = updateIngredientClusterTasteRatings(request_data)
    if err:
      err = f'[onboarding_ingredient_rating - ERROR]: Unable to update ingredient taste ratings, err = {err}'
      debug(err)
      return err
    # Update user's document with ingredient ratings
    err = updateIngredientClusterFamiliarityRatings(request_data)
    if err:
      err = f'[onboarding_ingredient_rating - ERROR]: Unable to update ingredient familiarity ratings, err = {err}'
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
def onboarding_recipe_rating():
  debug(f'[onboarding_recipe_rating - INFO]: Starting.')
  if request.method == 'POST':
    debug('[onboarding_recipe_rating - INFO]: POST request')
    request_data = json.loads(request.data)
    debug(f'[onboarding_recipe_rating - DATA]: request_data: {request_data}')
    user_id =  request_data['userID']

    # Update user's document with recipe ratings
    err = updateRecipeTasteRatings(request_data)
    if err:
      err = f'[onboarding_recipe_rating - ERROR]: Unable to update recipe taste ratings, err = {err}'
      debug(err)
      return err
    err = updateRecipeFamiliarityRatings(request_data)
    if err:
      err = f'[onboarding_recipe_rating - ERROR]: Unable to update recipe familiarity ratings, err = {err}'
      debug(err)
      return err
    # Return json of test recipes that a user should liked
    onboarding_recipes2 = getTasteRecipes(user_id, recipesReturned)
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