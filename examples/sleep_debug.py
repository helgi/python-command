from __future__ import print_function
import command
import os.path
import logging
logging.basicConfig(level=logging.DEBUG, format='%(message)s')

print("Go go gadget")
response = command.run(['python', os.path.join(os.path.dirname(__file__), 'sleep.py')], debug=logging.debug)
print("\nOutput:")
print(response.output)
print("\nReturn Code:")
print(response.exit)
