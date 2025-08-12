#!/usr/bin/env bash
set -euo pipefail

# 1. Ensure Python ≥ 3.9
PYTHON=${PYTHON:-python3}
version=$("$PYTHON" --version 2>&1 | awk '{print $2}')
major=${version%%.*}
minor=${version#*.}; minor=${minor%%.*}
if (( major < 3 || (major == 3 && minor < 9) )); then
  echo "❌ Python 3.9+ required, found $version"
  exit 1
fi

# 2. Create venv if it doesn't exist
if [ ! -d ".venv" ]; then
  echo "🔧 Creating virtualenv..."
  "$PYTHON" -m venv .venv
fi

# 3. Install/up-date dependencies
PIP=.venv/bin/pip
echo "📦 Installing dependencies..."
"$PIP" install --upgrade pip
"$PIP" install -r requirements.txt

# 4. Run the app
STREAMLIT=.venv/bin/streamlit
echo "🚀 Launching Streamlit..."
exec "$STREAMLIT" run Home.py
