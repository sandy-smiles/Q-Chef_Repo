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
# MAIN
################################################################################
def main():
  global save_folder

  ic_data, r_data = {}, {}
  print("Welcome to the Q-Chef Notebook Testing...")
  user_name = input("What is your username? ") # test_notebook
  if user_name == '':
    user_name = 'test_notebook'
    save_folder = test_folder
  print(f"userID: {user_name}")
  print("")

  # Import the needed json data
  print("Loading json data...")
  with open(data_folder+'/qchef_ingredient_clusters.json', 'r') as f:
    ic_data = json.load(f)
  with open(data_folder+'/qchef_recipes.json', 'r') as f:
    r_data = json.load(f)
  print("Finished json data.")

  #-----------------------------------------------------------------------------

  #/onboarding_recipe_rating GET
  url_path = '/onboarding_recipe_rating'
  request_type = 'GET'
  response = requests.get(url_domain+url_path)
  print(f"Sent {request_type} request to {url_domain+url_path}")
  print(f"Response Status code: {response.status_code}")

  #/onboarding_recipe_rating POST
  url_path = '/onboarding_recipe_rating'
  request_type = 'POST'
  response_data = response.json()
  try:
    print(f"Attempting to load {test_folder+url_path+'-'+str(user_name)}.json")
    with open(save_folder+url_path+f'-{user_name}.json', 'r') as f:
      request_data = json.load(f)
  except:
    print(f"Unable to load {test_folder+url_path+'-'+str(user_name)}.json")
    request_data = {
      "userID": user_name,
      "manualID": True}
    request_data['familiarity_ratings'] = {}
    request_data['taste_ratings'] = {}
    request_data['surprise_ratings'] = {}
    for r_key in response_data.keys():
      print(f"Recipe {response_data[r_key]['title']}\'s ingredients:")
      for i_name in response_data[r_key]['ingredient_names']:
        print(f" --> {i_name}")

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
        r_sur_rating = input(f"Surpise of {response_data[r_key]['title']}: ")
      request_data['surprise_ratings'][r_key] = min(max(0, int(r_sur_rating)), 2)
      print()
    with open(save_folder+url_path+f'-{user_name}.json', 'a') as f:
      f.write('')
    with open(save_folder+url_path+f'-{user_name}.json', 'w') as f:
      f.write(json.dumps(request_data))

  response = requests.post(url_domain+url_path, json=request_data)
  print(f"Sent {request_type} request to {url_domain+url_path}")
  print(f"Response Status code: {response.status_code}")
  try:
    print(f"{response.json()}")
  except:
    print(f"No response json data")
    print(f"{response.text}")

  #-----------------------------------------------------------------------------

  #/onboarding_ingredient_rating GET
  url_path = '/onboarding_ingredient_rating'
  request_type = 'GET'
  response = requests.get(url_domain+url_path)
  print(f"Sent {request_type} request to {url_domain+url_path}")
  print(f"Response Status code: {response.status_code}")

  #/onboarding_ingredient_rating POST
  url_path = '/onboarding_ingredient_rating'
  request_type = 'POST'
  response_data = response.json()
  try:
    print(f"Attempting to load {test_folder+url_path+'-'+str(user_name)}.json")
    with open(save_folder+url_path+f'-{user_name}.json', 'r') as f:
      request_data = json.load(f)
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
        ic_fam_rating = input(f"Familiarity of {ic_data[str(ic_key)]['name']}: ")
      request_data['familiarity_ratings'][ic_key] = min(max(0, int(ic_fam_rating)), 2)
      print(taste_question_str, end='')
      ic_tas_rating = ''
      while not ic_tas_rating:
        ic_tas_rating = input(f"Taste of {ic_data[str(ic_key)]['name']}: ")
      request_data['taste_ratings'][ic_key] = min(max(0, int(ic_tas_rating)), 2)
      print()
    with open(save_folder+url_path+f'-{user_name}.json', 'a') as f:
      f.write('')
    with open(save_folder+url_path+f'-{user_name}.json', 'w') as f:
      f.write(json.dumps(request_data))

  response = requests.post(url_domain+url_path, json=request_data)
  print(f"Sent {request_type} request to {url_domain+url_path}")
  print(f"Response Status code: {response.status_code}")
  try:
    print(f"{response.json()}")
  except:
    print(f"No response json data")
    print(f"{response.text}")

  #-----------------------------------------------------------------------------

  #/validation_recipe_rating POST
  url_path = '/validation_recipe_rating'
  request_type = 'POST'
  response_data = response.json()
  try:
    print(f"Attempting to load {test_folder+url_path+'-'+str(user_name)}.json")
    with open(save_folder+url_path+f'-{user_name}.json', 'r') as f:
      request_data = json.load(f)
  except:
    print(f"Unable to load {test_folder+url_path+'-'+str(user_name)}.json")
    request_data = {
      "userID": user_name,
      "manualID": True}
    request_data['familiarity_ratings'] = {}
    request_data['taste_ratings'] = {}
    request_data['surprise_ratings'] = {}
    for r_key in response_data.keys():
      print(f"Recipe {response_data[r_key]['title']}\'s ingredients:")
      for i_name in response_data[r_key]['ingredient_names']:
        print(f" --> {i_name}")

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
        r_sur_rating = input(f"Surpise of {response_data[r_key]['title']}: ")
      request_data['surprise_ratings'][r_key] = min(max(0, int(r_sur_rating)), 2)
      print()
    with open(save_folder+url_path+f'-{user_name}.json', 'a') as f:
      f.write('')
    with open(save_folder+url_path+f'-{user_name}.json', 'w') as f:
      f.write(json.dumps(request_data))

  response = requests.post(url_domain+url_path, json=request_data)
  print(f"Sent {request_type} request to {url_domain+url_path}")
  print(f"Response Status code: {response.status_code}")
  try:
    print(f"{response.json()}")
  except:
    print(f"No response json data")
    print(f"{response.text}")

  #-----------------------------------------------------------------------------
  #-----------------------------------------------------------------------------

  print("Now testing taste model...")
  testing_continue = ''
  while (testing_continue.lower() == 'y' or testing_continue.lower() == 'yes') or  not testing_continue:
    
    #/get_meal_plan_selection
    url_path = '/get_meal_plan_selection'
    request_type = 'POST'
    request_data = {
      "userID": user_name,
      "manualID": True,
      "number_of_recipes": 10}
    response = requests.post(url_domain+url_path, json=request_data)
    print(f"Sent {request_type} request to {url_domain+url_path}")
    print(f"Response Status code: {response.status_code}")

    #/validation_recipe_rating POST
    # instead of /review_recipe to bypass needed images
    url_path = '/validation_recipe_rating'
    request_type = 'POST'
    response_data = response.json()
    request_data = {
      "userID": user_name,
      "manualID": True}
    request_data['familiarity_ratings'] = {}
    request_data['taste_ratings'] = {}
    request_data['surprise_ratings'] = {}
    for r_key in response_data.keys():
      print(f"Recipe {response_data[r_key]['title']}\'s ingredients:")
      for i_name in response_data[r_key]['ingredient_names']:
        print(f" --> {i_name}")

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
        r_sur_rating = input(f"Surpise of {response_data[r_key]['title']}: ")
      request_data['surprise_ratings'][r_key] = min(max(0, int(r_sur_rating)), 2)
      print()

    response = requests.post(url_domain+url_path, json=request_data)
    print(f"Sent {request_type} request to {url_domain+url_path}")
    print(f"Response Status code: {response.status_code}")
    try:
      print(f"{response.json()}")
    except:
      print(f"No response json data")
      print(f"{response.text}")
    testing_continue = input("Do you wish to continue? (Y/n) ")

  print("")
  print("Finished testing...")
  print("Have a great day!")


if __name__ == "__main__":
  main()
