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

def readIniFile(iniFilePath):
  """ Reads the INI file.
      Returns: ?
  """
  config = ConfigParser()

  config.read(iniFilePath)

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

    print(f'{copyGroup.directory}')
    print(f'{copyGroup.destDir}')
    print(f'{copyGroup.copySubdirs}')
    print(f'{copyGroup.excludeExtensions}')
    print(f'{copyGroup.excludeSubdirs}')
    print(f'{copyGroup.excludeFiles}')
    print()
  return ''


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

    fileListObj = readIniFile(iniFilePath)

  # Test: list files in directory:
    files = os.listdir(r'\\almond\HardDrive')
    print(r'Files in \\almond\HardDrive:')
    for f in files:
      print(f)

  except IndexError as inst:
    print(inst)
  except FileNotFoundError as inst:
    print(inst)
  except:
    print('Unexpected error:', sys.exc_info()[0])
