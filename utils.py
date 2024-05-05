import logging

def logInfoAndPrint(message):
  print(message)
  logging.info(message)

def logErrorAndPrint(message):
  print(message)
  logging.error(message)