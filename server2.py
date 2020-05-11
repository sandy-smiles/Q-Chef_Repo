################################################################################
# Q-Chef Server
# Authors: Q-Chef Backend Programmers
# Updated: 20200418
################################################################################
# Imports and application creation
################################################################################
import json
import random as rand
from flask import Flask, request, jsonify, render_template

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Use the application default credentials
cred = credentials.Certificate("/home/sandy/Documents/Q-Chef/database_keys/sandy-smiles_q-chef-back-end-firebase-adminsdk-kyeic-a3564abe5f.json")
firebase_admin.initialize_app(cred, {
  'projectId': 'q-chef-back-end',
})
db = firestore.client()

# Create a web server
app = Flask(__name__)

################################################################################
# Debugging
################################################################################
DEBUG = True
WARN = True
INFO = False
DATA = False
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
# "Database"
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

##########################################
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

##########################################
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

##########################################
# checkUserData
# Work out whether the user is in the DB
# Input:
#  - (string) user's ID
# Output:
#  - (json) user's data
#  - (string) error
def checkUserData(userID, userDB):
  debug(f'[checkUserData - INFO]: Starting checkUserData.')

  if userID in userDB:
    debug(f'[checkUserData - INFO]: Found user {userID} in the userDB.')
    return userDB, ''

  # Add user to the userDB
  debug(f'[checkUserData - WARNING]: Unable to find user {userID} in the userDB.')
  debug(f'[checkUserData - INFO]: Creating section for user {userID} in the userDB.')
  userDB[userID] = {"Ingredients":{}, "Ingredient_Sub_Cluster":{}, "Ingredient_Cluster":{}, "Recipes":{}}
  return userDB, ''


##########################################
# checkData
# Work out whether the user is in the DB
# Input:
#  - (string) user's ID
# Output:
#  - (json) user's data
#  - (string) error
def checkData(icDB, iscDB, iDB, rDB):
  debug(f'[checkData - INFO]: Starting checkData.')
  data = {}

  # For each recipe that we have
  for recipeID in rDB.keys():
    debug(f'[checkData - INFO]: Checking recipe {recipeID}.')

    # Check each ingredient within the recipe
    for ID in rDB[recipeID]["ingredient_ids"]:
      # If the ingredient is not found
      ingredientID = str(ID)
      try:
        ingredient = iDB[ingredientID]
      except:
        try:
          data[recipeID]["Not_found_ingredients"].append(ingredientID)
        except:
          try:
            data[recipeID]["Not_found_ingredients"] = [ingredientID]
          except:
            data[recipeID] = {"Not_found_ingredients":[ingredientID]}
        continue

      # If the ingredient sub cluster is not found
      sub_cluster_ingredientID = str(ingredient["subcluster"])
      try:
        sub_cluster = iscDB[sub_cluster_ingredientID]
      except:
        debug(f'[checkData - HELP]: For ingredient {ingredientID}: {iDB[ingredientID]}.')
        debug(f'[checkData - HELP]: Unable to find sub cluster {sub_cluster_ingredientID}.')
        try:
          data[recipeID]["Not_found_sub_cluster_ingredients"].append(sub_cluster_ingredientID)
        except:
          try:
            data[recipeID]["Not_found_sub_cluster_ingredients"] = [sub_cluster_ingredientID]
          except:
            data[recipeID] = {"Not_found_sub_cluster_ingredients":[sub_cluster_ingredientID]}

      # If the ingredient cluster is not found
      cluster_ingredientID = str(ingredient["cluster"])
      try:
        cluster = icDB[cluster_ingredientID]
      except:
        debug(f'[checkData - HELP]: For ingredient {ingredientID}: {iDB[ingredientID]}.')
        debug(f'[checkData - HELP]: Unable to find cluster {cluster_ingredientID}.')
        try:
          data[recipeID]["Not_found_cluster_ingredients"].append(cluster_ingredientID)
        except:
          try:
            data[recipeID]["Not_found_cluster_ingredients"] = [cluster_ingredientID]
          except:
            data[recipeID] = {"Not_found_cluster_ingredients":[cluster_ingredientID]}

  return data, ''

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
# recipeFood - returns list of food items for the recipe
# Input:
#  - (string) name of recipe
# Output:
#  - ([]string) list of food items
#  - (string) error
def recipeFood(rDB, targetRecipe):
  debug(f'[recipeFood - INFO]: Starting recipeFood.')
  targetRecipe = str(targetRecipe)

  if targetRecipe in rDB:
    return rDB[targetRecipe]["ingredient_ids"], ""

  debug(f'[recipeFood - ERROR]: Unable to retrieve the ingredient list for recipe {targetRecipe}.')
  return None, f'Unable to retrieve the ingredient list for recipe {targetRecipe}' # (list) Food item(s) within the targetRecipe

