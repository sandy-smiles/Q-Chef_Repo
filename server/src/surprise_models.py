from flask import g
from joblib import load
import csv,math
from scipy.spatial import distance
import numpy as np

from func import retrieveDocument

######## Surprise Helper Functions ########

# recipeSimilarity - returns cosine similarity between two recipe vectors
# Input:
#  - (dict): the first recipe object
#  - (dict): the second recipe object
# Output:
#  - (float): the similarity
#  - (string): error
def recipeSimilarity(recipe1,recipe2):
    return distance.cdist(recipe1["vector"], recipe2["vector"], "cosine")[0],""

# getRecipeArchetypes - returns IDs for the onboarding recipe set, initialising if needed
# Input:
#  - None
# Output:
#  - (list of dicts): the archetype recipe objects
#  - (string): error
def getRecipeArchetypes():
    archetypes = g.get("archetype_recipes",None)
    if archetypes == None:
        try:
            archetype_ids = retrieveDocument("onboarding","recipes")
            archetypes = {id:retrieveDocument("recipes",id) for id in archetype_ids}
            g.archetype_recipes = archetypes
        except:
            return None, f"Failed to load archetypes from db."
    return archetypes,""

# archetypeSimilarities - returns similarities between a target recipe and the onboarding recipe set
# Input:
#  - (dict): the recipe object
# Output:
#  - (list of floats): the archetype similarities, ordered by key
#  - (string): error
def archetypeSimilarities(recipe):
    archetype_recipes,error = getRecipeArchetypes()
    if len(error):
        return None,error
    archetype_ids = sorted(archetype_recipes.keys())
    sims = [recipeSimilarity(recipe,archetype_recipes[id]) for id in archetype_ids] #this will return a list of similarity,error tuples
    if any(len(s[1]) for s in sims):
        return None,"".join([s[1] for s in sims])
    return [s[0] for s in sims],""

# userRecipeSurpriseRating - returns the surprise rating a user has given for a recipe.
# Input:
#  - (dict): the user object
#  - (recipe ID): the recipe ID
# Output:
#  - (float): the surprise rating provided by the user
#  - (string): error
def userRecipeSurpriseRating(user,recipeID):
    if not recipeID in user["r_surprise"]:
        return None,"The surprise of this recipe has not been rated by this user."
    return user["r_surprise"][recipeID],""

# userArchetypeSurpRatings - returns user ratings of the archetypes (from onboarding)
# Input:
#  - (dict): user object
# Output:
#  - (list of floats): the user's ratings of the archetypal recipe's surprises (from onboarding)
#  - (string): error
def userArchetypeSurpRatings(user):
    archetypes,error = getRecipeArchetypes()
    if len(error):
        return None,error
    arch_surps = []
    for arch in archetypes:
        arch_id = arch[""]
        arch_surp,error = userRecipeSurpriseRating(user,arch_id)
        if len(error):
            return None, error
        arch_surps.append(arch_surp)
    return arch_surps,""


# getModels - returns the pretrained classifier used in neural surprise, initialising if needed
# Input:
#  - (string): filename to load
# Output:
#  - (dict): dict of four sklearn BaseEstimator objects (fam_high,fam_low,surp_pos,surp_neg)
#  - (string): error
def getModels(fn="nn_surprise_model.joblib"):
    model = g.get("nn",None)
    if model == None:
        # TODO(kazjon@): Should we be doing something smarter than loading from file?
        try:
            model = load(fn)
            g.nn = model
            print("Loaded",fn)
        except:
            return None,f"Failed to load model from file. Does {fn} exist?"
    return model,""

# rawSurpRecipe - returns the ingredient co-occurrence based surprise score for a recipe
# Input:
#  - (json): recipe
# Keyword input:
#  - precentile (float): At what percentile of all pairs of ingredient clusters to return the surprise value, usually 100, 95 or 90.
# Output:
#  - (float: Raw surprise score
#  - (string): error
def rawSurpRecipe(recipe,percentile=100):
    if "surprises" not in recipe.keys() or not len(recipe["surprises"]):
        return None,"No surprises found for this recipe."
    if not str(percentile)+"%" in recipe["surprises"].keys():
        return None,"That percentile was not found in the pre-calculated surprises for this recipe."
    return recipe["surprises"][str(percentile)+"%"], ""

