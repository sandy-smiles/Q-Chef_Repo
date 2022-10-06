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
import json

################################################################################
# Constants
################################################################################
r_data = {}
# Grab the data from their jsons
with open('../server/src/data/qchef_recipes_pruned.json', 'r') as f:
  r_data = json.load(f)

def getRecipeURL(rid):
    return r_data[rid]["url"].replace("www_bbc_co_uk_food_recipes_","www.bbc.co.uk/food/recipes/")

def main():
    # Use the application default credentials
    cred = credentials.Certificate("../server/src/keyKey.json")
    firebase_admin.initialize_app(cred, {
        'projectId': 'q-chef-backend-api-server',
    })

    db = firestore.client()

    # Ask for the user's ID
    num_ratings_required = int(input("How many meal plans does the user need to have generated before I extract their ratings?"))

    settings_doc_ref = db.collection('server').document("settings")
    settings_doc = settings_doc_ref.get()
    usrIDs = settings_doc.to_dict()["experimental_participants"]

    for usrID in usrIDs:

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
        if "pickedRecipes" in user_dict.keys() and user_dict["pickedRecipes"]["latest"] >= num_ratings_required:
            print("Extracting reviews for "+ usrID)

            highestSurp = 10000
            highestSurpRow = -1
            highestPref = -10000
            highestPrefRow = -1
            hasPicked = False

            # Write the data out to CSV
            rows = []
            for week, week_ratings in user_dict["servedRecipes"].items():
                if week != "latest":
                    # Figure out which recipes they picked
                    picked = {rid: "-" for rid in week_ratings["recipes"]}
                    if str(int(week) - 1) in user_dict["pickedRecipes"].keys():
                        for picked_recipe in user_dict["pickedRecipes"][str(int(week) - 1)]:
                            picked[picked_recipe] = "P"
                            hasPicked = True
                    urls = [getRecipeURL(rid) for rid in week_ratings["recipes"]]
                    for recipe in zip(week_ratings["recipes"], urls, week_ratings["predicted_surp_ratings"],
                                      week_ratings["predicted_unfam_ratings"], week_ratings["raw_surp_100_ratings"],
                                      week_ratings["taste_ratings"]):
                        recipe = list(recipe)
                        if picked[recipe[0]] == "P":
                            if recipe[3] < highestSurp:
                                highestSurp = recipe[3]
                                highestSurpRow = len(rows)
                            if recipe[4] > highestPref:
                                highestPref = recipe[4]
                                highestPrefRow = len(rows)
                        rows.append([week] + recipe + [picked[recipe[0]]])

            if hasPicked:
                rows[highestSurpRow][-1] += "S"
                rows[highestPrefRow][-1] += "T"
            if len(rows):
                import csv
                with open(usrID + "_ratings.csv", "w") as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(["planID", "recipeID", "url","predSurp" ,"predUnfam", "rawSurp", "predTaste", "picked"])
                    writer.writerows(rows)
            else:
                print("Skipping " + usrID + " as they haven't done anything.")
        else:
                print("Skipping "+usrID + " as they haven't picked enough meals.")


if __name__ == "__main__":
    main()
