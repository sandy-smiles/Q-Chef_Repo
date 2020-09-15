################################################################################
# Q-Chef Server
# Authors: Q-Chef Backend Programmers
# Updated: 20200612

from func import *
from surprise_models import *

################################################################################
# Constants
################################################################################
TASTE_RECIPES_RETURNED = 10

rating_types = ['taste',
                'familiarity',
                'surprise']

################################################################################
# Helper Functions
################################################################################
# getIngredientRating
# Returns a json of the recipe info needed to give to the front end.
# - Input:
#   - (document) user_doc,
#   - (string) ingredient_id,
#   - (string) rating_type
# - Output:
#   - (float) ingredient preference,
#   - (string) error
def getIngredientRating(user_doc, ingredient_id, rating_type):
  debug(f'[getIngredientRating - {rating_type} - INFO]: Starting.')
  user_dict = user_doc.to_dict()
  rating_type = rating_type.lower()

  if not (rating_type in rating_types):
    err = f'[getIngredientRating - {rating_type} - WARN]: rating_type {rating_type} is not a known rating type.'
    debug(err)
    return None, err

  if ingredient_id == str(None):
    err = f'[getIngredientRating - {rating_type} - WARN]: Weird ID, ingredient_id = {ingredient_id}.'
    debug(err)
    return None, err

  i_id = ingredient_id
  is_id, ic_id = g.i_data[i_id]['subcluster'], g.i_data[i_id]['cluster']
  try:
    ingredientTasteRating = user_dict['i_'+rating_type][i_id]['rating']
  except:
    try:
      ingredientTasteRating = user_dict['is_'+rating_type][is_id]['rating']
    except:
      try:
        ingredientTasteRating = user_dict['ic_'+rating_type][ic_id]['rating']
      except:
        # TODO(kbona): Figure out how to return an ingredient rating from a closely located rated ingredient.
        # For now, return as if there was no rating.
        ingredientTasteRating = 0

  return ingredientTasteRating, ''

################################################################################
# getRecipeRating
# Returns a json of the recipe info needed to give to the front end.
# - Input:
#   - (document) user_doc,
#   - (string) recipe_id,
#   - (string) rating_type
# - Output:
#   - (float) recipe preference,
#   - (string) error
def getRecipeRating(user_doc, recipe_id, rating_type):
  rating_type = rating_type.lower()
  debug(f'[getRecipeRating - {rating_type} - INFO]: Starting.')

  if not (rating_type in rating_types):
    err = f'[getRecipeRating - {rating_type} - ERROR]: rating_type {rating_type} is not a known rating type.'
    debug(err)
    return None, err

  # Obtain all of the recipe ingredients
  recipe_dict = g.r_data[recipe_id]
  debug(f'[getRecipeRating - {rating_type} - HELP]: recipe_id = {recipe_id}')
  ingredient_ids = recipe_dict["ingredient_ids"]
  debug(f'[getRecipeRating - {rating_type} - HELP]: ingredient_ids = {ingredient_ids}')
  sumIngredientRatings = 0
  numIngredientRatings = 0
  for ingredient_id in ingredient_ids:
    ingredient_id = str(ingredient_id)
    ingredientRating, err = getIngredientRating(user_doc, ingredient_id, rating_type)
    if err:
      err = f'[getRecipeRating - {rating_type} - WARN]: Unable to get ingredient {ingredient_id} rating for recipe {recipe_id}.'
      debug(err)
      continue # Just skip this rating, and hope it doesn't matter.
    sumIngredientRatings += ingredientRating
    numIngredientRatings += 1

  return sumIngredientRatings/numIngredientRatings, ''

