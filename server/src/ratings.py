################################################################################
# Q-Chef Server
# Authors: Q-Chef Backend Programmers
# Updated: 20200612

from func import *
from surprise_models import *
from scipy.stats import gmean
from sklearn.preprocessing import minmax_scale
import numpy as np
import copy
from time import time
from scipy.spatial import distance

################################################################################
# Constants
################################################################################
TASTE_RECIPES_RETURNED = 10
MILLIS_PER_MONTH = 2629800000

EXPERIMENTAL_STATE_OVERRIDE = "" # Set to "experimental", "longitudinal", "taste","surprise", or "taste+surprise" to override server, or "" to follow server behaviour
COMBO_ALGO_OVERRIDE = "" # Set to "avg" or "pareto" to override server, or "" to follow server config
USE_VECTOR_ESTIMATOR = True
SIMILAR_RECIPE_PENALTY = 0.1
SERVED_RECIPE_PENALTY = 0.1
MAX_SIM_BEFORE_PENALTY = 0.8 #The penalty will be 0 for anything with a cosine similarity less than this, ranging up to SIMILARITY_RECIPE_PENALTY for recipes substantially identical to the candidate.

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
        if rating_type != "taste" or not USE_VECTOR_ESTIMATOR:
          err = f'[getIngredientRating - {rating_type} - HELP]: No saved rating for ingredient_id = {ingredient_id}.'
          debug(err)
          return None, err
        try:
          ingredientTasteRating = getIngredientRatingByNeighbour(ic_id,user_dict['ic_'+rating_type])
          debug(f'[getIngredientRating - {rating_type} - DATA]: ingredientTasteRating inferred from neighbour estimate = {ingredientTasteRating}')
        except:
          err = f'[getIngredientRating - {rating_type} - HELP]: No saved rating for ingredient_id = {ingredient_id} and neighbour estimation failed.'
          debug(err)
          return None, err
  return ingredientTasteRating, ''

################################################################################
# getIngredientRatingByNeighbour
# Uses vector-based nearest neighbours to estimate a user's rating of an unrated cluster from ratings of nearby clusters.
# - Input:
#   - (string) ID of the cluster to estimate a rating for,
#   - (dict) of ingredient id:rating, the user's ratings for all ingredient clusters,
#   - (list) of weights to use for the closest, second closest, and third closest ingredients.
# - Output:
#   - (float) estimated ingredient cluster preference,
def getIngredientRatingByNeighbour(ingredient_id, ratings, weights=[0.5, 0.3, 0.2], discount_factor = 0.75):
  debug(f'[getIngredientRatingByNeighbour - INFO]: Starting for ingredient {ingredient_id}.')
  my_neighbours = g.neighbours[int(ingredient_id)]
  debug(f'[getIngredientRatingByNeighbour - DATA]: Retrieved neghbours for ingredient {ingredient_id} of: {my_neighbours}')
  debug(f'[getIngredientRatingByNeighbour - DATA]: Provided ratings ingredient {ingredient_id} of: {ratings}')
  names = ['most_similar_id', 'second_most_similar_id', 'third_most_similar_id']

  # get neighbour ratings unless id is -1 in which case we have manually removed that neighbour from the precomputed file
  my_neighbour_ratings = [ratings[my_neighbours[n]]['rating'] if my_neighbours[n] in ratings else None for n in names]

  # convert to floats unless removed in which case return None
  my_neighbour_ratings = [float(r) if r is not None else None for r in my_neighbour_ratings]

  # fancy normalising dot product
  score = 0
  total_weight = 0
  for index, weight in enumerate(weights):
    if my_neighbour_ratings[index] is not None:
      score += weight * my_neighbour_ratings[index]
      total_weight += weight

  if total_weight == 0:
    raise ValueError('No ratings found for any neighbour ingredients')
  else:
    debug(f'[getIngredientRatingByNeighbour - INFO]: Returning {score * 1 / total_weight} for ingredient {ingredient_id}.')
    return (score * 1 / total_weight) * discount_factor  # normalize

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

    #The ratings engine isn't realising that some people hate individual ingredients a lot.  These weights adjust for that by emphasising negative ratings.
    if ingredientRating < 0:
      ingredientRating *= 2

    sumIngredientRatings += ingredientRating
    numIngredientRatings += 1


  if (numIngredientRatings == 0):
    err = f'[getRecipeRating - {rating_type} - WARN]: No rating available for recipe_id = {recipe_id}.'
    debug(err)
    return None, err

  return sumIngredientRatings/numIngredientRatings, ''

