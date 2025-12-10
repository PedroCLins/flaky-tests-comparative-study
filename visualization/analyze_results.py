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
from datetime import datetime
from pathlib import Path
import re
from typing import Dict, List, Tuple
import argparse

# Import metrics module
from metrics import FlakinessMetrics, TestMetrics, parse_pytest_runs_csv

class FlakyTestAnalyzer:
    def __init__(self, results_dir: str):
        self.results_dir = Path(results_dir)
        self.projects = []
        self.tools = []
        self.data = []
        self.test_metrics = {}  # project -> test_name -> TestMetrics
        self.project_metrics = {}  # project -> aggregate metrics
        
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
        
        # Calculate metrics for all projects
        print("📊 Calculando métricas de flakiness...")
        self._calculate_all_metrics()
    
    def _calculate_all_metrics(self) -> None:
        """Calculate flakiness metrics for all tests in all projects."""
        for project_dir in self.results_dir.iterdir():
            if not project_dir.is_dir():
                continue
            
            project_name = project_dir.name
            
            # Look for pytest-rerun results (has runs.csv with per-test data)
            pytest_dir = project_dir / "pytest-rerun"
            if pytest_dir.exists():
                self._calculate_pytest_metrics(project_name, pytest_dir)
            
            # Look for nondex results (Java projects)
            nondex_dir = project_dir / "nondex"
            if nondex_dir.exists():
                self._calculate_nondex_metrics(project_name, nondex_dir)
    
    def _calculate_pytest_metrics(self, project_name: str, pytest_dir: Path) -> None:
        """Calculate metrics for pytest results."""
        # Find the most recent run directory
        run_dirs = sorted(pytest_dir.glob("*/"), reverse=True)
        if not run_dirs:
            return
        
        run_dir = run_dirs[0]  # Most recent
        runs_csv = run_dir / "runs.csv"
        
        if not runs_csv.exists():
            return
        
        try:
            # Parse CSV to get per-test failure data
            test_failures = parse_pytest_runs_csv(str(runs_csv))
            
            if not test_failures:
                return
            
            # Calculate metrics for each test
            project_test_metrics = {}
            for test_name, failure_list in test_failures.items():
                metrics = FlakinessMetrics.calculate_test_metrics(test_name, failure_list)
                project_test_metrics[test_name] = metrics
            
            self.test_metrics[project_name] = project_test_metrics
            
            # Calculate aggregate project metrics
            metrics_list = list(project_test_metrics.values())
            self.project_metrics[project_name] = FlakinessMetrics.calculate_project_metrics(metrics_list)
            
            print(f"  ✓ {project_name}: {len(project_test_metrics)} tests analyzed")
            
        except Exception as e:
            print(f"  ⚠️ Erro ao calcular métricas para {project_name}: {e}")
    
    def _calculate_nondex_metrics(self, project_name: str, nondex_dir: Path) -> None:
        """Calculate aggregate metrics for NonDex results (Java projects)."""
        try:
            # Collect all flaky tests detected across all NonDex runs
            all_flaky_tests = set()
            total_tests_run = 0
            
            # Find all run directories
            run_dirs = sorted(nondex_dir.glob("*/"))
            if not run_dirs:
                return
            
            for run_dir in run_dirs:
                log_file = run_dir / "nondex.log"
                if not log_file.exists():
                    continue
                
                # Extract flaky tests from this run
                flaky_tests = self._extract_flaky_tests(log_file, 'nondex')
                all_flaky_tests.update(flaky_tests)
                
                # Try to get total tests count from the log
                tests_count = self._extract_total_tests(log_file, 'nondex')
                if tests_count and tests_count > total_tests_run:
                    total_tests_run = tests_count
            
            if not all_flaky_tests and total_tests_run == 0:
                return
            
            # For NonDex, we don't have per-run failure data for each test,
            # so we can't calculate detailed statistical metrics like pytest.
            # Instead, we provide aggregate project-level metrics.
            flaky_count = len(all_flaky_tests)
            
            self.project_metrics[project_name] = {
                'total_tests': total_tests_run,
                'flaky_tests': flaky_count,
                'flaky_percentage': 100 * flaky_count / total_tests_run if total_tests_run > 0 else 0.0,
                'avg_failure_rate': 0.0,  # Not available for NonDex without per-run data
                'median_failure_rate': 0.0,  # Not available
                'severity_distribution': {'nondex_detected': flaky_count},  # Simple count
                'tool': 'nondex',
                'note': 'NonDex metrics are based on nondeterminism detection, not multiple reruns'
            }
            
            print(f"  ✓ {project_name}: {flaky_count} flaky tests detected (NonDex)")
            
        except Exception as e:
            print(f"  ⚠️ Erro ao calcular métricas NonDex para {project_name}: {e}")
    
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
            
            # Parse log para detectar testes flaky e total de testes
            if log_file.exists():
                flaky_tests = self._extract_flaky_tests(log_file, tool)
                run_data['flaky_tests'] = flaky_tests
                run_data['total_flaky'] = len(flaky_tests)
                run_data['total_tests'] = self._extract_total_tests(log_file, tool)
            
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
                # Padrão típico: [WARNING] org.package.ClassName#testMethod
                # O padrão deve começar na linha e capturar o formato completo
                warning_pattern = r'^\[WARNING\]\s+([^\s]+)#([^\s]+)'
                matches = re.findall(warning_pattern, content, re.MULTILINE)
                
                for match in matches:
                    test_class = match[0]
                    test_method = match[1]
                    test_name = f"{test_class}#{test_method}"
                    if test_name not in flaky_tests:
                        flaky_tests.append(test_name)
            
            elif tool == 'idflakies':
                # Para iDFlakies, procura por padrões específicos
                # Adaptar conforme o formato de saída do iDFlakies
                pass
                
        except Exception as e:
            print(f"⚠️  Erro ao extrair testes flaky de {log_file}: {e}")
            
        return flaky_tests
    
    def _extract_total_tests(self, log_file: Path, tool: str) -> int:
        """Extrai o número total de testes no projeto (não apenas os executados)."""
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            if tool == 'pytest-rerun':
                # Pytest format at the end: "2 failed, 1017 passed, 5 skipped, 4 xfailed, 143 warnings in 125.07s"
                # Look for the summary line (usually near the end)
                for line in reversed(lines):
                    # Match pytest summary that includes timing
                    if re.search(r'in\s+[\d.]+s', line):
                        total = 0
                        # Extract all test counts from the summary line
                        for match in re.finditer(r'(\d+)\s+(failed|passed|skipped|error|xfailed|xpassed)', line):
                            total += int(match.group(1))
                        if total > 0:
                            return total
                        
            elif tool == 'nondex':
                # Maven NonDex format: "[WARNING] Tests run: 18549, Failures: 0, Errors: 0, Skipped: 20"
                # Look for the final summary (appears after "Results:")
                found_results = False
                for i in range(len(lines) - 1, -1, -1):
                    line = lines[i]
                    
                    # Look for summary with WARNING/INFO prefix
                    match = re.search(r'\[(WARNING|INFO)\]\s+Tests run:\s+(\d+)', line)
                    if match:
                        return int(match.group(2))
                    
                    # Also check for lines after "Results:"
                    if 'Results:' in line:
                        found_results = True
                        # Check next few lines for the test count
                        for j in range(i + 1, min(i + 10, len(lines))):
                            match = re.search(r'Tests run:\s+(\d+)', lines[j])
                            if match:
                                return int(match.group(1))
            
            return None
            
        except Exception as e:
            print(f"⚠️  Erro ao extrair total de testes de {log_file}: {e}")
            return None
    
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
        """Prepara dados para visualização (gráficos gerados via HTML/dashboard)."""
        if not self.data:
            print("⚠️  Nenhum dado para visualizar")
            return
            
        df = pd.DataFrame(self.data)
        
        # Exporta dados agregados para visualização
        # 1. Testes flaky por projeto
        flaky_by_project = df.groupby('project')['total_flaky'].sum().sort_values(ascending=False)
        flaky_by_project.to_csv(output_dir / 'chart_data_flaky_by_project.csv')
        
        # 2. Distribuição de erros por ferramenta
        error_stats = df.groupby('tool')['error_lines'].describe()
        error_stats.to_csv(output_dir / 'chart_data_errors_by_tool.csv')
        
        # 3. Timeline de execuções
        if len(df) > 1:
            df['datetime'] = pd.to_datetime(df['timestamp'], format='%Y-%m-%d_%H-%M-%S', errors='coerce')
            timeline_data = df[['datetime', 'project', 'total_flaky']].sort_values('datetime')
            timeline_data.to_csv(output_dir / 'chart_data_timeline.csv', index=False)
        
        print(f"✅ Dados de visualização preparados em {output_dir}")
    
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
            base_summary = {
                'project': project,
                'total_runs': len(project_data),
                'total_flaky_tests': project_data['total_flaky'].sum(),
                'avg_errors': project_data['error_lines'].mean(),
                'avg_warnings': project_data['warning_lines'].mean(),
                'last_run': project_data['timestamp'].max()
            }
            
            # Add metrics if available (or zeros if no flaky tests detected)
            if project in self.project_metrics:
                pm = self.project_metrics[project]
                base_summary.update({
                    'total_tests_analyzed': pm['total_tests'],
                    'flaky_tests_detected': pm['flaky_tests'],
                    'flaky_percentage': pm['flaky_percentage'],
                    'avg_failure_rate': pm['avg_failure_rate'],
                    'median_failure_rate': pm['median_failure_rate'],
                    'severity_high': pm['severity_distribution'].get('high', 0),
                    'severity_medium': pm['severity_distribution'].get('medium', 0),
                    'severity_low': pm['severity_distribution'].get('low', 0)
                })
            else:
                # No flaky tests detected - fill with zeros
                base_summary.update({
                    'total_tests_analyzed': 0,
                    'flaky_tests_detected': 0,
                    'flaky_percentage': 0.0,
                    'avg_failure_rate': 0.0,
                    'median_failure_rate': 0.0,
                    'severity_high': 0,
                    'severity_medium': 0,
                    'severity_low': 0
                })
            
            summary_data.append(base_summary)
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_csv(output_dir / 'project_summary.csv', index=False)
        
        # Export detailed test metrics
        self._export_test_metrics(output_dir)
        
        print(f"✅ Dados exportados para {output_dir}")
    
    def _export_test_metrics(self, output_dir: Path) -> None:
        """Export detailed per-test metrics to CSV."""
        if not self.test_metrics:
            return
        
        all_metrics = []
        for project, tests in self.test_metrics.items():
            for test_name, metrics in tests.items():
                all_metrics.append({
                    'project': project,
                    'test_name': test_name,
                    'total_runs': metrics.total_runs,
                    'failures': metrics.failures,
                    'failure_rate': metrics.failure_rate,
                    'is_flaky': metrics.is_flaky,
                    'severity': metrics.flakiness_severity,
                    'variance': metrics.variance,
                    'std_dev': metrics.std_dev,
                    'ci_lower': metrics.confidence_interval_95[0],
                    'ci_upper': metrics.confidence_interval_95[1],
                    'p_value': metrics.p_value
                })
        
        if all_metrics:
            metrics_df = pd.DataFrame(all_metrics)
            metrics_df.to_csv(output_dir / 'test_metrics_detailed.csv', index=False)
            
            # Export only flaky tests for easier analysis
            flaky_df = metrics_df[metrics_df['is_flaky'] == True]
            if not flaky_df.empty:
                flaky_df.to_csv(output_dir / 'flaky_tests_metrics.csv', index=False)
                print(f"  📊 Exportadas métricas detalhadas de {len(flaky_df)} testes flaky")

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
    
    # Exporta dados
    print("💾 Exportando dados...")
    analyzer.export_data(output_dir)
    
    # Prepara dados de visualização
    print("📊 Preparando dados de visualização...")
    analyzer.generate_visualizations(output_dir)
    
    print(f"\n✅ Análise completa! Resultados salvos em: {output_dir}")
    print(f"📖 Relatório principal: {output_dir / 'summary_report.md'}")

if __name__ == "__main__":
    main()
