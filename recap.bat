@echo off
REM Recap CLI - Windows batch wrapper
REM Place this file in a directory that's in your PATH to use 'recap' command globally
REM Or run from the recap folder directly

python "%~dp0main.py" %*
