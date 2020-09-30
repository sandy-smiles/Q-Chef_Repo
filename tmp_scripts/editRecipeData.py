################################################################################

# Q-Chef API Server Data Checking and Editing
# Authors: K. di Bona

# In order to run this file alone:
# $ python editRecipeData.py

# This script runs through all of the recipe data within qchef_recipes.json and 
# changes any 'null' times to 0.
# Additionally it lets the user know all recipes with a listed 'null' ingredient

################################################################################
# Imports
################################################################################
import json

################################################################################
# Constants
################################################################################
r_data = {}
# Grab the data from their jsons
with open('../server/src/data/qchef_recipes.json', 'r') as f:
  r_data = json.load(f)

################################################################################
# MAIN
################################################################################
if __name__ == "__main__":
  new_r_data = {}

  # Go through all of the recipes
  for r_id, r_info in r_data.items():
    new_r_id = r_id

    len_r_id = len(r_id)
    if len_r_id < 5:
      # Create the new r_id number
      new_r_id = "0"*(5-len_r_id)+r_id
      print(f"Changed {r_id} to {new_r_id}")

    new_r_data[new_r_id] = r_info
    for i_id in r_info["ingredient_ids"]:
      if i_id == None:
        print(f"ingredient_id: 'null' found in recipe {new_r_id}")
    if r_info["prepTime"] == None:
      print(f"prepTime: 'null' found in recipe {new_r_id}")
      r_data[r_id]["prepTime"] = 0
    if r_info["cookTime"] == None:
      print(f"cookTime: 'null' found in recipe {new_r_id}")
      r_data[r_id]["cookTime"] = 0


  # Save the modified data back into their jsons
  #with open('../server/src/data/qchef_recipes.json', 'a') as f:
    #f.write('')
  #with open('../server/src/data/qchef_recipes.json', 'w') as f:
    #f.write(json.dumps(new_r_data))
