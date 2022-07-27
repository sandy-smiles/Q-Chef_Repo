################################################################################
# Q-Chef Server
# Authors: Q-Chef Backend Programmers
# Updated: 20200627

from func import *

################################################################################
# Constants
################################################################################

################################################################################
# Helper Functions
################################################################################
# updateActionLog
# Updates the user's action log
# - Input:
#   - (dict) data containing user_id, recipe_ids, actions.
# - Output:
#   - (string) error
def updateActionLog(data):
  debug(f'[updateActionLog - INFO]: Starting.')
  updating_data = {}
  user_id = data['userID']

  # Retrieve the user document
  user_doc_ref, user_doc, err = retrieveDocument('actions', user_id)
  if err:
    return err
  user_main_doc_ref, user_main_doc, err = retrieveDocument('users', user_id)
  if err:
    return err

  updating_data = user_doc.to_dict()
  user_profile = user_main_doc.to_dict()
  action_log = data['action_log']
  for timestamp, recipe_id, action in action_log:
    timestamp = str(timestamp)
    recipe_id = str(recipe_id)
    action = str(action)
    if not user_profile["onboarded"]:
      action = "validated"
    try:
      updating_data[recipe_id][timestamp] = action
    except:
      try:
        updating_data[recipe_id] = {timestamp: action}
      except:
        err = f'[updateActionLog - ERROR]: Unable to update user action log for recipe {recipe_id} with {action} at {timestamp}'
        debug(err)

  # Update the user's review document
  err = updateDocument('actions', user_id, updating_data)
  if err:
    err = f'[updateActionLog - ERROR]: Unable to update user action log document with actions, err: {err}'
    debug(err)
    return err
  return ''
