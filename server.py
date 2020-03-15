from flask import Flask, request, jsonify

# Create a web server
app = Flask(__name__)

######## API URLs ########
# API index - shows when people visit the home page
@app.route('/')
def home():
    return 'Hello!\nYou have reached the backend API for Q-Chef.'

# API about - page about contacts that might be needed?
@app.route('/about')
def about():
    return 'Q-Chef is ...'

######## Server Activation ########
# Start the web server!
if __name__ == "__main__":
    app.run()