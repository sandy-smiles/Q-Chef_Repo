################################################################################

# Q-Chef API Server Script Helper Functions
# Authors: K. di Bona

# Can be included in other files through:
# from helpFunc import *

################################################################################

# Load in all data
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
# getIngredientInformation
# Returns a name of the ingredient (needed to give to the front end).
# - Input:
#   - (string) ingredient_id
# - Output:
#   - (string) ingredient's information (which is just the name),
#   - (string) error
def getIngredientInformation(ingredient_id):
  #print(f'[getIngredientInformation - INFO]: Starting.')
  ingredients_dict = i_data[ingredient_id]
  ingredientName = ingredients_dict["name"].replace('_', ' ').capitalize()
  return ingredientName, ''

################################################################################
# getIngredientSubclusterInformation
# Returns a name of the ingredient subcluster (needed to give to the front end).
# - Input:
#   - (string) ingredient_subcluster_id
# - Output:
#   - (string) ingredient subcluster's information (which is just the name),
#   - (string) error
def getIngredientSubclusterInformation(ingredient_subcluster_id):
  #print(f'[getIngredientSubclusterInformation - INFO]: Starting.')
  ingredients_dict = is_data[ingredient_subcluster_id]
  ingredientName = ingredients_dict["name"].replace('_', ' ').capitalize()
  return ingredientName, ''

################################################################################
# getIngredientClusterInformation
# Returns a name of the ingredient cluster (needed to give to the front end).
# - Input:
#   - (string) ingredient_cluster_id
# - Output:
#   - (string) ingredient cluster's information (which is just the name),
#   - (string) error
def getIngredientClusterInformation(ingredient_cluster_id):
  #print(f'[getIngredientClusterInformation - INFO]: Starting.')
  ingredients_dict = ic_data[ingredient_cluster_id]
  ingredientName = ingredients_dict["name"].replace('_', ' ').capitalize()
  return ingredientName, ''

################################################################################
# getRecipeInformation
# Returns a json of the recipe info needed to give to the front end.
# - Input:
#   - (string) recipe_id
# - Output:
#   - (dict) recipe's information,
#   - (string) error
def getRecipeInformation(recipe_id):
  #print(f'[getRecipeInformation - INFO]: Starting.')
  recipes_dict = r_data[recipe_id]

  # Change the ingredient ids to ingredient names
  ingredientNames = []
  for ingredient_id in recipes_dict["ingredient_ids"]:
    # Check that the ingredient id is not null/None
    if not ingredient_id or str(ingredient_id) == str(None):
      continue # Skip this ingredient
    # Find the ingredient name
    ingredients_dict = i_data[str(ingredient_id)]
    # Change the ingredient name to one without underscores
    ingredientName = ingredients_dict["name"].replace('_', ' ')
    # Add the ingredient name to the list if it isn't already there
    if not (ingredientName in ingredientNames):
      ingredientNames.append((ingredientName, str(ingredient_id)))
  recipes_dict["ingredient_names"] = ingredientNames

  # Remove the image field
  del recipes_dict["image"]
  # Remove the surprises field
  del recipes_dict["surprises"]
  # Remove the url field
  del recipes_dict["url"]
  # Remove the vector field
  del recipes_dict["vector"]
  # Remove the vegetarian field
  del recipes_dict["vegetarian"]

  return recipes_dict, ''

