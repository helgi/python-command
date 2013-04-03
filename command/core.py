# -*- coding: utf-8 -*-
"""
The MIT License

Copyright (c) 2013 Helgi Þorbjörnsson

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import subprocess
import time
import os
from os.path import isfile, split, join
import tempfile
import threading


class Command(object):
    @classmethod
    def run(cls, command, timeout=None, cwd=None, env=None, debug=None):
        """
        Runs a given command on the system within a set time period, providing an easy way to access
        command output as it happens without waiting for the command to finish running.

        :type list
        :param command: Should be a list that contains the command that should be ran on the given
                        system. The only whitespaces that can occur is for paths that use a backslash
                        to escape it appropriately

        :type int
        :param timeout: Specificed in seconds. If a command outruns the timeout then the command and
                        its child processes will be terminated. The default is to run

        :type string
        :param cwd: If cwd is set then the current directory will be changed to cwd before it is executed.
                    Note that this directory is not considered when searching the executable, so you
                    can’t specify the program’s path relative to cwd.

        :type dict
        :param env: A dict of any ENV variables that should be combined into the OS ENV that will help
                    the command to run successfully. Note that more often than not the command run
                    does not have the same ENV variables available as your shell by default and as such
                    require some assistance.

        :type function
        :param debug: A function (also a class function) can be passed in here and all output, line by line,
                      from the command being run will be passed to it as it gets outputted to stdout.
                      This allows for things such as logging (using the built in python logging lib)
                      what is happening on long running commands or redirect output of a tail -f call
                      as lines get outputted without having to wait till the command finishes.

        :return returns :class:`Command.Response` that contains the exit code and the output from the command
        """

        # Merge together the system ENV details and the passed in ones if any
        environ = dict(os.environ)
        environ.update(env or {})

        # Check if the executable is executable and in fact exists
        which(command[0], environ)

        # Use tempfile to get past a limitation with subprocess.PIPE and 64kb.
        # Also to have a file to plug into the track generator
        outputtmp = tempfile.NamedTemporaryFile()

        try:
            # Verify debug is in fact a function we can call
            debug_output = False
            if debug and (callable(debug) or hasattr(debug, "__call__")):
                debug_output = True

            if debug_output:
                def track(thefile, shutdown=None):
                    """Process the temp file until a valid line is found and return it"""
                    thefile.seek(0, 2)
                    while True:
                        if shutdown and shutdown.isSet():
                            break

                        line = thefile.readline()
                        if not line:
                            time.sleep(0.00001)
                            continue
                        yield line

                def track_run(output, debug, shutdown_event):
                    """Wrap track and pass information on the fly to the debug process"""
                    for line in track(output, shutdown_event):
                        debug(line.rstrip())

                # Run the track generator in a separate thread so we can run the command
                shutdown_event = threading.Event()
                thread = threading.Thread(
                    target=track_run,
                    args=(open(outputtmp.name, 'rb'), debug, shutdown_event),
                    name='Monitoring'
                )
                thread.start()

            def target():
                # Run the actual command
                cls.process = subprocess.Popen(
                    command,
                    universal_newlines=True,
                    shell=False,
                    env=environ,
                    cwd=cwd,
                    preexec_fn=os.setsid,
                    stdout=outputtmp,
                    stderr=outputtmp
                )

                cls.process.communicate()

            # Deal with timeout
            thread = threading.Thread(target=target, name='Command Runner')
            thread.start()
            thread.join(timeout)

            if thread.is_alive():
                cls.process.terminate()
                thread.join()
                if thread.is_alive():
                    cls.process.kill()

            # Prime the response
            response = Response
            response.command = command
            response.exit = cls.process.returncode

            # Fetch from the temp file
            outputtmp.seek(0, 0)
            response.output = outputtmp.read().strip()
            outputtmp.close()

            if response.exit < 0:
                raise CommandException("command ('%s') was terminated by signal: %s"
                                       % (' '.join(command), -response.exit),
                                       response.exit,
                                       response.output)
            if response.exit > 0:
                raise CommandException("command ('%s') exited with value: %s\n\n%s"
                                       % (' '.join(command), str(response.exit), response.output),
                                       response.exit,
                                       response.output)

            return response
        except OSError as error:
            # Use fake exit code since we can't get the accurate one from this
            raise CommandException("command failed: %s" % error, 1, error)
        except subprocess.CalledProcessError as error:
            raise CommandException(error.output, error.returncode, error.output)
        finally:
            if debug_output:
                shutdown_event.set()


class CommandException(Exception):
    """
    Class for commanbd exceptions. Beside a specific error message it also stores the
    return code and the output of the command

    :type string
    :param Class specific message

    :type int
    :param exit_code: Exit code of the failed program (default: 1)

    :type string
    :param output: Any output associated with the failure from the program ran (default: None)
    """
    def __init__(self, message, exit_code=1, output=None):
        Exception.__init__(self, message)
        self.message = message
        self.exit = exit_code
        if output is None:
            output = message
        self.output = output

    def __str__(self):
        return repr(self.message)


class Response(object):
    """Contain the response information for a given command"""
    exit = 0
    output = ''
    command = []


def which(program, environ=None):
    """
    Find out if an executable exists in the supplied PATH.
    If so, the absolute path to the executable is returned.
    If not, an exception is raised.

    :type string
    :param program: Executable to be checked for

    :param dict
    :param environ: Any additional ENV variables required, specifically PATH

    :return string|:class:`command.CommandException` Returns the location if found, otherwise raises exception
    """
    def is_exe(path):
        """
        Helper method to check if a file exists and is executable
        """
        return isfile(path) and os.access(path, os.X_OK)

    if program is None:
        raise CommandException("Invalid program name passed")

    fpath, fname = split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        if environ is None:
            environ = os.environ

        for path in environ['PATH'].split(os.pathsep):
            exe_file = join(path, program)
            if is_exe(exe_file):
                return exe_file

    raise CommandException("Could not find %s" % program)


def run(command, timeout=None, cwd=None, env=None, debug=None):
    """
    Runs a given command on the system within a set time period, providing an easy way to access
    command output as it happens without waiting for the command to finish running.

    :type list
    :param command: Should be a list that contains the command that should be ran on the given
                    system. The only whitespaces that can occur is for paths that use a backslash
                    to escape it appropriately

    :type int
    :param timeout: Specificed in seconds. If a command outruns the timeout then the command and
                    its child processes will be terminated. The default is to run

    :type string
    :param cwd: If cwd is set then the current directory will be changed to cwd before it is executed.
                Note that this directory is not considered when searching the executable, so you
                can’t specify the program’s path relative to cwd.

    :type dict
    :param env: A dict of any ENV variables that should be combined into the OS ENV that will help
                the command to run successfully. Note that more often than not the command run
                does not have the same ENV variables available as your shell by default and as such
                require some assistance.

    :type function
    :param debug: A function (also a class function) can be passed in here and all output, line by line,
                  from the command being run will be passed to it as it gets outputted to stdout.
                  This allows for things such as logging (using the built in python logging lib)
                  what is happening on long running commands or redirect output of a tail -f call
                  as lines get outputted without having to wait till the command finishes.

    :return returns :class:`Command.Response` that contains the exit code and the output from the command
    """
    return Command.run(command, timeout=timeout, cwd=cwd, env=env, debug=debug)