################################################################################
# getTasteRecipes
# Returns a constant times wanted number of recipes 
# that we think the user will enjoy.
# - Input:
#   - (string) user_id,
#   - (int) recipes_wanted
#     - number of recipes user wants
# - Output:
#   - (dict) recipes and their information,
#   - (string) error
def getTasteRecipes(user_id, recipes_wanted):
  debug(f'[getTasteRecipes - INFO]: Starting.')
  numWantedRecipes = TASTE_RECIPES_RETURNED #recipes_wanted

  ## Collect list of possible recipes to pick from
  ## Noting that we won't give a user a recipe they have already tried.

  # Retrieve the user document
  user_doc_ref, user_doc, err = retrieveDocument('users', user_id)
  if err:
    return None, err
  user_dict = user_doc.to_dict()
  user_recipes = list(user_dict['r_taste'].keys())
  
  # Retrieve the recipe collection
  possibleRecipes = []
  recipe_ids = g.r_data.keys()
  err = f'[getTasteRecipes - WARN]: For user {user_id}, recipe {user_recipes} have already been rated.'
  debug(err)
  for recipe_id in recipe_ids:
    if recipe_id in user_recipes:
      err = f'[getTasteRecipes - WARN]: For user {user_id}, recipe {recipe_id} has already been rated, therefore continuing...'
      debug(err)
      continue
    userRecipePref, err = getRecipeRating(user_doc, recipe_id, 'taste')
    if err:
      err = f'[getTasteRecipes - ERROR]: Unable to find user {user_id} taste preference for recipe {recipe_doc.id}, err = {err}'
      debug(err)
      continue # Just ignore this recipe then.
    userRecipeSurp, err = surpRecipe(user_doc.to_dict(), g.r_data[recipe_id])
    if err:
      err = f'[getTasteRecipes - ERROR]: Unable to find user {user_id} surprise preference for recipe {recipe_id}, err = {err}'
      debug(err)
      continue # Just ignore this recipe then.
    #possibleRecipes.append((userRecipeSurp, recipe_id))
    possibleRecipes.append((userRecipePref, recipe_id))

  possibleRecipes.sort(reverse=True)
  # Check that there are enough recipes to serve up.
  numPossibleRecipes = len(possibleRecipes)
  if numPossibleRecipes > numWantedRecipes:
    possibleRecipes = possibleRecipes[:numWantedRecipes]

  # Grab the recipe information to be returned in the json
  recipe_info = {}
  for pref, recipe_id in possibleRecipes:
    # Get the recipe information
    recipeInfo, err = getRecipeInformation(recipe_id)
    if err:
      err = f'[getTasteRecipes - ERROR]: Unable to get recipe {recipe_id} information, err = {err}'
      debug(err)
      continue
    recipe_info[recipe_id] = recipeInfo

  return recipe_info, ''

################################################################################
# updateSingleIngredientRating
# Updates the user's rating of the ingredient, ingredient subcluster and cluster.
# - Input:
#   - (document) user_doc,
#   - (string) ingredient_id,
#   - (dict)  ratings,
#   - (array - string) rating_types
# - Output:
#   - (dict) update_dict,
#   - (string) error
def updateSingleIngredientRating(user_doc, ingredient_id, ratings, rating_types):
  debug(f'[updateSingleIngredientRating - INFO]: Starting.')
  updating_data = {}

  for rating_type in rating_types:
    if not (rating_type in rating_types):
      err = f'[updateSingleIngredientRating - ERROR]: rating_type {rating_type} is not a known rating type.'
      debug(err)
      return None, err

  # Retrieve the user document
  user_dict = user_doc.to_dict()

  # Retrieve the ingredients document
  ingredients_dict = g.i_data[ingredient_id]

  # Update the ingredient rating
  for rating_type in rating_types:
    rating = ratings[rating_type]
    updating_data['i_'+rating_type] = user_dict['i_'+rating_type]
    try:
      r = user_dict['i_'+rating_type][ingredient_id]['rating']
      n = user_dict['i_'+rating_type][ingredient_id]['n_ratings']
      r = (r*n+rating)/(n+1)
      n += 1
      updating_data['i_'+rating_type][ingredient_id] =  {'rating': r, 'n_ratings': n}
    except:
      updating_data['i_'+rating_type][ingredient_id] = {'rating': rating, 'n_ratings': 1}

    # Update the ingredient subcluster rating
    subcluster_id = str(ingredients_dict["subcluster"])
    if subcluster_id != None:
      updating_data['is_'+rating_type] = user_dict['is_'+rating_type]
      try:
        r = user_dict['is_'+rating_type][subcluster_id]['rating']
        n = user_dict['is_'+rating_type][subcluster_id]['n_ratings']
        r = (r*n+rating)/(n+1)
        n += 1
        updating_data['is_'+rating_type][subcluster_id] = {'rating': r, 'n_ratings': n}
      except:
        updating_data['is_'+rating_type][subcluster_id] = {'rating': rating, 'n_ratings': 1}

    # Update the ingredient cluster rating
    cluster_id = str(ingredients_dict["cluster"])
    if cluster_id != None:
      updating_data['ic_'+rating_type] = user_dict['ic_'+rating_type]
      try:
        r = user_dict['ic_'+rating_type][cluster_id]['rating']
        n = user_dict['ic_'+rating_type][cluster_id]['n_ratings']
        r = (r*n+rating)/(n+1)
        n += 1
        updating_data['ic_'+rating_type][cluster_id] = {'rating': r, 'n_ratings': n}
      except:
        updating_data['ic_'+rating_type][cluster_id] = {'rating': rating, 'n_ratings': 1}

  # Update the user's document:
  return updating_data, ''

