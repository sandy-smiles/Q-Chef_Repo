################################################################################

# Q-Chef API Server Data Viewing
# Authors: K. di Bona, K Grace

# In order to run this file alone:
# $ python viewUserRatings.py

# This script asks for a user's id and returns the user's data in human readable
#  form.

################################################################################
# Imports
################################################################################
import json

import scipy.stats
from PIL import Image, ImageOps, ImageDraw
from io import BytesIO
import base64, sys, numpy as np


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

lab_study_archive = {}
with open('qchef_study1_archive.json', 'r') as f:
  lab_study_archive = json.load(f)["__collections__"]

################################################################################
# Helper Functions
################################################################################
#
from helpFunc import *

USER_PROMPT = False

users_to_retrieve = [
"Ugz4CpIZ7zd7Xtt2Kb3uSgtEvnZ2",
"LK8AnDfW5mUYuXfSU9asmkhG9k72",
"wu2FAsOyHDVFTq79c20XFA147s23",
"RSAIrniW3jTB3j6j22fur3Ar7IR2",
"Q2Xz6zh5gEP8kthJE0W8bw1z8F03",
"2cRUCrys1IOXWIiFnO4gnxDXecp1",
"CRX9fl05t1eK2zcxNuK3WeBWGUM2",
"2W1pXNiWVdaikzJEE2S4sNONfBU2",
"qzg2879RA0QDw3rUvpTzv5D9kmH2",
"ofvHF940blYdZT9p2X6AUo11JB92",
"ARhxs80CSKfarQRUmdtTJz8ZNj72",
"fwwo78HyYIRFEI5lpFosLwuZvTH3",
"KLAIfQmEOmQIpbSeBbpwvaNj5FO2",
"vZUVACD6gGcEzPjwo5NAs3CcMvh2",
"lIxqjOEJnHdc3YgBDdIgY7Bcga72",
"wKgTCjws3sfDXwNxyrsJuTDwpJD2",
"B2FnUqiCVsSjiSmxWOOfnJNYfm83",
"T0vudFqAk5eX9D5rj7uY0elN1qi2",
"Hu2UzYiyKrQ44VJA9ZPb7IyRDqG2",
"5tRxVHOsFYTvYxnf48DktGd1mX32",
"8JwDGaR8JqZMcMu7BwX4NfH4fY82",
"tuLZo2rrXOUe5dcAZaKNL8dAUds2",
"WjOzaz7F7XhmCFiOv5OT8yMD1yk2",
"28yOEtRa7CXKNuEz5ZJWOMmWYHI3",
"QywcahVn8zOa01m0mBIRN6kDSeO2",
"9jTSePpzEvZdYdQmWmniD8uusAf2",
"PpSBB4hL2xPnU1TgswipgNuQFsI3",
"nQZ8nIqLQNfVzfG1cLXBrKRjwnq2",
"Y2GoCFpMOZOmCXjEQNBoW9TFJOH2",
"pRBZnN7i0NUKI2lVX2amTqcZNjZ2",
"UzElE5h28pZ7Aq8VZVQXlu3aVHv1",
"sBwU6K28CkdesTpuwOgUv0lR6WT2",
"4hebVk8S3rR60wndnmJbb6F2ySf1",
"niv235RqSObJME7pII7JImfNV2u2",
"3yjlCGZdrSSPOoSrJXKtlSEAiXo2",
"e9f1Y4svv0O4xQiqAmKCR1Loyie2",
"u5rpFDeXiXXmh786zzi3J3hSv2n1",
"zv87l7yCVeZohjetRgeBevumt983",
"s9fP6QS0HDXvhtw0bfAnkoN2w9B3",
"ehwwz08O8bRenB6A3AF3T5jHzO82",
"WMxkZyQIgHXfJ60xyFQuOwZKuuq1",
"c5s6q8drvRbXbu9l2hLz0LuM5S03",
"97UmP8G37Yb8ZKdqWAfzEKaC5F23"
]

