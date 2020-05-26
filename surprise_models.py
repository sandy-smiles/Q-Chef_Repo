from flask import g
from joblib import load
import csv
from scipy.spatial import distance

######## Surprise Helper Functions ########

# getRecipeVector - returns a similarity vector for a recipe, initialising if needed
# Input:
#  - (ID): the recipe ID
#  - (string): filename to load
# Output:
#  - (list of floats): the recipe vector
#  - (string): error
def getRecipeVector(recipeID,fn="recipe_vectors.csv"):
    vectors = g.get("recipe_vectors",None)
    if vectors == None:
        # TODO(kazjon@): Should we be doing something smarter than loading from file?
        try:
            with open(fn,mode="r",encoding="utf-8") as rvf:
                reader = csv.reader(rvf)
                vectors = {}
                for row in reader:
                    vectors[row[0]] = [float(r) for r in row[1:]]
                g.recipe_vectors = vectors
            print("Loaded",fn)
        except:
            return None,f"Failed to load vectors from file. Does {fn} exist?"
    return vectors[recipeID],""

# recipeSimilarity - returns cosine similarity between two recipe vectors
# Input:
#  - (ID): the first recipe ID
#  - (ID): the second recipe ID
# Output:
#  - (float): the similarity
#  - (string): error
def recipeSimilarity(recipe1,recipe2):
    recipe1_vec,error = getRecipeVector(recipe1)
    if len(error):
        return None,error
    recipe2_vec,error = getRecipeVector(recipe2)
    if len(error):
        return None,error
    return distance.cdist(recipe1_vec, recipe2_vec, "cosine")[0],""

# getRecipeArchetypes - returns IDs for the onboarding recipe set, initialising if needed
# Input:
#  - (string): filename to load
# Output:
#  - (list of IDs): the archetype IDs
#  - (string): error
def getRecipeArchetypes(fn="archetype_ids.csv"):
    archetypes = g.get("archetype_ids",None)
    if archetypes == None:
        # TODO(kazjon@): Should we be doing something smarter than loading from file?
        try:
            with open(fn, mode="r", encoding="utf-8") as raf:
                reader = csv.reader(raf)
                archetypes = [row[0] for row in reader]
                g.archetype_ids = archetypes
            print("Loaded", fn)
        except:
            return None, f"Failed to load archetypes from file. Does {fn} exist?"
    return archetypes,""

# archetypeSimilarities - returns similarities between a target recipe and the onboarding recipe set
# Input:
#  - (ID): the recipe ID
# Output:
#  - (list of floats): the archetype similarities
#  - (string): error
def archetypeSimilarities(recipe):
    archetype_ids,error = getRecipeArchetypes()
    if len(error):
        return None,error
    sims = [recipeSimilarity(recipe,id) for id in archetype_ids] #this will return a list of similarity,error tuples
    if any(len(s[1]) for s in sims):
        return None,"".join([s[1] for s in sims])
    return [s[0] for s in sims],""

# userRecipeSurpriseRating - returns the surprise rating a user has given for a recipe.
# Input:
#  - (user ID): the user ID
#  - (recipe ID): the recipe ID
# Output:
#  - (float): the surprise rating provided by the user
#  - (string): error
def userRecipeSurpriseRating(userID,recipeID):
    # TODO(kazjon@): Replace this with a DB call
    return 0,""

# userArchetypeSurpRatings - returns user ratings of the archetypes (from onboarding)
# Input:
#  - (ID): the user ID
# Output:
#  - (list of floats): the user's ratings of the archetypal recipe's surprises (from onboarding)
#  - (string): error
def userArchetypeSurpRatings(userID):
    archetype_ids,error = getRecipeArchetypes()
    if len(error):
        return None,error
    arch_surps = []
    for arch_id in archetype_ids:
        arch_surp,error = userRecipeSurpriseRating(userID,arch_id)
        if len(error):
            return None, error
        arch_surps.append(arch_surp)
    return arch_surps,""


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
            g.nn = model
            print("Loaded",fn)
        except:
            return None,f"Failed to load model from file. Does {fn} exist?"
    return model,""

# rawSurpRecipe - returns the ingredient co-occurrence based surprise score for a recipe
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
#  - (dict): user object
# Output:
#  - (string: experience level ["novice","moderate","foodie"]
#  - (string): error
def culinaryExperience(user):
    #TODO(kazjon@): Retrieve onboarding scores & classify the user's level of "foodiness"


    return "novice",""

# simpleSurpRecipe - surprise score for a given user-recipe pair
# Input:
#  - (dict): user object
#  - (dict): recipe object
# Output:
#  - (float) calculated surprise score in [0..1]
#  - (string) error
def simpleSurpRecipe(user, targetRecipe, sigma=2, delta=1):
    # TODO(kazjon@): Assign a familiarity-modified surprise score to the recipe
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


# neuralSurpRecipe - returns the surprise score for a given user-recipe pair
# Input:
#  - (dict): user object
#  - (dict): recipe object
# Keyword input:
#  - simpleSurprise (boolean): Whether to use the simple or neural surprise models.
# Output:
#  - (float) calculated surprise score in [0..1]
#  - (string) error
def neuralSurpRecipe(user, targetRecipe, simpleSurprise=True):
    model = getNN()
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
        return neuralSurpRecipe(user,targetRecipe)


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
        responses = {k:neuralSurpRecipe(user,r) for k,r in recipes}
    errors = {}
    surprises = {}
    for key,rating in responses.items():
        errors[key] = rating[0]
        surprises[key] = rating[1]
    return surprises,errors

#If I need to update something in the DB I need to call "update document" with a collection ID and a userID.