##########################################
# userFoodRating - returns the calculated user's food item score
# Input:
#  - (string) user's ID
#  - (string) name of food item
# Output:
#  - (float) calculated user's preference of food item
#  - (float) number of times user has rated this food item
#  - (string) error
def userFoodRating(userID, userDB, iDB, targetFood):
  debug(f'[userFoodRating - INFO]: Starting userFoodRating for ingredient {targetFood}.')
  ingredient = str(targetFood)

  if ingredient in userDB[userID]["Ingredients"]:
    current_rating = userDB[userID]["Ingredients"][ingredient]["current_rating"]
    num_ratings = userDB[userID]["Ingredients"][ingredient]["num_ratings"]
    return current_rating, num_ratings, ""
  debug(f'[userFoodRating - WARNING]: Unable to find user ingredient rating.')
  debug(f'[userFoodRating - WARNING]: Now looking at ingredient sub cluster rating.')

  if ingredient in iDB:
    subcluster = str(iDB[ingredient]["subcluster"])
  if subcluster in userDB[userID]["Ingredient_Sub_Cluster"]:
    current_rating = userDB[userID]["Ingredient_Sub_Cluster"][subcluster]["current_rating"]
    num_ratings = userDB[userID]["Ingredient_Sub_Cluster"][subcluster]["num_ratings"]
    return current_rating, num_ratings, ""
  debug(f'[userFoodRating - WARNING]: Unable to find user ingredient sub cluster rating.')
  debug(f'[userFoodRating - WARNING]: Now looking at ingredient cluster rating.')

  if ingredient in iDB:
    cluster = str(iDB[ingredient]["cluster"])
  if cluster in userDB[userID]["Ingredient_Cluster"]:
    current_rating = userDB[userID]["Ingredient_Cluster"][cluster]["current_rating"]
    num_ratings = userDB[userID]["Ingredient_Cluster"][cluster]["num_ratings"]
    return current_rating, num_ratings, ""
  debug(f'[userFoodRating - WARNING]: Unable to find user ingredient cluster rating.')

  # TODO(kbona@): Calculate the preference from the surrounding information.
  debug(f'[userFoodRating - ERROR]: Unable to obtain any information from user ingredient ratings.')
  return None, None, "" # (float) 

##########################################
# userRecipeRating - returns the calculated user's preference score
# for a particular recipe
# Input:
#  - (string) user's ID
#  - (json) read in user database
#  - (string) name of recipe
# Output:
#  - (float) calculated preference score
#  - (string) error
def userRecipeRating(userID, userDB, icDB, iscDB, iDB, rDB, targetRecipe):
  targetRecipe = str(targetRecipe)

  sumScores = 0
  foodItems, err = recipeFood(rDB, targetRecipe)
  if err:
    return None, err

  for food in foodItems:
    rating, _, err = userFoodRating(userID, userDB, iDB, food)
    if err:
      return None, err
    if rating == None:
      rating = 2.5 # TODO(kbona@) Change to less random/magic number.

    sumScores += rating

  return sumScores/len(foodItems), ""

