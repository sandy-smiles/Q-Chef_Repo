################################################################################
# Q-Chef Server
# Authors: Q-Chef Backend Programmers
# Updated: 20200418
################################################################################
# Imports and application creation
################################################################################
import json
import requests
from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS, cross_origin

# Create a web server
app = Flask(__name__)

################################################################################
# Constants
################################################################################
documentationUrl = "https://www.docs.google.com/document/d/1iNerEqPo3D_fMmJwdRgAc42P3XKh6JzDNiu1Xo1z5hc/edit?usp=sharing"

backendIndexUrl = "https://q-chef-test.herokuapp.com"

listDelimiter = ";"

collectionIDs = ['users',
                 'recipes',
                 'ingredients',
                 'ingredient_clusters',
                 'ingredient_subclusters',
                 'onboarding']

userStartingDoc = {
  'i_taste' : {},
  'is_taste': {},
  'ic_taste': {},
  'r_taste' : {},
  'i_familiarity' : {},
  'is_familiarity': {},
  'ic_familiarity': {},
  'r_familiarity' : {},
  'pickedRecipes': []
}

exampleIngredientDict = """
{"338": "tortillas/pita/flat breads", 
 "160": "horseradish", 
 "93": "coconut"}
"""

exampleRecipeDict = """
{"60372": {
  "cookTime": 30,
  "ingredient_phrases": [
    "450g/1lb boneless chicken breasts, skinned, cut into 2.5cm/1in cubes",
    "2 tsp light soy sauce",
    "1 tsp Shaoxing rice wine (or dry sherry)",
    "1 tsp cornflour",
    "1 tbsp groundnut (peanut) oil",
    "1 tsp salt",
    "freshly ground white pepper",
    "2 tbsp finely chopped orange zest",
    "1 tbsp finely chopped lemon zest",
    "2 tsp sesame oil",
    "3 tbsp finely chopped fresh coriander",
    "enough long-grain rice to fill a measuring jug to 400ml/14fl oz level",
    "1 tbsp groundnut or peanut oil",
    "3 garlic cloves, finely sliced",
    "2 tsp salt",
    "750g/1.5lb Chinese greens, such as choi sum or bok choi"
  ],
  "prepTime": 30,
  "servings": "Serves 4",
  "steps": [
    "Combine the cubed chicken with the soy sauce, rice wine (or dry sherry) and cornflour in a small bowl. Put the mixture in the fridge for about 15 minutes.",
    "For the rice, put the rice into a heavy pan with 600ml/21 fl oz water. The general rule of thumb is that the water should come up above the level of the rice by about 2.5cm/1in, or the top part of the thumb!",
    "Bring the water to the boil and cook until most of the surface liquid has evaporated - this should take about 15 minutes. The surface of the rice should have small indentations like a pitted crater.",
    "At this point, cover the pan with a very tight-fitting lid, turn the heat as low as possible and let the rice cook undisturbed for 15 minutes.  There is no need to 'fluff' the rice, let it rest for five minutes before serving it.",
    "To finish the chicken, heat a wok until it is very hot and then add the oil. When the oil is very hot and slightly smoking, add the chicken to the wok, together with the salt, pepper and orange and lemon zest.",
    "Stir-fry the mixture for four minutes, or until the chicken is cooked.  Stir in the sesame oil and give the mixture two turns and cook for another three minutes. Finally add the coriander and continue to stir-fry for another minute. Turn onto a platter and serve at once.",
    "For the greens, heat a wok or large frying-pan over high heat until it is hot. Add the oil, and, when it is very hot and slightly smoking, add the garlic and salt. Stir-fry the mixture for 15 seconds. Quickly add the Chinese greens.  Stir-fry for 3-4 minutes, or until the greens have wilted, but are still slightly crisp.",
    "Serve the chicken with the Chinese greens and rice."
  ],
  "title": "Quick orange and lemon chicken"},
"27455": {
  "cookTime": 120,
  "ingredient_phrases": [
    "4 tbsp vegetable oil",
    "500g/1lb 2oz good-quality beef steak, finely diced",
    "500g/1lb 2oz good-quality beef mince",
    "1 white onion, peeled, finely chopped",
    "1 red onion, peeled, finely chopped",
    "2 sticks celery, trimmed, chopped",
    "1 dried chipotle chilli",
    "1 tbsp dried chilli flakes",
    ".5 tbsp chilli powder",
    "2 tsp dried oregano",
    "3 tbsp light brown sugar",
    "2 x 400g/14oz cans chopped tomatoes",
    "500ml/17fl oz beef stock",
    "1 x 400g/14oz can kidney beans, drained and rinsed",
    "1 x 400g/14oz can black-eyed beans, drained and rinsed",
    "sea salt flakes and freshly ground black pepper",
    "75g/3oz plain chocolate, minimum 70% cocoa solids, roughly chopped",
    "bunch fresh coriander",
    "steamed rice",
    "8 tbsp soured cream",
    "4 spring onions, trimmed, finely sliced"
  ],
  "prepTime": 30,
  "servings": "Serves 6-8",
  "steps": [
    "Heat two tablespoons of the oil over a medium to high heat in a large, heavy-based pan with a tight fitting lid.",
    "Fry the diced beef steak in batches until browned all over, setting each batch aside on a plate using a slotted spoon.",
    "Add another tablespoon of oil to the pan and add the beef mince, frying until browned all over. Remove the mince from the pan using a slotted spoon and set aside with the beef steak.",
    "Add the remaining tablespoon of oil to the pan and fry the white onion, red onion and celery for 3-4 minutes, or until the onions have softened but not browned.",
    "Stir in the chipotle chilli, chilli flakes, chilli powder and oregano until well combined. Cook for a further two minutes.",
    "Return the diced and minced beef to the pan, then stir in the sugar, chopped tomatoes, beef stock, kidney beans and black-eyed peas. Bring the mixture to the boil, then reduce the heat until the mixture is simmering. Cover and continue to simmer over a low heat for 2-3 hours. (Alternatively, preheat the oven to 140C/280F/Gas 1 to cook in an ovenproof dish for the same amount of time.)",
    "Just before serving, season the chilli with crushed sea salt flakes and freshly ground pepper. Stir in the chocolate until melted, then stir in the chopped coriander.",
    "Serve the chilli with a bowl of steamed rice and top each serving with a dollop of soured cream. Garnish with the sliced spring onions."
  ],
  "title": "Beef chilli with bitter chocolate"}}
"""

