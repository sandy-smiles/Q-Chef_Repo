################################################################################
# Q-Chef Server
# Authors: Q-Chef Backend Programmers
# Updated: 20200612

from func import *

################################################################################
# Constants
################################################################################

################################################################################
# Familiarity Helper Functions
################################################################################
# getIngredientFamiliarityRating
# Returns a json of the recipe info needed to give to the front end.
# - Input:
#   - (document) user_doc,
#   - (string) ingredient_id
# - Output:
#   - (float) ingredient preference,
#   - (string) error
def getIngredientFamiliarityRating(user_doc, ingredient_id):
  debug(f'[getIngredientFamiliarityRating - INFO]: Starting.')
  user_dict = user_doc.to_dict()

  try:
    ingredientFamiliarityRating = user_dict['i_familiarity'][ingredient_id]['rating']
  except:
    try:
      ingredientFamiliarityRating = user_dict['is_familiarity'][ingredient_id]['rating']
    except:
      try:
        ingredientFamiliarityRating = user_dict['ic_familiarity'][ingredient_id]['rating']
      except:
        # TODO(kbona): Figure out how to return an ingredient rating from a closely located rated ingredient.
        # For now, finding the overall average ingredient rating.
        sumIngredientRatings = 0
        numIngredientRatings = 0
        for ingredient_rating_dict_val in user_dict['i_familiarity'].values():
          sumIngredientRatings += ingredient_rating_dict_val['rating']
          numIngredientRatings += 1
        ingredientFamiliarityRating = sumIngredientRatings/numIngredientRatings

  return ingredientFamiliarityRating, ''

################################################################################
# getRecipeFamiliarityRating
# Returns a json of the recipe info needed to give to the front end.
# - Input:
#   - (document) user_doc,
#   - (document) recipe_doc
# - Output:
#   - (float) recipe preference,
#   - (string) error
def getRecipeFamiliarityRating(user_doc, recipe_doc):
  debug(f'[getRecipeFamiliarityRating - INFO]: Starting.')
  recipe_id = recipe_doc.id
  debug(f'[getRecipeFamiliarityRating - DATA]: recipe_id = {recipe_id}.')
  debug(f'[getRecipeFamiliarityRating - DATA]: recipe_doc = {recipe_doc}.')
  # Obtain all of the recipe ingredients
  recipe_dict = recipe_doc.to_dict()
  ingredient_ids = recipe_dict["ingredient_ids"]
  sumIngredientRatings = 0
  numIngredientRatings = 0
  for ingredient_id in ingredient_ids:
    ingredient_id = str(ingredient_id)
    ingredientRating, err = getIngredientFamiliarityRating(user_doc, ingredient_id)
    if err:
      err = f'[getRecipeFamiliarityRating - ERROR]: Unable to get ingredient {ingredient_id} familiarity rating for recipe {recipe_id}.'
      debug(err)
      continue # Just skip this rating, and hope it doesn't matter.
    sumIngredientRatings += ingredientRating
    numIngredientRatings += 1

  return sumIngredientRatings/numIngredientRatings, ''

################################################################################
# updateSingleIngredientFamiliarityRating
# Updates the user's familiarity rating of the ingredient, ingredient subcluster and cluster.
# - Input:
#   - (string) user id,
#   - (string) ingredient id
#   - (float)  rating
# - Output:
#   - (string) error
def updateSingleIngredientFamiliarityRating(user_id, ingredient_id, rating):
  debug(f'[updateSingleIngredientFamiliarityRating - INFO]: Starting.')
  updating_data = {}

  # Retrieve the user document
  doc_ref, doc, err = retrieveDocument('users', user_id)
  if err:
    return err
  user_dict = doc.to_dict()

  # Retrieve the ingredients document
  doc_ref, doc, err = retrieveDocument('ingredients', ingredient_id)
  if err:
    err = '[updateSingleIngredientFamiliarityRating - ERROR]: Unable to obtain ingredient {ingredient_id} information from DB.'
    debug(err)
    return err
  ingredients_dict = doc.to_dict()

  # Update the ingredient rating
  updating_data['i_familiarity'] = user_dict['i_familiarity']
  try:
    r = user_dict['i_familiarity'][ingredient_id]['rating']
    n = user_dict['i_familiarity'][ingredient_id]['n_ratings']
    r = (r*n+rating)/(n+1)
    n += 1
    updating_data['i_familiarity'][ingredient_id] =  {'rating': r, 'n_ratings': n}
  except:
    updating_data['i_familiarity'][ingredient_id] = {'rating': rating, 'n_ratings': 1}

  # Update the ingredient subcluster rating
  subcluster_id = str(ingredients_dict["subcluster"])
  if subcluster_id != None:
    updating_data['is_familiarity'] = user_dict['is_familiarity']
    try:
      r = user_dict['is_familiarity'][subcluster_id]['rating']
      n = user_dict['is_familiarity'][subcluster_id]['n_ratings']
      r = (r*n+rating)/(n+1)
      n += 1
      updating_data['is_familiarity'][subcluster_id] = {'rating': r, 'n_ratings': n}
    except:
      updating_data['is_familiarity'][subcluster_id] = {'rating': rating, 'n_ratings': 1}

  # Update the ingredient cluster rating
  cluster_id = str(ingredients_dict["cluster"])
  if cluster_id != None:
    updating_data['ic_familiarity'] = user_dict['ic_familiarity']
    try:
      r = user_dict['ic_familiarity'][cluster_id]['rating']
      n = user_dict['ic_familiarity'][cluster_id]['n_ratings']
      r = (r*n+rating)/(n+1)
      n += 1
      updating_data['ic_familiarity'][cluster_id] = {'rating': r, 'n_ratings': n}
    except:
      updating_data['ic_familiarity'][cluster_id] = {'rating': rating, 'n_ratings': 1}

  # Update the user's document:
  err = updateDocument('users', user_id, updating_data)
  if err:
    err = f'[updateSingleIngredientFamiliarityRating - ERROR]: Unable to update user document with familiarity ratings for ingredient {ingredient_id}, err: {err}'
    debug(err)
    return err
  return ''

