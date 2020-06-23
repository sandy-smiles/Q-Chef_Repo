################################################################################
# Q-Chef Server
# Authors: Q-Chef Backend Programmers
# Updated: 20200330
################################################################################
# Imports and application creation
################################################################################
import json
import random as rand
from flask import Flask, request, jsonify

from surprise_models import rateSurprise,surpRecipe

DEBUG = True
WARN = True
INFO = False
DATA = False

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

################################################################################
# Startup
################################################################################
# startupDB
# Input:
#  - (void)
# Output:
#  - (json) ingredient_clusters
#  - (json) ingredient_sub_clusters
#  - (json) ingredients
#  - (json) recipes
#  - (string) error
def startupDB():
  try:
    debug(f'[startupDB - INFO]: Starting startupDB.')
    with open("./data/qchef_ingredient_clusters.json", "r") as f:
      ingredient_clusters = json.load(f)
      debug(f'[startupDB - DATA]: ingredient_clusters = {ingredient_clusters.keys()}')
    with open("./data/qchef_ingredient_subclusters.json", "r") as f:
      ingredient_sub_clusters = json.load(f)
      debug(f'[startupDB - DATA]: ingredient_sub_clusters = {ingredient_sub_clusters.keys()}')
    with open("./data/qchef_ingredients.json", "r") as f:
      ingredients = json.load(f)
      debug(f'[startupDB - DATA]: ingredients = {ingredients.keys()}')
    with open("./data/qchef_recipes.json", "r") as f:
      recipes = json.load(f)
      debug(f'[startupDB - DATA]: recipes = {recipes.keys()}')
    debug(f'[startupDB - INFO]: Successfully read in data.')
    return ingredient_clusters, ingredient_sub_clusters, ingredients, recipes, ''
  except:
    debug(f'[startupDB - ERROR]: Unable to read in data.')
    return None, None, None, None, f'Unable to read in data.'

# openUserDB
# Reads in the saved user data base
# Input:
#  - (void)
# Output:
#  - (json) userDB
#  - (string) error
def openUserDB():
  try:
    debug(f'[openUserDB - INFO]: Starting openUserDB.')
    # Append so that file is created if it does not already exist.
    with open("./data/qchef_users.json", "a") as f:
      debug(f'[openUserDB - INFO]: Appending to userDB to make sure the file exists.')
    with open("./data/qchef_users.json", "r") as f:
      content = f.read()
      debug(f'[openUserDB - DATA]: content = {content}')
      # Check that the file is not empty.
      if content == "":
        debug(f'[openUserDB - WARN]: userDB is empty, or was not saved earlier.')
        debug(f'[openUserDB - INFO]: Creating new userDB.')
        return {}, ''
    with open("./data/qchef_users.json", "r") as f:
      userDB = json.load(f)
      debug(f'[openUserDB - DATA]: userDB = {userDB.keys()}')
    debug(f'[openUserDB - INFO]: Successfully read in user data.')
    return userDB, ''
  except:
    debug(f'[openUserDB - ERROR]: Unable to read in user data.')
    return None, f'Unable to read in user data.'

# saveUserDB
# Reads in the saved user data base
# Input:
#  - (void)
# Output:
#  - (string) error
def saveUserDB(userDB):
  try:
    debug(f'[saveUserDB - INFO]: Starting saveUserDB.')
    with open("./data/qchef_users.json", "a") as f:
      debug(f'[saveUserDB - INFO]: Appending to userDB to make sure the file exists.')
    with open("./data/qchef_users.json", "w") as f:
      json.dump(userDB, f)
    debug(f'[saveUserDB - INFO]: Successfully saved the user data.')
    return ''
  except:
    debug(f'[saveUserDB - ERROR]: Unable to save the user data.')
    return f'Unable to save the user data.'

# checkUserData
# Work out whether the user is in the DB
# Input:
#  - (string) user's ID
# Output:
#  - (json) user's data
#  - (string) error
def checkUserData(userID):
  debug(f'[checkUserData - INFO]: Starting checkUserData.')
  # Open up the userDB
  userDB, err = openUserDB()
  if err:
    debug(f'[checkUserData - ERROR]: Unable to open the userDB.')
    return None, f'Unable to open the userDB, err: {err}'

  if userID in userDB:
    debug(f'[checkUserData - INFO]: Found user {userID} in the userDB.')
    return userDB[userID], ''

  # Add user to the userDB
  debug(f'[checkUserData - WARNING]: Unable to find user {userID} in the userDB.')
  debug(f'[checkUserData - INFO]: Creating section for user {userID} in the userDB.')
  userDB[userID] = {"Ingredients":{}, "Recipes":{}}

  # Save userDB due to newly created value
  err = saveUserDB(userDB)
  if err:
    debug(f'[checkUserData - ERROR]: Unable to save the userDB.')
    return None, f'Unable to save the userDB, err: {err}'
  return userDB[userID], ''

################################################################################
# Credential Checking
################################################################################
# TODO(kbona@): Work out credential checking.
# Input:
#  - (string) user's ID
# Output:
#  - (string) error
def checkID(userID):
  return ""

################################################################################
# Taste Preference
################################################################################
# userFoodRating - returns the calculated user's food item score
# Input:
#  - (string) user's ID
#  - (string) name of food item
# Output:
#  - (float) calculated user's preference of food item
#  - (string) error
def userFoodRating(userID, targetFood):
  # Grab the user's data
  data, err = checkUserData(userID)
  if err:
    return None, f'Unable to retrieve the user data, err: {err}'

  if targetFood in data["Ingredients"]:
    return data["Ingredients"][targetFood], ""

  # TODO(kbona@): Calculate the preference from the surrounding information.
  return 2.5, "" # (float) 

