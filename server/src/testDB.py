import json
from random import randint
from time import sleep

import firebase_admin
from firebase_admin import credentials, firestore

def mainIngredients():
  d = {}
  try:
    collectionName = 'onboarding'
    documentName = 'ingredients'
    doc_ref = db.collection(collectionName).document(documentName)

    updateData = {'ingredient_ids' : ['219',
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
                                      '275'] }

    doc_ref.update(updateData)
  except:
    print(f"Unable to update stuff.")
    return

  print("Finished placing everything in???")
  return

def mainRecipes():
  d = {}
  try:
    collectionName = 'onboarding'
    documentName = 'recipes'
    doc_ref = db.collection(collectionName).document(documentName)

    updateData = {'recipe_ids' : ['86478',
                                  '27455',
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
                                  '85763',
                                  '90056',
                                  '66299',
                                  '27230',
                                  '22262',
                                  '85442',
                                  '50051',
                                  '89284',
                                  '90049',
                                  '84758',
                                  '68770'] }

    doc_ref.update(updateData)
  except:
    print(f"Unable to update stuff.")
    return

  print("Finished placing everything in???")
  return

if __name__ == "__main__":
  # Use the application default credentials
  cred = credentials.Certificate("./keyKey.json")
  firebase_admin.initialize_app(cred)
  db = firestore.client()

  mainIngredients()