# Retrieve the recipes the user has seen, with options to ignore validation and onboarding
def getSeenRecipes(user_dict, exclude_validation=True, exclude_onboarding=True):
  exclude_list = []
  if exclude_validation and "-1" in user_dict["servedRecipes"].keys():
    exclude_list += user_dict["servedRecipes"]["-1"]
  if exclude_onboarding:
    # Retrieve the onboarding recipes
    onboarding_doc_ref, onboarding_doc, err = retrieveDocument('onboarding', 'recipes')
    if err:
      return None, err
    onboarding_dict = onboarding_doc.to_dict()
    exclude_list += onboarding_dict.keys()
  #debug(f'[getSeenRecipes - ALWAYS]: user_dict["r_taste"].keys(): {user_dict["r_taste"].keys()}')
  #debug(f'[getSeenRecipes - ALWAYS]: user_dict["pickedRecipes"]: {user_dict["pickedRecipes"]}')
  return [rid for rid in user_dict['r_taste'].keys() if not rid in exclude_list]

#Score penaliser for greedy diversity pruner
def getSimilarityPenalisedScore(candidate_vector, candidate_score, best_recipe_vectors):
  debug(f'[getSimilarityPenalisedScore - DATA]: candidate vector shape: {candidate_vector.shape}, best_recipe_vectors shapes: {[brv.shape for brv in best_recipe_vectors]}')
  sims = [1. - distance.cosine(candidate_vector, rv) for rv in best_recipe_vectors]
  max_sim = max(0,max(sims)) # If somehow all recipes are opposites, take 0 instead
  max_sim *= max_sim # Square the (now guaranteed to be positive) similarity.
  max_sim = max(max_sim-(MAX_SIM_BEFORE_PENALTY*MAX_SIM_BEFORE_PENALTY),0) #Subtract the square of the max unpenalised sim from the result and take 0 if it's negative.
  return candidate_score - (SIMILAR_RECIPE_PENALTY * max_sim)

def greedyRecipeDiversitySelection(possibleRecipes,numWantedRecipes, existing = [], fill=True):
  debug(f'[greedyRecipeDiversitySelection - ALWAYS]: Beginning. Selecting {numWantedRecipes} from among {len(possibleRecipes)}')
  try:
    debug(f'[greedyRecipeDiversitySelection - ALWAYS]: existing shapes: {[e.shape for e in existing]}')
  except:
    debug(f'[greedyRecipeDiversitySelection - ALWAYS]: existing has no shape.')
  skipped_recipe_ids = []
  next_best_index = 0
  if len(existing):
    #Then we can't guarantee that the first one is the best starting candidate
    bestRecipes = []
    bestRecipeVectors = {}
  else:
    bestRecipes = [possibleRecipes[0]]
    bestRecipeVectors = {possibleRecipes[0][1]: np.array(g.r_data[possibleRecipes[0][1]]["vector"])}
    debug(f'[greedyRecipeDiversitySelection - ALWAYS]: {next_best_index} has been selected to be kept, currently {len(bestRecipes)} in the selected list.')
    next_best_index = 1
  next_best_vector = np.array(g.r_data[possibleRecipes[next_best_index][1]]["vector"])
  next_best_penalised_score = getSimilarityPenalisedScore(next_best_vector, possibleRecipes[next_best_index][0], existing +
                                                          [bestRecipeVectors[rid] for _, rid in bestRecipes])
  candidate_index = next_best_index + 1
  while len(bestRecipes) < numWantedRecipes and next_best_index < len(possibleRecipes):  #
    if candidate_index >= len(possibleRecipes) or possibleRecipes[candidate_index][0] <= next_best_penalised_score:
      # We've hit the end of the list or we've hit the point where we can't possibly find a higher score, so we add this recipe and reset the search.
      bestRecipes.append(possibleRecipes[next_best_index])
      bestRecipeVectors[possibleRecipes[next_best_index][1]] = next_best_vector
      debug(f'[greedyRecipeDiversitySelection - ALWAYS]: {next_best_index} has been selected to be kept, currently {len(bestRecipes)} in the selected list.')
      next_best_index = next_best_index + 1
      if next_best_index < len(possibleRecipes):
        next_best_vector = np.array(g.r_data[possibleRecipes[next_best_index][1]]["vector"])
        next_best_penalised_score = getSimilarityPenalisedScore(next_best_vector, possibleRecipes[next_best_index][0], existing +
                                                                [bestRecipeVectors[rid] for _, rid in bestRecipes])

        debug(f'[greedyRecipeDiversitySelection - ALWAYS]: Current candidate is {next_best_index} with a penalised score of {next_best_penalised_score}, and it has become the best current candidate to be kept.')
        candidate_index = next_best_index + 1
    else:
      candidate_vector = np.array(g.r_data[possibleRecipes[candidate_index][1]]["vector"])
      candidate_penalised_score = getSimilarityPenalisedScore(candidate_vector, possibleRecipes[candidate_index][0], existing +
                                                              [bestRecipeVectors[rid] for _, rid in bestRecipes])
      debug(f'[greedyRecipeDiversitySelection - ALWAYS]: Current candidate is {candidate_index} with a penalised score of {candidate_penalised_score} vs the current best {next_best_penalised_score} (#{next_best_index})')
      if candidate_penalised_score > next_best_penalised_score:
        debug(f'[greedyRecipeDiversitySelection - ALWAYS]: {candidate_index} has become the best current candidate to be kept.')
        next_best_index = candidate_index
        next_best_vector = candidate_vector
        next_best_penalised_score = candidate_penalised_score
        candidate_index = next_best_index + 1
      else:
        skipped_recipe_ids.append(possibleRecipes[candidate_index][1])
        candidate_index += 1
  if len(possibleRecipes) >= numWantedRecipes:
    selected_avg = sum([r[0] for r in bestRecipes]) / float(numWantedRecipes)
    top_avg = sum([r[0] for r in possibleRecipes[:numWantedRecipes]]) / float(numWantedRecipes)
    debug(f'[greedyRecipeDiversitySelection - ALWAYS]: {len(set(skipped_recipe_ids))} skipped of {len(possibleRecipes)} total options.  Average score of selection was {selected_avg} vs average score of top {numWantedRecipes}: {top_avg}')
  else:
    debug(f'[greedyRecipeDiversitySelection - ALWAYS]: {len(set(skipped_recipe_ids))} skipped of {len(possibleRecipes)} total options.  There were fewer options than the number of wanted recipes.')
  if fill and len(bestRecipes) < numWantedRecipes:
    missing_recipes = numWantedRecipes - len(bestRecipes)
    return bestRecipes + [possibleRecipes[rid] for rid in skipped_recipe_ids[:missing_recipes]]
  else:
    return bestRecipes

