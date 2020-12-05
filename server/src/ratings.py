################################################################################
# Q-Chef Server
# Authors: Q-Chef Backend Programmers
# Updated: 20200612

from func import *
from surprise_models import *
from scipy.stats import gmean

################################################################################
# Constants
################################################################################
TASTE_RECIPES_RETURNED = 10

EXPERIMENTAL_STATE_OVERRIDE = "" # Set to "experimental", "taste","surprise", or "taste+surprise" to override server, or "" to follow server behaviour

rating_types = ['taste',
                'familiarity',
                'surprise']

################################################################################
# Helper Functions
################################################################################
# getIngredientRating
# Returns a json of the recipe info needed to give to the front end.
# - Input:
#   - (dict) user_doc,
#   - (string) ingredient_id,
#   - (string) rating_type
# - Output:
#   - (float) ingredient preference,
#   - (string) error
def getIngredientRating(user_dict, ingredient_id, rating_type):
  debug(f'[getIngredientRating - {rating_type} - INFO]: Starting.')
  rating_type = rating_type.lower()

  if not (rating_type in rating_types):
    err = f'[getIngredientRating - {rating_type} - ERROR]: rating_type {rating_type} is not a known rating type.'
    debug(err)
    return None, err

  if ingredient_id == str(None):
    err = f'[getIngredientRating - {rating_type} - HELP]: Weird ID, ingredient_id = {ingredient_id}.'
    debug(err)
    return None, err

  i_id = ingredient_id
  is_id = str(g.i_data[i_id]['subcluster'])
  ic_id = str(g.i_data[i_id]['cluster'])
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
        # ingredientTasteRating = 0
        # Changed to having the algo skip this ingredient's rating.
        err = f'[getIngredientRating - {rating_type} - HELP]: No saved rating for ingredient_id = {ingredient_id}.'
        debug(err)
        return None, err

  return ingredientTasteRating, ''

################################################################################
# getRecipeRating
# Returns a json of the recipe info needed to give to the front end.
# - Input:
#   - (dict) user_dict,
#   - (string) recipe_id,
#   - (string) rating_type
# - Output:
#   - (float) recipe preference,
#   - (string) error
def getRecipeRating(user_dict, recipe_id, rating_type):
  rating_type = rating_type.lower()
  debug(f'[getRecipeRating - {rating_type} - INFO]: Starting.')

  if not (rating_type in rating_types):
    err = f'[getRecipeRating - {rating_type} - ERROR]: rating_type {rating_type} is not a known rating type.'
    debug(err)
    return None, err

  # Obtain all of the recipe ingredients
  recipe_dict = g.r_data[recipe_id]
  debug(f'[getRecipeRating - {rating_type} - DATA]: recipe_id = {recipe_id}')
  ingredient_ids = recipe_dict["ingredient_ids"]
  debug(f'[getRecipeRating - {rating_type} - DATA]: ingredient_ids = {ingredient_ids}')
  sumIngredientRatings = 0
  numIngredientRatings = 0
  for ingredient_id in ingredient_ids:
    ingredient_id = str(ingredient_id)
    ingredientRating, err = getIngredientRating(user_dict, ingredient_id, rating_type)
    if err:
      err = f'[getRecipeRating - {rating_type} - INFO]: Unable to get ingredient {ingredient_id} rating for recipe {recipe_id}. Skipping this ingredient...'
      debug(err)
      continue # Just skip this rating, and hope it doesn't matter.
    sumIngredientRatings += ingredientRating
    numIngredientRatings += 1


  if (numIngredientRatings == 0):
    err = f'[getRecipeRating - {rating_type} - WARN]: No rating available for recipe_id = {recipe_id}.'
    debug(err)
    return None, err

  return sumIngredientRatings/numIngredientRatings, ''

################################################################################
# getTasteRecipes
# Returns a constant times wanted number of recipes 
# that we think the user will enjoy.
# - Input:
#   - (dict) user_dict
# - Output:
#   - (dict) recipes and their information,
#   - (string) error
def getTasteRecipes(user_dict):
  debug(f'[getTasteRecipes - INFO]: Starting.')
  user_id = user_dict['user_id']
  numWantedRecipes = TASTE_RECIPES_RETURNED #recipes_wanted

  ## Collect list of possible recipes to pick from
  ## Noting that we won't give a user a recipe they have already tried.

  # Retrieve the user's info
  user_recipes = list(user_dict['r_taste'].keys())
  
  # Retrieve the recipe collection
  possibleRecipes = []
  recipe_ids = g.r_data.keys()
  err = f'[getTasteRecipes - HELP]: For user {user_id}, recipe {user_recipes} have already been rated.'
  debug(err)
  for recipe_id in recipe_ids:
    if recipe_id in user_recipes:
      err = f'[getTasteRecipes - INFO]: For user {user_id}, recipe {recipe_id} has already been rated, therefore continuing...'
      debug(err)
      continue
    userRecipePref, err = getRecipeRating(user_dict, recipe_id, 'taste')
    if err:
      err = f'[getTasteRecipes - ERROR]: Unable to find user {user_id} taste preference for recipe {recipe_id}, err = {err}'
      debug(err)
      continue # Just ignore this recipe then.
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
      err = f'[getTasteRecipes - WARN]: Unable to get recipe {recipe_id} information, err = {err}. Skipping...'
      debug(err)
      continue
    recipe_info[recipe_id] = recipeInfo

  return recipe_info, ''

