#!/usr/bin/env python3
import sys
print("Python:", sys.version)
try:
    import hermes_tools
    print("hermes_tools OK:", hermes_tools.__file__)
except Exception as e:
    print("hermes_tools ImportError:", e)
