################################################################################

# Q-Chef API Server Endpoint Testing
# Authors: K. di Bona

# In order to run this file alone:
# $ python testServerAPI.py

# This script runs through all endpoints, in user usage order, using pre-created
#  user answers.
# This script additionally times how long it takes to hit and then receive a 
# reply from each endpoint.

################################################################################
# Imports
################################################################################
import json
import requests
import time

################################################################################
# Constants
################################################################################
test_folder = './test_requests'
data_folder = '../server/src/data'

endpoints = ['/onboarding_recipe_rating GET',
             '/onboarding_recipe_rating POST',
             '/onboarding_ingredient_rating GET',
             '/onboarding_ingredient_rating POST',
             '/validation_recipe_rating POST',
             '/get_meal_plan_selection POST',
             '/save_meal_plan POST',
             '/retrieve_meal_plan POST',
             '/review_recipe POST']

url_domain = 'https://q-chef-backend-api-server.web.app'
#url_domain = 'http://127.0.0.1:5000'

################################################################################
# MAIN
################################################################################
def main():
  start_times, end_times = [], []
  for endpoint in endpoints:
    # GET or POST?
    url_path, request_type = endpoint.split()

    # GET Request
    if request_type == 'GET':
      ## Send Request
      start_times.append(time.time())
      response = requests.get(url_domain+url_path)
      end_times.append(time.time())

    # POST Request
    if request_type == 'POST':
      ## Load up json
      json_data = {}
      with open(test_folder+url_path+'.json', 'r') as f:
        json_data = json.load(f)
      ## Send Request
      start_times.append(time.time())
      response = requests.post(url_domain+url_path, json=json_data)
      end_times.append(time.time())

    # Print out final 'stuff'
    print(f"Sent {request_type} request to {url_domain+url_path}")
    print(f"Response Status code: {response.status_code}")

    # Check status
    if request_type == 'POST':
      print(f"Printing Entire Response...")
      try:
        print(f"{json.dumps(response.json(), indent=2, sort_keys=True)}")
      except:
        print(f"No response json data")
        print(f"{response.text}")

    # Next endpoint
    print(f"")

  # Print out the time results
  for i, endpoint in enumerate(endpoints):
    print(f"Endpoint {endpoint} took {(end_times[i] - start_times[i]):.4f} seconds")


if __name__ == "__main__":
  main()
