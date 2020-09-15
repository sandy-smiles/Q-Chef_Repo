import json
from random import randint
from time import sleep

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

#fileNames = [
#  "../server/src/data/qchef_ingredient_clusters.json",
#  "../server/src/data/qchef_ingredient_subclusters.json",
fileNames = [
#  "../server/src/data/qchef_ingredients.json",
#  "../server/src/data/qchef_recipes.json"
]

def main():
  # Load in all of the data files
  for fileName in fileNames:
    try:
      collectionName = fileName[13:-5]
      print(f"collectionName = {collectionName}")
      print(f"Loading {fileName}")
      with open(fileName, "r") as f:
        file_dic = json.load(f)
        print(f"Finished loading {fileName}")
        # Create the ingredient cluster documents
        for info_id, info_dic in file_dic.items():
          doc_ref = db.collection(collectionName).document(str(info_id))
          doc_ref.set(info_dic)
    except:
      print(f"Unable to load {fileName}")
      return

  print("Finished placing everything in???")
  return

if __name__ == "__main__":
  # Use the application default credentials
  cred = credentials.Certificate("../server/src/keyKey.json")
  firebase_admin.initialize_app(cred, {
    'projectId': 'q-chef-backend-api-server',
  })

  db = firestore.client()

  main()