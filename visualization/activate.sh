#!/bin/bash
# Script para ativar o ambiente de visualização
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
source "$PROJECT_ROOT/.venv/bin/activate"
echo "✅ Ambiente de visualização ativo!"
echo "Para executar o dashboard: streamlit run visualization/dashboard.py"
echo "Para gerar relatórios: python visualization/analyze_results.py --help"