################################################################################
# getTasteRecipes
# Returns a constant times wanted number of recipes 
# that we think the user will enjoy.
# - Input:
#   - (dict) user_dict
# - Output:
#   - (dict) recipes and their information,
#   - (string) error
def getTasteRecipes(user_dict, trim_surprise=0, for_validation=False):
  debug(f'[getTasteRecipes - INFO]: Starting.')
  user_id = user_dict['user_id']
  print(f'[getTasteRecipes: Serving tasty recipes for {user_id}')
  numWantedRecipes = TASTE_RECIPES_RETURNED #recipes_wanted

  ## Collect list of possible recipes to pick from
  ## Noting that we won't give a user a recipe they have already tried.


  user_recipes = getSeenRecipes(user_dict, exclude_onboarding = not for_validation)
  #if -1 in user_dict["servedRecipes"].keys(): # If they've done the validation step of the onboarding
  #  #Then the recipes they won't see are the ones that weren't part of validation but do have a taste rating
  #  user_recipes = [rid for rid in user_dict['r_taste'].keys() if not rid in user_dict["servedRecipes"][-1]]
  #else:
  #  user_recipes = list(user_dict['r_taste'].keys())

  
  # Retrieve the recipe collection and its preferences
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

  if trim_surprise > 0:
    untrimmedRecipes = copy.copy(possibleRecipes)
    userRecipeSurps, userPredictedSurpAndFam, error = surpRecipes(user_dict, [x[1] for x in possibleRecipes], simpleSurprise=False, return_raw=True)
    if error != "":
      return None, error

    userRecipeSurps = minmax_scale(userRecipeSurps)
    user_surp_thresh = np.percentile(userRecipeSurps, trim_surprise * 100.)
    debug(f'[getTasteRecipes - ALWAYS]: For user {user_id},user_surp_thresh was {user_surp_thresh}')
    untrimmed_length = len(possibleRecipes)
    possibleRecipes = [r for i,r in enumerate(possibleRecipes) if userRecipeSurps[i] <= user_surp_thresh]
    debug(f'[getTasteRecipes - ALWAYS]: {untrimmed_length - len(possibleRecipes)} out of {untrimmed_length} recipes were removed for being too high surprise.')

  # Reduce the preferences of any recipes that we've seen before.
  for k,v in enumerate(possibleRecipes):
    pref = v[0]
    rid = v[1]
    if rid in user_dict["history"].keys() and ("served" in user_dict["history"][rid].values() or user_dict["servedRecipes"]["latest"] < 1):
      # If we're in the first two meal plans and something has been onboarded or validated, it won't have been "served", hence max.
      num_times_served = max(1, list(user_dict["history"][rid].values()).count("served"))
      debug(f'[getTasteRecipes - DATA]: For user {user_id}, recipe {rid} has already been recommended, so subtracting {SERVED_RECIPE_PENALTY*num_times_served}.')
      possibleRecipes[k] = (pref - SERVED_RECIPE_PENALTY*num_times_served,rid)


  possibleRecipes.sort(reverse=True)

  if len(possibleRecipes) == 0:
    error = f'[getTasteRecipes - ERROR]: For user {user_id}, no possible recipes were found.'
    return None,error
  if SIMILAR_RECIPE_PENALTY > 0 and len(possibleRecipes) > numWantedRecipes:
    possibleRecipes = greedyRecipeDiversitySelection(possibleRecipes,numWantedRecipes)
    debug(f'[getTasteRecipes - ALWAYS]: possibleRecipes[:10] after diversity selection: {possibleRecipes[:10]}')
  else:
    debug(f'[getTasteRecipes - ALWAYS]: possibleRecipes[:10] {possibleRecipes[:10]}')
    # Check that there are enough recipes to serve up.
    if len(possibleRecipes) >= numWantedRecipes:
      possibleRecipes = possibleRecipes[:numWantedRecipes]
    elif len(untrimmedRecipes) >= numWantedRecipes: # If we don't have enough recipes post surprise-trim, include some of the higher surprise ones anyway.
      possibleRecipes = untrimmedRecipes[:numWantedRecipes]

  if trim_surprise > 0:
    updateServedRecipes(user_id, user_dict,
                      recipe_ids=[r[1] for r in possibleRecipes],
                      taste_ratings=[r[0] for r in possibleRecipes],
                      raw_surp_max_ratings=[g.r_data[r[1]]["surprises"]["100%"] for r in possibleRecipes],
                      raw_surp_95_ratings=[g.r_data[r[1]]["surprises"]["95%"] for r in possibleRecipes],
                      predicted_surp_ratings=[userPredictedSurpAndFam[r[1]][0] for r in possibleRecipes],
                      predicted_unfam_ratings=[userPredictedSurpAndFam[r[1]][1] for r in possibleRecipes])
  else:
    updateServedRecipes(user_id, user_dict,
                      recipe_ids=[r[1] for r in possibleRecipes],
                      taste_ratings=[r[0] for r in possibleRecipes],
                      raw_surp_max_ratings=[g.r_data[r[1]]["surprises"]["100%"] for r in possibleRecipes],
                      raw_surp_95_ratings=[g.r_data[r[1]]["surprises"]["95%"] for r in possibleRecipes],
                      predicted_surp_ratings=[-1] * len(possibleRecipes),
                      predicted_unfam_ratings=[-1] * len(possibleRecipes))

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
def getTasteAndSurpRecipes(user_dict, server_dict, drop_thresh = 0.33, surp_drop_thresh = -1, taste_drop_thresh = -1, taste_surp_combo_method = ""):
  if surp_drop_thresh <0:
    surp_drop_thresh = drop_thresh
  if taste_drop_thresh <0:
    taste_drop_thresh = drop_thresh
  if "history" in user_dict.keys():
    debug(f'[getTasteAndSurpRecipes - ALWAYS]: Starting.  user_dict["history"]: {user_dict["history"]}')
  else:
    debug(f'[getTasteAndSurpRecipes - ALWAYS]: Starting.  No user_dict["history"].')
  user_id = user_dict['user_id']
  print(f'[getTasteAndSurpRecipes: Serving tasty+surprising recipes for {user_id}')
  numWantedRecipes = TASTE_RECIPES_RETURNED  # recipes_wanted

  # If there's a combo algo override in the settings use that, if not use the one in the method header, if there's not one use the one in the server flags.
  if len(COMBO_ALGO_OVERRIDE):
    taste_surp_combo_method = COMBO_ALGO_OVERRIDE
  elif not len(taste_surp_combo_method):
    try:
      taste_surp_combo_method = server_dict["comboAlgo"]
    except KeyError:
      debug(f'[getTasteAndSurpRecipes - ERROR]: No "comboAlgo" flag in server config and no override provided! Defaulting to averaging.')

  ## Collect list of possible recipes to pick from
  ## Noting that we won't give a user a recipe they have already tried.

  user_recipes = getSeenRecipes(user_dict)
  #if -1 in user_dict["servedRecipes"].keys():
  #  user_recipes = [rid for rid in user_dict['r_taste'].keys() if not rid in user_dict["servedRecipes"][-1]]
  #else:
  #  user_recipes = list(user_dict['r_taste'].keys())


  # Retrieve the recipe collection
  userRecipeSurps = []
  userRecipePrefs = []
  kept_recipe_ids = []
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

    userRecipePrefs.append(userRecipePref)
    kept_recipe_ids.append(recipe_id)

    ''' # Old, serial recipe suprise code, left here in case I broke something bad.
    userRecipeSurp, err = surpRecipe(user_dict, recipe_id, simpleSurprise=False)
    if err:
      err = f'[getTasteAndSurpRecipes - ERROR]: Unable to find user {user_id} surprise preference for recipe {recipe_id}, err = {err}'
      debug(err)
      continue  # Just ignore this recipe then.
    debug(f'[getTasteAndSurpRecipes - DATA]: for user {user_id} and recipe {recipe_id} userRecipeSurp was {userRecipeSurp} and userRecipePref was {userRecipePref}')
    userRecipeSurps.append(userRecipeSurp)
    '''

  if taste_surp_combo_method == "pareto_raw":
    userRecipeSurps, userPredictedSurpAndFam, error = surpRecipes(user_dict,kept_recipe_ids, simpleSurprise=True, return_raw=True)
  else:
    userRecipeSurps, userPredictedSurpAndFam, error = surpRecipes(user_dict,kept_recipe_ids, simpleSurprise=False, return_raw=True)
  if error != "":
    return None,error

  userRecipeSurps = minmax_scale(userRecipeSurps)
  user_surp_thresh = np.percentile(userRecipeSurps,surp_drop_thresh*100.)
  userRecipePrefDict = {i:p for i,p in zip(kept_recipe_ids,userRecipePrefs)}
  userRecipePrefs = minmax_scale(userRecipePrefs)
  user_pref_thresh = np.percentile(userRecipePrefs,taste_drop_thresh*100.)

  possibleRecipesDict = {rid: (surp, pref) for surp, pref, rid in zip(userRecipeSurps, userRecipePrefs, kept_recipe_ids)
                     if surp > user_surp_thresh and pref > user_pref_thresh}


  # Reduce the preferences of any recipes that we've seen before.
  for rid,prefs in possibleRecipesDict.items():
    if rid in user_dict["history"].keys() and ("served" in user_dict["history"][rid].values() or user_dict["servedRecipes"]["latest"] < 1):
      # If we're in the first two meal plans and something has been onboarded or validated, it won't have been "served", hence max.
      num_times_served = max(1, list(user_dict["history"][rid].values()).count("served"))
      possibleRecipesDict[rid] = (prefs[0] - SERVED_RECIPE_PENALTY*num_times_served, prefs[1]  - SERVED_RECIPE_PENALTY*num_times_served)
      debug(f'[getTasteAndSurpRecipes - DATA]: For user {user_id}, recipe {rid} has already been recommended, so subtracting {SERVED_RECIPE_PENALTY*num_times_served}.')


  # Check that there are enough recipes to serve up, and if so run the sorting algorithm.
  if len(possibleRecipesDict.keys()) > numWantedRecipes:
    if taste_surp_combo_method == "avg":
      possibleRecipes = [((val[0]+val[1])/2., rid) for rid,val in possibleRecipesDict.items()]
      possibleRecipes.sort(reverse=True)
      if SIMILAR_RECIPE_PENALTY > 0 :
        possibleRecipes = greedyRecipeDiversitySelection(possibleRecipes, numWantedRecipes)
      else:
        possibleRecipes = possibleRecipes[:numWantedRecipes]
      chosenRecipeIDs = [r[1] for r in possibleRecipes]
    elif "pareto" in taste_surp_combo_method:
      chosenRecipeIDs = paretoRecipeSort(possibleRecipesDict,numWantedRecipes)
  else:
    #possibleRecipes = [(1,rid) for rid in possibleRecipesDict.keys()]
    chosenRecipeIDs = possibleRecipesDict.keys()
    debug(f"[getTasteAndSurpRecipes - WARNING]: Too few recipes available to choose from, returning: {chosenRecipeIDs}")

  debug(f"[getTasteAndSurpRecipes - DATA]: Found chosenRecipeIDs: {chosenRecipeIDs}")


  updateServedRecipes(user_id, user_dict,
                      recipe_ids=chosenRecipeIDs,
                      taste_ratings=[userRecipePrefDict[rid] for rid in chosenRecipeIDs],
                      raw_surp_max_ratings=[g.r_data[rid]["surprises"]["100%"] for rid in chosenRecipeIDs],
                      raw_surp_95_ratings=[g.r_data[rid]["surprises"]["95%"] for rid in chosenRecipeIDs],
                      predicted_surp_ratings=[userPredictedSurpAndFam[rid][0] for rid in chosenRecipeIDs],
                      predicted_unfam_ratings=[userPredictedSurpAndFam[rid][1] for rid in chosenRecipeIDs])


  # Grab the recipe information to be returned in the json
  recipe_info = {}
  for recipe_id in chosenRecipeIDs:
    # Get the recipe information
    recipeInfo, err = getRecipeInformation(recipe_id)
    if err:
      err = f'[getTasteAndSurpRecipes - WARN]: Unable to get recipe {recipe_id} information, err = {err}. Skipping...'
      debug(err)
      continue
    recipe_info[recipe_id] = recipeInfo
  debug(f"[getTasteAndSurpRecipes - DATA]: Returning recipe_info: {recipe_info}")
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
  user_id = user_dict['user_id']
  debug(f'[getSurpRecipes - ALWAYS]: Serving surprising recipes for {user_id}')

  numWantedRecipes = TASTE_RECIPES_RETURNED  # recipes_wanted

  ## Collect list of possible recipes to pick from
  ## Noting that we won't give a user a recipe they have already tried.


  user_recipes = getSeenRecipes(user_dict)
  #user_recipes = list(user_dict['r_taste'].keys())

  # Retrieve the recipe collection
  possibleRecipes = []
  predictedSurps = {}
  predictedFams = {}
  recipe_ids = g.r_data.keys()
  err = f'[getSurpRecipes - HELP]: For user {user_id}, recipe {user_recipes} have already been rated.'
  debug(err)
  for recipe_id in recipe_ids:
    if recipe_id in user_recipes:
      err = f'[getSurpRecipes - INFO]: For user {user_id}, recipe {recipe_id} has already been rated, therefore continuing...'
      debug(err)
      continue

    print(f'[getSurpRecipes - INFO]: Predicting surprise for recipe id: {recipe_id} and user {user_id}')
    userRecipeSurp, predicted_surp_and_fam, err = surpRecipe(user_dict, recipe_id, simpleSurprise=False, return_raw=True)
    print(f'[getSurpRecipes - INFO]: userRecipeSurp: {userRecipeSurp}')
    print(f'[getSurpRecipes - INFO]: predicted_surp_and_fam: {predicted_surp_and_fam}')
    if err:
      err = f'[getSurpRecipes - ERROR]: Unable to find user {user_id} surprise preference for recipe {recipe_id}, err = {err}'
      debug(err)
      continue  # Just ignore this recipe then.
    debug(f'[getSurpRecipes - DATA]: userRecipeSurp :{userRecipeSurp}')
    predictedSurps[recipe_id] = predicted_surp_and_fam[0]
    predictedFams[recipe_id] = predicted_surp_and_fam[1]
    possibleRecipes.append((userRecipeSurp, recipe_id))

  # Reduce the preferences of any recipes that we've seen before.
  for k,v in enumerate(possibleRecipes):
    surp = v[0]
    rid = v[1]
    if rid in user_dict["history"].keys() and ("served" in user_dict["history"][rid].values() or user_dict["servedRecipes"]["latest"] < 1):
      # If we're in the first two meal plans and something has been onboarded or validated, it won't have been "served", hence max.
      num_times_served = max(1, list(user_dict["history"][rid].values()).count("served"))
      debug(f'[getSurpRecipes - DATA]: For user {user_id}, recipe {rid} has already been recommended, so subtracting {SERVED_RECIPE_PENALTY*num_times_served}.')
      possibleRecipes[k] = (surp - SERVED_RECIPE_PENALTY*num_times_served, rid)

  if len(possibleRecipes) == 0:
    error = f'[getTasteRecipes - ERROR]: For user {user_id}, no possible recipes were found.'
    return None,error

  possibleRecipes.sort(reverse=True)

  if SIMILAR_RECIPE_PENALTY > 0 and len(possibleRecipes) > numWantedRecipes:
    possibleRecipes = greedyRecipeDiversitySelection(possibleRecipes,numWantedRecipes)
  else:
    # Just check that there are enough recipes to serve up, then truncate
    numPossibleRecipes = len(possibleRecipes)
    if numPossibleRecipes > numWantedRecipes:
      possibleRecipes = possibleRecipes[:numWantedRecipes]

  updateServedRecipes(user_id, user_dict,
                      recipe_ids=[r[1] for r in possibleRecipes],
                      taste_ratings=[-1]* len(possibleRecipes),
                      raw_surp_max_ratings=[g.r_data[r[1]]["surprises"]["100%"] for r in possibleRecipes],
                      raw_surp_95_ratings=[g.r_data[r[1]]["surprises"]["95%"] for r in possibleRecipes],
                      predicted_surp_ratings=[predictedSurps[r[1]] for r in possibleRecipes],
                      predicted_unfam_ratings=[predictedFams[r[1]] for r in possibleRecipes])

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


