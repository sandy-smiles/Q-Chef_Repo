################################################################################

# Q-Chef API Server Model Testing
# Authors: K. di Bona

# In order to run this file alone:
# $ python manualUserTest.py

# This script allows the user to pretend to be a q-chef user to test the server 
# model as different types of foodies.

################################################################################
# Imports
################################################################################
import json
import requests

################################################################################
# Constants
################################################################################
test_folder = './test_requests'
data_folder = '../server/src/data'
save_folder = './tmp'

endpoints = ['/onboarding_recipe_rating',
             '/onboarding_ingredient_rating',
             '/validation_recipe_rating',
             '/get_meal_plan_selection',
             '/save_meal_plan',
             '/retrieve_meal_plan',
             '/review_recipe']

familiarity_question_str = """Familiarity Question...
      2) I know how this tastes.
      1) I have some idea how this tastes.
      0) I don't really know how this tastes.
      """

taste_question_str = """Taste Question...
      2) I like to eat this.
      1) I sometimes like to eat this.
      0) I don't like to eat this.
      """

surprise_question_str = """Surprise Question...
      2) I think these ingredients are rarely, if ever, seen together.
      1) I think these ingredients sometimes appear together, maybe?
      0) I think these ingredients often appear in recipes together.
      """

#url_domain = 'https://q-chef-backend-api-server.web.app'
url_domain = 'http://127.0.0.1:5000'

################################################################################
# Static Data
################################################################################
i_data, is_data, ic_data, r_data = {}, {}, {}, {}
i_names = {}

# Grab the data from their jsons
with open('../server/src/data/qchef_ingredients.json', 'r') as f:
  i_data = json.load(f)
  for i_id, i_v in i_data.items():
    i_names[i_v['name'].replace('_', ' ')] = str(i_id)
with open('../server/src/data/qchef_ingredient_subclusters.json', 'r') as f:
  is_data = json.load(f)
with open('../server/src/data/qchef_ingredient_clusters.json', 'r') as f:
  ic_data = json.load(f)
with open('../server/src/data/qchef_recipes.json', 'r') as f:
  r_data = json.load(f)

################################################################################
# Helper Functions
################################################################################
def welcome():
  global save_folder

  print("Welcome to the Q-Chef Notebook Testing...")
  user_name = input("What is your username? ") # test_notebook
  if user_name == '':
    user_name = 'test_notebook'
    save_folder = test_folder
  print(f"userID: {user_name}")
  print("")
  return user_name, save_folder

#-------------------------------------------------------------------------------
def obtainResponseGET(user_name, url_domain_path):
  req_type = 'GET'
  response = requests.get(url_domain_path)
  print(f"Sent {req_type} request to {url_domain_path} for user {user_name}")
  print(f"Response Status code: {response.status_code}")
  return response.json()

#-------------------------------------------------------------------------------
def obtainResponsePOST(user_name, url_domain_path, request_data):
  req_type = 'POST'
  response = requests.post(url_domain_path, json=request_data)
  print(f"Sent {req_type} request to {url_domain_path} for user {user_name}")
  print(f"Response Status code: {response.status_code}")
  try:
    return response.json()
    #print(f"{response.json()}")
  except:
    print(f"No response json data")
    #print(f"{response.text}")
  return ''

#-------------------------------------------------------------------------------
def obtainUserPred(user_name, url_domain, list_recipe_ids):
  url_domain_path = url_domain+'/lookup_user_predicted'
  request_data = {
    "userID": user_name,
    "manualID": True,
    "recipe_ids": list_recipe_ids,
  }
  return obtainResponsePOST(user_name, url_domain_path, request_data)

#-------------------------------------------------------------------------------
def obtainUserDict(user_name, url_domain):
  url_domain_path = url_domain+'/lookup_user_saved'
  request_data = {
    "userID": user_name,
    "manualID": True}
  return obtainResponsePOST(user_name, url_domain_path, request_data)

