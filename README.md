Command
=======

Wrapper around subprocess.popen with on the fly debug / logging capabilities with
timeout handling.

Uses tempfiles for stdout/stderr to get past the 64kb subprocess.PIPE bug/limitation in python.

```
import command
response = command.run(['ls'])
print response.output
print response.exit
```

License
=======
MIT - See LICENSE