##########################################
# updateUserFoodRating - update the calculated user's food item score
# Input:
#  - (string) user's ID
#  - (string) name of food item
#  - (float) user's new rating of food item
# Output:
#  - (json) updated userDB
#  - (string) error
def updateUserFoodRating(userID, userDB, icDB, iscDB, iDB, targetFood, newRating):
  debug(f'[updateUserFoodRating - INFO]: Starting updateUserFoodRating.')
  ingredientID = str(targetFood)
  try:
    ingredientSubclusterID = str(iDB[ingredientID]["subcluster"])
    ingredientClusterID = str(iDB[ingredientID]["cluster"])
    newRating = float(newRating)
    debug(f'[updateUserFoodRating - DATA]: targetFood {ingredientID} has in ingredients DB: {iDB[ingredientID]}.')
  except:
    debug(f'[updateUserFoodRating - ERROR]: Unable to find ingredient {ingredientID} in the ingredients DB.')
    return userDB, f'Unable to find ingredient {ingredientID} in the ingredients DB.'

  # Update individual ingredient rating
  if not(targetFood in userDB[userID]["Ingredients"]):
    debug(f'[updateUserFoodRating - WARNING]: Unable to obtain data for food item {ingredientID}.')
    debug(f'[updateUserFoodRating - WARNING]: Creating data for food item {ingredientID} now.')
    userDB[userID]["Ingredients"][ingredientID] = {"current_rating": 0.0, "num_ratings" : 0}

  currentRating = userDB[userID]["Ingredients"][ingredientID]["current_rating"]
  numRatings = userDB[userID]["Ingredients"][ingredientID]["num_ratings"]
  currentRating = (currentRating*numRatings+newRating)/(numRatings+1)
  numRatings += 1

  userDB[userID]["Ingredients"][ingredientID]["current_rating"] = currentRating
  userDB[userID]["Ingredients"][ingredientID]["num_ratings"] = numRatings

  # Update ingredient's subcluster rating
  if not (targetFood in userDB[userID]["Ingredient_Sub_Cluster"]):
    debug(f'[updateUserFoodRating - WARNING]: Unable to obtain data for food sub cluster {ingredientSubclusterID}.')
    debug(f'[updateUserFoodRating - WARNING]: Creating data for food sub cluster {ingredientSubclusterID} now.')
    userDB[userID]["Ingredient_Sub_Cluster"][ingredientSubclusterID] = {"current_rating": 0.0, "num_ratings" : 0}

  currentRating = userDB[userID]["Ingredient_Sub_Cluster"][ingredientSubclusterID]["current_rating"]
  numRatings = userDB[userID]["Ingredient_Sub_Cluster"][ingredientSubclusterID]["num_ratings"]
  currentRating = (currentRating*numRatings+newRating)/(numRatings+1)
  numRatings += 1

  userDB[userID]["Ingredient_Sub_Cluster"][ingredientSubclusterID]["current_rating"] = currentRating
  userDB[userID]["Ingredient_Sub_Cluster"][ingredientSubclusterID]["num_ratings"] = numRatings

  # Update ingredient's cluster rating
  if not (targetFood in userDB[userID]["Ingredient_Cluster"]):
    debug(f'[updateUserFoodRating - WARNING]: Unable to obtain data for food cluster {ingredientClusterID}.')
    debug(f'[updateUserFoodRating - WARNING]: Creating data for food cluster {ingredientClusterID} now.')
    userDB[userID]["Ingredient_Cluster"][ingredientClusterID] = {"current_rating": 0.0, "num_ratings" : 0}

  currentRating = userDB[userID]["Ingredient_Cluster"][ingredientClusterID]["current_rating"]
  numRatings = userDB[userID]["Ingredient_Cluster"][ingredientClusterID]["num_ratings"]
  currentRating = (currentRating*numRatings+newRating)/(numRatings+1)
  numRatings += 1

  userDB[userID]["Ingredient_Cluster"][ingredientClusterID]["current_rating"] = currentRating
  userDB[userID]["Ingredient_Cluster"][ingredientClusterID]["num_ratings"] = numRatings

  return userDB, ""