################################################################################
# getTasteAndSurpRecipes
# Returns a constant times wanted number of recipes
# that we think the user will enjoy but find surprising.
# - Input:
#   - (dict) user_dict
# - Output:
#   - (dict) recipes and their information,
#   - (string) error
def getTasteAndSurpRecipes(user_dict):
  debug(f'[getTasteAndSurpRecipes - INFO]: Starting.')
  user_id = user_dict['user_id']
  numWantedRecipes = TASTE_RECIPES_RETURNED  # recipes_wanted

  ## Collect list of possible recipes to pick from
  ## Noting that we won't give a user a recipe they have already tried.

  # Retrieve the user's info
  user_recipes = list(user_dict['r_taste'].keys())

  # Retrieve the recipe collection
  possibleRecipes = []
  recipe_ids = g.r_data.keys()
  err = f'[getTasteAndSurpRecipes - HELP]: For user {user_id}, recipe {user_recipes} have already been rated.'
  debug(err)
  for recipe_id in recipe_ids:
    if recipe_id in user_recipes:
      err = f'[getTasteAndSurpRecipes - INFO]: For user {user_id}, recipe {recipe_id} has already been rated, therefore continuing...'
      debug(err)
      continue
    userRecipePref, err = getRecipeRating(user_dict, recipe_id, 'taste')
    if err:
      err = f'[getTasteAndSurpRecipes - ERROR]: Unable to find user {user_id} taste preference for recipe {recipe_id}, err = {err}'
      debug(err)
      continue  # Just ignore this recipe then.
    userRecipeSurp, err = surpRecipe(user_dict, recipe_id, simpleSurprise=False)
    if err:
      err = f'[getTasteAndSurpRecipes - ERROR]: Unable to find user {user_id} surprise preference for recipe {recipe_id}, err = {err}'
      debug(err)
      continue  # Just ignore this recipe then.
    #We decided on the geometric mean (sqrt(a*b)) to combine preference and surprise as it biases the rating towards the lower.
    debug(f'[getTasteAndSurpRecipes - DATA]: for user {user_id} and recipe {recipe_id} userRecipeSurp was {userRecipeSurp} and userRecipePref was {userRecipePref}')
    possibleRecipes.append((gmean([userRecipeSurp,userRecipePref]), recipe_id))

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
      err = f'[getTasteAndSurpRecipes - WARN]: Unable to get recipe {recipe_id} information, err = {err}. Skipping...'
      debug(err)
      continue
    recipe_info[recipe_id] = recipeInfo

  return recipe_info, ''

################################################################################
# getSurpRecipes
# Returns a constant times wanted number of recipes
# that we think the user will find surprising.
# - Input:
#   - (dict) user_dict
# - Output:
#   - (dict) recipes and their information,
#   - (string) error
def getSurpRecipes(user_dict):
  debug(f'[getSurpRecipes - INFO]: Starting.')
  user_id = user_dict['user_id']
  numWantedRecipes = TASTE_RECIPES_RETURNED  # recipes_wanted

  ## Collect list of possible recipes to pick from
  ## Noting that we won't give a user a recipe they have already tried.

  # Retrieve the user's info
  user_recipes = list(user_dict['r_taste'].keys())

  # Retrieve the recipe collection
  possibleRecipes = []
  recipe_ids = g.r_data.keys()
  err = f'[getSurpRecipes - HELP]: For user {user_id}, recipe {user_recipes} have already been rated.'
  debug(err)
  for recipe_id in recipe_ids:
    if recipe_id in user_recipes:
      err = f'[getSurpRecipes - INFO]: For user {user_id}, recipe {recipe_id} has already been rated, therefore continuing...'
      debug(err)
      continue
    userRecipeSurp, err = surpRecipe(user_dict, recipe_id, simpleSurprise=False)
    debug(f'[getSurpRecipes - DATA]: userRecipeSurp :{userRecipeSurp}')
    if err:
      err = f'[getSurpRecipes - ERROR]: Unable to find user {user_id} surprise preference for recipe {recipe_id}, err = {err}'
      debug(err)
      continue  # Just ignore this recipe then.
    possibleRecipes.append((userRecipeSurp, recipe_id))

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
      err = f'[getTasteAndSurpRecipes - WARN]: Unable to get recipe {recipe_id} information, err = {err}. Skipping...'
      debug(err)
      continue
    recipe_info[recipe_id] = recipeInfo

  return recipe_info, ''

