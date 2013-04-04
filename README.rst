Command
=======

.. image:: https://travis-ci.org/helgi/python-command.png
   :target: https://travis-ci.org/helgi/python-command

Wrapper around subprocess.popen with on the fly debug / logging
capabilities and timeout handling.

Uses tempfiles for stdout/stderr to get past the 64kb subprocess.PIPE
bug/limitation in python.

Normal command run

.. code:: python

    import command
    response = command.run(['ls'])
    print response.output
    print response.exit

Print the output as it happens

.. code:: python

    import command
    def debug(text):
        print text

    response = command.run(['ls'], debug=debug)
    print response.output
    print response.exit

License
=======

MIT - See LICENSE