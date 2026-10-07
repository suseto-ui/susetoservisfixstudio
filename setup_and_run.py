import os
import sys

def setup():
    print("Initializing EUDCP Environment...")
    # Initialize SQLite DB
    # Run tests
    print("Running test suite...")
    os.system("pytest tests/")
    print("Launching Dashboard...")
    # Launch GUI app
    # os.system("python main.py")

if __name__ == "__main__":
    setup()
