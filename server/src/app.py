################################################################################
# Q-Chef Server
# Authors: Q-Chef Backend Programmers
# Updated: 20200715

################################################################################
# Imports and Server Initialisation
################################################################################
import os
import json

import firebase_admin
from firebase_admin import credentials, firestore

# Use the application default credentials
db_cred = credentials.Certificate("./keyKey.json")
default_app = firebase_admin.initialize_app(db_cred)
db = firestore.client()

auth_cred = credentials.Certificate("./authKey.json")
auth_app = firebase_admin.initialize_app(auth_cred, name='authApp')

from flask import Flask
app = Flask(__name__)
config = {}
with open("./config.json", 'r') as f:
  config = json.loads(f.read())

def authentication(func):
  def inner(*args, **kwargs):
    # Check the token
    id_token = request_data['userID']
    # If authenticated
    try:
      # Verify the ID token while checking if the token is revoked by
      # passing check_revoked=True.
      decoded_token = auth.verify_id_token(id_token, app=auth_app, check_revoked=True)
      # Token is valid and not revoked.
      user_id = decoded_token['uid']
      return func(*args, **kwargs)
    except auth.RevokedIdTokenError:
      # Token revoked, inform the user to reauthenticate or signOut().
      pass
    except auth.InvalidIdTokenError:
      # Token is invalid
      pass
    # else return an error
    return f'Unable to authenticate the user'



from routes import *

if __name__ == "__main__":
  app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))