##########################################
# updateUserRecipeRating - update the user's recipe score
# Input:
#  - (string) user's ID
#  - (string) name of food item
#  - (float) user's new rating of food item
# Output:
#  - (json) updated userDB
#  - (string) error
# Note:
#  - Also updates food items' score if possible.
def updateUserRecipeRating(userID, userDB, icDB, iscDB, iDB, rDB, targetRecipe, newRating):
  debug(f'[updateUserRecipeRating - INFO]: Starting updateUserRecipeRating.')
  newRating = float(newRating)

  # Obtain all of the food items within the recipe
  foodItems, err = recipeFood(rDB, targetRecipe)
  if err:
    debug(f'[updateUserRecipeRating - ERROR]: Unable to retrieve food items from recipe {targetRecipe}.')
    return userDB, err

  # Update all of the food items' ratings
  for food in foodItems:
    userDB, err = updateUserFoodRating(userID, userDB, icDB, iscDB, iDB, food, newRating)
    if err:
      debug(f'[updateUserRecipeRating - ERROR]: Unable to update food item {food} rating.')
      return userDB, err


  # Update the recipe's rating
  userDB[userID]["Recipes"][targetRecipe] = {"current_rating": newRating}
  return userDB, ''

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

def show_form():
  data = {'pageOutput':'', 'pageError':''}
  return render_template('index.html', data=data)

def grab_response():
  data = {'pageOutput':'Unable to find requested page.', 'pageError':''}
  err = ''
  r = ''
  try:
    pageInput = request.form.get('pageInput', '')
    pageName = request.form.get('pageName', '').split('|')
    debug(f'[Home - HELP]: pageName: {pageName}')
    debug(f'[Home - HELP]: pageInput: {pageInput}')
    if pageName[0] == '': # Home page
      r = ''
    if pageName[0] == 'taste_preference': # Taste Preference
      values = pageInput.split(',')
      for i, val in enumerate(values):
        values[i] = val.strip() # No additional spaces
      if len(values) != 1:
        err = 'Incorrect number of values given for '
        err += 'taste_preference(userID)'
      r = json.loads(taste_preference(values[0]).data)
    if pageName[0] == 'update_preference': # Update Preference
      values = pageInput.split(',')
      for i, val in enumerate(values):
        values[i] = val.strip() # No additional spaces
      if len(values) != 3:
        err = 'Incorrect number of values given for '
        err += 'update_preference(userID, recipeID, rating)'
      r = json.loads(update_preference(values[0], values[1], values[2]).data)
    if pageName[0] == 'retrieve_data': # Retrieve value from DB
      pageType = pageName[1]
      pageName = pageName[0]
      values = pageInput.split(',')
      for i, val in enumerate(values):
        values[i] = val.strip() # No additional spaces
      if len(values) != 1:
        err = 'Incorrect number of values given for '
        err += 'retrieve_data(databaseName, dataID)'
      r = json.loads(retrieve_data(pageType, values[0]).data)
    if pageName[0] == 'check_data': # Retrieve value from DB
      r = json.loads(check_data().data)
    if err:
      data['pageError'] = err
    data['pageOutput'] = json.dumps(r, sort_keys=True, indent=4)
  except:
    if err:
      data['pageError'] = err
      data['pageOutput'] = ''
    elif r:
      data['pageError'] = r
      data['pageOutput'] = ''
      
  if not r:
    data['pageOutput'] = ''
  debug(f"[Home - HELP]: r: {r}")
  debug(f"[Home - HELP]: data['pageOutput']: {data['pageOutput']}")
  debug(f"[Home - HELP]: data['pageError']: {data['pageError']}")
  return render_template('index.html', data=data)

