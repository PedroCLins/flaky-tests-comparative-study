#!/usr/bin/env bash
"""
Script para configurar o ambiente de visualização.
"""

set -euo pipefail

echo "🔧 Configurando ambiente de visualização para análise de testes flaky..."

# Diretório base
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Configurar Python
echo "📦 Configurando Python e dependências..."

# Verifica se Python está disponível
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado. Por favor, instale Python 3.8 ou superior."
    exit 1
fi

# Cria ambiente virtual se não existir
VENV_DIR="$SCRIPT_DIR/venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "🐍 Criando ambiente virtual Python..."
    python3 -m venv "$VENV_DIR"
fi

# Ativa o ambiente virtual
echo "🔄 Ativando ambiente virtual..."
source "$VENV_DIR/bin/activate"

# Atualiza pip
python -m pip install --upgrade pip

# Instala dependências
echo "📚 Instalando dependências Python..."
pip install -r "$SCRIPT_DIR/requirements.txt"

# Cria diretórios necessários
echo "📁 Criando diretórios de saída..."
mkdir -p "$SCRIPT_DIR/reports"
mkdir -p "$SCRIPT_DIR/exports"
mkdir -p "$SCRIPT_DIR/templates"

# Gera script de ativação
cat > "$SCRIPT_DIR/activate.sh" << 'EOF'
#!/bin/bash
# Script para ativar o ambiente de visualização
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/venv/bin/activate"
echo "✅ Ambiente de visualização ativo!"
echo "Para executar o dashboard: streamlit run dashboard.py"
echo "Para gerar relatórios: python analyze_results.py --help"
EOF

chmod +x "$SCRIPT_DIR/activate.sh"

echo ""
echo "✅ Configuração completa!"
echo ""
echo "📖 Como usar:"
echo "1. Ativar o ambiente: source visualization/activate.sh"
echo "2. Executar análise: python visualization/analyze_results.py" 
echo "3. Abrir dashboard: streamlit run visualization/dashboard.py"
echo ""
echo "📂 Os resultados serão salvos em:"
echo "   - Relatórios: visualization/reports/"
echo "   - Exports: visualization/exports/"
