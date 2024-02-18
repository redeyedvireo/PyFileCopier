# This wraps PyFileCopier into an executable file.

$arguments = 'cli.py',
             '--noconfirm',
             '--clean',
             '--name',
             'pyFileCopier',
             '--onefile'



pyinstaller $arguments 2>&1 > .\pyinstaller-build.log

# Zip the output directory
# 7z a -tzip dist\pyrss.zip dist\pyrss