def updateServedRecipes(user_id, user_dict, recipe_ids=[],taste_ratings=[], raw_surp_max_ratings=[],raw_surp_95_ratings=[],predicted_surp_ratings=[],predicted_unfam_ratings=[]):
  servedRecipes = user_dict["servedRecipes"]
  servedRecipes["latest"] += 1
  servedRecipes[str(servedRecipes["latest"])] = {
    "time": int(time()*1000),
    "recipes": recipe_ids,
    "taste_ratings": taste_ratings,
    "raw_surp_100_ratings": raw_surp_max_ratings,
    "raw_surp_95_ratings": raw_surp_95_ratings,
    "predicted_surp_ratings": predicted_surp_ratings,
    "predicted_unfam_ratings": predicted_unfam_ratings
  }
  updateData = {"servedRecipes": servedRecipes}
  err = updateDocument('users', user_id, updateData)
  if err:
    err = f"[{func_name} - ERROR]: Unable to update the data {updateData} for user {user_id}, err = {err}"
    debug(err)
    return err, 500

################################################################################
# isParetoEfficient
# Returns indices of pareto dominant tuples. From https://stackoverflow.com/questions/32791911/fast-calculation-of-pareto-front-in-python
# - Input:
#   :param costs: An (n_points, n_costs) array
#   :param return_mask: True to return a mask
# - Output:
#    :return: An array of indices of pareto-efficient points.
#      If return_mask is True, this will be an (n_points, ) boolean array
#      Otherwise it will be a (n_efficient_points, ) integer array of indices.
def isParetoEfficient(costs, return_mask=True):
  is_efficient = np.arange(costs.shape[0])
  n_points = costs.shape[0]
  next_point_index = 0  # Next index in the is_efficient array to search for
  while next_point_index < len(costs):
    nondominated_point_mask = np.any(costs > costs[next_point_index], axis=1)
    nondominated_point_mask[next_point_index] = True
    is_efficient = is_efficient[nondominated_point_mask]  # Remove dominated points
    costs = costs[nondominated_point_mask]
    next_point_index = np.sum(nondominated_point_mask[:next_point_index]) + 1
  if return_mask:
    is_efficient_mask = np.zeros(n_points, dtype=bool)
    is_efficient_mask[is_efficient] = True
    return is_efficient_mask
  else:
    return is_efficient

