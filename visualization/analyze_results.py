#!/usr/bin/env python3
"""
Script de análise de resultados para o projeto de detecção de testes flaky.

Este script processa os resultados dos experimentos (NonDex, iDFlakies, etc.)
e gera visualizações e relatórios detalhados.
"""

import os
import json
import glob
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from pathlib import Path
import re
from typing import Dict, List, Tuple
import argparse

class FlakyTestAnalyzer:
    def __init__(self, results_dir: str):
        self.results_dir = Path(results_dir)
        self.projects = []
        self.tools = []
        self.data = []
        
    def scan_results(self) -> None:
        """Escaneia o diretório de resultados e coleta todos os dados."""
        print("🔍 Escaneando resultados...")
        
        for project_dir in self.results_dir.iterdir():
            if not project_dir.is_dir():
                continue
                
            project_name = project_dir.name
            self.projects.append(project_name)
            
            for tool_dir in project_dir.iterdir():
                if not tool_dir.is_dir():
                    continue
                    
                tool_name = tool_dir.name
                if tool_name not in self.tools:
                    self.tools.append(tool_name)
                
                # Processa cada execução da ferramenta
                for run_dir in tool_dir.iterdir():
                    if not run_dir.is_dir():
                        continue
                        
                    run_data = self._parse_run_results(project_name, tool_name, run_dir)
                    if run_data:
                        self.data.append(run_data)
        
        print(f"✅ Encontrados {len(self.data)} execuções em {len(self.projects)} projetos usando {len(self.tools)} ferramentas")
    
    def _parse_run_results(self, project: str, tool: str, run_dir: Path) -> Dict:
        """Extrai dados de uma execução específica."""
        try:
            run_timestamp = run_dir.name
            
            # Lê o arquivo de summary se existir
            summary_file = run_dir / "summary.txt"
            metadata_file = run_dir / "metadata.json"
            log_file = run_dir / f"{tool}.log"
            
            run_data = {
                'project': project,
                'tool': tool,
                'timestamp': run_timestamp,
                'run_dir': str(run_dir),
                'error_lines': 0,
                'warning_lines': 0,
                'failed_lines': 0,
                'test_results': [],
                'flaky_tests': [],
                'total_tests': 0,
                'success_rate': 0.0
            }
            
            # Parse summary.txt
            if summary_file.exists():
                with open(summary_file, 'r', encoding='utf-8') as f:
                    summary_content = f.read()
                    
                # Extrai métricas do summary
                error_match = re.search(r'error_lines:\s*(\d+)', summary_content)
                warning_match = re.search(r'warning_lines:\s*(\d+)', summary_content) 
                failed_match = re.search(r'failed_lines:\s*(\d+)', summary_content)
                
                if error_match:
                    run_data['error_lines'] = int(error_match.group(1))
                if warning_match:
                    run_data['warning_lines'] = int(warning_match.group(1))
                if failed_match:
                    run_data['failed_lines'] = int(failed_match.group(1))
            
            # Parse log para detectar testes flaky
            if log_file.exists():
                flaky_tests = self._extract_flaky_tests(log_file, tool)
                run_data['flaky_tests'] = flaky_tests
                run_data['total_flaky'] = len(flaky_tests)
            
            # Parse metadata.json se existir
            if metadata_file.exists():
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    run_data.update(metadata)
            
            return run_data
            
        except Exception as e:
            print(f"⚠️  Erro ao processar {run_dir}: {e}")
            return None
    
    def _extract_flaky_tests(self, log_file: Path, tool: str) -> List[str]:
        """Extrai lista de testes flaky do log."""
        flaky_tests = []
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if tool == 'nondex':
                # Para NonDex, procura por padrões de testes que falharam inconsistentemente
                # Padrão típico: [WARNING] nome.do.teste#metodo
                warning_pattern = r'\[WARNING\]\s+([^\s]+)#?([^\s]*)'
                matches = re.findall(warning_pattern, content)
                
                for match in matches:
                    test_class = match[0]
                    test_method = match[1] if match[1] else ""
                    test_name = f"{test_class}#{test_method}" if test_method else test_class
                    if test_name not in flaky_tests:
                        flaky_tests.append(test_name)
            
            elif tool == 'idflakies':
                # Para iDFlakies, procura por padrões específicos
                # Adaptar conforme o formato de saída do iDFlakies
                pass
                
        except Exception as e:
            print(f"⚠️  Erro ao extrair testes flaky de {log_file}: {e}")
            
        return flaky_tests
    
    def generate_summary_report(self) -> str:
        """Gera um relatório resumido dos resultados."""
        if not self.data:
            return "Nenhum dado encontrado para análise."
        
        df = pd.DataFrame(self.data)
        
        report = []
        report.append("# 📊 Relatório de Análise de Testes Flaky\n")
        report.append(f"**Data de geração:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        
        # Estatísticas gerais
        report.append("## 🔍 Visão Geral\n")
        report.append(f"- **Projetos analisados:** {len(df['project'].unique())}")
        report.append(f"- **Ferramentas utilizadas:** {', '.join(df['tool'].unique())}")
        report.append(f"- **Total de execuções:** {len(df)}")
        report.append(f"- **Período de análise:** {df['timestamp'].min()} - {df['timestamp'].max()}\n")
        
        # Análise por projeto
        report.append("## 📋 Análise por Projeto\n")
        for project in df['project'].unique():
            project_data = df[df['project'] == project]
            total_flaky = project_data['total_flaky'].sum()
            avg_errors = project_data['error_lines'].mean()
            
            report.append(f"### {project}")
            report.append(f"- Execuções: {len(project_data)}")
            report.append(f"- Total de testes flaky detectados: {total_flaky}")
            report.append(f"- Média de linhas de erro: {avg_errors:.1f}")
            
            # Lista os testes flaky mais frequentes
            all_flaky = []
            for _, row in project_data.iterrows():
                all_flaky.extend(row['flaky_tests'])
            
            if all_flaky:
                flaky_counts = pd.Series(all_flaky).value_counts().head(5)
                report.append("- **Top 5 testes flaky mais frequentes:**")
                for test, count in flaky_counts.items():
                    report.append(f"  - {test}: {count} ocorrências")
            report.append("")
        
        # Análise por ferramenta
        report.append("## 🔧 Análise por Ferramenta\n")
        for tool in df['tool'].unique():
            tool_data = df[df['tool'] == tool]
            report.append(f"### {tool}")
            report.append(f"- Execuções: {len(tool_data)}")
            report.append(f"- Projetos testados: {len(tool_data['project'].unique())}")
            report.append(f"- Total de testes flaky: {tool_data['total_flaky'].sum()}")
            report.append(f"- Média de erros por execução: {tool_data['error_lines'].mean():.1f}")
            report.append("")
        
        return "\n".join(report)
    
    def generate_visualizations(self, output_dir: Path) -> None:
        """Gera gráficos e visualizações."""
        if not self.data:
            print("⚠️  Nenhum dado para visualizar")
            return
            
        df = pd.DataFrame(self.data)
        
        # Configura o estilo dos gráficos
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # 1. Gráfico de testes flaky por projeto
        plt.figure(figsize=(12, 6))
        flaky_by_project = df.groupby('project')['total_flaky'].sum().sort_values(ascending=False)
        
        plt.subplot(1, 2, 1)
        flaky_by_project.plot(kind='bar')
        plt.title('Testes Flaky por Projeto')
        plt.xlabel('Projeto')
        plt.ylabel('Total de Testes Flaky')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # 2. Distribuição de erros por ferramenta
        plt.subplot(1, 2, 2)
        df.boxplot(column='error_lines', by='tool', ax=plt.gca())
        plt.title('Distribuição de Erros por Ferramenta')
        plt.xlabel('Ferramenta')
        plt.ylabel('Linhas de Erro')
        plt.suptitle('')  # Remove o título automático
        
        plt.tight_layout()
        plt.savefig(output_dir / 'flaky_tests_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 3. Timeline de execuções
        if len(df) > 1:
            plt.figure(figsize=(14, 8))
            
            # Converte timestamp para datetime
            df['datetime'] = pd.to_datetime(df['timestamp'], format='%Y-%m-%d_%H-%M-%S')
            
            # Gráfico de linha temporal
            for project in df['project'].unique():
                project_data = df[df['project'] == project].sort_values('datetime')
                plt.plot(project_data['datetime'], project_data['total_flaky'], 
                        marker='o', label=project, linewidth=2)
            
            plt.title('Evolução dos Testes Flaky ao Longo do Tempo')
            plt.xlabel('Data/Hora')
            plt.ylabel('Número de Testes Flaky')
            plt.legend()
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            plt.savefig(output_dir / 'flaky_timeline.png', dpi=300, bbox_inches='tight')
            plt.close()
        
        print(f"✅ Gráficos salvos em {output_dir}")
    
    def export_data(self, output_dir: Path) -> None:
        """Exporta os dados processados."""
        if not self.data:
            return
            
        df = pd.DataFrame(self.data)
        
        # CSV com dados completos
        df.to_csv(output_dir / 'flaky_tests_data.csv', index=False)
        
        # JSON com dados estruturados
        with open(output_dir / 'flaky_tests_data.json', 'w') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
        
        # Resumo executivo em CSV
        summary_data = []
        for project in df['project'].unique():
            project_data = df[df['project'] == project]
            summary_data.append({
                'project': project,
                'total_runs': len(project_data),
                'total_flaky_tests': project_data['total_flaky'].sum(),
                'avg_errors': project_data['error_lines'].mean(),
                'avg_warnings': project_data['warning_lines'].mean(),
                'last_run': project_data['timestamp'].max()
            })
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_csv(output_dir / 'project_summary.csv', index=False)
        
        print(f"✅ Dados exportados para {output_dir}")

def main():
    parser = argparse.ArgumentParser(description='Analisador de Resultados de Testes Flaky')
    parser.add_argument('--results-dir', default='results', 
                       help='Diretório com os resultados dos experimentos')
    parser.add_argument('--output-dir', default='visualization/reports',
                       help='Diretório de saída para os relatórios')
    
    args = parser.parse_args()
    
    # Cria o diretório de saída
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Inicializa o analisador
    analyzer = FlakyTestAnalyzer(args.results_dir)
    
    # Escaneia e processa os resultados
    analyzer.scan_results()
    
    if not analyzer.data:
        print("❌ Nenhum resultado encontrado para análise!")
        return
    
    # Gera relatório em markdown
    print("📝 Gerando relatório...")
    report = analyzer.generate_summary_report()
    with open(output_dir / 'summary_report.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    # Gera visualizações
    print("📊 Gerando gráficos...")
    analyzer.generate_visualizations(output_dir)
    
    # Exporta dados
    print("💾 Exportando dados...")
    analyzer.export_data(output_dir)
    
    print(f"\n✅ Análise completa! Resultados salvos em: {output_dir}")
    print(f"📖 Relatório principal: {output_dir / 'summary_report.md'}")

if __name__ == "__main__":
    main()
