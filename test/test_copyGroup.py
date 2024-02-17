import unittest
from pyFileCopier.copyGroup import CopyGroup

class TestCopyGroup(unittest.TestCase):
  def setUp(self) -> None:
    self.copyGroup = CopyGroup()
    self.copyGroup.directory = 'd:\\temp'
    self.copyGroup.destDir = 'd:\\dest'
    self.copyGroup.copySubdirs = True
    self.copyGroup.excludeExtensions = [ 'txt', 'exe' ]
    self.copyGroup.excludeSubdirs = [ 'node_modules' ]
    self.copyGroup.excludeFiles = [ 'package-lock.json' ]
    return super().setUp()

  def tearDown(self) -> None:
    return super().tearDown()

  def test_fileContainsExcludeExtension(self):
    result = self.copyGroup.fileContainsExcludeExtension('somefile.txt')
    self.assertTrue(result)

  def test_fileContainsExcludeExtension_2(self):
    result = self.copyGroup.fileContainsExcludeExtension('somefile.ok')
    self.assertFalse(result)

  def test_fileIsAnExcludedFile(self):
    result = self.copyGroup.fileIsAnExcludedFile('package-lock.json')
    self.assertTrue(result)

  def test_fileIsAnExcludedFile_2(self):
    result = self.copyGroup.fileIsAnExcludedFile('goodFile.good')
    self.assertFalse(result)

  def test_pathContainsAnExcludedSubdir(self):
    result = self.copyGroup.pathContainsAnExcludedSubdir('c:\\src\\myproj\\node_modules\\thing')
    self.assertTrue(result)

  def test_pathContainsAnExcludedSubdir_2(self):
    result = self.copyGroup.pathContainsAnExcludedSubdir('c:\\src\\myproj\\src\\app')
    self.assertFalse(result)


if __name__ == '__main__':
  unittest.main()