################################################################################
# MAIN
################################################################################
def main():

  if USER_PROMPT:
    # Ask for the user's ID
    usrID = input("What is the user's id/name? ")

    # Attempt to retrieve the user's document
    try:
      usr_doc = lab_study_archive["users"][usrID]
    except KeyError:
      err = f"[MAIN - ERROR]: Unable to retreive document users/{usrID}."
      print(err)
      return
  else:
    reviews = {}
    validation_recipe_surprise_ratings = {}
    validation_recipe_familiarity_ratings = {}
    validation_recipe_taste_ratings = {}
    validation_recipes = {}
    onboarding_recipe_surprise_ratings = {}
    onboarding_recipe_familiarity_ratings = {}
    onboarding_recipe_taste_ratings = {}
    experimental_groups = {}
    picked_recipes = {}
    picked_recipe_surprise_raw_scores = {}
    picked_recipe_familiarity_ratings = {}
    picked_recipe_taste_ratings = {}
    print(lab_study_archive["onboarding"]["recipes"].keys())
    for uid in users_to_retrieve:
      print("** USER: ",uid)
      try:
        picked_recipes[uid] = {rid:r_data[rid] for rid in lab_study_archive["users"][uid]["pickedRecipes"]["0"]}
      except KeyError:
        picked_recipes[uid] = {}
      onboarding_recipe_surprise_ratings[uid] = {k:v["rating"] for k,v in lab_study_archive["users"][uid]["r_surprise"].items() if k in lab_study_archive["onboarding"]["recipes"].keys()}
      onboarding_recipe_familiarity_ratings[uid] = {k:v["rating"] for k,v in lab_study_archive["users"][uid]["r_familiarity"].items() if k in lab_study_archive["onboarding"]["recipes"].keys()}
      onboarding_recipe_taste_ratings[uid] = {k:v["rating"] for k,v in lab_study_archive["users"][uid]["r_taste"].items() if k in lab_study_archive["onboarding"]["recipes"].keys()}
      validation_recipe_surprise_ratings[uid] = {k:v["rating"] for k,v in lab_study_archive["users"][uid]["r_surprise"].items() if k not in lab_study_archive["onboarding"]["recipes"].keys() and k not in picked_recipes[uid]}
      validation_recipe_familiarity_ratings[uid] = {k:v["rating"] for k,v in lab_study_archive["users"][uid]["r_familiarity"].items()  if k not in lab_study_archive["onboarding"]["recipes"].keys() and k not in picked_recipes[uid]}
      validation_recipe_taste_ratings[uid] = {k:v["rating"] for k,v in lab_study_archive["users"][uid]["r_taste"].items() if k not in lab_study_archive["onboarding"]["recipes"].keys() and k not in picked_recipes[uid]}
      validation_recipes[uid] = {rid:r_data[rid] for rid in validation_recipe_surprise_ratings[uid].keys()}
      picked_recipe_familiarity_ratings[uid] = {k:v["rating"] for k,v in lab_study_archive["users"][uid]["r_familiarity"].items() if k in picked_recipes[uid]}
      picked_recipe_taste_ratings[uid] = {k:v["rating"] for k,v in lab_study_archive["users"][uid]["r_taste"].items() if k in picked_recipes[uid]}
      experimental_groups[uid] = lab_study_archive["users"][uid]["group"]
      print(len(onboarding_recipe_surprise_ratings[uid]),len(onboarding_recipe_familiarity_ratings[uid]),len(onboarding_recipe_taste_ratings[uid]),len(validation_recipe_surprise_ratings[uid]),len(validation_recipe_familiarity_ratings[uid]),len(validation_recipe_taste_ratings[uid]))
      print("  ",picked_recipes[uid])
      print("  ",lab_study_archive["users"][uid]["group"])
      print("  ",lab_study_archive["actions"][uid])
      # TO DO: iterate through users and populate the above, being careful of __collections__ and pruning out onboarding recipes.


  # TASTINESS SIGNIFICANCE
  # Calculate the difference and significance between per-user mean ratings between the two conditions
  test_val_taste_ratings = [validation_recipe_taste_ratings[uid] for uid in users_to_retrieve if experimental_groups[uid]]
  print(test_val_taste_ratings)
  test_val_taste_rating_means = [np.mean(list(user_list.values())) for user_list in test_val_taste_ratings]
  print(test_val_taste_rating_means)
  control_val_taste_ratings = [validation_recipe_taste_ratings[uid] for uid in users_to_retrieve if not experimental_groups[uid]]
  print(control_val_taste_ratings)
  control_val_taste_rating_means = [np.mean(list(user_list.values())) for user_list in control_val_taste_ratings]
  print(control_val_taste_rating_means)
  print("scipy.stats.ttest_ind(test_val_taste_rating_means,control_val_taste_rating_means)",scipy.stats.ttest_ind(test_val_taste_rating_means,control_val_taste_rating_means))
  # TODO: Consider looking at this as a binomial (% surprising) or as a categorical, or as a list of individual ratings rather than a list of means

  test_val_taste_ratings_flattened = [v for user_dict in test_val_taste_ratings for v in user_dict.values()]
  print(test_val_taste_ratings_flattened)
  control_val_taste_ratings_flattened = [v for user_dict in control_val_taste_ratings for v in user_dict.values()]
  print(control_val_taste_ratings_flattened)

  print("scipy.stats.ttest_ind(test_val_taste_ratings_flattened,control_val_taste_ratings_flattened)",scipy.stats.ttest_ind(test_val_taste_ratings_flattened,control_val_taste_ratings_flattened))


  # FAMILIARITY SIGNIFICANCE
  # Calculate the difference and significance between per-user mean ratings between the two conditions
  test_val_familiarity_ratings = [validation_recipe_familiarity_ratings[uid] for uid in users_to_retrieve if experimental_groups[uid]]
  print(test_val_familiarity_ratings)
  test_val_familiarity_rating_means = [np.mean(list(user_list.values())) for user_list in test_val_familiarity_ratings]
  print(test_val_familiarity_rating_means)
  control_val_familiarity_ratings = [validation_recipe_familiarity_ratings[uid] for uid in users_to_retrieve if not experimental_groups[uid]]
  print(control_val_familiarity_ratings)
  control_val_familiarity_rating_means = [np.mean(list(user_list.values())) for user_list in control_val_familiarity_ratings]
  print(control_val_familiarity_rating_means)
  print("scipy.stats.ttest_ind(test_val_familiarity_rating_means,control_val_familiarity_rating_means)",scipy.stats.ttest_ind(test_val_familiarity_rating_means,control_val_familiarity_rating_means))
  # TODO: Consider looking at this as a binomial (% surprising) or as a categorical, or as a list of individual ratings rather than a list of means

  test_val_familiarity_ratings_flattened = [v for user_dict in test_val_familiarity_ratings for v in user_dict.values()]
  print(test_val_familiarity_ratings_flattened)
  control_val_familiarity_ratings_flattened = [v for user_dict in control_val_familiarity_ratings for v in user_dict.values()]
  print(control_val_familiarity_ratings_flattened)

  print("scipy.stats.ttest_ind(test_val_familiarity_ratings_flattened,control_val_familiarity_ratings_flattened)",scipy.stats.ttest_ind(test_val_familiarity_ratings_flattened,control_val_familiarity_ratings_flattened))

  # SURPRISE SIGNIFICANCE
  # Calculatethe difference and significance between per-user mean ratings between the two conditions
  test_val_surprise_ratings = [validation_recipe_surprise_ratings[uid] for uid in users_to_retrieve if experimental_groups[uid]]
  print(test_val_surprise_ratings)
  test_val_surprise_rating_means = [np.mean(list(user_list.values())) for user_list in test_val_surprise_ratings]
  print(test_val_surprise_rating_means)
  control_val_surprise_ratings = [validation_recipe_surprise_ratings[uid] for uid in users_to_retrieve if not experimental_groups[uid]]
  print(control_val_surprise_ratings)
  control_val_surprise_rating_means = [np.mean(list(user_list.values())) for user_list in control_val_surprise_ratings]
  print(control_val_surprise_rating_means)
  print("scipy.stats.ttest_ind(test_val_surprise_rating_means,control_val_surprise_rating_means)",scipy.stats.ttest_ind(test_val_surprise_rating_means,control_val_surprise_rating_means))
  # TODO: Consider looking at this as a binomial (% surprising) or as a categorical, or as a list of individual ratings rather than a list of means

  test_val_surprise_ratings_flattened = [v for user_dict in test_val_surprise_ratings for v in user_dict.values()]
  print(test_val_surprise_ratings_flattened)
  control_val_surprise_ratings_flattened = [v for user_dict in control_val_surprise_ratings for v in user_dict.values()]
  print(control_val_surprise_ratings_flattened)

  print("scipy.stats.ttest_ind(test_val_surprise_ratings_flattened,control_val_surprise_ratings_flattened)",scipy.stats.ttest_ind(test_val_surprise_ratings_flattened,control_val_surprise_ratings_flattened))

  test_val_surprise_scores = [{rid:r_data[rid]["surprises"] for rid in rlist} for rlist in test_val_surprise_ratings]
  control_val_surprise_scores = [{rid:r_data[rid]["surprises"] for rid in rlist} for rlist in control_val_surprise_ratings]
  print(test_val_surprise_scores)
  print(control_val_surprise_scores)

  test_val_surprise_scores_100 = [v["100%"] for user_surprise in test_val_surprise_scores for v in user_surprise.values()]
  test_val_surprise_scores_95 = [v["95%"] for user_surprise in test_val_surprise_scores for v in user_surprise.values()]
  test_val_surprise_scores_90 = [v["90%"] for user_surprise in test_val_surprise_scores for v in user_surprise.values()]
  test_val_surprise_scores_50 = [v["50%"] for user_surprise in test_val_surprise_scores for v in user_surprise.values()]


  control_val_surprise_scores_100 = [v["100%"] for user_surprise in control_val_surprise_scores for v in user_surprise.values()]
  control_val_surprise_scores_95 = [v["95%"] for user_surprise in control_val_surprise_scores for v in user_surprise.values()]
  control_val_surprise_scores_90 = [v["90%"] for user_surprise in control_val_surprise_scores for v in user_surprise.values()]
  control_val_surprise_scores_50 = [v["50%"]  for user_surprise in control_val_surprise_scores for v in user_surprise.values()]


  print("scipy.stats.ttest_ind(test_val_surprise_scores_100,control_val_surprise_scores_100)",scipy.stats.ttest_ind(test_val_surprise_scores_100,control_val_surprise_scores_100))
  print("scipy.stats.ttest_ind(test_val_surprise_scores_95,control_val_surprise_scores_95)",scipy.stats.ttest_ind(test_val_surprise_scores_95,control_val_surprise_scores_95))
  print("scipy.stats.ttest_ind(test_val_surprise_scores_90,control_val_surprise_scores_90)",scipy.stats.ttest_ind(test_val_surprise_scores_90,control_val_surprise_scores_90))
  print("scipy.stats.ttest_ind(test_val_surprise_scores_50,control_val_surprise_scores_50)",scipy.stats.ttest_ind(test_val_surprise_scores_50,control_val_surprise_scores_50))

  # TODO:
  #    2) extend the above to familiarity and taste
  #    3) the difference and significance between the surprise scores of the recipes recommended in the validation set (to validate that it's actually showing people higher-surprise things)
  #    4) What is the correlation between surprise score and surprise rating for all validated recipes?

  # Ask if we wish to view the recipe reviews
  #prompt_str = f"\nDo you wish to see {usrID}'s recipe reviews? [Y/n] "
  #see_reviews = ('n' not in input(prompt_str).lower())
  #if see_reviews:
  #  reviews_dict = {id:val for id,val in lab_study_archive["reviews"][usrID].items() if id != "__collections__"}
  #  for id,val in reviews_dict.items():
  #    if "image" in reviews_dict[id].keys() and reviews_dict[id]["image"] is not None:
  #      im_base64 = reviews_dict[id]["image"].replace("data:image/jpeg;base64,","")
  #      im = Image.open(BytesIO(base64.b64decode(im_base64)))
  #      im.save(f"study1_review_u{usrID}.r{id}.jpg", format="JPEG")
  #      del reviews_dict[id]["image"]
  #  print(reviews_dict)

  sys.exit(0)
  # Ask if we wish to view the recipe ratings
  prompt_str = f"\nDo you wish to see the {usrID}'s recipe ratings? [Y/n] "
  see_r_ratings = ('n' not in input(prompt_str).lower())
  if see_r_ratings:
    # Obtain a list of all rate recipes
    # keys of all recipe taste ratings
    r_ids = sorted(user_dict['r_taste'].keys())
    for r_id in r_ids:
      # Change into a string (jUgz4CpIZ7zd7Xtt2Kb3uSgtEvnZ2ust in case)
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
