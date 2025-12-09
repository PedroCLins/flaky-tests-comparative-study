#!/usr/bin/env python3
"""
Dashboard web interativo para visualização de resultados de testes flaky.

Este dashboard permite visualizar e filtrar os resultados dos experimentos
de forma interativa usando Streamlit.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os
from pathlib import Path
from datetime import datetime
import sys

# Adiciona o diretório pai ao path para importar o analisador
sys.path.append(str(Path(__file__).parent))
from analyze_results import FlakyTestAnalyzer

def load_data(results_dir: str) -> pd.DataFrame:
    """Carrega e processa os dados."""
    analyzer = FlakyTestAnalyzer(results_dir)
    analyzer.scan_results()
    
    if not analyzer.data:
        return pd.DataFrame()
    
    df = pd.DataFrame(analyzer.data)
    # Converte timestamp para datetime
    df['datetime'] = pd.to_datetime(df['timestamp'], format='%Y-%m-%d_%H-%M-%S', errors='coerce')
    return df

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
        df = get_data(results_dir)
        
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
            flaky_by_project = filtered_df.groupby('project')['total_flaky'].sum().reset_index()
            fig_bar = px.bar(
                flaky_by_project, 
                x='project', 
                y='total_flaky',
                title="Testes Flaky por Projeto",
                labels={'total_flaky': 'Número de Testes Flaky', 'project': 'Projeto'}
            )
            fig_bar.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_bar, use_container_width=True)
        
        with col2:
            # Distribuição de erros por ferramenta
            fig_box = px.box(
                filtered_df, 
                x='tool', 
                y='error_lines',
                title="Distribuição de Erros por Ferramenta",
                labels={'error_lines': 'Linhas de Erro', 'tool': 'Ferramenta'}
            )
            st.plotly_chart(fig_box, use_container_width=True)
        
        # Timeline (se houver dados de tempo)
        if 'datetime' in filtered_df.columns and not filtered_df['datetime'].isna().all():
            st.subheader("⏰ Evolução Temporal")
            
            timeline_data = filtered_df.sort_values('datetime')
            fig_timeline = px.line(
                timeline_data, 
                x='datetime', 
                y='total_flaky',
                color='project',
                title="Evolução dos Testes Flaky ao Longo do Tempo",
                labels={'total_flaky': 'Testes Flaky', 'datetime': 'Data/Hora'}
            )
            st.plotly_chart(fig_timeline, use_container_width=True)
        
        # Tabela detalhada
        st.header("📋 Dados Detalhados")
        
        # Colunas para exibir na tabela
        display_columns = [
            'project', 'tool', 'timestamp', 'total_flaky', 
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
                
                fig_flaky = px.bar(
                    x=flaky_counts.values,
                    y=flaky_counts.index,
                    orientation='h',
                    title="Top 20 Testes Flaky Mais Frequentes",
                    labels={'x': 'Número de Ocorrências', 'y': 'Teste'}
                )
                fig_flaky.update_layout(height=600)
                st.plotly_chart(fig_flaky, use_container_width=True)
                
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