################################################################################
# paretoRecipeSort
# Returns the numWanted most-dominant recipes based on the provided preferences.
# - Input:
#   - (dict) possibleRecipesDict, with recipe ID keys and ,
#   - (dict) server_settings
# - Output:
#   - (dict) recipes and their information,
#   - (string) error
def paretoRecipeSort(possibleRecipesDict,numWanted):
  dominant_ids = []
  numRecursions = 0
  while(len(dominant_ids) < numWanted):
    possibleRecipeIDs,possibleRecipeList = zip(*[(k,v) for k,v in possibleRecipesDict.items() if k not in dominant_ids])
    possibleRecipesArray = np.array(possibleRecipeList)
    next_pareto_front = isParetoEfficient(possibleRecipesArray,return_mask = False)
    if SIMILAR_RECIPE_PENALTY > 0:
      rid_to_index = {possibleRecipeIDs[id]:id for id in next_pareto_front}
      possibleRecipesInFront = [(1,possibleRecipeIDs[id]) for id in next_pareto_front]
      if len(dominant_ids):
        existing_vectors = [np.array(g.r_data[rid]["vector"]) for rid in dominant_ids]
      else:
        existing_vectors = []
      next_pareto_front_rids = greedyRecipeDiversitySelection(possibleRecipesInFront, numWanted-len(dominant_ids), existing = existing_vectors, fill=False)
      next_pareto_front = [rid_to_index[rid] for _, rid in next_pareto_front_rids]
    elif next_pareto_front.shape[0] + len(dominant_ids) > numWanted:
        next_pareto_front = np.random.choice(next_pareto_front,size=numWanted-len(dominant_ids),replace=False)
    dominant_ids += [possibleRecipeIDs[id] for id in (next_pareto_front)]
    numRecursions += 1
  debug(f'[paretoRecipeSort - INFO]: Needed {numRecursions} to get required recipes.')
  return dominant_ids


