from __future__ import print_function
import command

response = command.run(['ls')])
print("\nOutput:")
print(response.output)
print("\nReturn Code:")
print(response.exit)
