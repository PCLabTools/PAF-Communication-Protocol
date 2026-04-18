@echo off
echo Running unit tests for communication module...

REM Change to the project root directory
cd /d "%~dp0.."

REM Run the tests using Python's unittest with package loading
python -c "import sys; sys.path.insert(0, '.'); import importlib.util; spec = importlib.util.spec_from_file_location('pkg', '__init__.py'); pkg = importlib.util.module_from_spec(spec); sys.modules['pkg'] = pkg; spec.loader.exec_module(pkg); sys.modules['protocol'] = pkg.protocol; sys.modules['message'] = pkg.message; sys.modules['module'] = pkg.module; import unittest; unittest.main(module=None, argv=['unittest', 'discover', '-s', 'tests', '-t', '.', '-v'])"

REM Check the exit code
if %errorlevel% equ 0 (
    echo All tests passed!
) else (
    echo Some tests failed!
)

REM Check the exit code
if %errorlevel% equ 0 (
    echo All tests passed!
) else (
    echo Some tests failed!
)
