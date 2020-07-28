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
    if r_info["cookTime"] == None:
      print(f"cookTime: 'null' found in recipe {r_id}")
