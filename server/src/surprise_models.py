from flask import g
from joblib import load
import csv,math
from scipy.spatial import distance
import numpy as np
import pandas as pd

from func import retrieveDocument
from sklearn.preprocessing import PolynomialFeatures

model_fns = fns={
    "fam_high":"best_fam_high_model_10board_poly_final.joblib",
    "fam_low":"best_fam_low_model_10board_poly_final.joblib",
    "surp_pos":"best_surp_pos_model_10board_poly_final.joblib",
    "surp_neg":"best_surp_neg_model_10board_poly_final.joblib"
}

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
# Output:
#  - (dict): dict of four sklearn BaseEstimator objects (fam_high,fam_low,surp_pos,surp_neg)
#  - (string): error
def getModels():
    models_dict = g.get("models_dict",None)
    if models_dict == None:
        for model_key,model_fn in fns.items():
            try:
                models_dict["model_key"] = load(model_fn)
            except:
                return None, f"Failed to load model from file. Does {model_fn} exist?"
            print("Loaded",model_fn)

        g.models_dict = models_dict
    return models_dict,""

# rawSurpRecipe - returns the ingredient co-occurrence based surprise score for a recipe
# Input:
#  - (json): recipe
# Keyword input:
#  - precentile (float): At what percentile of all pairs of ingredient clusters to return the surprise value, usually 100, 95 or 90.
# Output:
#  - (float: Raw surprise score
#  - (string): error
def rawSurpRecipe(recipe_id,percentile=100):
    try:
        recipe = g.r_data[recipe_id]
    except:
        return None,recipe_id + " not found in g.r_data."
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
#  - (string): recipe id
# Output:
#  - (float) calculated surprise score in [0..1]
#  - (string) error
def simpleSurpRecipe(user, recipe_id, sigma=2, delta=1):
    cul_ex,error = culinaryExperience(user)
    if len(error):
        return None,error
    raw_surprise,error = rawSurpRecipe(recipe_id)
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


def predict_many_users_one_recipe(model, users, recipe_id, weight_id = None):
    X = pd.dataFrame()
    for col in model["recipe_pset"]:
        if "nov" in col:
            try:
                percentile = col.split("_")[-1]
                feature = g.nov_data[recipe_id]["novelty_"+percentile]
            except:
                return None, col + " is not a supported model feature."
        elif "surp" in col:
            try:
                percentile = col.split("_")[-1]
                feature = g.surp_data[recipe_id]["surprise_"+percentile]
            except:
                return None, col + " is not a supported model feature."
        else:
            return None,col+" is not a supported model feature."
        X[col] = [feature] * len(users)
    # UNCONVERTED CODE BELOW THIS LINE.
        # TODO: In the testbed, we've precalculated the onboarding surprise, familiarity and taste weighted for all possible recipes in the validation set.
        #      here we'll have to do that manually!
    for col in model["user_pset"]:
        if "onboarding" in col and weight_id is not None:
            X[col] = users[col + "_weighted_"+weight_id]
        else:
            X[col] = users[col]
    if model["poly_features"] > 0:
        X = PolynomialFeatures(model["poly_features"]).fit_transform(X)
    X_scaled = model["scaler"].transform(X)
    if "decision_norm" in model.keys():
        return model["predictor"].decision_function(X_scaled) / model["decision_norm"]
    else:
        return model["predictor"].predict_proba(X_scaled)[:,1]

# advancedSurpRecipe - returns the surprise score for a given user-recipe pair
# Input:
#  - (dict): user object
#  - (string): recipe id
# Output:
#  - (float) calculated surprise score in [0..1]
#  - (string) error
def advancedSurpRecipe(user, recipe_id):
    model_dict = getModels()
    recipe_predictions = {}
    for model_name,model in model_dict.iter():
        recipe_predictions[model_name] = predict_many_users_one_recipe([user],recipe_id)

    return None,"Advanced (model-based) surprise is not implemented at this time."
    # Old code after this point
    archetype_surp_ratings,error = userArchetypeSurpRatings(user)
    if error is not None:
        return None,error
    archetype_sims,error = archetypeSimilarities(recipe_id)
    if error is not None:
        return None,error
    recipe_surp,error = rawSurpRecipe(recipe_id)
    if error is not None:
        return None,error

    X = archetype_surp_ratings+archetype_sims+[recipe_surp]
    y_hat = model.predict(X)
    return y_hat,""


# surpRecipe - returns the predicted surprise for a given user-recipe pair
# Input:
#  - (dict): user object
#  - (string): recipe id
# Keyword input:
#  - simpleSurprise (boolean): Whether to use the simple or neural surprise models.
# Output:
#  - (float) calculated surprise score in [0..1]
#  - (string) error
def surpRecipe(user, recipe_id, simpleSurprise=True):
    if simpleSurprise:
        return simpleSurpRecipe(user,recipe_id)
    else:
        return advancedSurpRecipe(user,recipe_id)


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