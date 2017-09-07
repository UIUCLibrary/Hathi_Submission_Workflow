@echo off


if [%1] == []               goto main
if "%1" == "install-dev"    goto install-dev
if "%1" == "gui"            goto gui
if "%1" == "test"           goto test
if "%1" == "release"        goto release
EXIT /B 0

:main
    call :install-dev
    call :gui
goto :eof
if
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

:release
    echo Creating standalone release
    setlocal
    set "VSCMD_START_DIR=%CD%"
    call "C:\Program Files (x86)\Microsoft Visual Studio\2017\Community\VC\Auxiliary\Build\vcvarsall.bat" x86_amd64
    REM call "%vs140comntools%..\..\VC\vcvarsall.bat" x86_amd64
    REM nuget install packages.config
    MSBuild make.proj
    endlocal

goto :eof