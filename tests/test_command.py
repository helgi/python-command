from __future__ import print_function
import sys
import os
from os.path import realpath, dirname

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
    def test_which_bin_sleep(self):
        command.which('/bin/sleep')

    def test_which_bin_sleep2(self):
        assert command.which('sleep') == '/bin/sleep'


    def test_which_foo(self):
        with py.test.raises(command.CommandException):
            command.which('foo')

    def test_which_full_foo(self):
        with py.test.raises(command.CommandException):
            command.which('/bin/foo')

    def test_which_not_x(self):
        with py.test.raises(command.CommandException):
            command.which('/etc/hosts')

    def test_which_relative_false(self):
        command.which('false')

    def test_which_none(self):
        with py.test.raises(command.CommandException):
            command.which(None)

    def test_run_ls(self):
        response = command.run(['ls', test_path])
        assert response.exit == 0
        assert response.output == b"""\
__pycache__
test_command.py"""

    def test_run_failure(self):
        with py.test.raises(command.CommandException):
            command.run(['ls', 'blahblah'])

    def test_run_timeout_successs(self):
        command.run(['sleep', '1'], timeout=10)

    def test_run_timeout_failure(self):
        with py.test.raises(command.CommandException):
            command.run(['sleep', '2'], timeout=1)

    def test_run_debug(self, capsys):
        def debug_print(line):
            print(line)

        response = command.run(['ls', test_path], debug=debug_print)
        out, err = capsys.readouterr()

        assert response.exit == 0
        assert response.output == b"""\
__pycache__
test_command.py"""

        # Pyton 2 vs 3 handles strings in different ways
        if sys.version_info[0] is 2:
            assert out == b"""\
__pycache__
test_command.py
"""
        elif sys.version_info.major is 3:
            assert out == "b'__pycache__'\nb'test_command.py'\n"

        assert err == ''