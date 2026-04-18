@echo off
echo Running unit tests for communication module...

REM Change to the project root directory
cd /d "%~dp0..\..\.."

REM Run the tests using Python's unittest module with full module paths
python -m unittest src.communication.tests.test_message src.communication.tests.test_protocol src.communication.tests.test_module -v

REM Check the exit code
if %errorlevel% equ 0 (
    echo All tests passed!
) else (
    echo Some tests failed!
)

pause