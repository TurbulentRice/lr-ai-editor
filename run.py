#!/usr/bin/env python3
import os, sys, subprocess, venv

MIN_PY = (3,9)
if sys.version_info < MIN_PY:
    sys.exit(f"❌ Requires Python {MIN_PY[0]}.{MIN_PY[1]}+, got {sys.version}")

# 1. Create venv if needed
venv_dir = os.path.join(os.getcwd(), ".venv")
if not os.path.isdir(venv_dir):
    print("🔧 Creating virtualenv…")
    venv.EnvBuilder(with_pip=True).create(venv_dir)

# 2. Paths to pip and streamlit executables
if os.name == "nt":
    pip_exe = os.path.join(venv_dir, "Scripts", "pip.exe")
    st_exe  = os.path.join(venv_dir, "Scripts", "streamlit.exe")
else:
    pip_exe = os.path.join(venv_dir, "bin", "pip")
    st_exe  = os.path.join(venv_dir, "bin", "streamlit")

# 3. Install dependencies
print("📦 Installing dependencies…")
subprocess.check_call([pip_exe, "install", "--upgrade", "pip"])
subprocess.check_call([pip_exe, "install", "-r", "requirements.txt"])

# 4. Launch Streamlit
print("🚀 Launching Streamlit…")
os.execv(st_exe, [st_exe, "run", "Home.py"])
