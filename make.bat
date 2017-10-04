@echo off


if [%1] == []                goto main
if "%~1" == "install-dev"    goto install-dev
if "%~1" == "gui"            goto gui
if "%~1" == "docs"           goto docs
if "%~1" == "venv"           goto venv
if "%~1" == "venvclean"      goto venvclean
if "%~1" == "test"           goto test
if "%~1" == "release"        goto release
if "%~1" == "clean"          goto clean
if "%~1" == "help"           goto help
goto :error %*

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
    echo Converting Qt5 .ui files located in the ./ui path into .py files:
    for %%f in (
     ui/*.ui ) do (
        echo     %%~nf
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
	call venv\Scripts\activate.bat
goto :eof

:venv
    if exist "venv" echo "%CD%\venv" folder already exists. To activate virtualenv, use venv\Scripts\activate.bat & goto :eof

    echo Creating a local virtualenv in "%CD%\venv"
    setlocal

    REM Create a new virtualenv in the venv path
    py -m venv venv

    REM activate the virtualenv
    call venv\Scripts\activate.bat

    REM Install development requirements inside the newly created virtualenv
    pip install -r requirements.txt
    endlocal
goto :eof

:venvclean
    if exist "venv" echo removing venv & RD /S /Q venv
goto :eof

:docs
    echo Creating docs
    setlocal

    REM if the virtualenv doesn't already exists, create it first
    if exist "venv" call venv\Scripts\activate.bat

    REM Use the custom build_sphinx target to generate the documentations
    python setup.py build_sphinx

    endlocal
goto :eof

:release
    echo Creating standalone release

    setlocal
    set "VSCMD_START_DIR=%CD%"

    REM if the virtualenv doesn't already exists, create it first
    if not exist "venv" call :venv

    REM Load the virtualenv
    if exist "venv" call venv\Scripts\activate.bat

    REM Run with the x64 environment
    call "%vs140comntools%..\..\VC\vcvarsall.bat" x86_amd64

    REM install required Nuget packages
    nuget install windows_build\packages.config -OutputDirectory build\nugetpackages

    REM Run the MSBuild script for creating the msi
    MSBuild release.pyproj /nologo /t:msi /p:ProjectRoot="%CD%
    endlocal

goto :eof

:clean
    setlocal
	if exist "venv" call venv\Scripts\activate.bat
    python setup.py clean --all
    
    REM Run with the x64 environment
    set "VSCMD_START_DIR=%CD%"
    call "%vs140comntools%..\..\VC\vcvarsall.bat" x86_amd64
    MSBuild /nologo release.pyproj /t:Clean /p:ProjectRoot=%CD%

    REM Delete any nugetpackages used to build a standalone release
    if exist "build\nugetpackages" (
        echo Deleting local nuget packages
        rmdir /s /q build\nugetpackages
    )

    REM Remove any generated documentation
    if exist "docs\build\" (
        echo Deleting generated package documentation
        rmdir /s /q docs\build
    )

    endlocal
goto :eof

:error
    echo Unknown option: %*
    call :help
goto :eof