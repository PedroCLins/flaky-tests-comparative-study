# 📊 Sistema de Visualização de Testes Flaky

Este sistema fornece ferramentas completas para análise, visualização e geração de relatórios dos resultados de detecção de testes flaky.

## 🚀 Configuração Rápida

### 1. Configurar Ambiente

```bash
# No diretório raiz do projeto
python visualization/main.py setup
```

### 2. Ativar Ambiente

```bash
source visualization/activate.sh
```

### 3. Executar Análise

```bash
# Análise completa com todos os relatórios
python visualization/main.py analyze

# Ou usar o dashboard interativo
python visualization/main.py dashboard
```

## 📋 Funcionalidades

### 🔍 Análise de Dados
- **Detecção automática** de resultados de experimentos
- **Processamento** de logs do NonDex, iDFlakies e outras ferramentas
- **Extração** de métricas e estatísticas detalhadas
- **Identificação** de testes flaky específicos

### 📊 Visualizações
- **Gráficos interativos** com Plotly/Matplotlib
- **Dashboards web** responsivos com Streamlit
- **Comparações** entre projetos e ferramentas
- **Timeline** de evolução dos testes flaky

### 📑 Relatórios
- **HTML elegante** com gráficos incorporados
- **Markdown** para documentação
- **CSV/JSON** para análise posterior
- **Exportação** de dados estruturados

## 🛠️ Comandos Disponíveis

### Análise Completa
```bash
python visualization/main.py analyze --results-dir results --format all
```

### Relatório HTML
```bash
python visualization/main.py html-report --results-dir results --output report.html
```

### Dashboard Web
```bash
python visualization/main.py dashboard --port 8501
```

### Configuração
```bash
python visualization/main.py setup
```

## 📊 Estrutura dos Resultados

O sistema espera a seguinte estrutura de diretórios:

```
results/
├── commons-lang/
│   ├── nondex/
│   │   ├── 2025-12-08_22-20-37/
│   │   │   ├── summary.txt
│   │   │   ├── nondex.log
│   │   │   └── metadata.json
│   │   └── ...
│   └── idflakies/
│       └── ...
├── mockito/
│   └── nondex/
│       └── ...
└── pandas/
    └── ...
```

### Formatos de Entrada Suportados

#### 1. Summary.txt
```
project: nome-do-projeto
tool: ferramenta-utilizada
log: caminho-para-log

error_lines: 123
warning_lines: 45
failed_lines: 12
```

#### 2. Metadata.json
```json
{
  "project": "nome-do-projeto",
  "tool": "nondex",
  "date": "2025-12-08T22:20:37",
  "build_system": "maven"
}
```

#### 3. Logs de Ferramentas
- **NonDex**: Detecta padrões `[WARNING] TestClass#method`
- **iDFlakies**: Processa saída específica da ferramenta
- **Outros**: Formatos personalizáveis

## 📈 Métricas Coletadas

### Por Projeto
- Total de execuções
- Testes flaky detectados
- Taxa de erro médio
- Evolução temporal

### Por Ferramenta
- Eficácia de detecção
- Tipos de problemas encontrados
- Comparação de performance

### Por Teste
- Frequência de falha
- Projetos afetados
- Histórico de ocorrências

## 🎨 Tipos de Visualização

### 1. Dashboard Interativo
- **Filtros dinâmicos** por projeto, ferramenta e data
- **Gráficos interativos** com zoom e hover
- **Tabelas ordenáveis** com busca
- **Exportação** de dados filtrados

### 2. Relatórios HTML
- **Design responsivo** para mobile/desktop
- **Gráficos incorporados** em alta qualidade
- **Navegação intuitiva** por seções
- **Impressão otimizada**

### 3. Análise Programática
- **APIs Python** para análise customizada
- **DataFrames Pandas** para manipulação
- **Exportação** em múltiplos formatos

## 🔧 Personalização

### Adicionando Nova Ferramenta

1. **Edite** `analyze_results.py`:
```python
def _extract_flaky_tests(self, log_file, tool):
    if tool == 'minha_ferramenta':
        # Adicione lógica de parsing aqui
        pass
```

2. **Teste** com dados reais:
```bash
python visualization/main.py analyze --results-dir meus_resultados
```

### Customizando Visualizações

1. **Modifique** `html_report.py` para novos gráficos
2. **Adicione** seções no template HTML
3. **Implemente** métricas específicas

### Configurando Filtros

1. **Edite** `dashboard.py` para novos filtros
2. **Adicione** widgets Streamlit
3. **Implemente** lógica de filtragem

## 📦 Dependências

### Principais
- `pandas` - Manipulação de dados
- `matplotlib/seaborn` - Gráficos estáticos
- `plotly` - Gráficos interativos
- `streamlit` - Dashboard web

### Opcionais
- `jupyter` - Notebooks de análise
- `openpyxl` - Export Excel
- `jinja2` - Templates avançados

## 🐛 Troubleshooting

### Problema: "Nenhum resultado encontrado"
**Solução**: Verifique se:
- O diretório `results/` existe
- Há arquivos `summary.txt` nas subpastas
- A estrutura de diretórios está correta

### Problema: "Módulo não encontrado"
**Solução**: 
```bash
# Reinstale dependências
source visualization/activate.sh
pip install -r visualization/requirements.txt
```

### Problema: Dashboard não abre
**Solução**:
```bash
# Verifique se Streamlit está instalado
streamlit --version

# Execute manualmente
streamlit run visualization/dashboard.py
```

## 📊 Exemplos de Uso

### Análise de Projeto Específico
```python
from analyze_results import FlakyTestAnalyzer

analyzer = FlakyTestAnalyzer('results')
analyzer.scan_results()

# Filtra por projeto
mockito_data = [d for d in analyzer.data if d['project'] == 'mockito']
print(f"Mockito teve {len(mockito_data)} execuções")
```

### Comparação de Ferramentas
```python
import pandas as pd

df = pd.DataFrame(analyzer.data)
comparison = df.groupby('tool')['total_flaky'].sum()
print(comparison)
```

### Export para Análise Externa
```bash
# Gera CSV para análise em Excel/R/etc
python visualization/main.py analyze --format csv
```

## 🤝 Contribuição

1. **Clone** o repositório
2. **Configure** o ambiente com `python visualization/main.py setup`
3. **Desenvolva** novas funcionalidades
4. **Teste** com dados reais
5. **Documente** as mudanças

## 📝 Licença

Este sistema de visualização é parte do projeto de detecção de testes flaky desenvolvido no CIn/UFPE.

---

Para dúvidas ou sugestões, consulte a documentação principal do projeto ou abra uma issue.