# userRecipeRating - returns the calculated user's recipe item score
# Input:
#  - (string) user's ID
#  - (string) name of recipe
# Output:
#  - (float) calculated preference score
#  - (string) error
def userRecipeRating(userID, targetRecipe):
  # Grab the user's data
  data, err = checkUserData(userID)
  if err:
    return None, f'Unable to retrieve the user data, err: {err}'

  if targetRecipe in data["Recipes"]:
    return data["Recipes"][targetRecipe], ""

  # Have not rated it before, so let's calculate it
  for 

  # TODO(kbona@): Grab from the database the user's rating of the recipe
  return 5.0, "" # (float) calculated user's preference of recipe

# recipeFood - returns list of food items for the recipe
# Input:
#  - (string) name of recipe
# Output:
#  - ([]string) list of food items
#  - (string) error
def recipeFood(targetRecipe):
  # TODO(kbona@): Grab from the database the list of ingredients in a recipe
  return ["chicken"], "" # (list) Food item(s) within the targetRecipe

# prefRecipe - returns the calculated user's preference score
# for a particular recipe
# Input:
#  - (string) user's ID
#  - (string) name of recipe
# Output:
#  - (float) calculated preference score
#  - (string) error
def prefRecipe(userID, targetRecipe):
  sumScores = 0
  foodItems, err = recipeFood(targetRecipe)
  if err:
    return 0.0, err

  for food in foodItems:
    rating, err = userFoodRating(userID, food)
    if err:
      return 0.0, err

    sumScores += rating

  return sumScores/len(foodItems), ""

# updateFoodRating - update the calculated user's food item score
# Input:
#  - (string) user's ID
#  - (string) name of food item
#  - (float) user's new rating of food item
# Output:
#  - (string) error
def updateFoodRating(userID, targetFood, newRating):
  currentRating, recipesRated, err = getFoodRating(userID, targetFood)
  if err:
    return err

  currentRating = (currentRating*recipesRated+newRating)/(recipesRated+1)
  recipesRated += 1

  # TODO(kbona@): Update database with new currentRating and recipesRated
  checkUserData(userID)
  userDB[userID]["Ingredients"][targetFood] = (currentRating, recipesRated)
  return ""

# updateRecipeRating - update the user's recipe score
# Input:
#  - (string) user's ID
#  - (string) name of food item
#  - (float) user's new rating of food item
# Output:
#  - (string) error
# Note:
#  - Also updates food items' score if possible.
def updateRecipeRating(userID, targetRecipe, newRating):
  foodItems, err = recipeFood(targetRecipe)
  if err:
    return err

  for food in foodItems:
    err = updateFoodRating(userID, food, newRating)
    if err:
      return err

  return ''

  # TODO(kbona@): Update database with new recipeRating
  # (also check that it hasn't already been rated?
  # if so, then need to save how many times it has been rated.)
  userRecipeRating, err = getRecipeRating(userID, targetRecipe)
  if err:
    return err
  userRecipeRating[targetRecipe] = newRating

  return ""

################################################################################
# API URLs
################################################################################
# API index - shows when people visit the home page
@app.route('/', methods=['GET'])
def home():
  return 'Hello!\nYou have reached the backend API for Q-Chef.'

# API about - page about contacts that might be needed?
@app.route('/about', methods=['GET'])
def about():
  return 'Q-Chef is ...'

# API save diet req - saving the user's dietary requirements
@app.route('/diet_req', methods=['GET', 'POST'])
def diet_req():
  try:
    requ = request.json
    resp = {}
    resp[user_id] = requ["user_id"]

    return jsonify(resp)
  except:
    return f'Unable to grab the request'

################################################################################
# Testing URLs
################################################################################
# API pref - returns json list of recipes
# TODO(kbona@): Return a list of 10 pref recipes.
@app.route('/pref/<userID>', methods=['GET', 'POST'])
def taste_preference(userID):
  debug(f'[taste_preference - INFO]: Starting taste_preference.')
  err = checkID(userID)
  if err:
    debug(f'[taste_preference - ERROR]: Unable to find user {id}.')
    debug(f'[taste_preference - ERROR]: Unable to return a list of preferenced recipes. err = {err}')
    return f'Unable to find user {id}. Unable to return a list of preferenced recipes. err = {err}'

  ingredient_clusters, ingredient_sub_clusters, ingredients, recipes, err = startupDB()
  if err:
    debug(f'[taste_preference - ERROR]: Unable to start up the server. err = {err}')
    return f'Unable to start up the server. err = {err}'

  

  #userPreferenced = {10: "Chicken Wrap", 8: "Gnocchi", 4: "Salmon Steak", 42: "Roti Canai"}
  userPreferenced = {}
  debug(f'[taste_preference - DATA]: recipes = {recipes}')
  allowedRecipes = list(recipes.keys())
  debug(f'[taste_preference - DATA]: allowedRecipes = {allowedRecipes}')
  picked = None # index not allowed.

  for i in range(10):
    while picked == None: # tolerance > choice:
      picked = rand.choice(allowedRecipes)
      recipePref, err = prefRecipe(userID, picked)
      if err:
        debug(f'[taste_preference - ERROR]: Unable find preference for recipe {picked}. err = {err}')
        return f'Unable find preference for recipe {picked}. err = {err}'

      allowedRecipes.remove(picked)
      userPreferenced[picked] = {"title": recipes[picked]["title"], "prefNum": recipePref}
    picked = None # TODO(kbona@): Remove once finalised while loop logic.

  return jsonify(userPreferenced)

################################################################################
# Server Activation
################################################################################
# Start the web server!
if __name__ == "__main__":
  app.run()
