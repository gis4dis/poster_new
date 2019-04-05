import sys
import os

FILE_PATH = os.path.abspath(os.path.dirname(__file__))
PROJECT_BASE_PATH = os.path.abspath(os.path.join(FILE_PATH, '..'))

# Allows the kernel to "see" the project during initialization. This
# FILE_PATH corresponds to Jupyter's "notebook-dir", but we want notebooks to
# behave as though they resided in the base directory to allow for clean
# imports.

sys.path.insert(1, PROJECT_BASE_PATH)