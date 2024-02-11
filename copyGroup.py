import sys
import os.path
from pathlib import Path
import shutil
import logging

class CopyGroup:
  def __init__(self) -> None:
    self.directory = ''             # Directory path
    self.destDir = ''               # Destination directory
    self.copySubdirs = False
    self.excludeExtensions = []     # File extensions to exclude
    self.excludeSubdirs = []        # Subdirectories to exclude
    self.excludeFiles = []          # List of file names to exclude
    self.copyDictList = []          # Array of dictionaries with information about files

  def printCopyDictList(self):
    for f in self.copyDictList:
      print(f)

  def numberOfFilesToCopy(self):
    return len(self.copyDictList)

  def scanFilesAndDirectories(self) -> None:
    self.copyDictList = self.__scanFilesAndDirectories(self.directory, '')

  def copy(self, verify=False) -> None:
    """ Copies the files.  If verify is true, the existence of each copied file will be verified. """
    for file in self.copyDictList:
      sourcePath = os.path.join(self.directory, file['parent'], file['name'])
      destPath = os.path.join(self.destDir, file['parent'], file['name'])
      logging.info(f'Copying {sourcePath} to {destPath}')

      # Make sure the destination directory exists
      head, tail = os.path.split(destPath)
      if not os.path.exists(head):
        os.makedirs(head, exist_ok=False)

      try:
        shutil.copyfile(sourcePath, destPath, follow_symlinks=False)
      except:
        print('Unexpected error:', sys.exc_info()[0])

      if verify:
        if not os.path.exists(destPath):
          print(f'**** FILE {destPath} WAS NOT COPIED')
          logging.error(f'**** FILE {destPath} WAS NOT COPIED')

  def verify(self) -> None:
    """ Goes through the copyDictList and verifies the existence of each copied file. """
    for file in self.copyDictList:
      destPath = os.path.join(self.destDir, file['parent'], file['name'])
      if not os.path.exists(destPath):
        print(f'**** FILE {destPath} WAS NOT COPIED')
        logging.error(f'**** FILE {destPath} WAS NOT COPIED')

  def __scanFilesAndDirectories(self, directory: str, relativeToRoot: str) ->list[dict]:
    """ Scans the directory tree and returns a list of files to copy.
        Returns an array of dictionaries, where each dictionary is of the form:
          name: file name
          parent: parent directory, relative to the source directory
    """
    directories = []
    files = []
    copyDicts = []
    with os.scandir(directory) as iter:
      for entry in iter:
        if not self.pathContainsAnExcludedSubdir(entry.path):
          if entry.is_file():
            if not self.fileIsAnExcludedFile(entry.name):
              if not self.fileContainsExcludeExtension(entry.name):
                files.append(entry.path)
                copyDicts.append({ 'name': entry.name, 'parent': relativeToRoot})
              else:
                logging.info(f'Excluding {entry.name} because its extension is in the excluded extensions list')
            else:
              logging.info(f'Excluding {entry.name} because it is in the excluded files list')
          else:
            directories.append(entry.name)
        else:
          logging.info(f'Excluding {entry.path} because one of its parents is in the excluded subdirectories list')

    # Recurse subdirectories
    for subdir in directories:
      subdirPath = os.path.join(directory, subdir)
      subdirDicts = self.__scanFilesAndDirectories(subdirPath, os.path.join(relativeToRoot, subdir))
      copyDicts = copyDicts + subdirDicts

    return copyDicts

  def pathContainsAnExcludedSubdir(self, path: str) -> bool:
    """ Returns whether the path contains the given subdirectory. """
    head, tail = os.path.split(path)      # Tail is the file name
    pathObj = Path(head)
    parts = pathObj.parts
    for subdir in self.excludeSubdirs:
      if subdir in parts:
        return True

    return False

  def fileIsAnExcludedFile(self, fileName: str) -> bool:
    """ Returns whether the fileName is an excluded file. """
    for file in self.excludeFiles:
      if file == fileName:
        return True

    return False

  def fileContainsExcludeExtension(self, fileName: str) -> bool:
    """ Determines if the given file's extension is contained in the given list of extensions. """
    root, extWithPeriod = os.path.splitext(fileName)

    ext = extWithPeriod[1:]

    for extension in self.excludeExtensions:
      if extension == ext:
        return True

    return False