#-------------------------------------------------------------------------------
def createRequestData(user_name, response_data, user_pred, user_dict):
  shift_indent = 8
  rate_indent = shift_indent*5
  name_indent = shift_indent*2
  types_to_print_for_ings = ["familiarity","taste"]

  r_types = ["familiarity", "surprise", "taste"]
  request_data = {
    "userID": user_name,
    "manualID": True}
  for r_type in r_types:
    request_data[r_type+'_ratings'] = {}
  for r_key in response_data.keys():
    print(f"Recipe {r_key} | {response_data[r_key]['title']}:")
    # Predicted recipe ratings
    r_r_str = ''
    for r_type in r_types:
      r_r = 'None '
      try:
        r_r, e = user_pred[r_key]["recipe"][r_type]
        r_r = 'None ' if r_r == None else f"{r_r:5.2f}"
      except:
        pass
      r_r_str += r_r + ' '
    print(' '*shift_indent+f" pred <=> {r_r_str}")
    # Saved recipe ratings
    r_r_str = ''
    for r_type in r_types:
      r_r = 'None '
      try:
        r_r = user_dict["r_"+r_type][r_key]['rating']
        r_r = 'None ' if r_r == None else f"{r_r:5.2f}"
      except:
        pass
      r_r_str += r_r + ' '
    print(' '*shift_indent+f" save <=> {r_r_str}")
    print(f"Recipe's ingredients:")
    # Ingredients
    for i_name in response_data[r_key]['ingredient_names']:
      i_key = str(i_names[i_name.lower()])
      i_key_str = i_key+' '*(5-len(i_key))
      print(f" --> {i_key_str} | {i_name}")
      # Predicted ingredient ratings
      i_r_str = ''
      for r_type in types_to_print_for_ings:
        i_r = 'None '
        try:
          i_r, e = user_pred[i_key]["ingredient"][r_type]
          i_r = 'None ' if i_r == None else f"{i_r:5.2f}"
        except:
          pass
        i_r_str += i_r + ' '
      print(' '*rate_indent+f" --> pred <=> {i_r_str}")
      # Saved ingredient ratings
      i_r_str = ''
      for r_type in types_to_print_for_ings:
        i_r = 'None '
        try:
          i_r = user_dict["i_"+r_type][i_key]['rating']
          i_r = 'None ' if i_r == None else f"{i_r:5.2f}"
        except:
          pass
        i_r_str += i_r + ' '
      print(' '*rate_indent+f" --> save <=> {i_r_str}")
      # Find the subcluster key
      is_key_str = 'None '
      is_name = 'None '
      try:
        is_key = str(i_data[i_key]['subcluster'])
        is_key_str = is_key+' '*(5-len(is_key))
        is_name = is_data[is_key]['name']
      except:
        continue # assume that if there is no subcluster there is no cluster.
      print(' '*name_indent+f" --> {is_key_str} | {is_name}")
      # Saved ingredient subcluster ratings
      is_r_str = ''
      for r_type in types_to_print_for_ings:
        is_r = 'None '
        try:
          is_r = user_dict["is_"+r_type][is_key]['rating']
          is_r = 'None ' if is_r == None else f"{is_r:5.2f}"
        except:
          pass
        is_r_str += is_r + ' '
      print(' '*rate_indent+f" --> save <=> {is_r_str}")
      # Find the cluster key
      ic_key_str = 'None '
      ic_name = 'None '
      try:
        ic_key = str(i_data[i_key]['cluster'])
        ic_key_str = ic_key+' '*(5-len(ic_key))
        ic_name = ic_data[ic_key]['name']
      except:
        continue # assume that if there is no subcluster there is no cluster.
      print(' '*name_indent+f" --> {ic_key_str} | {ic_name}")
      # Saved ingredient subcluster ratings
      ic_r_str = ''
      for r_type in types_to_print_for_ings:
        ic_r = 'None '
        try:
          ic_r = user_dict["ic_"+r_type][ic_key]['rating']
          ic_r = 'None ' if ic_r == None else f"{ic_r:5.2f}"
        except:
          pass
        ic_r_str += ic_r + ' '
      print(' '*rate_indent+f" --> save <=> {ic_r_str}")

    print(familiarity_question_str, end='')
    r_fam_rating = ''
    while not r_fam_rating:
      r_fam_rating = input(f"Familiarity of {response_data[r_key]['title']}: ")
    request_data['familiarity_ratings'][r_key] = min(max(0, int(r_fam_rating)), 2)
    print(taste_question_str, end='')
    r_tas_rating = ''
    while not r_tas_rating:
      r_tas_rating = input(f"Taste of {response_data[r_key]['title']}: ")
    request_data['taste_ratings'][r_key] = min(max(0, int(r_tas_rating)), 2)
    print(surprise_question_str, end='')
    r_sur_rating = ''
    while not r_sur_rating:
      r_sur_rating = input(f"Surprise of {response_data[r_key]['title']}: ")
    request_data['surprise_ratings'][r_key] = min(max(0, int(r_sur_rating)), 2)
    print()

  return request_data

################################################################################
# MAIN
################################################################################
def main():
  # Welcome
  user_name, save_folder = welcome()

  #/onboarding_recipe_rating GET
  url_path = '/onboarding_recipe_rating'
  response_data = obtainResponseGET(user_name, url_domain+url_path)

  #/onboarding_recipe_rating POST
  url_path = '/onboarding_recipe_rating'
  try:
    print(f"Attempting to load {test_folder+url_path+'-'+str(user_name)}.json")
    with open(save_folder+url_path+f'-{user_name}.json', 'r') as f:
      request_data = json.load(f)
    print(f"Using {test_folder+url_path+'-'+str(user_name)}.json")
  except:
    print(f"Unable to load {test_folder+url_path+'-'+str(user_name)}.json")
    # Create the request data
    user_pred = {}
    user_dict = obtainUserDict(user_name, url_domain)
    request_data = createRequestData(user_name, response_data, user_pred, user_dict)
    with open(save_folder+url_path+f'-{user_name}.json', 'a') as f:
      f.write('')
    with open(save_folder+url_path+f'-{user_name}.json', 'w') as f:
      f.write(json.dumps(request_data))

  response_data = obtainResponsePOST(user_name,  url_domain+url_path, request_data)

