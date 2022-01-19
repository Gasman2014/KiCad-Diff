
from __future__ import print_function
import pprint
import traceback
import sys

try:
    print("Starting kidiff")
    from kidiff import kidiff
    
except Exception as e:
    traceback.print_exc(file=sys.stdout)
    pprint.pprint(e)
