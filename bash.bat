REM this script is the entry point to the cli-utils, on windows
REM date: 20191112
REM 
REM this script creates a "bin" folder in the user's private folder, if it
REM   doesn't yet exist
REM
REM if run from a location outside the above "bin" folder, the codes will 
REM be copied over from the present folder
REM
REM Moreover, the program sets up a .bash_profile for the cygwin home for
REM the user
REM
REM by default, the script creates and navigates to a temporary ssd-based
REM folder
REM
REM can type "tmp" at the prompt to navigate there, and can type "bin" at
REM the prompt to navigate back to the "bin" folder 

IF EXIST R:\%USERNAME%\bin (
  echo "bin folder already existed"
  ) ELSE (
  echo "bin folder didn't already exist.. creating"
  mkdir R:\%USERNAME%\bin
)

IF EXIST "%cd%\bash.bat" (
  echo "found bash.bat"
  IF EXIST "%cd%\setup.sh" (
    echo "we're in a folder with expected data, go ahead and copy if not yet in main bin folder"

    IF "%cd%" == "R:\%USERNAME%\bin" (
      echo "we are in the bin folder"
    ) ELSE (
      echo "we're outside the bin folder.. copying"
      xcopy %cd% R:\%USERNAME%\bin /S /Y
    )
    echo ""

  ) ELSE (
    echo ""
  )

  echo ""
  ) ELSE (
    echo ""
)

@echo off
R:
chdir R:\%USERNAME%\bin\
C:
cp R:\%USERNAME%\bin\bash_profile C:\cygwin64\home\%USERNAME%\.bash_profile
chdir C:\cygwin64\bin
bash --login -i