################################################################################
# updateIngredientRating
# Updates the user's rating of the given ingredients.
# - Input:
#   - (dict) data containing user id, ingredient ids and ratings,
#   - (array - string) rating_type
# - Output:
#   - (string) error
def updateIngredientRatings(data, rating_types):
  debug(f'[updateIngredientRating - INFO]: Starting.')
  updating_data = {}
  user_id = data['userID']

  for rating_type in rating_types:
    if not (rating_type in rating_types):
      err = f'[updateIngredientRating - ERROR]: rating_type {rating_type} is not a known rating type.'
      debug(err)
      return err

  # Retrieve the user document
  user_doc_ref, user_doc, err = retrieveDocument('users', user_id)
  if err:
    return err

  ingredient_ids = data[rating_types[0]]
  for ingredient_id in ingredient_ids.keys():
    ratings = {}
    for rating_type in rating_types:
      # -1 to remap 0 -> 2 into -1 -> 1
      ratings[rating_type] = int(data[rating_type+'_ratings'][ingredient_id])-1
    update_dict, err = updateSingleIngredientRating(user_doc, ingredient_id, ratings, rating_types)
    if err:
      err = f'[updateIngredientRating - ERROR]: Unable to update ratings for ingredient {ingredient_id}, err: {err}'
      debug(err)
      return err
    updating_data.update(update_dict)

  # Update the user's document:
  err = updateDocument('users', user_id, updating_data)
  if err:
    err = f'[updateIngredientRating - ERROR]: Unable to update user document with ratings, err: {err}'
    debug(err)
    return err
  return ''

################################################################################
# updateIngredientClusterRatings
# Updates the user's rating of the given ingredient clusters.
# - Input:
#   - (dict) data containing user id, ingredient cluster ids and ratings,
#   - (array - string) rating_types
# - Output:
#   - (string) error
def updateIngredientClusterRatings(data, rating_types):
  debug(f'[updateIngredientClusterRatings - INFO]: Starting.')
  updating_data = {}
  user_id = data['userID']

  for rating_type in rating_types:
    if not (rating_type in rating_types):
      err = f'[updateIngredientClusterRatings - ERROR]: rating_type {rating_type} is not a known rating type.'
      debug(err)
      return err
    updating_data['ic_'+rating_type] = {}

  # Retrieve the user document
  doc_ref, doc, err = retrieveDocument('users', user_id)
  if err:
    return err
  user_dict = doc.to_dict()

  # Update the ic values
  ic_ids = data[rating_types[0]+'_ratings']
  for ic_id in ic_ids.keys():
    for rating_type in rating_types:
      # -1 to remap 0 -> 2 into -1 -> 1
      rating = int(data[rating_type+'_ratings'][ic_id])-1
      try:
        r = user_dict['ic_'+rating_type][ic_id]['rating']
        n = user_dict['ic_'+rating_type][ic_id]['n_ratings']
        r = (r*n+rating)/(n+1)
        n += 1
        updating_data['ic_'+rating_type][ic_id] = {'rating': r, 'n_ratings': n}
      except:
        updating_data['ic_'+rating_type][ic_id] = {'rating': rating, 'n_ratings': 1}

  # Update the user document
  err = updateDocument('users', user_id, updating_data)
  if err:
    err = f'[updateIngredientClusterRatings - ERROR]: Unable to update user document with ratings for ingredient clusters rated, err: {err}'
    debug(err)
    return err
  return ''