def grab_form_response():
  data = {'pageOutput':'Unable to find requested page.', 'pageError':''}
  try:
    pageInput = request.form.get('pageInput', '')
    pageName = request.form.get('pageName', '').split('|')
    debug(f'[Home - HELP]: pageName: {pageName}')
    debug(f'[Home - HELP]: pageInput: {pageInput}')
    if pageName[0] == '': # Home page
      return show_form()
    if pageName[0] == 'taste_preference': # Taste Preference
      values = pageInput.split(',')
      for i, val in enumerate(values):
        values[i] = val.strip() # No additional spaces
      if len(values) != 1:
        err = 'Incorrect number of values given for '
        err += 'taste_preference(userID)'
      return taste_preference(values[0])
    if pageName[0] == 'update_preference': # Update Preference
      values = pageInput.split(',')
      for i, val in enumerate(values):
        values[i] = val.strip() # No additional spaces
      if len(values) != 3:
        err = 'Incorrect number of values given for '
        err += 'update_preference(userID, recipeID, rating)'
      return update_preference(values[0], values[1], values[2])
    if pageName[0] == 'retrieve_data': # Retrieve value from DB
      pageType = pageName[1]
      pageName = pageName[0]
      values = pageInput.split(',')
      for i, val in enumerate(values):
        values[i] = val.strip() # No additional spaces
      if len(values) != 1:
        err = 'Incorrect number of values given for '
        err += 'retrieve_data(databaseName, dataID)'
      return retrieve_data(pageType, values[0])
    if pageName[0] == 'check_data': # Retrieve value from DB
      return check_data()
    if err:
      data['pageError'] = err
    data['pageOutput'] = json.dumps(r, sort_keys=True, indent=4)
  except:
    if err:
      return f'page name: {pageName}, page input: {pageInput}, err: {err}'
      
  if not r:
    data['pageOutput'] = ''
  debug(f"[Home - HELP]: r: {r}")
  debug(f"[Home - HELP]: data['pageOutput']: {data['pageOutput']}")
  debug(f"[Home - HELP]: data['pageError']: {data['pageError']}")
  return render_template('index.html', data=data)

@app.route('/', methods=['GET', 'POST'])
def home():
  print('Requesting the home page')
  if request.method == 'POST':
    print('POST request')
    print(request.form)
    return grab_form_response()
  else:
    print('GET request')
    print(request)
    return show_form()


################################################################################
# Testing URLs
################################################################################

# API pref - returns json list of recipes
# TODO(kbona@): Return a list of 10 pref recipes.
@app.route('/retrieve/<database>/<dataID>', methods=['GET', 'POST'])
def retrieve_data(database, dataID):
  debug(f'[retrieve_data - INFO]: Starting retrieve_data.')

  if database == "user":
    userDB, err = openUserDB()
    if err:
      debug(f'[retrieve_data - ERROR]: Unable to open up the userDB. err = {err}')
      return f'Unable to open up the userDB. err = {err}'
    if dataID in userDB:
      return userDB[dataID]
    return f'Unable to find data for user {dataID}.'

  icDB, iscDB, iDB, rDB, err = startupDB()
  if err:
    debug(f'[retrieve_data - ERROR]: Unable to start up the server. err = {err}')
    return f'Unable to start up the server. err = {err}'

  if database == "ingredient_cluster":
    if dataID in icDB:
      return icDB[dataID]
    return f'Unable to find data for ingredient cluster {dataID}.'

  if database == "ingredient_subcluster":
    if dataID in iscDB:
      return iscDB[dataID]
    return f'Unable to find data for ingredient sub cluster {dataID}.'

  if database == "ingredients":
    if dataID in iDB:
      return iDB[dataID]
    return f'Unable to find data for ingredient {dataID}.'

  if database == "recipes":
    if dataID in rDB:
      return rDB[dataID]
    return f'Unable to find data for recipe {dataID}.'
  

  return jsonify(userPreferenced)

##########################################
# API pref - returns json list of missing data per recipe.
@app.route('/check_data', methods=['GET', 'POST'])
def check_data():
  debug(f'[check_data - INFO]: Starting check_data.')
  debug(f'[check_data - INFO]: Note, we do not check user data.')

  icDB, iscDB, iDB, rDB, err = startupDB()
  if err:
    debug(f'[check_data - ERROR]: Unable to start up the server. err = {err}')
    return f'Unable to start up the server. err = {err}'

  data, err = checkData(icDB, iscDB, iDB, rDB)
  if err:
    debug(f'[check_data - ERROR]: Unable to check all of the data. err = {err}')
    return f'Unable to check all of the data. err = {err}'

  return jsonify(data)