################################################################################
# getRecipes
# Returns a constant times wanted number of recipes.
# - Input:
#   - (dict) user_dict,
#   - (dict) server_settings
# - Output:
#   - (dict) recipes and their information,
#   - (string) error
def getRecipes(user_dict, server_settings):
  debug(f'[getRecipes - INFO]: Starting.')

  ## Collect list of possible recipes to pick from
  ## Noting that we won't give a user a recipe they have already tried.

  ## Check current hard_code server setting override.
  if len(EXPERIMENTAL_STATE_OVERRIDE):
    if EXPERIMENTAL_STATE_OVERRIDE == 'experimental':
      expReturn = {0: getTasteRecipes, 1: getTasteAndSurpRecipes}
      try:
        user_group = int(user_dict['group'])
      except:
        return None,"No experimental group assignment found in user's record."
      return expReturn[user_group](user_dict)
    elif EXPERIMENTAL_STATE_OVERRIDE == "taste+surprise":
      return getTasteAndSurpRecipes(user_dict)
    elif EXPERIMENTAL_STATE_OVERRIDE == "taste":
      return getTasteRecipes(user_dict)
    if EXPERIMENTAL_STATE_OVERRIDE == "surprise":
      return getSurpRecipes(user_dict)


  # Retrieve the server document
  server_doc_ref, server_doc, err = retrieveDocument('server', 'settings')
  if err:
    return None, err
  server_dict = server_doc.to_dict()


  if server_dict['experimentalState']:
    debug(f'[getRecipes - REQU]: state = experimentalState')
    try:
      user_group = int(user_dict['group'])
    except:
      return None, "No experimental group assignment found in user's record."
    expReturn = {0: getTasteRecipes, 1:getTasteAndSurpRecipes}
    return expReturn[user_group](user_dict)

  if server_dict['returnTaste'] and server_dict['returnSurprise']:
    debug(f'[getRecipes - REQU]: state = tasteAndSurpState')
    return getTasteAndSurpRecipes(user_dict)

  if server_dict['returnSurprise']:
    debug(f'[getRecipes - REQU]: state = surpState')
    return getSurpRecipes(user_dict)

  # Else, default is to return just the tasty recipes.
  debug(f'[getRecipes - REQU]: state = tasteState')
  return getTasteRecipes(user_dict)


################################################################################
# updateSingleIngredientRating
# Updates the user's rating of the ingredient, ingredient subcluster and cluster.
# - Input:
#   - (dict) user_dict,
#   - (string) ingredient_id,
#   - (dict)  ratings,
#   - (array - string) rating_types
# - Output:
#   - (dict) update_dict,
#   - (string) error
def updateSingleIngredientRating(user_dict, ingredient_id, ratings, rating_types):
  debug(f'[updateSingleIngredientRating - INFO]: Starting.')

  for rating_type in rating_types:
    if not (rating_type in rating_types):
      err = f'[updateSingleIngredientRating - ERROR]: rating_type {rating_type} is not a known rating type.'
      debug(err)
      return None, err

  # Check that the ingredient is not None
  if ingredient_id == str(None):
    err = f'[updateSingleIngredientRating - HELP]: Weird ID, ingredient_id = {ingredient_id}.'
    debug(err)
    return None, err

  # Retrieve the ingredients document
  ingredients_dict = g.i_data[ingredient_id]
  # Update the ingredient rating
  for rating_type in rating_types:
    rating = ratings[rating_type]
    try:
      r = user_dict['i_'+rating_type][ingredient_id]['rating']
      n = user_dict['i_'+rating_type][ingredient_id]['n_ratings']
      r = (r*n+rating)/(n+1)
      n += 1
      user_dict['i_'+rating_type][ingredient_id] =  {'rating': r, 'n_ratings': n}
    except:
      user_dict['i_'+rating_type][ingredient_id] = {'rating': rating, 'n_ratings': 1}

    # Update the ingredient subcluster rating
    subcluster_id = str(ingredients_dict["subcluster"])
    if subcluster_id != None:
      try:
        r = user_dict['is_'+rating_type][subcluster_id]['rating']
        n = user_dict['is_'+rating_type][subcluster_id]['n_ratings']
        r = (r*n+rating)/(n+1)
        n += 1
        user_dict['is_'+rating_type][subcluster_id] = {'rating': r, 'n_ratings': n}
      except:
        user_dict['is_'+rating_type][subcluster_id] = {'rating': rating, 'n_ratings': 1}

    # Update the ingredient cluster rating
    cluster_id = str(ingredients_dict["cluster"])
    if cluster_id != None:
      try:
        r = user_dict['ic_'+rating_type][cluster_id]['rating']
        n = user_dict['ic_'+rating_type][cluster_id]['n_ratings']
        r = (r*n+rating)/(n+1)
        n += 1
        user_dict['ic_'+rating_type][cluster_id] = {'rating': r, 'n_ratings': n}
      except:
        user_dict['ic_'+rating_type][cluster_id] = {'rating': rating, 'n_ratings': 1}

  # Update the user's document by just returning to the upper level func
  return user_dict, ''

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
    ic_id = str(ic_id)
    for rating_type in rating_types:
      # -1 to remap 0 -> 2 into -1 -> 1
      rating = int(data[rating_type+'_ratings'][ic_id])-1
      try:
        r = user_dict['ic_'+rating_type][ic_id]['rating']
        n = user_dict['ic_'+rating_type][ic_id]['n_ratings']
        r = (r*n+rating)/(n+1)
        n += 1
        user_dict['ic_'+rating_type][ic_id] = {'rating': r, 'n_ratings': n}
      except:
        user_dict['ic_'+rating_type][ic_id] = {'rating': rating, 'n_ratings': 1}

  # Update the user document
  err = updateDocument('users', user_id, user_dict)
  if err:
    err = f'[updateIngredientClusterRatings - ERROR]: Unable to update user document with ratings for ingredient clusters rated, err: {err}'
    debug(err)
    return err
  return ''