################################################################################
# Debugging
################################################################################
DEBUG = True
WARN = True
INFO = True
DATA = True
HELP = True

def debug(fString):
  if DEBUG and 'ERROR' in fString:
    print(fString)
    return

  if DEBUG and WARN and 'WARNING' in fString:
    print(fString)
    return

  if DEBUG and INFO and 'INFO' in fString:
    print(fString)
    return

  if DEBUG and DATA and 'DATA' in fString:
    print(fString)
    return

  if DEBUG and HELP and 'HELP' in fString:
    print(fString)
    return

################################################################################
# API URLs
################################################################################
# API index - shows when people visit the home page
@app.route('/', methods=['GET', 'POST'])
def home():
  debug('[HOME - INFO]: Request for the home page...')
  try:
    debug(f'[HOME - INFO]: Redirecting to index page {backendIndexUrl}.')
    return redirect(backendIndexUrl)
  except:
    return f"[HOME - ERROR]: Something went wrong..."

################################################################################
# Backend End Points URLs
################################################################################
# onboarding_ingredient_rating [GET|POST]
# 1st end point used.
# GET: End point is for obtaining the ingredients for the user to rate
# during on-boarding.
# - Input:
#   - n/a
# - Output:
#   - (json)
# POST: End point is for saving the user's ratings of ingredients
# during on-boarding.
# - Input:
#   - (json)
# - Output:
#   - (string) error
@app.route('/onboarding_ingredient_rating', methods=['GET', 'POST'])
@cross_origin()
def onboarding_ingredient_rating():
  debug(f'[onboarding_ingredient_rating - INFO]: Starting.')
  try:
    if request.method == 'POST':
      debug('[onboarding_ingredient_rating - INFO]: POST request')
      request_data = json.loads(request.data)
      debug(f'[onboarding_ingredient_rating - DATA]: request_data: {request_data}')
      return ''

    debug('[onboarding_ingredient_rating - INFO]: GET request')
    return jsonify(json.loads(exampleIngredientDict))
  except:
    return f"[onboarding_recipe_rating - ERROR]: Something went wrong..."
  return ""

################################################################################
# onboarding_recipe_rating [GET|POST]
# 2nd end point used.
# GET: End point is for obtaining the recipes for the user to rate 
# during on-boarding.
# - Input:
#   - n/a
# - Output:
#   - (json)
# POST: End point is for saving the user's initial ratings of recipes 
# (during onboarding).
# - Input:
#   - (json)
# - Output:
#   - (json)
@app.route('/onboarding_recipe_rating', methods=['GET', 'POST'])
@cross_origin()
def onboarding_recipe_rating():
  debug(f'[onboarding_recipe_rating - INFO]: Starting.')
  try:
    if request.method == 'POST':
      debug('[onboarding_recipe_rating - INFO]: POST request')
      request_data = json.loads(request.data)
      debug(f'[onboarding_recipe_rating - DATA]: request_data: {request_data}')
      return jsonify(json.loads(exampleRecipeDict))

    debug('[onboarding_recipe_rating - INFO]: GET request')
    return jsonify(json.loads(exampleRecipeDict))
  except:
    return f"[onboarding_recipe_rating - ERROR]: Something went wrong..."
  return ""