# culinaryExperience - classifies user as novice, moderate, or foodie
# Input:
#  - (dict): user object
# Output:
#  - (string: experience level ["novice","moderate","foodie"]
#  - (string): error
def culinaryExperience(user):
    familiarities = list(user["ic_familiarity"].values())
    len_familiarities = len(familiarities)
    if len_familiarities < 20: #TODO(kazjon@): Replace this with a call to check if this user has completed onboarding
        return None,"User has not rated all onboarding ingredients."
    sum_familiarities = 0
    for fam_dict in familiarities:
      sum_familiarities += fam_dict['rating']
    fam_mean = float(sum_familiarities)/len_familiarities
    experience_levels = ["novice","moderate","foodie"]
    # +1 as fam_mean will be between -1 and 1
    return experience_levels[int(math.floor(fam_mean))+1],""


# simpleSurpRecipe - surprise score for a given user-recipe pair
# Input:
#  - (dict): user object
#  - (dict): recipe object
# Output:
#  - (float) calculated surprise score in [0..1]
#  - (string) error
def simpleSurpRecipe(user, targetRecipe, sigma=2, delta=1):
    cul_ex,error = culinaryExperience(user)
    if len(error):
        return None,error
    raw_surprise,error = rawSurpRecipe(targetRecipe)
    if len(error):
        return None,error
    # The target surprise level varies by culinary experience
    if cul_ex == "novice":
        surprise = raw_surprise - sigma
    elif cul_ex == "moderate":
        surprise = raw_surprise - sigma - delta
    elif cul_ex == "foodie":
        surprise = raw_surprise - sigma - (2 * delta)
    else:
        return None,"Unexpected value in culinary experience"
    surprise = abs(surprise / sigma)  # Gets the number of "sigmas" away from target
    surprise = min(surprise, 1)
    surprise = 1 - surprise
    return surprise,""


# advancedSurpRecipe - returns the surprise score for a given user-recipe pair
# Input:
#  - (dict): user object
#  - (dict): recipe object
# Output:
#  - (float) calculated surprise score in [0..1]
#  - (string) error
def advancedSurpRecipe(user, targetRecipe):
    return None,"Advanced (model-based) surprise is not implemented at this time."
    model = getModels()
    archetype_surp_ratings,error = userArchetypeSurpRatings(user)
    if error is not None:
        return None,error
    archetype_sims,error = archetypeSimilarities(targetRecipe)
    if error is not None:
        return None,error
    recipe_surp,error = rawSurpRecipe(targetRecipe)
    if error is not None:
        return None,error

    X = archetype_surp_ratings+archetype_sims+[recipe_surp]
    y_hat = model.predict(X)
    return y_hat,""


# surpRecipe - returns the predicted surprise for a given user-recipe pair
# Input:
#  - (dict): user object
#  - (dict): recipe object
# Keyword input:
#  - simpleSurprise (boolean): Whether to use the simple or neural surprise models.
# Output:
#  - (float) calculated surprise score in [0..1]
#  - (string) error
def surpRecipe(user, targetRecipe, simpleSurprise=True):
    if simpleSurprise:
        return simpleSurpRecipe(user,targetRecipe)
    else:
        return advancedSurpRecipe(user,targetRecipe)


#rateSurprise - returns surprises and errors for a set of recipes
# Input:
#  - (dict): user object
#  - (dict of dicts): list of recipe objects by id
# Keyword input:
#  - simpleSurprise (boolean): Whether to use the simple or neural surprise models.
# Output:
#  - (dict of id:float) per-recipe surprise
#  - (dict of id:string) per-recipe error
def rateSurprise(user, recipes, simpleSurprise=True):
    if simpleSurprise:
        responses = {k:simpleSurpRecipe(user,r) for k,r in recipes}
    else:
        responses = {k:advancedSurpRecipe(user,r) for k,r in recipes}
    errors = {}
    surprises = {}
    for key,rating in responses.items():
        errors[key] = rating[0]
        surprises[key] = rating[1]
    return surprises,errors

#If I need to update something in the DB I need to call "update document" with a collection ID and a userID.