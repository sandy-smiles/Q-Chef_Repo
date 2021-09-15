################################################################################
# Q-Chef Server
# Authors: Q-Chef Backend Programmers
# Updated: 20200612

from func import *
from PIL import Image, ImageOps, ImageDraw
from io import BytesIO
import base64
import sys

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
  print(f'[updateRecipeReviews - PRINT]: Starting review update for {user_id}')

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

  print(f'[updateRecipeReviews - PRINT]: Retrieved user doc for for {user_id}, adding reviews for {recipe_ids}')

  size = (1280,720)
  mask = Image.new('L', size, 0)
  draw = ImageDraw.Draw(mask)
  draw.rectangle((0,0) + size, fill=255)

  for recipe_id in recipe_ids:
    #try:
    if data['image'][recipe_id] is not None:
      # resize image
      if data['image'][recipe_id].startswith("data:image/jpeg"):
        print(f'[updateRecipeReviews - PRINT]: Beginning image resize for user {user_id} and recipe {recipe_id}. JPEG detected.')
        image_base64 = data['image'][recipe_id].replace("data:image/jpeg;base64,", "")
      elif data['image'][recipe_id].startswith("data:image/png"):
        print(f'[updateRecipeReviews - PRINT]: Beginning image resize for user {user_id} and recipe {recipe_id}. PNG detected.')
        image_base64 = data['image'][recipe_id].replace("data:image/png;base64,", "")
      else:
        print(f'[updateRecipeReviews - PRINT]: Beginning image resize for user {user_id} and recipe {recipe_id}. No format detected.')
        image_base64 = ""

      if image_base64 != "":
        print(f'[updateRecipeReviews - PRINT]: In image resize for user {user_id} and recipe {recipe_id}, line 72.')
        im = Image.open(BytesIO(base64.b64decode(image_base64)))
        output = ImageOps.fit(im, mask.size, centering=(0.5,0.5))
        
        print(f'[updateRecipeReviews - PRINT]: In image resize for user {user_id} and recipe {recipe_id}, line 76.')
        output2 = BytesIO()
        output.save(output2, format='JPEG')
        print(f'[updateRecipeReviews - PRINT]: In image resize for user {user_id} and recipe {recipe_id}, line 76.')
        im_data = output2.getvalue()
        base64_bytes = base64.b64encode(im_data)
        print(f'[updateRecipeReviews - PRINT]: In image resize for user {user_id} and recipe {recipe_id}, line 82.')
        base64_message = base64_bytes.decode('ascii')
        data_url = 'data:image/jpeg;base64,' + base64_message
        print(f'[updateRecipeReviews - PRINT]: In image resize for user {user_id} and recipe {recipe_id}, line 85.')
      else:
        data_url = data['image'][recipe_id]

      print(f'[updateRecipeReviews - PRINT]: Completed image resize for user {user_id} and recipe {recipe_id}, data_url is: {data_url}')
    else:
      data_url = None

    
    # debug(f"[{data_url} - INFO]: RESIZED IMAGE")
    recipe_review = {}
    recipe_review['recipe_id'] = recipe_id
    recipe_review['cook_rating'] = data['cook_ratings'][recipe_id]
    recipe_review['familiarity_ratings'] = data['familiarity_ratings'][recipe_id]
    recipe_review['taste_ratings'] = data['taste_ratings'][recipe_id]
    recipe_review['how'] = data['how_response'][recipe_id]
    recipe_review['why'] = data['why_response'][recipe_id]
    recipe_review['image'] = data_url

    size = str(sys.getsizeof(data_url))
    print(f'[updateRecipeReviews - PRINT]: In image resize for user {user_id} and recipe {recipe_id}. Final size of image is {size}')

    err = createSubDocument('reviews', user_id, recipe_id, 'review', recipe_review)
   
    debug(err)
    if err:
      err = f'[updateRecipeReviews - ERROR]: Unable to update user review document with ratings for recipes, err: {err}'
      debug(err)
    # except:
    #   err = f'[updateRecipeReviews - ERROR]: unable to properly save review for recipe {recipe_id}'
    #   debug(err)
  debug(err)
  if err:
    return err
  # Update the user's review document
  # get user review document
  return ''
