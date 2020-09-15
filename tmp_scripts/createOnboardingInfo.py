################################################################################
# Imports
################################################################################
import json

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

################################################################################
# Constants
################################################################################
i_data, ic_data, r_data = {}, {}, {}
# Grab the data from their jsons
with open('../server/src/data/qchef_ingredients.json', 'r') as f:
  i_data = json.load(f)
with open('../server/src/data/qchef_ingredient_clusters.json', 'r') as f:
  ic_data = json.load(f)
with open('../server/src/data/qchef_recipes.json', 'r') as f:
  r_data = json.load(f)

# Holds the onboarding ingredient cluster ids
ic_ids = ['219',
'233',
'154',
'221',
'120',
'346',
'47',
'83',
'205',
'338',
'314',
'160',
'178',
'93',
'21',
'5',
'17',
'112',
'50',
'33',
'147',
'28',
'232',
'239',
'336',
'204',
'211',
'106',
'300',
'275']


# Holds the onboarding recipe ids
r_ids = ['86478',
'85763',
'83964',
'59137',
'44423',
'06696',
'50575',
'92668',
'23591',
'80526',
'77132',
'68063',
'70563',
'09032',
'02350',
'83149',
'60372',
'73197',
'85851',
'27455']

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
  print(f'[getIngredientInformation - INFO]: Starting.')
  ingredients_dict = ic_data[ingredient_id]
  ingredientName = ingredients_dict["name"].replace('_', ' ')
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
  print(f'[getRecipeInformation - INFO]: Starting.')
  recipes_dict = r_data[recipe_id]

  # Change the ingredient ids to ingredient names
  ingredientNames = []
  for ingredient_id in recipes_dict["ingredient_ids"]:
    # Retrieve the recipe information
    ingredients_dict = i_data[str(ingredient_id)]
    ingredientName = ingredients_dict["name"].replace('_', ' ')
    if not (ingredientName in ingredientNames):
      ingredientNames.append(ingredientName)
  recipes_dict["ingredient_names"] = ingredientNames

  # Remove the image field
  del recipes_dict["image"]
  # Remove the ingredient_ids field
  del recipes_dict["ingredient_ids"]
  # Remove the surprises field
  del recipes_dict["surprises"]
  # Remove the url field
  del recipes_dict["url"]
  # Remove the vector field
  del recipes_dict["vector"]
  # Remove the vegetarian field
  del recipes_dict["vegetarian"]

  return recipes_dict, ''

################################################################################
# MAIN
################################################################################
if __name__ == "__main__":
  ic_onboarding, r_onboarding = {}, {}

  # Create the onboarding ingredient cluster data
  for ic_id in ic_ids:
    ic_id = str(ic_id)
    try:
      ic_onboarding[ic_id], err = getIngredientInformation(ic_id)
    except:
      print(f'Unable to find ingredient cluster {ic_id}')

  # Create the onboarding recipe data
  for r_id in r_ids:
    r_id = str(r_id)
    try:
      r_onboarding[r_id], err = getRecipeInformation(r_id)
    except:
      print(f'Unable to find ingredient cluster {r_id}')

  print('ic_onboarding')
  print(ic_onboarding)
  print('r_onboarding')
  print(type(r_onboarding))

  # Use the application default credentials
  cred = credentials.Certificate("../server/src/keyKey.json")
  firebase_admin.initialize_app(cred, {
    'projectId': 'q-chef-backend-api-server',
  })

  db = firestore.client()
  try:
    doc_ref = db.collection('onboarding').document('ingredients')
    try:
      doc_ref.set(ic_onboarding)
    except:
      print(f"Unable to set onboarding/ingredients")
  except:
    print(f"Unable to find onboarding/ingredients")

  try:
    doc_ref = db.collection('onboarding').document('recipes')
    try:
      doc_ref.set(r_onboarding)
    except:
      print(f"Unable to set onboarding/recipes")
  except:
    print(f"Unable to find onboarding/recipes")
