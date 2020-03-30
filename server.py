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

# Create a web server
app = Flask(__name__)

DEBUG = True

def debug(fString):
  if DEBUG:
    print(fString)

################################################################################
# Startup
################################################################################
# TODO(kbona@): Work out what needs to be done to make the endpoints ready.
# Input:
#  - (void)
# Output:
#  - (string) error
def startupDB():
  try:
    with open("./data/qchef_ingredient_clusters.json", "r") as f:
      ingredient_clusters = json.load(f)
      debug(f'ingredient_clusters = {ingredient_clusters.keys()}')
    with open("./data/qchef_ingredient_subclusters.json", "r") as f:
      ingredient_sub_clusters = json.load(f)
      debug(f'ingredient_sub_clusters = {ingredient_sub_clusters.keys()}')
    with open("./data/qchef_ingredients.json", "r") as f:
      ingredients = json.load(f)
      debug(f'ingredients = {ingredients.keys()}')
    with open("./data/qchef_recipes.json", "r") as f:
      recipes = json.load(f)
      debug(f'recipes = {recipes.keys()}')
    print(f'Successfully read in data.')
    return ingredient_clusters, ingredient_sub_clusters, ingredients, recipes, ''
  except:
    return None, None, None, None, f'Unable to read in data.'

# TODO(kbona@): Work out whether the user is in the DB
# Input:
#  - (string) user's ID
# Output:
#  - (string) error
def checkUser(userID):
  if userDB[userID]:
    return ""
  userDB[userID] = {"Ingredients":{}, "Recipes":{}}
  return ""

def saveUserDB(userDB):
  try:
    with open("./data/data.json", "a") as f:
      f.write("")
    with open("./data/data.json", "w") as f:
      f.write(json.dump(userDB))
    return ""
  except:
    return f'Unable to save the userDB'

def openUserDB():
  try:
    with open("./data/data.json", "r") as f:
      return json.load(f), ""
  except:
    return None, f'Unable to save the userDB'

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
#  - (float) calculated preference score
#  - (string) error
def userFoodRating(userID, targetFood):
  # TODO(kbona@): Grab from the database the user's rating of the food item
  return 2.0, "" # (float) calculated user's preference of food item

# userRecipeRating - returns the calculated user's recipe item score
# Input:
#  - (string) user's ID
#  - (string) name of recipe
# Output:
#  - (float) calculated preference score
#  - (string) error
def userRecipeRating(userID, targetRecipe):
  # TODO(kbona@): Grab from the database the user's rating of the recipe
  return 2.5, "" # (float) calculated user's preference of recipe

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
  checkUser(userID)
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
  err = checkID(userID)
  if err:
    return f'Unable to find user {id}. Unable to return a list of preferenced recipes. err = {err}'

  _, _, _, recipes, err = startupDB()
  if err:
    print(f'Unable to start up the server. err = {err}')

  #userPreferenced = {10: "Chicken Wrap", 8: "Gnocchi", 4: "Salmon Steak", 42: "Roti Canai"}
  userPreferenced = {}
  print(f'recipes = {recipes}')
  allowedRecipes = list(recipes.keys())
  print(f'allowedRecipes = {allowedRecipes}')
  picked = None # index not allowed.

  for i in range(10):
    while picked == None: # tolerance > choice:
      picked = rand.choice(allowedRecipes)
      recipePref, err = prefRecipe(userID, picked)
      if err:
        print(f'Unable find preference for recipe {picked}. err = {err}')

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