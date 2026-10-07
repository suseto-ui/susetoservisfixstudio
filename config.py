import os

# Binaries location path mappings
BIN_DIR = os.path.join(os.path.dirname(__file__), "bin")
ADB_PATH = os.path.join(BIN_DIR, "adb.exe" if os.name == "nt" else "adb")
FASTBOOT_PATH = os.path.join(BIN_DIR, "fastboot.exe" if os.name == "nt" else "fastboot")

# GEMINI CONFIG
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
DEFAULT_MODEL = "gemini-3.8-flash"
