# PyFileCopier
A program to copy files.

To run:

`python pyFileCopier.py <args>`

To see command-line argument options:

`python pyFileCopier.py --help`

The list of files to copy can be specified in an INI file.  For a description of the format of the INI file, see Documentation.md

# Virtual Environment

Before installing dependencies, create a virtual environment:

`py -m venv venv\`

Once it's installed, activate it:

`.\venv\Scripts\activate`

# Dependencies

PyInstaller

To install:
`pip install PyInstaller`

# Building the Executable

To build an executable file of this application, ensure the virtual environment is active (see above), and then:

`.\build-exe.ps1`
