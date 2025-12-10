#!/usr/bin/env python3
"""
Dashboard web interativo para visualização de resultados de testes flaky.

Este dashboard permite visualizar e filtrar os resultados dos experimentos
de forma interativa usando Streamlit.
"""

import streamlit as st
import pandas as pd
import json
import os
from pathlib import Path
from datetime import datetime
import sys

# Adiciona o diretório pai ao path para importar o analisador
sys.path.append(str(Path(__file__).parent))
from analyze_results import FlakyTestAnalyzer

def load_data(results_dir: str) -> tuple:
    """Carrega e processa os dados."""
    analyzer = FlakyTestAnalyzer(results_dir)
    analyzer.scan_results()
    
    if not analyzer.data:
        return pd.DataFrame(), analyzer
    
    df = pd.DataFrame(analyzer.data)
    # Converte timestamp para datetime
    df['datetime'] = pd.to_datetime(df['timestamp'], format='%Y-%m-%d_%H-%M-%S', errors='coerce')
    return df, analyzer

def main():
    st.set_page_config(
        page_title="Dashboard - Testes Flaky", 
        page_icon="🐛",
        layout="wide"
    )
    
    st.title("🐛 Dashboard de Análise de Testes Flaky")
    st.markdown("---")
    
    # Sidebar para configurações
    st.sidebar.header("⚙️ Configurações")
    
    # Seleção do diretório de resultados
    results_dir = st.sidebar.text_input(
        "Diretório de Resultados", 
        value="results",
        help="Caminho para o diretório contendo os resultados dos experimentos"
    )
    
    # Botão para carregar dados
    if st.sidebar.button("🔄 Carregar Dados"):
        st.cache_data.clear()
    
    # Carrega os dados
    @st.cache_data
    def get_data(results_dir):
        return load_data(results_dir)
    
    try:
        df, analyzer = get_data(results_dir)
        
        if df.empty:
            st.error(f"❌ Nenhum resultado encontrado em '{results_dir}'")
            st.info("Verifique se o diretório existe e contém resultados dos experimentos.")
            return
        
        # Filtros na sidebar
        st.sidebar.header("🔍 Filtros")
        
        # Filtro por projeto
        projects = ['Todos'] + list(df['project'].unique())
        selected_project = st.sidebar.selectbox("Projeto", projects)
        
        # Filtro por ferramenta  
        tools = ['Todas'] + list(df['tool'].unique())
        selected_tool = st.sidebar.selectbox("Ferramenta", tools)
        
        # Filtro por data
        if 'datetime' in df.columns and not df['datetime'].isna().all():
            date_range = st.sidebar.date_input(
                "Período",
                value=(df['datetime'].min().date(), df['datetime'].max().date()),
                min_value=df['datetime'].min().date(),
                max_value=df['datetime'].max().date()
            )
        
        # Aplica filtros
        filtered_df = df.copy()
        
        if selected_project != 'Todos':
            filtered_df = filtered_df[filtered_df['project'] == selected_project]
            
        if selected_tool != 'Todas':
            filtered_df = filtered_df[filtered_df['tool'] == selected_tool]
        
        if 'datetime' in df.columns and not df['datetime'].isna().all():
            if len(date_range) == 2:
                start_date, end_date = date_range
                filtered_df = filtered_df[
                    (filtered_df['datetime'].dt.date >= start_date) & 
                    (filtered_df['datetime'].dt.date <= end_date)
                ]
        
        # Métricas principais
        st.header("📊 Métricas Gerais")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total de Execuções",
                len(filtered_df),
                delta=len(filtered_df) - len(df) if selected_project != 'Todos' or selected_tool != 'Todas' else None
            )
        
        with col2:
            total_flaky = filtered_df['total_flaky'].sum()
            st.metric("Testes Flaky Detectados", total_flaky)
        
        with col3:
            avg_errors = filtered_df['error_lines'].mean()
            st.metric("Média de Erros", f"{avg_errors:.1f}")
        
        with col4:
            projects_count = filtered_df['project'].nunique()
            st.metric("Projetos Analisados", projects_count)
        
        # Gráficos principais
        st.header("📈 Visualizações")
        
        # Layout em duas colunas
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de testes flaky por projeto
            st.subheader("Testes Flaky por Projeto")
            flaky_by_project = filtered_df.groupby('project')['total_flaky'].sum().sort_values(ascending=False)
            st.bar_chart(flaky_by_project)
        
        with col2:
            # Média de erros por ferramenta
            st.subheader("Média de Erros por Ferramenta")
            error_by_tool = filtered_df.groupby('tool')['error_lines'].mean()
            st.bar_chart(error_by_tool)
        
        # Timeline (se houver dados de tempo)
        if 'datetime' in filtered_df.columns and not filtered_df['datetime'].isna().all():
            st.subheader("⏰ Evolução Temporal")
            
            # Prepara dados para line chart
            timeline_pivot = filtered_df.pivot_table(
                index='datetime',
                columns='project',
                values='total_flaky',
                aggfunc='sum'
            ).fillna(0)
            
            st.line_chart(timeline_pivot)
        
        # ========================================
        # METRICS SECTION - Advanced Analysis
        # ========================================
        if analyzer.test_metrics or analyzer.project_metrics:
            st.header("📊 Métricas Avançadas de Flakiness")
            st.markdown("""
            Esta seção fornece análises estatísticas detalhadas sobre a flakiness dos testes,
            incluindo taxas de falha, significância estatística e distribuição de severidade.
            """)
            
            # Project-level metrics
            if analyzer.project_metrics:
                st.subheader("📈 Métricas por Projeto")
                
                # Build metrics dataframe
                metrics_data = []
                for project, metrics in analyzer.project_metrics.items():
                    metrics_data.append({
                        'Projeto': project,
                        'Total de Testes': metrics['total_tests'],
                        'Testes Flaky': metrics['flaky_tests'],
                        'Taxa de Flakiness (%)': f"{metrics['flaky_percentage']:.2f}%",
                        'Taxa Média de Falha': f"{metrics['avg_failure_rate']:.1%}",
                        'Taxa Mediana de Falha': f"{metrics['median_failure_rate']:.1%}",
                        'Severidade Alta': metrics['severity_distribution'].get('high', 0),
                        'Severidade Média': metrics['severity_distribution'].get('medium', 0),
                        'Severidade Baixa': metrics['severity_distribution'].get('low', 0)
                    })
                
                if metrics_data:
                    metrics_df = pd.DataFrame(metrics_data)
                    st.dataframe(metrics_df, use_container_width=True)
                    
                    # Severity distribution chart
                    st.subheader("🎯 Distribuição de Severidade de Flakiness")
                    st.markdown("""
                    **Severidade** indica o quão intermitente é o teste:
                    - **Baixa**: 1-10% de taxa de falha (ocasional)
                    - **Média**: 10-40% de taxa de falha (frequente)
                    - **Alta**: 40-60% de taxa de falha (altamente instável)
                    """)
                    
                    severity_data = []
                    for project, metrics in analyzer.project_metrics.items():
                        severity_dist = metrics['severity_distribution']
                        severity_data.append({
                            'Projeto': project,
                            'Baixa': severity_dist.get('low', 0),
                            'Média': severity_dist.get('medium', 0),
                            'Alta': severity_dist.get('high', 0)
                        })
                    
                    if severity_data:
                        severity_df = pd.DataFrame(severity_data).set_index('Projeto')
                        st.bar_chart(severity_df)
            
            # Test-level detailed metrics
            if analyzer.test_metrics:
                st.subheader("🔬 Análise Detalhada de Testes Flaky")
                
                # Collect all flaky tests across projects
                all_flaky_metrics = []
                for project, tests in analyzer.test_metrics.items():
                    for test_name, metrics in tests.items():
                        if metrics.is_flaky:
                            all_flaky_metrics.append({
                                'Projeto': project,
                                'Teste': test_name[:80] + '...' if len(test_name) > 80 else test_name,
                                'Taxa de Falha': f"{metrics.failure_rate:.1%}",
                                'Severidade': metrics.flakiness_severity,
                                'Execuções': metrics.total_runs,
                                'Falhas': metrics.failures,
                                'P-Value': f"{metrics.p_value:.4f}",
                                'IC 95% Inferior': f"{metrics.confidence_interval_95[0]:.3f}",
                                'IC 95% Superior': f"{metrics.confidence_interval_95[1]:.3f}"
                            })
                
                if all_flaky_metrics:
                    flaky_metrics_df = pd.DataFrame(all_flaky_metrics)
                    
                    # Tabs for different views
                    tab1, tab2, tab3 = st.tabs(["📋 Todos os Testes", "⚠️ Alta Severidade", "📊 Estatísticas"])
                    
                    with tab1:
                        st.markdown(f"**Total de testes flaky detectados: {len(all_flaky_metrics)}**")
                        st.dataframe(
                            flaky_metrics_df.sort_values('Taxa de Falha', ascending=False),
                            use_container_width=True,
                            height=400
                        )
                    
                    with tab2:
                        high_severity = [m for m in all_flaky_metrics if m['Severidade'] == 'high']
                        if high_severity:
                            st.markdown(f"**Testes com alta severidade: {len(high_severity)}**")
                            st.warning("""
                            ⚠️ Estes testes falham entre 40-60% das execuções, indicando instabilidade crítica.
                            Requerem atenção imediata!
                            """)
                            high_severity_df = pd.DataFrame(high_severity)
                            st.dataframe(high_severity_df, use_container_width=True)
                        else:
                            st.success("✅ Nenhum teste com alta severidade detectado!")
                    
                    with tab3:
                        st.markdown("### Distribuição de Taxas de Falha")
                        st.markdown("""
                        Este gráfico mostra quantos testes caem em cada faixa de taxa de falha.
                        Idealmente, queremos a maioria dos testes flaky na faixa baixa (< 10%).
                        """)
                        
                        # Create histogram of failure rates
                        failure_rates = [float(m['Taxa de Falha'].rstrip('%')) / 100 for m in all_flaky_metrics]
                        import numpy as np
                        
                        bins = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
                        hist, bin_edges = np.histogram(failure_rates, bins=bins)
                        
                        hist_df = pd.DataFrame({
                            'Taxa de Falha': [f"{int(b*100)}-{int(bins[i+1]*100)}%" 
                                            for i, b in enumerate(bins[:-1])],
                            'Quantidade': hist
                        }).set_index('Taxa de Falha')
                        
                        st.bar_chart(hist_df)
                        
                        # Summary statistics
                        st.markdown("### Estatísticas Resumidas")
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Taxa Média", f"{np.mean(failure_rates):.1%}")
                        with col2:
                            st.metric("Taxa Mediana", f"{np.median(failure_rates):.1%}")
                        with col3:
                            st.metric("Taxa Mínima", f"{np.min(failure_rates):.1%}")
                        with col4:
                            st.metric("Taxa Máxima", f"{np.max(failure_rates):.1%}")
                    
                else:
                    st.info("ℹ️ Nenhum teste flaky detectado com significância estatística.")
            
            # Statistical Insights
            st.subheader("🔍 Insights Estatísticos")
            st.markdown("""
            ### Como interpretar as métricas:
            
            **Taxa de Falha**: Proporção de execuções em que o teste falhou (0-100%)
            - Valores próximos a 0% ou 100% indicam comportamento determinístico
            - Valores entre 10-90% indicam verdadeira flakiness
            
            **P-Value**: Significância estatística (teste binomial)
            - Valores < 0.05 indicam flakiness estatisticamente significativa
            - Valores > 0.05 podem ser falhas aleatórias ou dados insuficientes
            
            **Intervalo de Confiança (95%)**: Faixa estimada da verdadeira taxa de falha
            - Intervalos mais estreitos = maior certeza
            - Intervalos mais largos = menos execuções ou maior variabilidade
            
            **Severidade**:
            - **Baixa**: Falhas ocasionais (< 10%)
            - **Média**: Falhas frequentes (10-40%)  
            - **Alta**: Instabilidade crítica (40-60%)
            - **Stable Fail**: Sempre falha (não é flaky, é um bug)
            - **Stable Pass**: Sempre passa (determinístico)
            """)
        else:
            st.info("""
            ℹ️ **Métricas avançadas não disponíveis.**
            
            Execute testes com múltiplas rodadas usando `pytest-rerun` para gerar 
            métricas estatísticas detalhadas de flakiness.
            """)
        
        # Tabela detalhada
        st.header("📋 Dados Detalhados")
        
        # Colunas para exibir na tabela
        display_columns = [
            'project', 'tool', 'timestamp', 'total_tests', 'total_flaky', 
            'error_lines', 'warning_lines', 'failed_lines'
        ]
        
        available_columns = [col for col in display_columns if col in filtered_df.columns]
        
        # Tabela interativa
        st.dataframe(
            filtered_df[available_columns].sort_values('timestamp', ascending=False),
            use_container_width=True,
            height=400
        )
        
        # Análise de testes flaky específicos
        if 'flaky_tests' in filtered_df.columns:
            st.header("🎯 Análise de Testes Flaky Específicos")
            
            # Coleta todos os testes flaky
            all_flaky_tests = []
            for _, row in filtered_df.iterrows():
                if row['flaky_tests']:
                    all_flaky_tests.extend(row['flaky_tests'])
            
            if all_flaky_tests:
                # Top testes flaky
                flaky_counts = pd.Series(all_flaky_tests).value_counts().head(20)
                
                st.subheader("Top 20 Testes Flaky Mais Frequentes")
                # Cria DataFrame para melhor visualização
                flaky_df = pd.DataFrame({
                    'Teste': flaky_counts.index,
                    'Ocorrências': flaky_counts.values
                }).set_index('Teste')
                
                st.bar_chart(flaky_df, height=600)
                
                # Detalhes dos testes mais problemáticos
                st.subheader("🔍 Testes Mais Problemáticos")
                top_5_flaky = flaky_counts.head(5)
                
                for test_name, count in top_5_flaky.items():
                    with st.expander(f"🐛 {test_name} ({count} ocorrências)"):
                        # Mostra em quais execuções este teste apareceu
                        test_occurrences = []
                        for _, row in filtered_df.iterrows():
                            if test_name in row.get('flaky_tests', []):
                                test_occurrences.append({
                                    'projeto': row['project'],
                                    'ferramenta': row['tool'],
                                    'execução': row['timestamp']
                                })
                        
                        if test_occurrences:
                            st.write("**Ocorrências:**")
                            occurrence_df = pd.DataFrame(test_occurrences)
                            st.dataframe(occurrence_df, use_container_width=True)
        
        # Estatísticas por ferramenta
        st.header("🔧 Comparação de Ferramentas")
        
        tool_stats = filtered_df.groupby('tool').agg({
            'total_flaky': ['count', 'sum', 'mean'],
            'error_lines': 'mean',
            'warning_lines': 'mean'
        }).round(2)
        
        # Achata as colunas multi-nível
        tool_stats.columns = ['_'.join(col).strip() for col in tool_stats.columns.values]
        tool_stats = tool_stats.rename(columns={
            'total_flaky_count': 'Execuções',
            'total_flaky_sum': 'Total Testes Flaky',
            'total_flaky_mean': 'Média Testes Flaky',
            'error_lines_mean': 'Média Erros',
            'warning_lines_mean': 'Média Warnings'
        })
        
        st.dataframe(tool_stats, use_container_width=True)
        
        # Download dos dados
        st.header("💾 Download dos Dados")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Download CSV
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="📄 Download CSV",
                data=csv,
                file_name=f"flaky_tests_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        with col2:
            # Download JSON
            json_data = filtered_df.to_json(orient='records', indent=2)
            st.download_button(
                label="📋 Download JSON", 
                data=json_data,
                file_name=f"flaky_tests_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar os dados: {str(e)}")
        st.info("Verifique se o diretório de resultados está correto e contém dados válidos.")

if __name__ == "__main__":
    main()
