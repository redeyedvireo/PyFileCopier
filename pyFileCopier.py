# This is a Python version of FileCopier, though this version is intended to be a command-line
# utility, rather than a UI application.  A UI may be added later.

import sys
import os.path
import os
import argparse
from configparser import ConfigParser

gIniFileName = 'file-copier.ini'

class CopyGroup:
  def __init__(self) -> None:
    self.directory = ''             # Directory path
    self.destDir = ''               # Destination directory
    self.copySubdirs = False
    self.excludeExtensions = []     # File extensions to exclude
    self.excludeSubdirs = []        # Subdirectories to exclude
    self.excludeFiles = []          # List of file names to exclude

def readIniFile(iniFilePath) -> list[CopyGroup]:
  """ Reads the INI file.
      Returns: An array of CopyGroups
  """
  config = ConfigParser()

  config.read(iniFilePath)

  copyGroups = []

  print('Copy Groups:')
  sections = config.sections()

  for section in sections:
    print(section)
    copyGroup = CopyGroup()
    copyGroup.directory = config.get(section, 'directory', fallback='')
    copyGroup.destDir = config.get(section, 'destDir', fallback='')
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

    copyGroups.append(copyGroup)

    print(f'{copyGroup.directory}')
    print(f'{copyGroup.destDir}')
    print(f'{copyGroup.copySubdirs}')
    print(f'{copyGroup.excludeExtensions}')
    print(f'{copyGroup.excludeSubdirs}')
    print(f'{copyGroup.excludeFiles}')
    print()

  return copyGroups

"""
  Scans the directory tree and returns a tuple consisting of:
    - array of directory paths
    - array of file paths
"""
def scanFilesAndDirectories(directory: str) -> tuple[list[str], list[str]]:
  directories = []
  files = []
  with os.scandir(directory) as iter:
    for entry in iter:
      if entry.is_file():
        files.append(entry.path)
      else:
        directories.append(entry.path)

  # Recurse subdirectories
  newSubdirs = []
  for subdir in directories:
    (subdirs, subdirFiles) = scanFilesAndDirectories(subdir)
    newSubdirs = newSubdirs + subdirs
    files = files + subdirFiles

  directories = directories + newSubdirs
  return (directories, files)


# ------------------ Start ------------------
if __name__ == "__main__":
  scriptDir = os.path.dirname(os.path.realpath(__file__))
  argParser = argparse.ArgumentParser()

  argParser.add_argument('-c', '--config', help='Location of the config file', type=str)

  args = argParser.parse_args()

  try:
    # First, read the Config file

    # If not supplied by the user, assume the INI file is in the same directory as this script.
    iniFilePath = os.path.join(scriptDir, gIniFileName)

    if args.config is not None and len(args.config) > 0:
      # User supplied a path to the Config file.  Use this instead.
      iniFilePath = args.config

    # Make sure the Config file can be found
    if not os.path.exists(iniFilePath):
      raise FileNotFoundError('Config file not found.')

    copyGroups = readIniFile(iniFilePath)

    # Test: list files in directory of first copy group:
    directories, files = scanFilesAndDirectories(copyGroups[0].directory)
    # Print them
    print('DIRECTORIES')
    for f in directories:
      print(f)

    print()
    print('FILES')
    for f in files:
      print(f)

  except IndexError as inst:
    print(inst)
  except FileNotFoundError as inst:
    print(inst)
  except:
    print('Unexpected error:', sys.exc_info()[0])
