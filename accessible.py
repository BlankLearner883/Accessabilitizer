import sys

try:
    mode = sys.argv[1]

except IndexError:
    print("Usage: python accessible.py [MODE] (Changes based on mode selected)")

if mode == "subtitle" and sys.argv[
    