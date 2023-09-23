import subprocess

import sys

subprocess.check_call([sys.executable, "-m", "ensurepip"])

subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])

subprocess.check_call([sys.executable, "-m", "pip", "install", "mediapipe"])

subprocess.check_call([sys.executable, "-m", "pip", "install", "opencv-python"])