################################################################################
# updateSingleRecipeRating
# Updates the user's rating of the recipe and it's ingredients.
# - Input:
#   - (dict) user_dict,
#   - (string) recipe_id
#   - (dict)  ratings,
#   - (array - string) rating_types
# - Output:
#   - (dict) update_dict,
#   - (string) error
def updateSingleRecipeRating(user_dict, recipe_id, ratings, rating_types):
  debug(f'[updateSingleRecipeRating - INFO]: Starting.')

  for rating_type in rating_types:
    if not (rating_type in rating_types):
      err = f'[updateSingleRecipeRating - ERROR]: rating_type {rating_type} is not a known rating type.'
      debug(err)
      return err

  # Check that the user has NOT already rated this recipe...
  try:
    user_dict['r_'+rating_type[0]][recipe_id]
    err = f'[updateSingleRecipeRating - HELP]: recipe {recipe_id} has already been rated. Skipping re-rating.'
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
    rating = ratings[rating_type]
    try:
      r = user_dict['r_'+rating_type][recipe_id]['rating']
      n = user_dict['r_'+rating_type][recipe_id]['n_ratings']
      r = (r*n+rating)/(n+1)
      n += 1
      user_dict['r_'+rating_type][recipe_id] =  {'rating': r, 'n_ratings': n}
    except:
      user_dict['r_'+rating_type][recipe_id] = {'rating': rating, 'n_ratings': 1}

  # Update the ingredients.
  ingredient_ids = recipe_dict["ingredient_ids"]
  for ingredient_id in ingredient_ids:
    if not ingredient_id:
      continue # skip 'None' ingredient id
    ingredient_id = str(ingredient_id)
    user_dict, err = updateSingleIngredientRating(user_dict, ingredient_id, ratings, rating_types)
    if err:
      err = f'[updateSingleRecipeRating - WARN]: Unable to update ingredient {ingredient_id} ratings for recipe {recipe_id}, err: {err}. Skipping...'
      debug(err)
      continue

  # Update the user's document by just returning to the upper level func
  return user_dict, ''

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

  # Retrieve the user document
  user_dict = user_doc.to_dict()
  recipe_ids = data[rating_types[0]+'_ratings']
  err = f'[updateRecipeRatings - INFO]: For user {user_id}, saving  {recipe_ids} ratings.'
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
    user_dict, err = updateSingleRecipeRating(user_dict, recipe_id, ratings, rating_types)
    if err:
      err = f'[updateRecipeRatings - WARN]: Unable to update ratings for recipe {recipe_id}, err: {err}'
      debug(err)
      continue
  # Update the user document to be the new user dictionary
  err = updateDocument('users', user_id, user_dict)
  if err:
    err = f'[updateRecipeRatings - ERROR]: Unable to update user document with ratings for recipes and ingredients, err: {err}'
    debug(err)
    return err
  return ''
