################################################################################

# Q-Chef API Server Data Viewing
# Authors: K. di Bona

# In order to run this file alone:
# $ python viewUserRatings.py

# This script asks for a user's id and returns the user's data in human readable
#  form.

################################################################################
# Imports
################################################################################
import json

from PIL import Image, ImageOps, ImageDraw
from io import BytesIO
import base64

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

################################################################################
# Constants
################################################################################
i_data, is_data, ic_data, r_data = {}, {}, {}, {}
# Grab the data from their jsons
with open('../server/src/data/qchef_ingredients.json', 'r') as f:
  i_data = json.load(f)
with open('../server/src/data/qchef_ingredient_subclusters.json', 'r') as f:
  is_data = json.load(f)
with open('../server/src/data/qchef_ingredient_clusters.json', 'r') as f:
  ic_data = json.load(f)
with open('../server/src/data/qchef_recipes.json', 'r') as f:
  r_data = json.load(f)

################################################################################
# Helper Functions
################################################################################
#
from helpFunc import *

################################################################################
# MAIN
################################################################################
def main():
# Use the application default credentials
  cred = credentials.Certificate("../server/src/keyKey.json")
  firebase_admin.initialize_app(cred, {
    'projectId': 'q-chef-backend-api-server',
  })

  db = firestore.client()


  # Ask for the user's ID
  usrID = input("What is the user's id/name? ")

  # Attempt to retrieve the user's document
  usr_doc_ref = db.collection('users').document(usrID)
  usr_doc = usr_doc_ref.get()
  if not usr_doc.exists:
    err = f"[MAIN - ERROR]: Unable to retreive document users/{usrID}."
    print(err)
    return

  # Turn the user's document into a dictionary
  # so that we can read from it.
  user_dict = usr_doc.to_dict()


  # Ask if we wish to view the recipe reviews
  prompt_str = f"\nDo you wish to see the {usrID}'s recipe reviews? [Y/n] "
  see_reviews = ('n' not in input(prompt_str).lower())
  if see_reviews:
    usr_review_cols = [col.id for col in db.collection('reviews').document(usrID).collections()]
    reviews_ref_dict = {id: db.collection('reviews').document(usrID).collection(id).document("review") for id in usr_review_cols}
    reviews_doc_dict = {}
    for id,ref in reviews_ref_dict.items():
      doc = ref.get()
      if not doc.exists:
        err = f"[MAIN - ERROR]: Unable to retreive document reviews/{usrID}/{id}/review."
        print(err)
        return
      reviews_doc_dict[id] = doc.to_dict()
      if reviews_doc_dict[id]["image"] is not None:
        im_base64 = reviews_doc_dict[id]["image"].replace("data:image/jpeg;base64,","")
        im = Image.open(BytesIO(base64.b64decode(im_base64)))
        im.save(f"{usrID}.{id}.jpg", format="JPEG")
      del reviews_doc_dict[id]["image"]

  print(reviews_doc_dict)

  # Ask if we wish to view the recipe ratings
  prompt_str = f"\nDo you wish to see the {usrID}'s recipe ratings? [Y/n] "
  see_r_ratings = ('n' not in input(prompt_str).lower())
  if see_r_ratings:
    # Obtain a list of all rate recipes
    # keys of all recipe taste ratings
    r_ids = sorted(user_dict['r_taste'].keys())
    for r_id in r_ids:
      # Change into a string (just in case)
      r_id = str(r_id)

      # Obtain the recipe's information
      r_info, err = getRecipeMoreInformation(r_id)
      print(f"{r_id} | {r_info['title']}\'s ingredients:")
      for i_name, i_id in r_info['ingredient_names']:
        print(f" --> {i_id} | {i_name}")
      print(f"{usrID}'s ratings for {r_id} | {r_info['title']}:")

      # Obtain the recipe familiarity rating
      try:
        r_fam = user_dict['r_familiarity'][r_id]['rating']
        num_r_fam = user_dict['r_familiarity'][r_id]['n_ratings']
        print(f"\t rated {num_r_fam} times, familiarity = {r_fam}")
      except:
        pass # No familiarity rating for this recipe.
      

      # Obtain the recipe surprise rating
      try:
        r_sur = user_dict['r_surprise'][r_id]['rating']
        num_r_sur = user_dict['r_surprise'][r_id]['n_ratings']
        print(f"\t rated {num_r_sur} times, surprise = {r_sur}")
      except:
        pass # No familiarity rating for this recipe.

      # Obtain the recipe taste rating
      try:
        r_tas = user_dict['r_taste'][r_id]['rating']
        num_r_tas = user_dict['r_taste'][r_id]['n_ratings']
        print(f"\t rated {num_r_tas} times, taste = {r_tas}")
      except:
        pass # No familiarity rating for this recipe.


  # Ask if we wish to view the ingredient cluster ratings
  prompt_str = f"\nDo you wish to see the {usrID}'s ingredient cluster ratings? [Y/n] "
  see_ic_ratings = ('n' not in input(prompt_str).lower())
  if see_ic_ratings:
    # Obtain a list of all rate ingredient clusters
    # keys of all ingredient cluster taste ratings
    ic_ids = user_dict['ic_taste'].keys()
    for ic_id in ic_ids:
      # Change into a string (just in case)
      ic_id = str(ic_id)

      # Obtain the ingredient cluster's information
      ic_info, err = getIngredientClusterInformation(ic_id)
      print(f"{usrID}'s ratings for {ic_id} | {ic_info}:")

      # Obtain the ingredient cluster familiarity rating
      try:
        ic_fam = user_dict['ic_familiarity'][ic_id]['rating']
        num_ic_fam = user_dict['ic_familiarity'][ic_id]['n_ratings']
        print(f"\t rated {num_ic_fam} times, familiarity = {ic_fam}")
      except:
        pass # No familiarity rating for this ingredient cluster.

      # Obtain the ingredient cluster surprise rating
      try:
        ic_sur = user_dict['ic_surprise'][ic_id]['rating']
        num_ic_sur = user_dict['ic_surprise'][ic_id]['n_ratings']
        print(f"\t rated {num_ic_sur} times, surprise = {ic_sur}")
      except:
        pass # No surprise rating for this ingredient cluster.

      # Obtain the ingredient cluster taste rating
      try:
        ic_tas = user_dict['ic_taste'][ic_id]['rating']
        num_ic_tas = user_dict['ic_taste'][ic_id]['n_ratings']
        print(f"\t rated {num_ic_tas} times, taste = {ic_tas}")
      except:
        pass # No taste rating for this ingredient cluster.


  # Ask if we wish to view the ingredient subcluster ratings
  prompt_str = f"\nDo you wish to see the {usrID}'s ingredient subcluster ratings? [Y/n] "
  see_is_ratings = ('n' not in input(prompt_str).lower())
  if see_is_ratings:
    # Obtain a list of all rate ingredient subclusters
    # keys of all ingredient subcluster taste ratings
    is_ids = user_dict['is_taste'].keys()
    for is_id in is_ids:
      # Change into a string (just in case)
      is_id = str(is_id)

      # Obtain the ingredient subcluster's information
      is_info, err = getIngredientSubclusterInformation(is_id)
      print(f"{usrID}'s ratings for {is_id} | {is_info}:")

      # Obtain the ingredient cluster familiarity rating
      try:
        is_fam = user_dict['is_familiarity'][is_id]['rating']
        num_is_fam = user_dict['is_familiarity'][is_id]['n_ratings']
        print(f"\t rated {num_is_fam} times, familiarity = {is_fam}")
      except:
        pass # No familiarity rating for this ingredient subcluster.

      # Obtain the ingredient cluster surprise rating
      try:
        is_sur = user_dict['is_surprise'][is_id]['rating']
        num_is_sur = user_dict['is_surprise'][is_id]['n_ratings']
        print(f"\t rated {num_is_sur} times, surprise = {is_sur}")
      except:
        pass # No surprise rating for this ingredient subcluster.

      # Obtain the ingredient cluster taste rating
      try:
        is_tas = user_dict['is_taste'][is_id]['rating']
        num_is_tas = user_dict['is_taste'][is_id]['n_ratings']
        print(f"\t rated {num_is_tas} times, taste = {is_tas}")
      except:
        pass # No taste rating for this ingredient subcluster.

  # Ask if we wish to view the ingredient ratings
  prompt_str = f"\nDo you wish to see the {usrID}'s ingredient ratings? [Y/n] "
  see_i_ratings = ('n' not in input(prompt_str).lower())
  if see_i_ratings:
    # Obtain a list of all rate ingredients
    # keys of all ingredient taste ratings
    i_ids = user_dict['i_taste'].keys()
    for i_id in i_ids:
      # Change into a string (just in case)
      i_id = str(i_id)

      # Obtain the ingredient's information
      i_info, err = getIngredientInformation(i_id)
      print(f"{usrID}'s ratings for {i_id} | {i_info}:")

      # Obtain the ingredient familiarity rating
      try:
        i_fam = user_dict['i_familiarity'][i_id]['rating']
        num_i_fam = user_dict['i_familiarity'][i_id]['n_ratings']
        print(f"\t rated {num_i_fam} times, familiarity = {i_fam}")
      except:
        pass # No familiarity rating for this ingredient.

      # Obtain the ingredient surprise rating
      try:
        i_sur = user_dict['i_surprise'][i_id]['rating']
        num_i_sur = user_dict['i_surprise'][i_id]['n_ratings']
        print(f"\t rated {num_i_sur} times, surprise = {i_sur}")
      except:
        pass # No surprise rating for this ingredient.

      # Obtain the ingredient taste rating
      try:
        i_tas = user_dict['i_taste'][i_id]['rating']
        num_i_tas = user_dict['i_taste'][i_id]['n_ratings']
        print(f"\t rated {num_i_tas} times, taste = {i_tas}")
      except:
        pass # No taste rating for this ingredient.


if __name__ == "__main__":
  main()