################################################################################
# updateIngredientFamiliarityRating
# Updates the user's familiarity rating of the given ingredients.
# Input:
#  - (dict) data containing user id, ingredient ids and ratings
# Output:
#  - (string) error
def updateIngredientFamiliarityRatings(data):
  debug(f'[updateIngredientFamiliarityRating - INFO]: Starting.')

  user_id = data['userID']
  ingredient_ids = data['familiarity_ratings']
  for ingredient_id in ingredient_ids.keys():
    rating = ingredient_ids[ingredient_id]
    err = updateSingleIngredientFamiliarityRating(user_id, ingredient_id, rating)
    if err:
      err = f'[updateIngredientFamiliarityRating - ERROR]: Unable to update familiarity ratings for ingredient {ingredient_id}, err: {err}'
      debug(err)
      return err
  return ''

################################################################################
# updateIngredientClusterFamiliarityRating
# Updates the user's familiarity rating of the given ingredient clusters.
# Input:
#  - (dict) data containing user id, ingredient cluster ids and ratings
# Output:
#  - (string) error
def updateIngredientClusterFamiliarityRatings(data):
  debug(f'[updateIngredientClusterFamiliarityRatings - INFO]: Starting.')
  updating_data = {'ic_familiarity': {}}
  user_id = data['userID']
  ic_ids = data['familiarity_ratings']
  print(ic_ids)

  # Retrieve the user document
  doc_ref, doc, err = retrieveDocument('users', user_id)
  if err:
    return err
  user_dict = doc.to_dict()

  # Update the ic_familiarity values
  updating_data['ic_familiarity'] = user_dict['ic_familiarity']
  print(updating_data)
  for ic_id in ic_ids.keys():
    print(ic_id)
    rating = ic_ids[ic_id]
    try:
      r = user_dict['ic_familiarity'][ic_id]['rating']
      n = user_dict['ic_familiarity'][ic_id]['n_ratings']
      r = (r*n+rating)/(n+1)
      n += 1
      updating_data['ic_familiarity'][ic_id] = {'rating': r, 'n_ratings': n}
    except:
      updating_data['ic_familiarity'][ic_id] = {'rating': rating, 'n_ratings': 1}
    print(updating_data)

  # Update the user document
  print(updating_data)
  err = updateDocument('users', user_id, updating_data)
  if err:
    err = f'[updateIngredientClusterFamiliarityRatings - ERROR]: Unable to update user document with familiarity ratings for ingredient clusters rated, err: {err}'
    debug(err)
    return err
  return ''

################################################################################
# updateSingleRecipeFamiliarityRating
# Updates the user's familiarity rating of the recipe and it's ingredients.
# - Input:
#   - (string) user id,
#   - (string) recipe id
#   - (float)  rating
# - Output:
#   - (string) error
def updateSingleRecipeFamiliarityRating(user_id, recipe_id, rating):
  debug(f'[updateSingleRecipeFamiliarityRating - INFO]: Starting.')
  updating_data = {'r_familiarity': {}}

  # Retrieve the user document
  doc_ref, doc, err = retrieveDocument('users', user_id)
  if err:
    return err
  user_dict = doc.to_dict()

  # Retrieve the recipe document
  doc_ref, doc, err = retrieveDocument('recipes', recipe_id)
  if err:
    return err
  recipe_dict = doc.to_dict()

  # Update the recipe rating
  updating_data['r_familiarity'] = user_dict['r_familiarity']
  try:
    r = user_dict['r_familiarity'][recipe_id]['rating']
    n = user_dict['r_familiarity'][recipe_id]['n_ratings']
    r = (r*n+rating)/(n+1)
    n += 1
    updating_data['r_familiarity'][recipe_id] =  {'rating': r, 'n_ratings': n}
  except:
    updating_data['r_familiarity'][recipe_id] = {'rating': rating, 'n_ratings': 1}

  # Update the ingredients.
  ingredient_ids = recipe_dict["ingredient_ids"]
  for ingredient_id in ingredient_ids:
    ingredient_id = str(ingredient_id)
    err = updateSingleIngredientFamiliarityRating(user_id, ingredient_id, rating)
    if err:
      err = f'[updateSingleRecipeFamiliarityRating - ERROR]: Unable to update familiarity ratings for recipe {recipe_id}, err: {err}'
      debug(err)
      return err

  # Update the user's document:
  err = updateDocument('users', user_id, updating_data)
  if err:
    err = f'[updateSingleRecipeFamiliarityRating - ERROR]: Unable to update user document with familiarity ratings for recipe {recipe_id}, err: {err}'
    debug(err)
    return err
  return''

################################################################################
# updateRecipeFamiliarityRating
# Updates the user's recipe rating of the given recipes.
# Input:
#  - (dict) data containing user id, ingredient ids and ratings
# Output:
#  - (string) error
def updateRecipeFamiliarityRatings(data):
  debug(f'[updateRecipeFamiliarityRatings - INFO]: Starting.')

  user_id = data['userID']
  recipe_ids = data['familiarity_ratings']
  for recipe_id in recipe_ids.keys():
    rating = recipe_ids[recipe_id]
    err = updateSingleRecipeFamiliarityRating(user_id, recipe_id, rating)
    if err:
      err = f'[updateRecipeFamiliarityRatings - ERROR]: Unable to update familiarity ratings for recipe {recipe_id}, err: {err}'
      debug(err)
      return err
  return ''
