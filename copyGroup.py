import os.path
from pathlib import Path
import logging

class CopyGroup:
  def __init__(self) -> None:
    self.directory = ''             # Directory path
    self.destDir = ''               # Destination directory
    self.copySubdirs = False
    self.excludeExtensions = []     # File extensions to exclude
    self.excludeSubdirs = []        # Subdirectories to exclude
    self.excludeFiles = []          # List of file names to exclude
    self.copyList = []              # Complete list of file paths to copy

  def printCopyList(self):
    for f in self.copyList:
      print(f)

  def numberOfFilesToCopy(self):
    return len(self.copyList)

  def scanFilesAndDirectories(self) -> None:
    self.copyList = self.__scanFilesAndDirectories(self.directory)

  def __scanFilesAndDirectories(self, directory) -> tuple[list[str], list[str]]:
    """ Scans the directory tree and returns a list of files to copy. """
    directories = []
    files = []
    with os.scandir(directory) as iter:
      for entry in iter:
        if not self.pathContainsAnExcludedSubdir(entry.path):
          if entry.is_file():
            if not self.fileIsAnExcludedFile(entry.name):
              if not self.fileContainsExcludeExtension(entry.name):
                files.append(entry.path)
              else:
                logging.info(f'Excluding {entry.name} because its extension is in the excluded extensions list')
            else:
              logging.info(f'Excluding {entry.name} because it is in the excluded files list')
          else:
            directories.append(entry.path)
        else:
          logging.info(f'Excluding {entry.path} because one of its parents is in the excluded subdirectories list')

    # Recurse subdirectories
    for subdir in directories:
      subdirFiles = self.__scanFilesAndDirectories(subdir)
      files = files + subdirFiles

    return files

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
