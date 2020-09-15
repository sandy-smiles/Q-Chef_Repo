################################################################################

# Q-Chef API Server Testing
# Authors: K. di Bona
# Load testing https://q-chef-backend-api-server.web.app

# In order to run this file alone:
# $ python userTest.py -i userIDX

# In order to run in bash:
# $ bash
# $ for i in {0..9}
# > do
# > (python3 userTest.py userID${i} > ./tmp-output/userTest-output-userID${i}.txt) &
# > done

# for i in {0..99}; do (python3 userTest.py userID${i} > ./tmp-output/userTest-output-userID${i}.txt) & done; wait; echo "All finished!"

################################################################################
# Imports
################################################################################
import sys
import json
import requests
import random as rand

################################################################################
# Constants
################################################################################
test_folder = './test_requests'
data_folder = '../server/src/data'
save_folder = './tmp'

endpoints = ['/onboarding_ingredient_rating',
             '/onboarding_recipe_rating',
             '/validation_recipe_rating',
             '/get_meal_plan_selection',
             '/save_meal_plan',
             '/retrieve_meal_plan',
             '/review_recipe']

#url_domain = 'https://q-chef-backend-api-server.web.app'
url_domain = 'http://127.0.0.1:5000'

################################################################################
# MAIN
################################################################################
def main():
  ic_data, r_data = {}, {}
  print("Welcome to the Q-Chef Notebook Testing...")
  try:
    user_name = sys.argv[1]
  except:
    print(f"userID not specified...")
    print(f"Try: $ python userTest.py -i userID")
    return

  if user_name == '':
    user_name = 'test_notebook'
  print(f"userID: {user_name}")
  print("")

  # Import the needed json data
  print(f"Loading json data for {user_name}...")
  with open(data_folder+'/qchef_ingredient_clusters.json', 'r') as f:
    ic_data = json.load(f)
  with open(data_folder+'/qchef_recipes.json', 'r') as f:
    r_data = json.load(f)
  print(f"Finished json data for {user_name}.")

  #-----------------------------------------------------------------------------

  #/onboarding_recipe_rating GET
  url_path = '/onboarding_recipe_rating'
  request_type = 'GET'
  response = requests.get(url_domain+url_path)
  print(f"{user_name} - {url_path} {request_type}: Sent {request_type} request to {url_domain+url_path}")
  print(f"{user_name} - {url_path} {request_type}: Response Status code: {response.status_code}")

  #/onboarding_recipe_rating POST
  url_path = '/onboarding_recipe_rating'
  request_type = 'POST'
  try:
    response_data = response.json()
  except:
    print(f"{user_name} - {url_path} {request_type}: Unable to obtain response.json()")
    print(f"{user_name} - {url_path} {request_type}: Ending program now.")
    return
  
  request_data = {
    "userID": user_name,
    "manualID": True}
  request_data['familiarity_ratings'] = {}
  request_data['taste_ratings'] = {}
  request_data['surprise_ratings'] = {}
  for r_key in response_data.keys():
    request_data['familiarity_ratings'][r_key] = rand.randint(0, 2)
    request_data['taste_ratings'][r_key] = rand.randint(0, 2)
    request_data['surprise_ratings'][r_key] = rand.randint(0, 2)

  response = requests.post(url_domain+url_path, json=request_data)
  print(f"{user_name} - {url_path} {request_type}: Sent {request_type} request to {url_domain+url_path}")
  print(f"{user_name} - {url_path} {request_type}: Response Status code: {response.status_code}")
  try:
    print(f"{user_name} - {url_path} {request_type}: {response.json()}")
  except:
    print(f"{user_name} - {url_path} {request_type}: No response json data")
    print(f"{user_name} - {url_path} {request_type}: {response.text}")

  #-----------------------------------------------------------------------------

  #/onboarding_ingredient_rating GET
  url_path = '/onboarding_ingredient_rating'
  request_type = 'GET'
  response = requests.get(url_domain+url_path)
  print(f"{user_name} - {url_path} {request_type}: Sent {request_type} request to {url_domain+url_path}")
  print(f"{user_name} - {url_path} {request_type}: Response Status code: {response.status_code}")

  #/onboarding_ingredient_rating POST
  url_path = '/onboarding_ingredient_rating'
  request_type = 'POST'
  try:
    response_data = response.json()
  except:
    print(f"{user_name} - {url_path} {request_type}: Unable to obtain response.json()")
    print(f"{user_name} - {url_path} {request_type}: Ending program now.")
    return
  request_data = {
    "userID": user_name,
    "manualID": True}
  request_data['familiarity_ratings'] = {}
  request_data['taste_ratings'] = {}
  for ic_key in response_data.keys():
    request_data['familiarity_ratings'][ic_key] = rand.randint(0, 2)
    request_data['taste_ratings'][ic_key] = rand.randint(0, 2)

  response = requests.post(url_domain+url_path, json=request_data)
  print(f"{user_name} - {url_path} {request_type}: Sent {request_type} request to {url_domain+url_path}")
  print(f"{user_name} - {url_path} {request_type}: Response Status code: {response.status_code}")
  try:
    print(f"{user_name} - {url_path} {request_type}: {response.json()}")
  except:
    print(f"{user_name} - {url_path} {request_type}: No response json data")
    print(f"{user_name} - {url_path} {request_type}: {response.text}")

  #-----------------------------------------------------------------------------

  #/validation_recipe_rating POST
  url_path = '/validation_recipe_rating'
  request_type = 'POST'
  try:
    response_data = response.json()
  except:
    print(f"{user_name} - {url_path} {request_type}: Unable to obtain response.json()")
    print(f"{user_name} - {url_path} {request_type}: Ending program now.")
    return
  request_data = {
    "userID": user_name,
    "manualID": True}
  request_data['familiarity_ratings'] = {}
  request_data['taste_ratings'] = {}
  request_data['surprise_ratings'] = {}
  for r_key in response_data.keys():
    request_data['familiarity_ratings'][r_key] = rand.randint(0, 2)
    request_data['taste_ratings'][r_key] = rand.randint(0, 2)
    request_data['surprise_ratings'][r_key] = rand.randint(0, 2)

  response = requests.post(url_domain+url_path, json=request_data)
  print(f"{user_name} - {url_path} {request_type}: Sent {request_type} request to {url_domain+url_path}")
  print(f"{user_name} - {url_path} {request_type}: Response Status code: {response.status_code}")
  try:
    print(f"{user_name} - {url_path} {request_type}: {response.json()}")
  except:
    print(f"{user_name} - {url_path} {request_type}: No response json data")
    print(f"{user_name} - {url_path} {request_type}: {response.text}")

if __name__ == "__main__":
  main()
