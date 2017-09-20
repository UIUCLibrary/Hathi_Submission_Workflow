@echo off


if [%1] == []               goto main
if "%1" == "install-dev"    goto install-dev
if "%1" == "gui"            goto gui
if "%1" == "docs"           goto docs
if "%1" == "venv"           goto venv
if "%1" == "venvclean"      goto venvclean
if "%1" == "test"           goto test
if "%1" == "release"        goto release
if "%1" == "clean"          goto clean
if "%1" == "help"           goto help

EXIT /B 0

:main
    call :install-dev
    call :gui
goto :eof

:help
    echo Available options:
    echo     make install-dev       Installs the development requirements into active python environment
    echo     make venv              Creates a virtualenv with development requirements
    echo     make venvclean         Removes the generated virtualenv
    echo     make gui               Generates GUI source for all .ui files in the ./ui directory
    echo     make docs              Generates html documentation into the docs/build/html directory
    echo     make test              Runs tests
    echo     make release           Creates a Windows Release build
    echo     make clean             Removes generated files
goto :eof

:gui
setlocal
    echo Converting Qt .ui files into Python files
    for %%f in (
     ui/*.ui ) do (
        echo  %%~nf
        pyuic5 ui\%%f -o hsw\ui\%%~nf.py

    )
endlocal
goto :eof

:install-dev
    echo Installing development requirements
    pip install -r requirements.txt
goto :eof

:test
    python setup.py test
goto :eof

:venvactivate
	call .env\Scripts\activate.bat
goto :eof

:venv
    if exist ".env" echo "%CD%\.env" folder already exists. To activate virtualenv, use .env\Scripts\activate.bat & goto :eof
    echo Creating a local virtualenv in "%CD%\.env"
    setlocal
    py -m venv .env
    call .env\Scripts\activate.bat
    pip install -r requirements.txt
    endlocal
goto :eof

:venvclean
    if exist ".env" echo removing .env & RD /S /Q .env
goto :eof

:docs
    echo Creating docs
    setlocal
    if exist ".env" call .env\Scripts\activate.bat
    python setup.py build_sphinx
    endlocal
goto :eof

:release
    echo Creating standalone release
    setlocal
    set "VSCMD_START_DIR=%CD%"
    if not exist ".env" call :venv
    REM call "C:\Program Files (x86)\Microsoft Visual Studio\2017\Community\VC\Auxiliary\Build\vcvarsall.bat" x86_amd64
    if exist ".env" call .env\Scripts\activate.bat
    call "%vs140comntools%..\..\VC\vcvarsall.bat" x86_amd64
    nuget install windows_build\packages.config -OutputDirectory build\nugetpackages
    MSBuild release.pyproj /t:msi /p:ProjectRoot="%CD%
    endlocal

goto :eof

:clean
    echo Calling clean for Python
    setlocal
	if exist ".env" call .env\Scripts\activate.bat
    python setup.py clean --all
    
    set "VSCMD_START_DIR=%CD%"
    call "%vs140comntools%..\..\VC\vcvarsall.bat" x86_amd64
    MSBuild release.pyproj /t:Clean /p:ProjectRoot=%CD%
    endlocal
goto :eof