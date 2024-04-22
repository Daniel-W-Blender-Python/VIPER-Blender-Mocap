import subprocess

import sys

import os

python_exe = os.path.join(sys.prefix, 'bin', 'python.exe')

py_lib = os.path.join(sys.prefix, 'lib', 'site-packages','pip')

subprocess.check_call([sys.executable, "-m", "ensurepip"])

subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])

subprocess.check_call([sys.executable, "-m", "pip", "install", "mediapipe"])

subprocess.check_call([sys.executable, "-m", "pip", "install", "opencv-python"])
