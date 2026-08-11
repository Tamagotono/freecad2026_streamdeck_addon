import sys
import os

# Allow test files to import from the addon root without installation
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
