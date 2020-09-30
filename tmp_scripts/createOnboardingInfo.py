################################################################################

# Q-Chef API Server Onboarding Data Creation
# Authors: K. di Bona

# In order to run this file alone:
# $ python createOnboardingInfo.py

# Change the lists within `Constants`, ic_ids (ingredient cluster ids) and r_ids
#  (recipe ids) to those for onboarding.

# This script runs through all ingredient cluster ids listed in ic_ids, and sets
# the database onboarding ingredients document as the created json containing 
# the ids' information. 
# This script also runs through all recipe ids listed in r_ids, and sets the 
# database onboarding recipes document as the created json containing the ids'
# information.

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

from helpFunc import *

################################################################################
# MAIN
################################################################################
if __name__ == "__main__":
  ic_onboarding, r_onboarding = {}, {}

  # Create the onboarding ingredient cluster data
  for ic_id in ic_ids:
    ic_id = str(ic_id)
    try:
      ic_onboarding[ic_id], err = getIngredientClusterInformation(ic_id)
    except:
      print(f'Unable to find ingredient cluster {ic_id}')

  # Create the onboarding recipe data
  for r_id in r_ids:
    r_id = str(r_id)
    try:
      r_onboarding[r_id], err = getRecipeInformation(r_id)
    except:
      print(f'Unable to find ingredient cluster {r_id}')

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
