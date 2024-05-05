# This is a Python version of FileCopier, though this version is intended to be a command-line
# utility, rather than a UI application.  A UI may be added later.

import sys
import os.path
import os
import argparse
import traceback
from configparser import ConfigParser
from copyGroup import CopyGroup
import logging
from logging.handlers import RotatingFileHandler
from utils import logInfoAndPrint

gIniFileName = 'file-copier.ini'
kLogFile = 'PyFileCopier.log'

kMaxLogileSize = 1024 * 1024

def getScriptPath():
  if getattr(sys, 'frozen', False):
    # If the application is run as a bundle, the PyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app
    # path into variable _MEIPASS'.
    application_path, executable = os.path.split(sys.executable)
  else:
    application_path = os.path.dirname(os.path.abspath(__file__))

  return application_path

def getLogfilePath():
  return os.path.join(getScriptPath(), kLogFile)

def locateConfigFile(possibleConfigFilePath):
  iniFilePath = None
  if possibleConfigFilePath is not None and len(possibleConfigFilePath) > 0:
    # User supplied a path to the Config file.  Use this instead.
    iniFilePath = possibleConfigFilePath
  else:
    # Use the default config file, in the script directory
    iniFileDir = getScriptPath()

    iniFileDir = os.path.abspath(iniFileDir)
    iniFilePath = os.path.join(iniFileDir, gIniFileName)

  # Make sure the Config file can be found
  if not os.path.exists(iniFilePath):
    return (iniFilePath, False)
  else:
    return (iniFilePath, True)

def readIniFile(iniFilePath, copyParameters) -> list[CopyGroup]:
  """ Reads the INI file.
      Returns: An array of CopyGroups
  """
  config = ConfigParser()

  config.read(iniFilePath)

  copyGroups = []

  sections = config.sections()

  for section in sections:
    copyGroup = CopyGroup(section, copyParameters)
    copyGroup.directory = config.get(section, 'directory', fallback='')
    destDirLine = config.get(section, 'destDir', fallback='')
    if len(destDirLine) > 0:
      copyGroup.destDir =  destDirLine.split(',')

    copyGroup.copySubdirs = config.getboolean(section, 'copySubdirs', fallback=False)
    excludeExtensions = config.get(section, 'excludeExtensions', fallback=[])
    if len(excludeExtensions) > 0:
      copyGroup.excludeExtensions = excludeExtensions.split(',')

    excludeSubdirs = config.get(section, 'excludeSubdirs', fallback=[])
    if len(excludeSubdirs) > 0:
      copyGroup.excludeSubdirs = excludeSubdirs.split(',')

    excludeFiles = config.get(section, 'excludeFiles', fallback=[])
    if len(excludeFiles) > 0:
      copyGroup.excludeFiles = excludeFiles.split(',')

    # TODO: Need validation of fields, especially to check for missing required fields.
    copyGroups.append(copyGroup)

    logging.info(f'Copy Group: {section}')
    logging.info(f'Source directory: {copyGroup.directory}')
    logging.info(f'Destination directory: {copyGroup.destDir}')
    logging.info(f'Copy subdirectories: {copyGroup.copySubdirs}')
    logging.info(f'Exclude extensions: {copyGroup.excludeExtensions}')
    logging.info(f'Exclude subdirectories: {copyGroup.excludeSubdirs}')
    logging.info(f'Exclude files: {copyGroup.excludeFiles}')
    logging.info(' ')

  return copyGroups

def main():
  argParser = argparse.ArgumentParser()

  argParser.add_argument('-c', '--config', help='Config file (defaults to file-copier.ini in the script directory)', type=str)
  argParser.add_argument('-g', '--debug', help='Debug (logs everything)', action='store_true', default=False)
  argParser.add_argument('-n', '--nocopy', help='Do not do the actual copy', action='store_true', default=False)
  argParser.add_argument('-p', '--print', help='Print the entire list of files to be copied', action='store_true', default=False)
  argParser.add_argument('-q', '--quiet', help='Quiet mode', action='store_true', default=False)
  argParser.add_argument('-v', '--verify', help='Verify that each file was copied', action='store_true', default=False)
  argParser.add_argument('-d', '--deepverify', help='Deep file copy verification (slow)', action='store_true', default=False)

  args = argParser.parse_args()

  noCopy = args.nocopy
  printFiles = args.print

  copyParameters = {}       # Contains parameters for copying
  copyParameters['debug'] = args.debug
  copyParameters['verify'] = args.verify
  copyParameters['deepverify'] = args.deepverify
  copyParameters['quiet'] = args.quiet

  try:
    # console = logging.StreamHandler()   # Use the console logger for debugging
    rotatingFileHandler = RotatingFileHandler(getLogfilePath(), maxBytes=kMaxLogileSize, backupCount=9)
    # logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',
    #                         handlers=[ rotatingFileHandler, console ])    # Use the console logger only for debugging
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',
                            handlers=[ rotatingFileHandler ])

    scriptDir = os.path.dirname(os.path.realpath(__file__))

    logging.info(f' ')
    logging.info(f'**** PyFileCopier starting')

    if copyParameters['debug']:
      logging.debug('***** D E B U G    M O D E *****')

    # First, read the Config file
    iniFilePath, iniFileExists = locateConfigFile(args.config)
    if not iniFileExists:
      raise FileNotFoundError(f'{iniFilePath} not found.')

    copyGroups = readIniFile(iniFilePath, copyParameters)

    for copyGroup in copyGroups:
      # Scan directories to get the list of files to copy
      copyGroup.scanFilesAndDirectories()

    if printFiles:
      # Print them
      for copyGroup in copyGroups:
        copyGroup.printCopyDictList()

    # Do the copy
    if not noCopy:
      logging.info(f'** Starting copy')
      totalFilesCopied = 0

      for copyGroup in copyGroups:
        logging.info(f'Copy group: {copyGroup.copyGroupName}')

        totalFilesCopied += copyGroup.copy()
        logInfoAndPrint(f'Directory {copyGroup.directory}: copied {copyGroup.filesCopied} files, skipped: {copyGroup.filesSkipped}')

      # TODO: Not sure it is necessary to do this as a separate step, since files are verified as they are copied.
      if copyParameters['verify']:
        # Verify that each file was copied
        for copyGroup in copyGroups:
          copyGroup.verify()

      logInfoAndPrint(f'Total Files copied: {totalFilesCopied}')

  except IndexError as inst:
    print(inst)
  except FileNotFoundError as inst:
    print(inst)
  except:
    print('Unexpected error:', sys.exc_info()[0])
    print(traceback.format_exc())


# ---------------------------------------------------------------
if __name__ == "__main__":
    main()
