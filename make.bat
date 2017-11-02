@echo off


if [%1] == []                call:main          && goto:eof
if "%~1" == "install-dev"    call:install-dev   && goto:eof
if "%~1" == "gui"            call:gui           && goto:eof
if "%~1" == "docs"           call:docs %EXTRA_ARGS%     && goto:eof
if "%~1" == "venv"           call:venv          && goto:eof
if "%~1" == "venvclean"      call:venvclean     && goto:eof
if "%~1" == "test"           call:test          && goto:eof
if "%~1" == "wheel"          call:wheel         && goto:eof
if "%~1" == "sdist"          call:sdist         && goto:eof
if "%~1" == "release"        call:release       && goto:eof
if "%~1" == "clean"          call:clean         && goto:eof
if "%~1" == "help"           call:help          && goto:eof

if not %ERRORLEVEL% == 0 exit /b %ERRORLEVEL%
goto :error %*

EXIT /B 0

:main
    :: call:install-dev
    call:gui
    call:sdist
    call:wheel
    call:docs --build-dir dist/docs
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
    call:install-dev
    setlocal
    echo Converting Qt5 .ui files located in the ./ui path into .py files:
    for %%f in (
     ui/*.ui ) do (
        echo     %%~nf
        pyuic5 ui\%%f -o hsw\ui\%%~nf.py

    )
    endlocal
goto :eof

::=============================================================================
:: Setup a development environment
::=============================================================================
:install-dev
    call:venv
    setlocal
    echo Installing development requirements
    call venv\Scripts\activate.bat
    pip install -r requirements-dev.txt --upgrade-strategy only-if-needed
    pip install -r requirements.txt --upgrade-strategy only-if-needed
    endlocal
goto :eof


::=============================================================================
:: Run unit tests
::=============================================================================
:test
    call:install-dev
    setlocal
    call venv\Scripts\activate.bat && python setup.py test
    endlocal
goto :eof

:venvactivate
	call venv\Scripts\activate.bat
goto :eof


::=============================================================================
:: Build a virtualenv sandbox for development
::=============================================================================
:venv
    if exist "venv" echo "%CD%\venv" folder already exists. To activate virtualenv, use venv\Scripts\activate.bat & goto :eof

    echo Creating a local virtualenv in "%CD%\venv"
    setlocal

    REM Create a new virtualenv in the venv path
    py -m venv venv
    endlocal
goto :eof


::=============================================================================
:: Remove virtualenv sandbox
::=============================================================================
:venvclean
    if exist "venv" echo removing venv & RD /S /Q venv
goto :eof

::=============================================================================
:: Build html documentation
::=============================================================================
:docs
    call:install-dev
    echo Creating docs
    setlocal
    call venv\Scripts\activate.bat && python setup.py build_sphinx %*
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

::=============================================================================
:: Create a wheel distribution
::=============================================================================
:wheel
    call:install-dev
    setlocal
    call venv\Scripts\activate.bat && python setup.py bdist_wheel
    endlocal
goto :eof


::=============================================================================
:: Create a source distribution
::=============================================================================
:sdist
    call:install-dev
    setlocal
    call venv\Scripts\activate.bat && python setup.py sdist
    endlocal
goto :eof

::=============================================================================
:: Clean up any generated files
::=============================================================================
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