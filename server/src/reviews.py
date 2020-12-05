################################################################################
# Q-Chef Server
# Authors: Q-Chef Backend Programmers
# Updated: 20200612

from func import *

################################################################################
# Constants
################################################################################
review_types = ['cook_ratings',
                'how_response',
                'why_response',
                'image']

################################################################################
# Helper Functions
################################################################################
# updateRecipeReviews
# Updates the user's review of a recipe
# - Input:
#   - (dict) data containing user_id, recipe_ids, cook_ratings, why and how responses, and image strings.
# - Output:
#   - (string) error
def updateRecipeReviews(data):
  debug(f'[updateRecipeReviews - INFO]: Starting.')
  updating_data = {}
  user_id = data['userID']

  for review_type in review_types:
    if not (review_type in data.keys()):
      err = f'[updateRecipeReviews - ERROR]: review_type {review_type} has not been given.'
      debug(err)
      return err

  # Retrieve the user document
  user_doc_ref, user_doc, err = retrieveDocument('reviews', user_id)
  if err:
    return err

  updating_data = user_doc.to_dict()
  recipe_ids = data['cook_ratings'].keys()
  for recipe_id in recipe_ids:
    try:
      updating_data[recipe_id] = {}
      updating_data[recipe_id]['cook_rating'] = data['cook_ratings'][recipe_id]
      updating_data[recipe_id]['how'] = data['how_response'][recipe_id]
      updating_data[recipe_id]['why'] = data['why_response'][recipe_id]
      updating_data[recipe_id]['image'] = data['image'][recipe_id]
    except:
      err = f'[updateRecipeReviews - ERROR]: unable to properly save review for recipe {recipe_id}'
      debug(err)

  # Update the user's review document
  err = updateDocument('reviews', user_id, updating_data)
  if err:
    err = f'[updateRecipeReviews - ERROR]: Unable to update user review document with ratings for recipes, err: {err}'
    debug(err)
    return err
  return ''