################################################################################
# validation_recipe_rating [POST]
# POST: End point is for saving the final set of user's reviews of recipes
# given (during onboarding).
# - Input:
#   - (json)
# - Output:
#   - (string) error
@app.route('/validation_recipe_rating', methods=['POST'])
@cross_origin()
def validation_recipe_rating():
  debug(f'[validation_recipe_rating - INFO]: Starting.')
  try:
    if request.method == 'POST':
      debug('[validation_recipe_rating - INFO]: POST request')
      request_data = json.loads(request.data)
      debug(f'[validation_recipe_rating - DATA]: request_data: {request_data}')
  except:
    return f"[validation_recipe_rating - ERROR]: Something went wrong..."
  return ""

################################################################################
# get_meal_plan_selection [POST]
# POST: End point is for saving the user's chosen number of recipes 
# for the week and retrieving the recipes to be picked from.
# Note: This function is fairly involved and may take some time 
# (so there is a wait screen in the app).
# - Input:
#   - (json)
# - Output:
#   - (json)
@app.route('/get_meal_plan_selection', methods=['POST'])
@cross_origin()
def get_meal_plan_selection():
  debug(f'[get_meal_plan_selection - INFO]: Starting.')
  try:
    if request.method == 'POST':
      debug('[get_meal_plan_selection - INFO]: POST request')
      request_data = json.loads(request.data)
      debug(f'[get_meal_plan_selection - DATA]: request_data: {request_data}')

      return jsonify(json.loads(exampleRecipeDict))
  except:
    return f"[get_meal_plan_selection - ERROR]: Something went wrong..."
  return ""

################################################################################
# save_meal_plan [POST]
# POST: End point is for saving the user's chosen recipes.
# Note: This function is fairly involved and may take some time 
# (so there is a wait screen in the app).
# - Input:
#   - (json) {"userID": <user_id>, "picked": [<recipe_id>, …, <recipe_id>], "action_log": [(<timestamp_epoch_milliseconds>, <recipe_id>, <action>), … ]}
# - Output:
#   - (string) error
@app.route('/save_meal_plan', methods=['POST'])
@cross_origin()
def save_meal_plan():
  debug(f'[save_meal_plan - INFO]: Starting.')
  try:
    if request.method == 'POST':
      debug('[save_meal_plan - INFO]: POST request')
      request_data = json.loads(request.data)
      debug(f'[save_meal_plan - DATA]: request_data: {request_data}')
  except:
    return f"[save_meal_plan - ERROR]: Something went wrong..."
  return ""

################################################################################
# retrieve_meal_plan [POST]
# POST: End point is for retrieving all info about the user's chosen recipes.
# - Input:
#   - (json) {"userID": <user_id>}
# - Output:
#   - (json)
@app.route('/retrieve_meal_plan', methods=['POST'])
@cross_origin()
def retrieve_meal_plan():
  debug(f'[retrieve_meal_plan - INFO]: Starting.')
  try:
    if request.method == 'POST':
      debug('[retrieve_meal_plan - INFO]: POST request')
      request_data = json.loads(request.data)
      debug(f'[retrieve_meal_plan - DATA]: request_data: {request_data}')

      return jsonify(json.loads(exampleRecipeDict))
  except:
    return f"[retrieve_meal_plan - ERROR]: Something went wrong..."
  return ""

################################################################################
# review_recipe [POST]
# POST: End point is for saving the user's reviews of recipes they cooked.
# - Input:
#   - (json) {"userID": <user_id>}
# - Output:
#   - (json)
@app.route('/review_recipe', methods=['POST'])
@cross_origin()
def review_recipe():
  debug(f'[review_recipe - INFO]: Starting.')
  try:
    if request.method == 'POST':
      debug('[review_recipe - INFO]: POST request')
      request_data = json.loads(request.data)
      debug(f'[review_recipe - DATA]: request_data: {request_data}')
  except:
    return f"[review_recipe - ERROR]: Something went wrong..."
  return ""

################################################################################
# Server Activation
################################################################################
# Start the web server!
if __name__ == "__main__":
  app.run(debug=True)