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
  # Go through all of the recipes
  for r_id, r_info in r_data.items():
    for i_id in r_info["ingredient_ids"]:
      if i_id == None:
        print(f"ingredient_id: 'null' found in recipe {r_id}")
    if r_info["prepTime"] == None:
      print(f"prepTime: 'null' found in recipe {r_id}")
      r_data[r_id]["prepTime"] = 0
    if r_info["cookTime"] == None:
      print(f"cookTime: 'null' found in recipe {r_id}")
      r_data[r_id]["cookTime"] = 0

  # Save the modified data back into their jsons
  with open('../server/src/data/qchef_recipes.json', 'a') as f:
    f.write('')
  with open('../server/src/data/qchef_recipes.json', 'w') as f:
    f.write(json.dumps(r_data))
