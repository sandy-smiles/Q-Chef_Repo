################################################################################

# Q-Chef API Server Testing
# Authors: K. di Bona
# Load testing https://q-chef-backend-api-server.web.app

# In order to run this file alone:
# $ python3 userTest-Output.py

# for i in {0..99}; do (python3 userTest.py userID${i} > ./tmp-output/userTest-output-userID${i}.txt) & done; wait; echo "Looking into output..."; python3 userTest-Output.py; wait; echo "All finished!"

# This program checks for any errors within the output of the load tests.

################################################################################
# Imports
import os
import math

################################################################################
# Global variables
inputDir = "./tmp-output/" # Holds all of the original photos
outputDir = "./tmp-output/"

################################################################################
# Testing/Debugging
# For testing, so that print statements can be turned off as needed.
DEBUG = True
WARN = True
INFO = False
DATA = False

def debug(s):
  if DEBUG and 'ERROR' in s:
    print(s)
    return

  if DEBUG and 'WARN' in s and WARN:
    print(s)
    return

  if DEBUG and 'INFO' in s and INFO:
    print(s)
    return

  if DEBUG and 'DATA' in s and DATA:
    print(s)
    return

################################################################################
# File Functions
################################################################################
# retrieveFolderFileNames
# Returns a list of all the file names within the given folder.
# - Input:
#   - (string) relativeFolderPath
#     - relative path of folder files needed are in
# - Output:
#   - (list) fileNames
#     - contains a list of all the file names in the given folder.
def retrieveFolderFileNames(relativeFolderPath):
  debug("[retrieveFolderFileNames - INFO]: Starting.")
  # Note os.walk("...") returns a tuple
  for rootFolder, directories, fileNames in os.walk(relativeFolderPath):
    fileNames.sort()
    return fileNames # Only need the list of file names

################################################################################
# checkFile
# Returns whether the file has any non-200 errors.
# - Input:
#   - (string) relativeFilePath
#     - relative path of the output file
# - Output:
#   - (string) err
def checkFile(relativeFilePath):
  debug("[checkFile - INFO]: Starting.")
  try:
    with open(relativeFilePath, 'r') as f:
      try:
        num_l = 1
        for l in f:
          l = l.strip()
          if "error" in l.lower():
            err = "[checkFile - ERROR]: In file "
            err += relativeFilePath
            err += " the word 'error' was seen on line "
            err += str(num_l) + ".\n"
            err += l
            debug(err)
            return err
          num_l += 1
      except:
        err = "[checkFile - ERROR]: Unable to check through file: "
        err += relativeFilePath
        debug(err)
        return err
    return ""
  except:
    err = "[checkFile - ERROR]: Unable to retrieve file: "
    err += relativeFilePath
    debug(err)
    return err

################################################################################
# Main Functions
################################################################################
def main():
  debug("[MAIN - INFO]: Starting.")
  fileNames = retrieveFolderFileNames(inputDir)
  debug("[MAIN - DATA]: fileNames = "+str(fileNames))

  num_err = 0
  for fileName in fileNames:
    if fileName[-4:] != ".txt":
      continue

    if "output" in fileName:
      err = checkFile(inputDir+fileName)
      if err:
        num_err += 1

  debug(f"[MAIN - WARN]: Total of errors found: {num_err}.")

################################################################################
if __name__ == "__main__":
  main()

################################################################################
# Additional Notes
################################################################################
# retrieveFolderFileNames function taken from 470203101, 470205127, 470386390's MTRX5700 Major Project imageRetrieval.py
