from flask import g
from joblib import load
import sklearn

######## Surprise Helper Functions ########

def recipeSimilarity(recipe1,recipe2):
    pass

def archetypeSimilarities(recipe):
    pass

def userRecipeSurpriseRating(userID,recipeID):
    pass

def archetypeSurpRatings(userID):
    pass

# getNN - returns the pretrained classifier used in neural surprise, initialising if needed
# Input:
#  - (string): filename to load
# Output:
#  - (model): sklearn BaseEstimator object
#  - (string): error
def getNN(fn="nn_surprise_model.joblib"):
    model = g.get("nn",None)
    if model == None:
        # TODO(kazjon@): Should we be doing something smarter than loading from file?
        try:
            model = load(fn)
            print("Loaded",fn)
        except:
            return None,f"Failed to load model from file. Does {fn} exist?"
    return model,""

# rawSurpRcipe - returns the ingredient co-occurrence based surprise score for a recipe
# Input:
#  - (string): recipe ID
# Output:
#  - (float: Raw surprise score
#  - (string): error
def rawSurpRecipe(recipeID):
    #TODO(kazjon@): retrieve the surprise score from the DB
    return 2,""

# culinaryExperience - classifies user as novice, moderate, or foodie
# Input:
#  - (string): user ID
# Output:
#  - (string: experience level ["novice","moderate","foodie"]
#  - (string): error
def culinaryExperience(userID):
    #TODO(kazjon@): Retrieve onboarding scores & classify the user's level of "foodiness"
    return "novice",""

# simpleSurpRecipe - surprise score for a given user-recipe pair
# Input:
#  - (string): user ID
#  - (string): recipe ID
# Output:
#  - (float) calculated surprise score in [0..1]
#  - (string) error
def simpleSurpRecipe(userID, targetRecipe):
    # TODO(kazjon@): Assign a familiarity-modified surprise score to the recipe
    cul_ex,error = culinaryExperience(userID)
    if len(error):
        return None,error
    raw_surprise,error = rawSurpRecipe(targetRecipe)
    if len(error):
        return None,error
    sigma = 2. #TODO(kazjon@): Replace this with a DB call
    delta = 1. #TODO(kazjon@): Replace this with a DB call
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

# neuralSurpRecipe - returns the surprise score for a given user-recipe pair
# Input:
#  - (string): user ID
#  - (string): recipe ID
# Keyword input:
#  - simpleSurprise (boolean): Whether to use the simple or neural surprise models.
# Output:
#  - (float) calculated surprise score in [0..1]
#  - (string) error
def neuralSurpRecipe(userID, targetRecipe, simpleSurprise=True):
    model = getNN()
    archetype_surp_ratings,error = archetypeSurpRatings(userID)
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


# surpRecipe - returns the surprise score for a given user-recipe pair
# Input:
#  - (string): user ID
#  - (string): recipe ID
# Keyword input:
#  - simpleSurprise (boolean): Whether to use the simple or neural surprise models.
# Output:
#  - (float) calculated surprise score in [0..1]
#  - (string) error
def surpRecipe(userID, targetRecipe, simpleSurprise=True):
    if simpleSurprise:
        return simpleSurpRecipe(userID,targetRecipe)
    else:
        return neuralSurpRecipe(userID,targetRecipe)
