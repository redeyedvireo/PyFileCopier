import sys
import os.path
from pathlib import Path
import shutil
import filecmp
import logging
import datetime
from globalCopyParams import GlobalCopyParams
from utils import logErrorAndPrint

class CopyGroup:
  def __init__(self, copyGroupName: str, copyParameters: dict, globalCopyParams: GlobalCopyParams) -> None:
    self.copyGroupName = copyGroupName
    self.copyParameters = copyParameters
    self.globalCopyParams = globalCopyParams
    self._directory = ''            # Directory path
    self.destDir: None | str = None              # Destination directory.  If present, this overrides the global destination directory
    self.individualFiles = []       # Individual files (don't copy the entire directory if this is non-empty)
    self.copySubdirs = False
    self.noPreserveDirectoryStructure = False   # If true, all files will be copied directly to the destination directory
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

  def getDestFilePath(self, copyDict: dict):
    """ Gets the destination path of the given copy dict. """
    # First, see if this copy group has a destDir; if so, this will override the one in the GlobalCopyParams
    if self.destDir is not None:
      destDir = self.destDir
    else:
      destDir = self.globalCopyParams.destinationDir

    if destDir is None:
      logging.error(f'[getDestFilePath] Destination directory from both copy group and global are unspecified')
      # If both self.destDir and self.globalCopyParams.destinationDir are None, then return None, as there is no destination directory
      return None

    if self.globalCopyParams.dateRoot:
      dateStr = datetime.date.today().strftime('%Y-%m-%d')
      if self.noPreserveDirectoryStructure:
        return os.path.join(destDir, dateStr, self.copyGroupName, copyDict['name'])
      else:
        return os.path.join(destDir, dateStr, self.copyGroupName, copyDict['parent'], copyDict['name'])
    else:
      if self.noPreserveDirectoryStructure:
        return os.path.join(destDir, self.copyGroupName, copyDict['name'])
      else:
        return os.path.join(destDir, self.copyGroupName, copyDict['parent'], copyDict['name'])

  def scanFilesAndDirectories(self) -> None:
    if len(self.individualFiles) > 0:
      self._addIndividualFiles()
    else:
      self.filesSkipped = 0
      self.copyDictList = self.__scanFilesAndDirectories(self._directory, '')

  def copy(self) -> None:
    """ Copies the files.  If verify is true, the existence of each copied file will be verified. """
    self.filesCopied = 0

    for file in self.copyDictList:
      sourcePath = self.getSourceFilePath(file)

      destPath = self.getDestFilePath(file)

      if destPath is None:
        logErrorAndPrint(f'** FILE {sourcePath} WAS NOT COPIED - no destination path specified')
        continue

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
        copyMessage = f'Copied {sourcePath} to {destPath}'
        if self.copyParameters['verbose']:
          print(copyMessage)

        # Log the file copied regardless of the quiet setting
        logging.info(copyMessage)

        self.filesCopied += 1
    except:
      logErrorAndPrint(f'Error copying {sourcePath} to {destPath}: {sys.exc_info()[0]}')

  def _verifyFile(self, sourcePath, destPath):
    """ Verifies a copied file. """
    if not os.path.exists(destPath):
      logErrorAndPrint(f'** FILE {destPath} WAS NOT COPIED')
    else:
      if self.copyParameters['verify'] or self.copyParameters['deepverify']:
        shallow = not self.copyParameters['deepverify']
        if not filecmp.cmp(sourcePath, destPath, shallow=shallow):
          logErrorAndPrint(f'** FILE {destPath} WAS NOT COPIED')

  def verify(self) -> None:
    """ Goes through the copyDictList and verifies the existence of each copied file. """
    for file in self.copyDictList:
      destPath = self.getDestFilePath(file)
      if not os.path.exists(destPath):
        logErrorAndPrint(f'** FILE {destPath} WAS NOT COPIED')

  def __scanFilesAndDirectories(self, directory: str, relativeToRoot: str) ->list[dict]:
    """ Scans the directory tree and returns a list of files to copy.
        Returns an array of dictionaries, where each dictionary is of the form:
          name: file name
          parent: parent directory, relative to the source directory
    """
    directories = []
    copyDicts = []

    if not os.path.exists(directory):
      logErrorAndPrint(f'** {directory} DOES NOT EXIST')
      return []

    with os.scandir(directory) as iter:
      for entry in iter:
        if not self.pathContainsAnExcludedSubdir(entry.path):
          if entry.is_file():
            if not self.fileIsAnExcludedFile(entry.name):
              if not self.fileContainsExcludeExtension(entry.name):
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

  def _addIndividualFiles(self) -> None:
    self.copyDictList =[]

    for file in self.individualFiles:
      self.copyDictList.append({ 'name': file, 'parent': ''})