#-------------------------------------------------------------------------------

  #/onboarding_ingredient_rating GET
  url_path = '/onboarding_ingredient_rating'
  response_data = obtainResponseGET(user_name, url_domain+url_path)

  #/onboarding_ingredient_rating POST
  url_path = '/onboarding_ingredient_rating'
  try:
    print(f"Attempting to load {test_folder+url_path+'-'+str(user_name)}.json")
    with open(save_folder+url_path+f'-{user_name}.json', 'r') as f:
      request_data = json.load(f)
    print(f"Using {test_folder+url_path+'-'+str(user_name)}.json")
  except:
    print(f"Unable to load {test_folder+url_path+'-'+str(user_name)}.json")
    request_data = {
      "userID": user_name,
      "manualID": True}
    request_data['familiarity_ratings'] = {}
    request_data['taste_ratings'] = {}
    for ic_key in response_data.keys():
      print(familiarity_question_str, end='')
      ic_fam_rating = ''
      while not ic_fam_rating:
        ic_fam_rating = input(f"Familiarity of {ic_key} | {ic_data[str(ic_key)]['name']}: ")
      request_data['familiarity_ratings'][ic_key] = min(max(0, int(ic_fam_rating)), 2)
      print(taste_question_str, end='')
      ic_tas_rating = ''
      while not ic_tas_rating:
        ic_tas_rating = input(f"Taste of {ic_key} | {ic_data[str(ic_key)]['name']}: ")
      request_data['taste_ratings'][ic_key] = min(max(0, int(ic_tas_rating)), 2)
      print()
    with open(save_folder+url_path+f'-{user_name}.json', 'a') as f:
      f.write('')
    with open(save_folder+url_path+f'-{user_name}.json', 'w') as f:
      f.write(json.dumps(request_data))

  response_data = obtainResponsePOST(user_name,  url_domain+url_path, request_data)
  #-----------------------------------------------------------------------------

  #/validation_recipe_rating POST
  url_path = '/validation_recipe_rating'
  try:
    print(f"Attempting to load {test_folder+url_path+'-'+str(user_name)}.json")
    with open(save_folder+url_path+f'-{user_name}.json', 'r') as f:
      request_data = json.load(f)
    print(f"Using {test_folder+url_path+'-'+str(user_name)}.json")
  except:
    print(f"Unable to load {test_folder+url_path+'-'+str(user_name)}.json")
    # Create the request data
    user_pred = obtainUserPred(user_name, url_domain, list(response_data.keys()))
    user_dict = obtainUserDict(user_name, url_domain)
    request_data = createRequestData(user_name, response_data, user_pred, user_dict)
    with open(save_folder+url_path+f'-{user_name}.json', 'a') as f:
      f.write('')
    with open(save_folder+url_path+f'-{user_name}.json', 'w') as f:
      f.write(json.dumps(request_data))

  response_data = obtainResponsePOST(user_name,  url_domain+url_path, request_data)

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

  print("Now testing taste model...")
  testing_continue = ''
  while (testing_continue.lower() == 'y' or testing_continue.lower() == 'yes') or  not testing_continue:
    
    #/get_meal_plan_selection
    url_path = '/get_meal_plan_selection'
    request_data = {
      "userID": user_name, "manualID": True, "number_of_recipes": 10
    }
    response_data = obtainResponsePOST(user_name,  url_domain+url_path, request_data)

    #/validation_recipe_rating POST
    # instead of /review_recipe to bypass needed images
    url_path = '/validation_recipe_rating'
    # Create the request data
    user_pred = obtainUserPred(user_name, url_domain, list(response_data.keys()))
    user_dict = obtainUserDict(user_name, url_domain)
    request_data = createRequestData(user_name, response_data, user_pred, user_dict)
    with open(save_folder+url_path+f'-{user_name}.json', 'a') as f:
      f.write('')
    with open(save_folder+url_path+f'-{user_name}.json', 'w') as f:
      f.write(json.dumps(request_data))

    response_data = obtainResponsePOST(user_name,  url_domain+url_path, request_data)

    testing_continue = input("Do you wish to continue? (Y/n) ")

  print("")
  print("Finished testing...")
  print("Have a great day!")


if __name__ == "__main__":
  main()
