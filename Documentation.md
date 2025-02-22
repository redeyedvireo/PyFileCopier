# Copy Config File Structure

The `file-copier.ini` file is an INI file where each section (in '[' ']') represents a *copy group*.

The possible members of each copy group are:

 - `directory` Source directory

- `files` A multi-line list of files to copy.  If this is specified, only these files will be copied, rather then the entire directory.  Also, the `copySubdirs` parameter is ignored (subdirectories will not be copied.)  The second and following lines must be indented.

- `destDir` Destination directory.  The name of the copy group will be at the root directory of the copied files.  *Note: this only supports a single directory.  A comma-separated list of directories is no longer supported.*

- `copySubdirs` Whether to copy files in subdirectories of `directory`.

- `excludeFiles` Comma-separated list of files to exclude from copying.  Do not use spaces after a comma.

- `excludeExtensions` Comma-separated list of file extensions to exclude from copying.  Do not use spaces after a comma.

- `excludeSubdirs` Comma-separated list of subdirectory names to exclude from copying.  Do not use spaces after a comma.

- `fileExcludeSubstrings` **Not yet implemented** A comma-separated list of substrings.  Do not use spaces after a comma.  If any of these substrings is found in a file, the file will be skipped.

- `directoryExcludeSubstrings` **Not yet implemented** A comma-separated list of substrings.  Do not use spaces after a comma.  If any of these substrings is found in a directory, the file will be skipped.

A semi-colon or hashtag (#) at the beginning of a line is a comment; such lines are ignored.

It is also possible to speciy global copy parameters, in the `GlobalCopyParams` section.  This section is completely optional.  Individual copy groups can override some of the parameters specified in this section.

Parameters that can be specified in this section are:

- `destinationDirectory` - The destination directory for the entire copy operation.  Individual copy groups can override this.
- `dateRoot` - Indicates whether to create a subdirectory under the root directory indicating the date at which the copy was made.  Defaults to false.

### Example `file-copier.ini` file:

```
; This comment line is ignored.

[GlobalCopyParams]
destinationDirectory: d:\CopyFilesHere
dateRoot: True

[Temp]
directory: d:\temp
destDir: d:\TempCopyDest
copySubdirs: True
excludeExtensions: dll,exe,wav,mp3,mov
excludeSubdirs: temp2,scratch,Virtual Active Usb Sticks
excludeFiles: thumbs.txt,deleteme.txt
fileExcludeSubstrings: skipme,log.
directoryExcludeSubstrings: distro,logs

[Udemy]
directory: d:\Udemy
destDir: d:\TempCopyDest
copySubdirs: True
excludeExtensions: dll,exe
excludeSubdirs: node_modules,.parcel-cache,html-css,auth-graphql-starter
excludeFiles: package-lock.json

[Documents]
directory: c:\My Documents
files: An Important File.doc
  Copy Me too.txt
  Don't forget me.xls
destDir: d:\TempCopyDest
```