################################################################################
# updateSingleRecipeRating
# Updates the user's rating of the recipe and it's ingredients.
# - Input:
#   - (document) user_doc,
#   - (string) recipe_id
#   - (dict)  ratings,
#   - (array - string) rating_types
# - Output:
#   - (dict) update_dict,
#   - (string) error
def updateSingleRecipeRating(user_doc, recipe_id, ratings, rating_types):
  debug(f'[updateSingleRecipeRating - INFO]: Starting.')
  updating_data = {}

  for rating_type in rating_types:
    if not (rating_type in rating_types):
      err = f'[updateSingleRecipeRating - ERROR]: rating_type {rating_type} is not a known rating type.'
      debug(err)
      return err
    updating_data['ic_'+rating_type] = {}

  # Retrieve the user document
  user_dict = user_doc.to_dict()

  # Check that the user has NOT already rated this recipe...
  try:
    user_dict['r_'+rating_type[0]][recipe_id]
    err = f'[updateSingleRecipeRating - ERROR]: recipe {recipe_id} has already been rated.'
    debug(err)
    return err
  except:
    pass

  # Retrieve the recipe document
  try:
    recipe_dict = g.r_data[recipe_id]
  except:
    err = f'[updateSingleRecipeRating - ERROR]: recipe {recipe_id} does not seem to exist.'
    debug(err)
    return err


  # Update the recipe ratings
  for rating_type in rating_types:
    updating_data['r_'+rating_type] = user_dict['r_'+rating_type]
    err = f'[updateSingleRecipeRating - WARN]: updating_data = {updating_data}'
    debug(err)
    rating = ratings[rating_type]
    try:
      r = user_dict['r_'+rating_type][recipe_id]['rating']
      n = user_dict['r_'+rating_type][recipe_id]['n_ratings']
      r = (r*n+rating)/(n+1)
      n += 1
      updating_data['r_'+rating_type][recipe_id] =  {'rating': r, 'n_ratings': n}
    except:
      updating_data['r_'+rating_type][recipe_id] = {'rating': rating, 'n_ratings': 1}
  err = f'[updateSingleRecipeRating - WARN]: updating_data = {updating_data}'
  debug(err)

  # Update the ingredients.
  ingredient_ids = recipe_dict["ingredient_ids"]
  for ingredient_id in ingredient_ids:
    ingredient_id = str(ingredient_id)
    update_dict, err = updateSingleIngredientRating(user_doc, ingredient_id, ratings, rating_types)
    if err:
      err = f'[updateSingleRecipeRating - WARN]: Unable to update ingredient {ingredient_id} ratings for recipe {recipe_id}, err: {err}'
      debug(err)
      continue
    updating_data.update(update_dict)
  err = f'[updateSingleRecipeRating - WARN]: updating_data = {updating_data}'
  debug(err)

  # Update the user's document:
  return updating_data, ''

################################################################################
# updateRecipeRatings
# Updates the user's recipe rating of the given recipes.
# - Input:
#   - (dict) data containing user id, ingredient ids and ratings,
#   - (array - string) rating_types
# - Output:
#   - (string) error
def updateRecipeRatings(data, rating_types):
  debug(f'[updateRecipeRatings - INFO]: Starting.')
  updating_data = {}
  user_id = data['userID']

  for rating_type in rating_types:
    if not (rating_type in rating_types):
      err = f'[updateRecipeRatings - ERROR]: rating_type {rating_type} is not a known rating type.'
      debug(err)
      return err

  # Retrieve the user document
  user_doc_ref, user_doc, err = retrieveDocument('users', user_id)
  if err:
    return err

  recipe_ids = data[rating_types[0]+'_ratings']
  err = f'[updateRecipeRatings - WARN]: For user {user_id}, saving  {recipe_ids} ratings.'
  debug(err)
  for recipe_id in recipe_ids.keys():
    ratings = {}
    for rating_type in rating_types:
      # -1 to remap 0 -> 2 into -1 -> 1
      try:
        ratings[rating_type] = int(data[rating_type+'_ratings'][recipe_id])-1
      except:
        err = f'[updateRecipeRatings - WARN]: Missing {rating_type} rating for recipe {recipe_id}, err: {err}'
        debug(err)
    update_dict, err = updateSingleRecipeRating(user_doc, recipe_id, ratings, rating_types)
    if err:
      err = f'[updateRecipeRatings - WARN]: Unable to update ratings for recipe {recipe_id}, err: {err}'
      debug(err)
      continue
    err = f'[updateRecipeRatings - WARN]: update_dict = {update_dict}'
    debug(err)
    # merge 2 dictionaries' dictionaries together
    for key in update_dict.keys():
      try:
        updating_data[key].update(update_dict[key])
      except:
        err = f'[updateRecipeRatings - WARN]: key {key} not yet in updating_data'
        debug(err)
        updating_data[key] = update_dict[key]
    err = f'[updateRecipeRatings - WARN]: updating_data = {updating_data}'
    debug(err)

  # Update the user document
  err = updateDocument('users', user_id, updating_data)
  if err:
    err = f'[updateRecipeRatings - ERROR]: Unable to update user document with ratings for recipes and ingredients, err: {err}'
    debug(err)
    return err
  return ''
