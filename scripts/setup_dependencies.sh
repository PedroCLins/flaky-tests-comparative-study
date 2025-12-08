#!/usr/bin/env bash
set -e

echo "===================================="
echo " Checking and installing dependencies"
echo "===================================="

#############################
# JAVA + MAVEN
#############################

echo "[*] Checking Java..."
if ! command -v java >/dev/null 2>&1; then
    echo "Java not found. Please install Java 8 or 11 manually."
else
    echo "Java found: $(java -version 2>&1 | head -n 1)"
fi

echo "[*] Checking Maven..."
if ! command -v mvn >/dev/null 2>&1; then
    echo "Maven not found. Installing Maven..."
    sudo apt-get update && sudo apt-get install -y maven
else
    echo "Maven found: $(mvn -v | head -n 1)"
fi

#############################
# PYTHON
#############################

echo "[*] Checking Python3..."
if ! command -v python3 >/dev/null 2>&1; then
    echo "Python3 not found. Please install Python 3.8+ manually."
    exit 1
fi

echo "[*] Setting up Python virtual environment..."
VENV_DIR=".venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment in $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
else
    echo "Virtual environment already exists."
fi

echo "[*] Activating virtual environment..."
source "$VENV_DIR/bin/activate"

echo "[*] Checking pip..."
if ! command -v pip >/dev/null 2>&1; then
    echo "pip not found in virtual environment. Something went wrong."
    exit 1
fi

#############################
# PYTHON LIBRARIES
#############################

echo "[*] Installing Python test related packages..."
pip install --upgrade pip
pip install pytest pytest-rerunfailures pytest-randomly

#############################
# IDFLAKIES
#############################
echo "[*] Checking iDFlakies clone..."
IFL=./tools/iDFlakies

if [ ! -d "$IFL" ]; then
    echo "iDFlakies not found in tools/. Cloning repo..."
    git clone https://github.com/iDFlakies/iDFlakies.git "$IFL"
    cd "$IFL"
    mvn install -DskipTests
    cd - >/dev/null
else
    echo "iDFlakies already present."
fi

echo "===================================="
echo " Dependency setup complete!"
echo "===================================="
