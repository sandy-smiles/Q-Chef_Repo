################################################################################

# Q-Chef API Server Onboarding Data Deletion
# Authors: K. di Bona

# In order to run this file alone:
# $ python cleanUpUsers.py

# Change the lists within `Constants`.

# This script runs through all specified file ids and deletes them from the specified collections in the database.

################################################################################
# Imports
################################################################################
import json, time

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


################################################################################
# Constants
################################################################################
# Holds the document ids to be deleted

f_ids = ['0', '84']
test_ids = ['userID'+str(i) for i in range(99)]


collection_ids = ['users', 'actions', 'reviews']
################################################################################
# MAIN
################################################################################
if __name__ == "__main__":

  # Use the application default credentials
  cred = credentials.Certificate("../server/src/keyKey.json")
  firebase_admin.initialize_app(cred, {
    'projectId': 'q-chef-backend-api-server',
  })

  db = firestore.client()

  for c_id in collection_ids:
    for f_id in f_ids:
      try:
        doc_ref = db.collection(c_id).document(f_id)
        try:
          doc_ref.delete()
          print(f"Deleted {c_id}/{f_id}")
        except:
          print(f"Unable to delete {c_id}/{f_id}")
      except:
        print(f"Unable to find {c_id}/{f_id}")


  for c_id in collection_ids:
    for test_id in test_ids:
      try:
        doc_ref = db.collection(c_id).document(test_id)
        try:
          doc_ref.delete()
          print(f"Deleted {c_id}/{test_id}")
        except:
          print(f"Unable to delete {c_id}/{test_id}")
      except:
        print(f"Unable to find {c_id}/{test_id}")