################################################################################
# getRecipes
# Returns a constant times wanted number of recipes.
# - Input:
#   - (dict) user_dict,
#   - (dict) server_settings
# - Output:
#   - (dict) recipes and their information,
#   - (string) error
def getRecipes(user_dict, server_settings, validation=False):
  debug(f'[getRecipes - INFO]: Starting.')

  ## Collect list of possible recipes to pick from
  ## Noting that we won't give a user a recipe they have already tried.




  # Retrieve the server document
  server_doc_ref, server_doc, err = retrieveDocument('server', 'settings')
  if err:
    return None, err
  server_dict = server_doc.to_dict()

  if validation:
    return getTasteRecipes(user_dict, for_validation=True)

  ## Check current hard_code server setting override.
  if len(EXPERIMENTAL_STATE_OVERRIDE):
    # If we're in the long-term study situation, with three user groups.
    if EXPERIMENTAL_STATE_OVERRIDE == "longitudinal":
      try:
        user_group = int(user_dict['group'])
      except:
        return None,"No experimental group assignment found in user's record."
      if user_group == 0:
        return getTasteRecipes(user_dict, trim_surprise=0.67)
      elif user_group == 1:
        return getTasteAndSurpRecipes(user_dict, server_dict, drop_thresh = 0.5, taste_surp_combo_method="avg")
      elif user_group == 2:
        return getTasteAndSurpRecipes(user_dict, server_dict, taste_drop_thresh=0.33, surp_drop_thresh=0, taste_surp_combo_method="pareto")
      elif user_group == 3:
        return getTasteAndSurpRecipes(user_dict, server_dict, taste_drop_thresh=0.33, surp_drop_thresh=0, taste_surp_combo_method="pareto_raw")
    #If we're in teh lab study situation, with two user groups.
    elif EXPERIMENTAL_STATE_OVERRIDE == 'experimental':
      expReturn = {0: getTasteRecipes, 1: getTasteAndSurpRecipes}
      try:
        user_group = int(user_dict['group'])
      except:
        return None,"No experimental group assignment found in user's record."
      return expReturn[user_group](user_dict)
    elif EXPERIMENTAL_STATE_OVERRIDE == "taste+surprise":
      return getTasteAndSurpRecipes(user_dict,server_dict)
    elif EXPERIMENTAL_STATE_OVERRIDE == "taste":
      return getTasteRecipes(user_dict)
    elif EXPERIMENTAL_STATE_OVERRIDE == "surprise":
      return getSurpRecipes(user_dict)


  # If we're in the long-term study situation, with three user groups.
  if server_dict['longitudinalState']:
    debug(f'[getRecipes - REQU]: state = longitudinalState')
    try:
      user_group = int(user_dict['group'])
    except:
      # if there is not specified group, assume they're a test user
      debug(f'[getRecipes - REQU]: no testing group found, assuming group 1')
      user_group = 1
    if user_group == 0:
      return getTasteRecipes(user_dict, trim_surprise=0.67)
    elif user_group == 1:
      return getTasteAndSurpRecipes(user_dict, server_dict, drop_thresh = 0.5, taste_surp_combo_method="avg")
    elif user_group == 2:
      return getTasteAndSurpRecipes(user_dict, server_dict, taste_drop_thresh=0.33, surp_drop_thresh=0., taste_surp_combo_method="pareto")
    elif user_group == 3:
      return getTasteAndSurpRecipes(user_dict, server_dict, taste_drop_thresh=0.33, surp_drop_thresh=0, taste_surp_combo_method="pareto_raw")

  # If we're in the lab study situation, with two user groups.
  if server_dict['experimentalState']:
    debug(f'[getRecipes - REQU]: state = experimentalState')
    try:
      user_group = int(user_dict['group'])
    except:
      # if there is not specified group, assume they're a test user
      debug(f'[getRecipes - REQU]: no testing group found, assuming group 1')
      user_group = 1 
    expReturn = {0: getTasteRecipes, 1:getTasteAndSurpRecipes}
    return expReturn[user_group](user_dict)

  if server_dict['returnTaste'] and server_dict['returnSurprise']:
    debug(f'[getRecipes - REQU]: state = tasteAndSurpState')
    return getTasteAndSurpRecipes(user_dict, server_dict)

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
    if 'i_' + rating_type not in user_dict:
      user_dict['i_'+rating_type] = {}
    if 'is_' + rating_type not in user_dict:
      user_dict['is_'+rating_type] = {}
    if 'ic_' + rating_type not in user_dict:
      user_dict['ic_'+rating_type] = {}
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
      return None, err

  # Check that the user has NOT already rated this recipe...
  try:
    user_dict['r_'+rating_type[0]][recipe_id]
    err = f'[updateSingleRecipeRating - HELP]: recipe {recipe_id} has already been rated. Skipping re-rating.'
    debug(err)
    return None, err
  except:
    pass

  # Retrieve the recipe document
  try:
    recipe_dict = g.r_data[recipe_id]
  except:
    err = f'[updateSingleRecipeRating - ERROR]: recipe {recipe_id} does not seem to exist.'
    debug(err)
    return None, err

  # Update the recipe ratings
  for rating_type in rating_types:
    rating = ratings[rating_type]
    
    if 'r_' + rating_type not in user_dict:
      user_dict['r_'+rating_type] = {}
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
