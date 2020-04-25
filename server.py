from flask import Flask, request, jsonify, send_file

# Create a web server
app = Flask(__name__)
imgStrLen = 5

######## API URLs ########
# API index - shows when people visit the home page
@app.route('/')
def home():
    return 'Hello!\nYou have reached the backend API for Q-Chef.'

# API about - page about contacts that might be needed?
@app.route('/image/<imgId>')
def images(imgId):
  try:
    filename = f'{"./images/"+"0"*(imgStrLen-len(imgId))+imgId}.jpg'
    return send_file(filename, mimetype='image/jpg')
  except:
    return f'Unable to find an image for {imgId}.'

######## Server Activation ########
# Start the web server!
if __name__ == "__main__":
    app.run()