import json

with open("./data/qchef_recipes.json") as f:
  d = json.load(f)
  print(list(d.keys()).sort())