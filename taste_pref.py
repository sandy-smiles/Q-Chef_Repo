######## Predicition Helper Functions ########

# userFoodRating - returns the calculated user's food item score
# Input:
#  - (string) user's ID
#  - (string) name of food item
# Output:
#  - (float) calculated preference score
#  - (string) error
def userFoodRating(userID, targetFood):
    # TODO(kbona@): Grab from the database the user's rating of the food item
    return 0.0, "" # (float) calculated user's preference of food item

# userRecipeRating - returns the calculated user's recipe item score
# Input:
#  - (string) user's ID
#  - (string) name of recipe
# Output:
#  - (float) calculated preference score
#  - (string) error
def userRecipeRating(userID, targetRecipe):
    # TODO(kbona@): Grab from the database the user's rating of the recipe
    return 0.0, "" # (float) calculated user's preference of recipe

# recipeFood - returns list of food items for the recipe
# Input:
#  - (string) name of recipe
# Output:
#  - ([]string) list of food items
#  - (string) error
def recipeFood(targetRecipe):
    # TODO(kbona@): Grab from the database the list of ingredients in a recipe
    return ["chicken"], "" # (list) Food item(s) within the targetRecipe

# prefRecipe - returns the calculated user's preference score
# for a particular recipe
# Input:
#  - (string) user's ID
#  - (string) name of recipe
# Output:
#  - (float) calculated preference score
#  - (string) error
def prefRecipe(userID, targetRecipe):
    sumScores = 0
    foodItems, err = recipeFood(targetRecipe)
    if err:
        return 0.0, err

    for food in foodItems:
        rating, err = userFoodRating(userID, food)
        if err:
            return 0.0, err

        sumScores += rating

    return sumScores/len(foodItems), ""

# updateFoodRating - update the calculated user's food item score
# Input:
#  - (string) user's ID
#  - (string) name of food item
#  - (float) user's new rating of food item
# Output:
#  - (string) error
def updateFoodRating(userID, targetFood, newRating):
    currentRating, recipesRated, err = getFoodRating(userID, targetFood)
    if err:
        return err

    currentRating = (currentRating*recipesRated+newRating)/(recipesRated+1)
    recipesRated += 1

    # TODO(kbona@): Update database with new currentRating and recipesRated
    return ""

# updateRecipeRating - update the user's recipe score
# Input:
#  - (string) user's ID
#  - (string) name of food item
#  - (float) user's new rating of food item
# Output:
#  - (string) error
# Note:
#  - Also updates food items' score if possible.
def updateRecipeRating(userID, targetRecipe, newRating):
    foodItems, err = recipeFood(targetRecipe)
    if err:
        return err

    for food in foodItems:
        err = updateFoodRating(userID, food, newRating)
        if err:
            return err

    # TODO(kbona@): Update database with new recipeRating
    # (also check that it hasn't already been rated?
    # if so, then need to save how many times it has been rated.)
    userRecipeRating, err = getRecipeRating(userID, targetRecipe)
    if err:
        return err
    userRecipeRating[targetRecipe] = newRating

    return ""
