######## Surprise Helper Functions ########


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
    if cul_ex == "novice":
        surprise = raw_surprise - sigma #The target surprise level
    elif cul_ex == "moderate":
        surprise = raw_surprise - sigma - delta #The target surprise level
    elif cul_ex == "foodie":
        surprise = raw_surprise - sigma - (2 * delta) #The target surprise level
    else:
        return None,"Unexpected value in culinary experience"
    surprise = abs(surprise / sigma)  # Gets the number of "deltas" away from target
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
    # TODO(kazjon@): Query a (pretrained) classifier for the surprise score
    return 0,""


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
