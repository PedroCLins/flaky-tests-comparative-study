#!/usr/bin/env python3
"""
Gerador de relatórios HTML elegantes para análise de testes flaky.
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import base64
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from analyze_results import FlakyTestAnalyzer

class HTMLReportGenerator:
    def __init__(self):
        self.template_dir = Path(__file__).parent / "templates"
        self.template_dir.mkdir(exist_ok=True)
        
    def create_html_template(self) -> str:
        """Cria template HTML responsivo e elegante."""
        return '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f8f9fa;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }
        
        .header p {
            font-size: 1.1rem;
            opacity: 0.9;
        }
        
        .metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }
        
        .metric-card {
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
            border-left: 4px solid #667eea;
        }
        
        .metric-value {
            font-size: 2rem;
            font-weight: bold;
            color: #667eea;
            display: block;
        }
        
        .metric-label {
            color: #666;
            font-size: 0.9rem;
            margin-top: 0.5rem;
        }
        
        .section {
            background: white;
            margin-bottom: 2rem;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .section-header {
            background: #f8f9fa;
            padding: 1rem 1.5rem;
            border-bottom: 1px solid #e9ecef;
        }
        
        .section-header h2 {
            color: #495057;
            font-size: 1.3rem;
        }
        
        .section-content {
            padding: 1.5rem;
        }
        
        .chart-container {
            text-align: center;
            margin: 1rem 0;
        }
        
        .chart-container img {
            max-width: 100%;
            height: auto;
            border-radius: 4px;
        }
        
        .table {
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
        }
        
        .table th,
        .table td {
            padding: 0.75rem;
            text-align: left;
            border-bottom: 1px solid #e9ecef;
        }
        
        .table th {
            background: #f8f9fa;
            font-weight: 600;
            color: #495057;
        }
        
        .table tbody tr:hover {
            background: #f8f9fa;
        }
        
        .alert {
            padding: 1rem;
            border-radius: 4px;
            margin: 1rem 0;
        }
        
        .alert-info {
            background: #d1ecf1;
            border: 1px solid #bee5eb;
            color: #0c5460;
        }
        
        .alert-warning {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            color: #856404;
        }
        
        .badge {
            display: inline-block;
            padding: 0.3rem 0.6rem;
            font-size: 0.75rem;
            font-weight: 600;
            border-radius: 12px;
            color: white;
        }
        
        .badge-primary { background: #667eea; }
        .badge-success { background: #28a745; }
        .badge-warning { background: #ffc107; color: #212529; }
        .badge-danger { background: #dc3545; }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1rem;
        }
        
        .footer {
            text-align: center;
            padding: 2rem;
            color: #666;
            font-size: 0.9rem;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            .header h1 {
                font-size: 2rem;
            }
            
            .metrics {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>{{ title }}</h1>
            <p>{{ subtitle }}</p>
        </header>
        
        {{ content }}
        
        <footer class="footer">
            <p>Relatório gerado em {{ generation_date }} | 
               Sistema de Análise de Testes Flaky - CIn/UFPE</p>
        </footer>
    </div>
</body>
</html>
        '''
    
    def generate_summary_section(self, df: pd.DataFrame) -> str:
        """Gera seção com métricas resumidas."""
        total_runs = len(df)
        total_projects = df['project'].nunique()
        total_tools = df['tool'].nunique()
        total_flaky = df['total_flaky'].sum()
        
        return f'''
        <div class="metrics">
            <div class="metric-card">
                <span class="metric-value">{total_runs}</span>
                <div class="metric-label">Total de Execuções</div>
            </div>
            <div class="metric-card">
                <span class="metric-value">{total_projects}</span>
                <div class="metric-label">Projetos Analisados</div>
            </div>
            <div class="metric-card">
                <span class="metric-value">{total_tools}</span>
                <div class="metric-label">Ferramentas Utilizadas</div>
            </div>
            <div class="metric-card">
                <span class="metric-value">{total_flaky}</span>
                <div class="metric-label">Testes Flaky Detectados</div>
            </div>
        </div>
        '''
    
    def generate_project_analysis(self, df: pd.DataFrame) -> str:
        """Gera análise detalhada por projeto."""
        content = []
        
        for project in df['project'].unique():
            project_data = df[df['project'] == project]
            total_flaky = project_data['total_flaky'].sum()
            avg_errors = project_data['error_lines'].mean()
            runs = len(project_data)
            
            # Determina o status do projeto
            if total_flaky > 50:
                status_badge = '<span class="badge badge-danger">Alto Risco</span>'
            elif total_flaky > 10:
                status_badge = '<span class="badge badge-warning">Risco Médio</span>'
            else:
                status_badge = '<span class="badge badge-success">Baixo Risco</span>'
            
            content.append(f'''
            <div class="section">
                <div class="section-header">
                    <h2>📦 {project} {status_badge}</h2>
                </div>
                <div class="section-content">
                    <div class="grid">
                        <div>
                            <strong>Estatísticas:</strong>
                            <ul>
                                <li>Execuções: {runs}</li>
                                <li>Testes flaky detectados: {total_flaky}</li>
                                <li>Média de erros: {avg_errors:.1f}</li>
                            </ul>
                        </div>
                        <div>
                            <strong>Ferramentas utilizadas:</strong>
                            <ul>
                                {self._generate_tool_list(project_data)}
                            </ul>
                        </div>
                    </div>
                    
                    {self._generate_flaky_tests_summary(project_data)}
                </div>
            </div>
            ''')
        
        return ''.join(content)
    
    def _generate_tool_list(self, project_data: pd.DataFrame) -> str:
        """Gera lista de ferramentas para um projeto."""
        tool_stats = project_data.groupby('tool').agg({
            'total_flaky': 'sum'
        }).reset_index()
        
        items = []
        for _, row in tool_stats.iterrows():
            items.append(f'<li>{row["tool"]}: {row["total_flaky"]} testes flaky</li>')
        
        return ''.join(items)
    
    def _generate_flaky_tests_summary(self, project_data: pd.DataFrame) -> str:
        """Gera resumo dos testes flaky mais problemáticos."""
        all_flaky_tests = []
        for _, row in project_data.iterrows():
            if row.get('flaky_tests'):
                all_flaky_tests.extend(row['flaky_tests'])
        
        if not all_flaky_tests:
            return '<div class="alert alert-info">✅ Nenhum teste flaky específico identificado.</div>'
        
        # Top 5 testes mais problemáticos
        flaky_counts = pd.Series(all_flaky_tests).value_counts().head(5)
        
        table_rows = []
        for test_name, count in flaky_counts.items():
            # Encurta nomes muito longos
            display_name = test_name if len(test_name) <= 60 else test_name[:57] + "..."
            table_rows.append(f'''
                <tr>
                    <td><code>{display_name}</code></td>
                    <td><span class="badge badge-warning">{count}</span></td>
                </tr>
            ''')
        
        return f'''
        <div>
            <strong>🎯 Top 5 Testes Mais Problemáticos:</strong>
            <table class="table">
                <thead>
                    <tr>
                        <th>Teste</th>
                        <th>Ocorrências</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(table_rows)}
                </tbody>
            </table>
        </div>
        '''
    
    def generate_charts_section(self, df: pd.DataFrame, output_dir: Path) -> str:
        """Gera gráficos e os incorpora no HTML."""
        charts_content = []
        
        # Gráfico 1: Testes flaky por projeto
        plt.figure(figsize=(10, 6))
        flaky_by_project = df.groupby('project')['total_flaky'].sum().sort_values(ascending=False)
        
        ax = flaky_by_project.plot(kind='bar', color=['#667eea', '#764ba2', '#f093fb'])
        plt.title('Testes Flaky Detectados por Projeto', fontsize=14, fontweight='bold')
        plt.xlabel('Projeto')
        plt.ylabel('Número de Testes Flaky')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        chart1_path = output_dir / 'chart_flaky_by_project.png'
        plt.savefig(chart1_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        # Converte para base64 para incorporar no HTML
        with open(chart1_path, 'rb') as f:
            chart1_b64 = base64.b64encode(f.read()).decode()
        
        charts_content.append(f'''
        <div class="section">
            <div class="section-header">
                <h2>📊 Distribuição de Testes Flaky</h2>
            </div>
            <div class="section-content">
                <div class="chart-container">
                    <img src="data:image/png;base64,{chart1_b64}" alt="Gráfico de Testes Flaky por Projeto">
                </div>
            </div>
        </div>
        ''')
        
        return ''.join(charts_content)
    
    def generate_full_report(self, results_dir: str, output_path: str) -> None:
        """Gera relatório HTML completo."""
        print("📊 Gerando relatório HTML...")
        
        # Carrega e processa dados
        analyzer = FlakyTestAnalyzer(results_dir)
        analyzer.scan_results()
        
        if not analyzer.data:
            print("❌ Nenhum dado encontrado para gerar relatório")
            return
        
        df = pd.DataFrame(analyzer.data)
        output_path = Path(output_path)
        output_dir = output_path.parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Gera conteúdo das seções
        summary_section = self.generate_summary_section(df)
        project_analysis = self.generate_project_analysis(df)
        charts_section = self.generate_charts_section(df, output_dir)
        
        # Monta conteúdo completo
        content = f'''
        {summary_section}
        {charts_section}
        {project_analysis}
        '''
        
        # Aplica template
        template = self.create_html_template()
        html_content = template.replace('{{ title }}', '🐛 Análise de Testes Flaky')
        html_content = html_content.replace('{{ subtitle }}', 'Relatório Detalhado de Detecção e Análise')
        html_content = html_content.replace('{{ content }}', content)
        html_content = html_content.replace('{{ generation_date }}', 
                                          datetime.now().strftime('%d/%m/%Y às %H:%M:%S'))
        
        # Salva arquivo HTML
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Relatório HTML gerado: {output_path}")
        print(f"🌐 Abra no navegador: file://{output_path.absolute()}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Gera relatório HTML de testes flaky')
    parser.add_argument('--results-dir', default='results',
                       help='Diretório com resultados dos experimentos')
    parser.add_argument('--output', default='visualization/reports/flaky_tests_report.html',
                       help='Arquivo de saída do relatório HTML')
    
    args = parser.parse_args()
    
    generator = HTMLReportGenerator()
    generator.generate_full_report(args.results_dir, args.output)

if __name__ == "__main__":
    main()
