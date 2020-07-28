################################################################################
# Imports
################################################################################
import json
import requests

################################################################################
# Constants
################################################################################
data_folder = './test_requests'

endpoints = ['/onboarding_ingredient_rating GET',
             '/onboarding_ingredient_rating POST',
             '/onboarding_recipe_rating GET',
             '/onboarding_recipe_rating POST',
             '/validation_recipe_rating POST',
             '/get_meal_plan_selection POST',
             '/save_meal_plan POST',
             '/retrieve_meal_plan POST',
             '/review_recipe POST']

url_domain = 'https://q-chef-backend-api-server.web.app'

################################################################################
# MAIN
################################################################################
def main():
  for endpoint in endpoints:
    # GET or POST?
    url_path, request_type = endpoint.split()

    # GET Request
    if request_type == 'GET':
      ## Send Request
      response = requests.get(url_domain+url_path)

    # POST Request
    if request_type == 'POST':
      ## Load up json
      json_data = {}
      with open(data_folder+url_path+'.json', 'r') as f:
        json_data = json.load(f)
      ## Send Request
      response = requests.post(url_domain+url_path, json=json_data)

    # Print out final 'stuff'
    print(f"Sent {request_type} request to {url_domain+url_path}")
    print(f"Response Status code: {response.status_code}")

    # Check status
    if response.status_code != 200:
      print(f"Printing Entire Response...")
      try:
        print(f"{response.json()}")
      except:
        print(f"No response data")


if __name__ == "__main__":
  main()