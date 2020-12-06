from flask import g
from joblib import load
import csv,math
from scipy.spatial import distance
import numpy as np
import pandas as pd
import traceback

from func import *
from sklearn.preprocessing import PolynomialFeatures

model_fns = fns={
    "fam_high":"./data/best_fam_high_model_10board_poly_final.joblib",
    "fam_low":"./data/best_fam_low_model_10board_poly_final.joblib",
    "surp_pos":"./data/best_surp_pos_model_10board_poly_final.joblib",
    "surp_neg":"./data/best_surp_neg_model_10board_poly_final.joblib"
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
    return distance.cdist([recipe1["vector"]], [recipe2["vector"]], "cosine")[0].item(),""

# getRecipeArchetypes - returns IDs for the onboarding recipe set, initialising if needed
# Input:
#  - None
# Output:
#  - (list of dicts): the archetype recipe objects
#  - (string): error
def getRecipeArchetypes():
    archetypes = g.get("archetype_recipes",None)
    if archetypes == None:
        _, archetype_ids, err = retrieveDocument("onboarding","recipes")
        if err:
            return None, f"Failed to load archetypes from db."
        archetype_ids = archetype_ids.to_dict().keys()
        archetypes = {}
        for a_id in archetype_ids:
            try:
                archetypes[a_id] = g.r_data[a_id]
            except:
                return None, f"Failed to load archetype recipe id {a_id} from g.r_data."
        g.archetype_recipes = archetypes
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
    archetype_ids = archetype_recipes.keys()
    sims = []
    for id in archetype_ids:
        sim, err = recipeSimilarity(recipe,archetype_recipes[id])
        if err:
            return None,err
        sims.append(max(0,1-sim))
    return sims

# userArchetypeSurpRatings - returns user ratings of the archetypes (from onboarding)
# Input:
#  - (dict): user object
# Output:
#  - (list of floats): the user's surprise ratings of the archetypal recipes (from onboarding)
#  - (string): error
def userArchetypeSurpRatings(user):
    archetypes,error = getRecipeArchetypes()
    if len(error):
        return None,error
    arch_surps = []
    for arch_id,arch in archetypes.items():
        try:
            arch_surp = user["r_surprise"][arch_id]["rating"]
        except:
            return None, f"No surprise rating for {arch_id} found for user {user}"
        arch_surps.append(arch_surp)
    return arch_surps,""

# userArchetypeTasteRatings - returns user ratings of the archetypes (from onboarding)
# Input:
#  - (dict): user object
# Output:
#  - (list of floats): the user's taste ratings of the archetypal recipes (from onboarding)
#  - (string): error
def userArchetypeTasteRatings(user):
    archetypes,error = getRecipeArchetypes()
    if len(error):
        return None,error
    arch_tastes = []
    for arch_id,arch in archetypes.items():
        try:
            arch_taste = user["r_taste"][arch_id]["rating"]
        except:
            return None, "No taste rating for {arch_id} found for user {user}"
        arch_tastes.append(arch_taste)
    return arch_tastes,""

# userArchetypeFamRatings - returns user ratings of the archetypes (from onboarding)
# Input:
#  - (dict): user object
# Output:
#  - (list of floats): the user's familiarity ratings of the archetypal recipes (from onboarding)
#  - (string): error
def userArchetypeFamRatings(user):
    archetypes,error = getRecipeArchetypes()
    if len(error):
        return None,error
    arch_fams = []
    for arch_id,arch in archetypes.items():
        try:
            arch_fam = user["r_familiarity"][arch_id]["rating"]
        except:
            return None, "No familiarity rating for {arch_id} found for user {user}"
        arch_fams.append(arch_fam)
    return arch_fams,""


# getModels - returns the pretrained classifier used in neural surprise, initialising if needed
# Output:
#  - (dict): dict of four sklearn BaseEstimator objects (fam_high,fam_low,surp_pos,surp_neg)
#  - (string): error
def getModels():
    models_dict = g.get("models_dict",None)
    if models_dict == None:
        models_dict = {}
        for model_key,model_fn in fns.items():
            try:
                models_dict[model_key] = load(model_fn)
            except:
                traceback.print_exc()
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
    debug(f'[simpleSurpRecipe - DATA]: surprise for {recipe_id} :{surprise}')
    return surprise,""


def predict_many_users_one_recipe(model, users, recipe_id, weight_id = None):
    X = pd.DataFrame()
    debug(f'[predict_many_users_one_recipe - INFO]: Starting, model= {model}')
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
    archetype_similarities = archetypeSimilarities(g.r_data[recipe_id])
    for col in model["user_pset"]:
        if not "onboarding" in col:
                return None, col + " is not a supported model feature."
        features = []
        for user in users:
            if "taste_avg" in col:
                archetype_ratings, error = userArchetypeTasteRatings(user)
            elif "surp_avg" in col:
                archetype_ratings, error = userArchetypeSurpRatings(user)
            elif "fam_avg" in col:
                archetype_ratings, error = userArchetypeFamRatings(user)
            if error != "":
                return None, error
            if weight_id is not None:
                features.append(np.average(archetype_ratings, weights=archetype_similarities))
            else:
                features.append(np.mean(archetype_ratings))
        X[col] = features
    if model["poly_features"] > 0:
        X = PolynomialFeatures(model["poly_features"]).fit_transform(X)
    X_scaled = model["scaler"].transform(X)
    if "decision_norm" in model.keys():
        return model["predictor"].decision_function(X_scaled) / model["decision_norm"],""
    else:
        return model["predictor"].predict_proba(X_scaled)[:,1],""

# advancedSurpRecipe - returns the surprise score for a given user-recipe pair
# Input:
#  - (dict): user object
#  - (string): recipe id
# Output:
#  - (float) calculated surprise score in [0..1]
#  - (string) error
def advancedSurpRecipe(user, recipe_id):
    model_dict,error = getModels()
    if error != "":
        return None,error
    recipe_predictions = {}
    for model_name,model in model_dict.items():
        recipe_predictions[model_name],error = predict_many_users_one_recipe(model, [user],recipe_id, weight_id=recipe_id)
        if error != "":
            return None,error
    net_fam = recipe_predictions["fam_low"] - recipe_predictions["fam_high"]

    #debug(f'[advancedSurpRecipe - DATA]: fam_high for {recipe_id} :{recipe_predictions["fam_high"]}')
    #debug(f'[advancedSurpRecipe - DATA]: fam_low for {recipe_id} :{recipe_predictions["fam_low"]}')
    debug(f'[advancedSurpRecipe - DATA]: net_fam for {recipe_id} :{net_fam}')
    net_surp = recipe_predictions["surp_pos"] - recipe_predictions["surp_neg"]
    #debug(f'[advancedSurpRecipe - DATA]: surp_pos for {recipe_id} :{recipe_predictions["surp_pos"]}')
    #debug(f'[advancedSurpRecipe - DATA]: surp_neg for {recipe_id} :{recipe_predictions["surp_neg"]}')
    debug(f'[advancedSurpRecipe - DATA]: net_surp for {recipe_id} :{net_surp}')

    surprise = max(net_fam,net_surp).item()
    debug(f'[advancedSurpRecipe - DATA]: surprise for {recipe_id} :{surprise}')
    return surprise,""

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