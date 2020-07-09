from flask import Flask, request, jsonify, send_file

# Create a web server
app = Flask(__name__)
recipeImgStrLen = 5
ingredientImgStrLen = 3

######## API URLs ########
# API index - shows when people visit the home page
@app.route('/')
def home():
    return 'Hello!\nYou have reached the backend API for Q-Chef.'

@app.route('/recipe_image/<imgId>')
def recipe_image(imgId):
  try:
    filename = f'{"./recipe_images/"+"0"*(recipeImgStrLen-len(imgId))+imgId}.jpg'
    return send_file(filename, mimetype='image/jpg')
  except:
    return f'Unable to find the recipe image for {imgId}.'

@app.route('/ingredient_image/<imgId>')
def ingredient_image(imgId):
  try:
    filename = f'{"./ingredient_images/"+"0"*(ingredientImgStrLen-len(imgId))+imgId}.jpg'
    return send_file(filename, mimetype='image/jpg')
  except:
    return f'Unable to find the ingredient image for {imgId}.'

################################################################################
# Returns the participant information statement for the Q-Chef surveys
@app.route('/participant_info')
def participant_info():
  return send_file('Participant Information Statement - Survey.pdf', attachment_filename='Participant Information Statement - Survey.pdf', mimetype='application/pdf')

######## Server Activation ########
# Start the web server!
if __name__ == "__main__":
    app.run()