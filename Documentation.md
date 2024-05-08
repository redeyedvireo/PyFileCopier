# Copy Config File Structure

The `file-copier.ini` file is an INI file where each section (in '[' ']') represents a *copy group*.

The possible members of each copy group are:

`directory` Source directory

`destDir` Comma-separated list of destination directories.  The name of the copy group will be at the root directory of the copied files.  Do not use spaces after a comma.

`copySubdirs` Whether to copy files in subdirectories of `directory`.

`excludeExtensions` Comma-separated list of file extensions to exclude from copying.  Do not use spaces after a comma.

`excludeSubdirs` Comma-separated list of subdirectory names to exclude from copying.  Do not use spaces after a comma.

A semi-colon at the beginning of a line is a comment; such lines are ignored.

### Example `file-copier.ini` file:

```
; This comment line is ignored.

[Temp]
directory: d:\temp
destDir: d:\TempCopyDest
copySubdirs: True
excludeExtensions: dll,exe,wav,mp3,mov
excludeSubdirs: temp2,scratch,Virtual Active Usb Sticks
excludeFiles: thumbs.txt,deleteme.txt

[Udemy]
directory: d:\Udemy
destDir: d:\TempCopyDest
copySubdirs: True
excludeExtensions: dll,exe
excludeSubdirs: node_modules,.parcel-cache,html-css,auth-graphql-starter
excludeFiles: package-lock.json

```