################################################################################
# Taste Preference URLs
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

  icDB, iscDB, iDB, rDB, err = startupDB()
  if err:
    debug(f'[taste_preference - ERROR]: Unable to start up the server. err = {err}')
    return f'Unable to start up the server. err = {err}'

  userDB, err = openUserDB()
  if err:
    debug(f'[taste_preference - ERROR]: Unable to open up the userDB. err = {err}')
    return f'Unable to open up the userDB. err = {err}'

  userDB, err = checkUserData(userID, userDB)
  if err:
    debug(f'[taste_preference - ERROR]: Unable to find the user {userID} in the userDB. err = {err}')
    return f'Unable to find the user {userID} in the userDB. err = {err}'

  #userPreferenced = {10: "Chicken Wrap", 8: "Gnocchi", 4: "Salmon Steak", 42: "Roti Canai"}
  userPreferenced = {}
  debug(f'[taste_preference - DATA]: recipes = {rDB}')
  allowedRecipes = list(rDB.keys())
  debug(f'[taste_preference - DATA]: allowedRecipes = {allowedRecipes}')
  picked = None # index not allowed.

  for i in range(10):
    while picked == None: # tolerance > choice:
      picked = rand.choice(allowedRecipes)
      recipePref, err = userRecipeRating(userID, userDB, icDB, iscDB, iDB, rDB, picked)
      if err:
        debug(f'[taste_preference - ERROR]: Unable find preference for recipe {picked}. err = {err}')
        return f'Unable find preference for recipe {picked}. err = {err}'

      allowedRecipes.remove(picked)
      userPreferenced[picked] = {"title": rDB[picked]["title"], "prefNum": recipePref}
    picked = None # TODO(kbona@): Remove once finalised while loop logic.

  return jsonify(userPreferenced)

##########################################
# API pref - returns json list of recipes
# TODO(kbona@): Return a list of 10 pref recipes.
@app.route('/update_pref/<userID>/<recipeID>/<rating>', methods=['GET', 'POST'])
def update_preference(userID, recipeID, rating):
  debug(f'[update_preference - INFO]: Starting update_preference.')
  err = checkID(userID)
  if err:
    debug(f'[update_preference - ERROR]: Unable to find user {id}.')
    return f'Unable to find user {id}. Unable to find user {id}. err = {err}'

  icDB, iscDB, iDB, rDB, err = startupDB()
  if err:
    debug(f'[update_preference - ERROR]: Unable to start up the server. err = {err}')
    return f'Unable to start up the server. err = {err}'

  userDB, err = openUserDB()
  if err:
    debug(f'[update_preference - ERROR]: Unable to open up the userDB. err = {err}')
    return f'Unable to open up the userDB. err = {err}'

  userDB, err = checkUserData(userID, userDB)
  if err:
    debug(f'[taste_preference - ERROR]: Unable to find the user {userID} in the userDB. err = {err}')
    return f'Unable to find the user {userID} in the userDB. err = {err}'

  userDB, err = updateUserRecipeRating(userID, userDB, icDB, iscDB, iDB, rDB, recipeID, rating)
  if err:
    debug(f'[update_preference - ERROR]: Unable update rating for recipe {recipeID}. err = {err}')
    return f'Unable update rating for recipe {recipeID}. err = {err}'

  err = saveUserDB(userDB)
  if err:
    debug(f'[update_preference - ERROR]: Unable to save the userDB. err = {err}')
    return f'Unable to save the userDB. err = {err}'

  return f'Updated recipe {recipeID} ({rDB[recipeID]["title"]}) with a rating of {rating}.'


################################################################################
# Server Activation
################################################################################
# Start the web server!
if __name__ == "__main__":
  app.run(debug=True)