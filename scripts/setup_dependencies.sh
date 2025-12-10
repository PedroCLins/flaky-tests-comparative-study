#!/usr/bin/env bash
set -e

echo "===================================="
echo " Checking and installing dependencies"
echo "===================================="

#############################
# JAVA + MAVEN
#############################

OS=$(uname -s)

echo "[*] Detected OS: $OS"

install_linux_pkg() {
    # $@ packages
    sudo apt-get update && sudo apt-get install -y "$@"
}

install_macos_pkg() {
    # $@ packages via Homebrew
    if ! command -v brew >/dev/null 2>&1; then
        echo "Homebrew not found. Please install Homebrew first:"
        echo "/bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        exit 1
    fi
    brew install "$@"
}

echo "[*] Checking Java..."
if ! command -v java >/dev/null 2>&1; then
    echo "Java not found. Installing OpenJDK..."
    if [ "$OS" = "Linux" ]; then
        install_linux_pkg openjdk-21-jdk || install_linux_pkg openjdk-11-jdk
    elif [ "$OS" = "Darwin" ]; then
        install_macos_pkg openjdk
    else
        echo "Unsupported OS: $OS. Please install Java manually."
        exit 1
    fi
else
    echo "Java found: $(java -version 2>&1 | head -n 1)"
fi

echo "[*] Checking Java compiler (javac)..."
if ! command -v javac >/dev/null 2>&1; then
    echo "Java compiler not found. Installing JDK..."
    if [ "$OS" = "Linux" ]; then
        install_linux_pkg openjdk-21-jdk || install_linux_pkg openjdk-11-jdk
    elif [ "$OS" = "Darwin" ]; then
        install_macos_pkg openjdk
    else
        echo "Unsupported OS: $OS. Please install a JDK manually."
        exit 1
    fi
else
    echo "Java compiler found: $(javac -version 2>&1)"
fi

echo "[*] Checking Maven..."
if ! command -v mvn >/dev/null 2>&1; then
    echo "Maven not found. Installing Maven..."
    if [ "$OS" = "Linux" ]; then
        install_linux_pkg maven
    elif [ "$OS" = "Darwin" ]; then
        install_macos_pkg maven
    else
        echo "Unsupported OS: $OS. Please install Maven manually."
        exit 1
    fi
else
    echo "Maven found: $(mvn -v | head -n 1)"
fi

#############################
# PYTHON
#############################

echo "[*] Checking Python3..."
if ! command -v python3 >/dev/null 2>&1; then
    echo "Python3 not found. Installing Python3..."
    sudo apt-get update && sudo apt-get install -y python3 python3-pip python3-venv
else
    echo "Python3 found: $(python3 --version)"
fi

echo "[*] Checking python3-venv (venv module)..."
if ! python3 -c "import venv" >/dev/null 2>&1; then
    echo "python3 venv module not available. Installing..."
    if [ "$OS" = "Linux" ]; then
        install_linux_pkg python3-venv
    elif [ "$OS" = "Darwin" ]; then
        # Homebrew's python includes venv by default
        install_macos_pkg python
    else
        echo "Unsupported OS: $OS. Please ensure python3 venv is available."
        exit 1
    fi
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
pip install pytest>=8.3.4 pytest-rerunfailures pytest-randomly

echo "[*] Installing visualization and analysis packages..."
pip install pandas streamlit scipy

#############################
# VISUALIZATION SETUP
#############################

echo "[*] Setting up visualization directories..."
mkdir -p ./visualization/reports
mkdir -p ./visualization/exports
mkdir -p ./visualization/templates

echo "[*] Creating visualization activation script..."
cat > ./visualization/activate.sh << 'EOF'
#!/bin/bash
# Script para ativar o ambiente de visualização
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
source "$PROJECT_ROOT/.venv/bin/activate"
echo "✅ Ambiente de visualização ativo!"
echo "Para executar o dashboard: streamlit run visualization/dashboard.py"
echo "Para gerar relatórios: python visualization/analyze_results.py --help"
EOF

chmod +x ./visualization/activate.sh

echo "===================================="
echo " Dependency setup complete!"
echo "===================================="
