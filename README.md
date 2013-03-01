Command
=======

Wrapper around subprocess.popen with on the fly debug / logging capabilities.

```
import command
response = command.run(['ls'])
print response.output
print response.exit
```

License
=======
MIT - See LICENSE