import os
import sys
import subprocess

python_exe = os.path.join(sys.prefix, 'bin', 'python.exe')
py_lib = os.path.join(sys.prefix, 'lib', 'site-packages','pip')
subprocess.check_call([sys.executable, "-m", "ensurepip"])
subprocess.check_call([sys.executable, "-m", "pip", "install", "opencv-python"])
subprocess.check_call([sys.executable, "-m", "pip", "install", "tensorflow"])
subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "jaxlib"])
subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "jax"])
