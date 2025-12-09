#!/usr/bin/env python3
"""
Script principal para análise e visualização de testes flaky.

Este é o ponto de entrada unificado para todas as funcionalidades
de análise e visualização dos resultados.
"""

import os
import sys
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(
        description='Sistema de Análise de Testes Flaky',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Exemplos de uso:

  # Análise básica e geração de relatórios
  python main.py analyze --results-dir results

  # Gerar apenas relatório HTML
  python main.py html-report --results-dir results

  # Executar dashboard interativo
  python main.py dashboard

  # Configurar ambiente
  python main.py setup

Para mais informações sobre cada comando, use:
  python main.py <comando> --help
        '''
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponíveis')
    
    # Comando: analyze
    analyze_parser = subparsers.add_parser('analyze', help='Executa análise completa dos resultados')
    analyze_parser.add_argument('--results-dir', default='results', 
                               help='Diretório com os resultados (default: results)')
    analyze_parser.add_argument('--output-dir', default='visualization/reports',
                               help='Diretório de saída (default: visualization/reports)')
    analyze_parser.add_argument('--format', choices=['all', 'markdown', 'html', 'csv'], 
                               default='all', help='Formato de saída (default: all)')
    
    # Comando: html-report  
    html_parser = subparsers.add_parser('html-report', help='Gera relatório HTML elegante')
    html_parser.add_argument('--results-dir', default='results',
                            help='Diretório com os resultados (default: results)')
    html_parser.add_argument('--output', default='visualization/reports/report.html',
                            help='Arquivo de saída HTML (default: visualization/reports/report.html)')
    
    # Comando: dashboard
    dashboard_parser = subparsers.add_parser('dashboard', help='Executa dashboard web interativo')
    dashboard_parser.add_argument('--port', type=int, default=8501,
                                 help='Porta do servidor (default: 8501)')
    
    # Comando: setup
    setup_parser = subparsers.add_parser('setup', help='Configura o ambiente de visualização')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Verifica se estamos no diretório correto
    current_dir = Path.cwd()
    if not (current_dir / 'visualization').exists():
        print("❌ Execute este script a partir do diretório raiz do projeto!")
        print(f"   Diretório atual: {current_dir}")
        print("   Esperado: diretório contendo a pasta 'visualization'")
        return
    
    try:
        if args.command == 'setup':
            setup_environment()
        
        elif args.command == 'analyze':
            run_analysis(args)
        
        elif args.command == 'html-report':
            generate_html_report(args)
        
        elif args.command == 'dashboard':
            run_dashboard(args)
            
    except KeyboardInterrupt:
        print("\n🛑 Operação cancelada pelo usuário")
    except Exception as e:
        print(f"❌ Erro: {e}")
        sys.exit(1)

def setup_environment():
    """Configura o ambiente de visualização."""
    print("🔧 Configurando ambiente de visualização...")
    
    # Executa o script de setup
    setup_script = Path('visualization/setup.sh')
    if setup_script.exists():
        import subprocess
        result = subprocess.run(['bash', str(setup_script)], capture_output=True, text=True)
        if result.returncode == 0:
            print(result.stdout)
        else:
            print(f"❌ Erro na configuração: {result.stderr}")
    else:
        print("❌ Script de configuração não encontrado!")

def run_analysis(args):
    """Executa análise completa dos resultados."""
    print("📊 Executando análise completa...")
    
    # Importa e executa o analisador
    sys.path.append('visualization')
    from analyze_results import FlakyTestAnalyzer
    
    # Cria diretório de saída
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Executa análise
    analyzer = FlakyTestAnalyzer(args.results_dir)
    analyzer.scan_results()
    
    if not analyzer.data:
        print(f"❌ Nenhum resultado encontrado em '{args.results_dir}'")
        return
    
    # Gera relatórios conforme o formato solicitado
    if args.format in ['all', 'markdown']:
        print("📝 Gerando relatório Markdown...")
        report = analyzer.generate_summary_report()
        with open(output_dir / 'summary_report.md', 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"✅ Relatório Markdown: {output_dir / 'summary_report.md'}")
    
    if args.format in ['all', 'html']:
        print("🌐 Gerando relatório HTML...")
        from html_report import HTMLReportGenerator
        generator = HTMLReportGenerator()
        html_path = output_dir / 'detailed_report.html'
        generator.generate_full_report(args.results_dir, str(html_path))
    
    if args.format in ['all', 'csv']:
        print("💾 Exportando dados...")
        analyzer.export_data(output_dir)
    
    # Gera visualizações
    print("📈 Gerando gráficos...")
    analyzer.generate_visualizations(output_dir)
    
    print(f"\n✅ Análise completa! Resultados em: {output_dir}")

def generate_html_report(args):
    """Gera relatório HTML elegante."""
    print("🌐 Gerando relatório HTML...")
    
    sys.path.append('visualization')
    from html_report import HTMLReportGenerator
    
    generator = HTMLReportGenerator()
    generator.generate_full_report(args.results_dir, args.output)

def run_dashboard(args):
    """Executa o dashboard web interativo."""
    print("🚀 Iniciando dashboard web...")
    print(f"🌐 Acesse: http://localhost:{args.port}")
    
    # Executa Streamlit
    import subprocess
    dashboard_script = Path('visualization/dashboard.py')
    
    if not dashboard_script.exists():
        print("❌ Arquivo do dashboard não encontrado!")
        return
    
    cmd = ['streamlit', 'run', str(dashboard_script), '--server.port', str(args.port)]
    
    try:
        subprocess.run(cmd, check=True)
    except FileNotFoundError:
        print("❌ Streamlit não encontrado! Execute primeiro: python main.py setup")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar dashboard: {e}")

if __name__ == "__main__":
    main()
