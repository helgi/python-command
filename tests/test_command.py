import sys
import os
from os.path import join, realpath, dirname, exists

try:
    import command
except ImportError:
    print('Unable to import command.  Is it installed?')
    sys.exit(1)

try:
    import py.test
except ImportError:
    print('Unable to import py.test.  Is py.test installed?')
    sys.exit(1)

# figure out the base path to use for file include
test_path = realpath(dirname(__file__))

class TestCommand:
    def test_executable_exists_bin_sleep(self):
        command.executable_exists('/bin/sleep')

    def test_executable_exists_foo(self):
        with py.test.raises(command.CommandException):
            command.executable_exists('foo')

    def test_executable_exists_full_foo(self):
        with py.test.raises(command.CommandException):
            command.executable_exists('/bin/foo')

    def test_executable_exists_not_x(self):
        with py.test.raises(command.CommandException):
            command.executable_exists('/etc/hosts')

    def test_executable_exists_relative_false(self):
        command.executable_exists('false')

    def test_executable_exists_none(self):
        with py.test.raises(command.CommandException):
            command.executable_exists(None)

    def test_run_ls(self):
        response = command.run(['ls', test_path])
        assert response.exit == 0
        assert response.output == """__pycache__
test_command.py"""

    def test_run_failure(self):
        with py.test.raises(command.CommandException):
            command.run(['ls', 'blahblah'])

    def test_run_timeout_successs(self):
        command.run(['sleep', '1'], timeout=10)

    def test_run_timeout_failure(self):
        with py.test.raises(command.CommandException):
            command.run(['sleep', '2'], timeout=1)