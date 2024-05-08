import sys
import os.path
from pathlib import Path
import shutil
import filecmp
import logging
from utils import logErrorAndPrint

class CopyGroup:
  def __init__(self, copyGroupName, copyParameters) -> None:
    self.copyGroupName = copyGroupName
    self.copyParameters = copyParameters
    self._directory = ''            # Directory path
    self.destDir = []               # Destination directory array
    self.copySubdirs = False
    self.excludeExtensions = []     # File extensions to exclude
    self.excludeSubdirs = []        # Subdirectories to exclude
    self.excludeFiles = []          # List of file names to exclude
    self.copyDictList = []          # Array of dictionaries with information about files
    self.filesCopied = 0            # Actual number of files copied
    self.filesSkipped = 0           # Actual number of files excluded

  def printCopyDictList(self):
    for f in self.copyDictList:
      print(self.getSourceFilePath(f))

    print(f'{self.fileCount} files')
    return self.fileCount

  @property
  def directory(self):
    return self._directory

  @directory.setter
  def directory(self, value):
    self._directory = value

  @property
  def fileCount(self):
    return len(self.copyDictList)

  def getSourceFilePath(self, copyDict) -> str:
    """ Gets the source path of the given copy dict. """
    return os.path.join(self._directory, copyDict['parent'], copyDict['name'])

  def getDestFilePath(self, copyDict, destDir) -> str:
    """ Gets the destination path of the given copy dict. """
    return os.path.join(destDir, self.copyGroupName, copyDict['parent'], copyDict['name'])

  def scanFilesAndDirectories(self) -> None:
    self.filesSkipped = 0
    self.copyDictList = self.__scanFilesAndDirectories(self._directory, '')

  def copy(self) -> None:
    """ Copies the files.  If verify is true, the existence of each copied file will be verified. """
    self.filesCopied = 0

    for file in self.copyDictList:
      sourcePath = self.getSourceFilePath(file)

      # Loop over all destination directories in self.destDir
      for destDir in self.destDir:
        destPath = self.getDestFilePath(file, destDir)

        self._copyFile(sourcePath, destPath)

        # Do a quick check to verify if the destination file exists
        self._verifyFile(sourcePath, destPath)

    return self.filesCopied

  def _copyFile(self, sourcePath, destPath):
    """ Copies a single file. """
    # Make sure the destination directory exists
    head, tail = os.path.split(destPath)
    if not os.path.exists(head):
      os.makedirs(head, exist_ok=False)

    try:
      # Before copying, should check if the source and dest files are identical.
      shouldCopyFile = True
      if os.path.exists(destPath):
        shouldCopyFile = not filecmp.cmp(sourcePath, destPath, shallow=True)

      if shouldCopyFile:
        shutil.copy2(sourcePath, destPath, follow_symlinks=False)
        if not self.copyParameters['quiet']:
          print(f'Copied {sourcePath} to {destPath}')

        self.filesCopied += 1
    except:
      logErrorAndPrint(f'Error copying {sourcePath} to {destPath}: {sys.exc_info()[0]}')

  def _verifyFile(self, sourcePath, destPath):
    """ Verifies a copied file. """
    if not os.path.exists(destPath):
      logErrorAndPrint(f'**** FILE {destPath} WAS NOT COPIED')
    else:
      if self.copyParameters['verify'] or self.copyParameters['deepverify']:
        shallow = not self.copyParameters['deepverify']
        if not filecmp.cmp(sourcePath, destPath, shallow=shallow):
          logErrorAndPrint(f'**** FILE {destPath} WAS NOT COPIED')

  def verify(self) -> None:
    """ Goes through the copyDictList and verifies the existence of each copied file. """
    for file in self.copyDictList:
      # Loop over all destination directories in self.destDir
      for destDir in self.destDir:
        destPath = self.getDestFilePath(file, destDir)
        if not os.path.exists(destPath):
          logErrorAndPrint(f'**** FILE {destPath} WAS NOT COPIED')

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
                if self.copyParameters['debug']:
                  logging.debug(f'Excluding {entry.name} because its extension is in the excluded extensions list')
                self.filesSkipped += 1
            else:
              if self.copyParameters['debug']:
                logging.debug(f'Excluding {entry.name} because it is in the excluded files list')
              self.filesSkipped += 1
          else:
            directories.append(entry.name)
        else:
          if self.copyParameters['debug']:
            logging.debug(f'Excluding {entry.path} because one of its parents is in the excluded subdirectories list')
          self.filesSkipped += 1      # Not accurate, as we don't count the files in this directory that we are skipping

    # Recurse subdirectories
    if self.copySubdirs:
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
