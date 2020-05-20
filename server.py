################################################################################
# Q-Chef Server
# Authors: Q-Chef Backend Programmers
# Updated: 20200418
################################################################################
# Imports and application creation
################################################################################
import json
import requests
from flask import Flask, request, jsonify, render_template, redirect, url_for

# Create a web server
app = Flask(__name__)

################################################################################
# Constants
################################################################################
documentationUrl = "https://www.docs.google.com/document/d/1iNerEqPo3D_fMmJwdRgAc42P3XKh6JzDNiu1Xo1z5hc/edit?usp=sharing"

backendUrl = "https://q-chef-test-back-end.herokuapp.com"

################################################################################
# Debugging
################################################################################
DEBUG = True
WARN = True
INFO = True
DATA = True
HELP = True

def debug(fString):
  if DEBUG and 'ERROR' in fString:
    print(fString)
    return

  if DEBUG and WARN and 'WARNING' in fString:
    print(fString)
    return

  if DEBUG and INFO and 'INFO' in fString:
    print(fString)
    return

  if DEBUG and DATA and 'DATA' in fString:
    print(fString)
    return

  if DEBUG and HELP and 'HELP' in fString:
    print(fString)
    return

################################################################################
# API URLs
################################################################################
# API index - shows when people visit the home page
def show_form(data):
  return render_template('index.html', data=data)

def grab_form_response(data):
  #try:
  pageInput = request.form.get('pageInput', '')
  pageName, pageRequestType = request.form.get('pageName', '').split('|')
  debug(f'[Home - HELP]: pageName = {pageName}')
  debug(f'[Home - HELP]: pageRequestType = {pageRequestType}')
  debug(f'[Home - HELP]: pageInput = {pageInput}')

  # Now redirect to the new url.
  if pageRequestType == "POST":
    debug(f"[Home - HELP]: Attempting to send a POST request to {backendUrl}/{pageName}")
    response = requests.post(backendUrl+url_for(pageName), json=pageInput)
    try:
      debug(f"[Home - DATA]: response.json() = {response.json()}")
      return response.json()
    except:
      debug(f"[Home - DATA]: response.text = {response.text}")
      return response.text

  debug(f"[Home - HELP]: Attempting to send a GET request to {backendUrl}/{pageName}")
  response = requests.get(backendUrl+url_for(pageName))
  try:
    debug(f"[Home - DATA]: response.json() = {response.json()}")
    return response.json()
  except:
    debug(f"[Home - DATA]: response.text = {response.text}")
    return response.text
  return f"Send help, I'm stuck in the back end... pageName: {pageName}, pageRequestType: {pageRequestType}, pageInput: {pageInput}"

@app.route('/', methods=['GET', 'POST'])
def home():
  debug('[HOME - INFO]: Request for the home page...')
  try:
    data = {}
    data["title"] = "Q-Chef Back-end Home Page"
    data["requestType"] = request.method
    data["intro"] = "Welcome to the Q-Chef Back-end"
    data["url"] = documentationUrl
    data["pageOutput"] = ""
    data["pageError"] = ""

    if request.method == 'POST':
      debug("[HOME - INFO]: POST request")
      debug(f"[HOME - DATA]: request.form = {request.form}")
      return grab_form_response(data)
    debug("[HOME - INFO]: GET request")
    return show_form(data)
  except:
    return f"[HOME - ERROR]: Something went wrong..."
  return ""

################################################################################
# Server Activation
################################################################################
# Start the web server!
if __name__ == "__main__":
  app.run(debug=True)