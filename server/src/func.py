################################################################################
# Q-Chef Server
# Authors: Q-Chef Backend Programmers
# Updated: 20200621

from app import db

################################################################################
# Constants
################################################################################
collectionIDs = ['users',
                 'recipes',
                 'ingredients',
                 'ingredient_clusters',
                 'ingredient_subclusters',
                 'onboarding']

################################################################################
# Debugging
################################################################################
DEBUG = True
WARN = True
INFO = False
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
# "Database"
################################################################################
# retrieveCollection
# Retrieve a collection of documents.
# Input:
#  - (string) collectionID <- Database collection name (ID)
# Output:
#  - (col_ref) collection reference
#  - (string) error
def retrieveCollection(collectionID):
  debug(f'[retrieveCollection - INFO]: Starting.')
  collectionID = f'{collectionID}'

  if not (collectionID in collectionIDs):
    err = f'[retrieveCollection - ERROR]: Collection name {collectionID} is not a known collection.'
    debug(err)
    return None, err

  col_ref = db.collection(collectionID)
  return col_ref, ''

################################################################################
# createDocument
# Create a document within a specified document collection.
# Input:
#  - (string) collectionID <- Database collection name (ID)
#  - (string) documentID <- Database document name (ID)
#  - (dict) creationData <- Dictionary containing values to set in the doc
# Output:
#  - (string) error
def createDocument(collectionID, documentID, creationData):
  debug(f'[createDocument - INFO]: Starting.')
  collectionID = f'{collectionID}'
  documentID = f'{documentID}'

  doc_ref = db.collection(collectionID).document(documentID)
  doc_ref.set(creationData)
  doc = doc_ref.get()
  if not doc.exists:
    err = f'[retrieveDocument - ERROR]: Document {documentID} does not exist in collection {collectionID}.'
    debug(err)
    return err

  return ''

################################################################################
# retrieveDocument
# Retrieve a document within a specified document collection.
# Input:
#  - (string) collectionID <- Database collection name (ID)
#  - (string) documentID <- Database document name (ID)
# Output:
#  - (doc_ref) document reference
#  - (doc) document itself (if it exists)
#  - (string) error
def retrieveDocument(collectionID, documentID):
  debug(f'[retrieveDocument - INFO]: Starting.')
  collectionID = f'{collectionID}'
  documentID = f'{documentID}'

  if not (collectionID in collectionIDs):
    err = f'[retrieveDocument - ERROR]: Collection name {collectionID} is not a known collection.'
    debug(err)
    return None, None, err

  doc_ref = db.collection(collectionID).document(documentID)
  doc = doc_ref.get()
  if not doc.exists:
    err = f'[retrieveDocument - ERROR]: Document {documentID} does not exist in collection {collectionID}.'
    debug(err)
    return None, None, err

  return doc_ref, doc, ''

################################################################################
# deleteDocument
# Delete a document within a specified document collection.
# Input:
#  - (string) collectionID <- Database collection name (ID)
#  - (string) documentID <- Database document name (ID)
# Output:
#  - (string) error
def deleteDocument(collectionID, documentID):
  debug(f'[deleteDocument - INFO]: Starting.')
  collectionID = f'{collectionID}'
  documentID = f'{documentID}'

  doc_ref, doc, err = retrieveDocument(collectionID, documentID)
  if err:
    err = f'[deleteDocument - ERROR]: Unable to retrieve document, err: {err}'
    debug(err)
    return err

  if not doc.exists:
    return ''

  doc_ref.delete()
  return ''

################################################################################
# updateDocument
# Update a document within a specified document collection.
# Input:
#  - (string) collectionID <- Database collection name (ID)
#  - (string) documentID <- Database document name (ID)
#  - (dict) updateData <- Dictionary containing values to update in the doc
# Output:
#  - (string) error
def updateDocument(collectionID, documentID, updateData):
  debug(f'[updateDocument - INFO]: Starting.')
  collectionID = f'{collectionID}'
  documentID = f'{documentID}'

  doc_ref, doc, err = retrieveDocument(collectionID, documentID)
  if not doc.exists:
    err = f'[updateDocument - ERROR]: Document {documentID} does not exist in collection {collectionID}.'
    debug(err)
    return err

  doc_ref.update(updateData)
  return ''

################################################################################
# Helper Functions
################################################################################
# getIngredientInformation
# Returns a name of the ingredient (needed to give to the front end).
# - Input:
#   - (string) ingredient_id
# - Output:
#   - (string) ingredient's information (which is just the name),
#   - (string) error
def getIngredientInformation(ingredient_id):
  debug(f'[getIngredientInformation - INFO]: Starting.')
  # Retrieve the ingredient information
  doc_ref, doc, err = retrieveDocument('ingredients', ingredient_id)
  if err:
    return None, err

  ingredients_dict = doc.to_dict()
  ingredientName = ingredients_dict["name"].replace('_', ' ')
  return ingredientName, ''

################################################################################
# getRecipeInformation
# Returns a json of the recipe info needed to give to the front end.
# - Input:
#   - (string) recipe_id
# - Output:
#   - (dict) recipe's information,
#   - (string) error
def getRecipeInformation(recipe_id):
  debug(f'[getRecipeInformation - INFO]: Starting.')
  # Retrieve the recipe information
  doc_ref, doc, err = retrieveDocument('recipes', recipe_id)
  if err:
    return None, err
  recipes_dict = doc.to_dict()

  # Change the ingredient ids to ingredient names
  ingredientNames = []
  for ingredient_id in recipes_dict["ingredient_ids"]:
    # Retrieve the recipe information
    doc_ref, doc, err = retrieveDocument('ingredients', ingredient_id)
    if err:
      return None, err
    ingredients_dict = doc.to_dict()
    ingredientName = ingredients_dict["name"].replace('_', ' ')
    if not (ingredientName in ingredientNames):
      ingredientNames.append(ingredientName)
  recipes_dict["ingredient_names"] = ingredientNames

  # Remove the image field
  del recipes_dict["image"]
  # Remove the ingredient_ids field
  del recipes_dict["ingredient_ids"]
  # Remove the url field
  del recipes_dict["url"]
  # Remove the vector field
  del recipes_dict["vector"]
  # Remove the vegetarian field
  del recipes_dict["vegetarian"]

  return recipes_dict, ''
