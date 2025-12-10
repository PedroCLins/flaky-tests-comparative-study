# 🔬 Flaky Tests Comparative Study

**Estudo Empírico Comparativo de Detecção de Testes Flaky em Projetos Open-Source**

> Projeto da disciplina IF1009 - Testes e Validação de Software  
> Centro de Informática - UFPE | 2025.1

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Java](https://img.shields.io/badge/Java-8%2F11+-orange.svg)](https://www.java.com/)
[![License](https://img.shields.io/badge/license-Academic-green.svg)](LICENSE)

---

## 📚 Índice

- [Visão Geral](#-visão-geral)- [Quick Start](#-quick-start)- [Setup Inicial](#-setup-inicial)
- [Comandos Makefile](#-comandos-makefile)
- [Documentação Completa](#-documentação-completa)
- [Principais Conclusões](#-principais-conclusões)
- [FAQ e Troubleshooting](#-faq-e-troubleshooting)
- [Requisitos](#-requisitos)
- [Referências](#-referências)
- [Equipe](#-equipe)

## 📋 Visão Geral

## �📋 Visão Geral
Este projeto conduz um **estudo empírico comparativo** sobre detecção de testes flaky em 8 projetos open-source, utilizando análise estatística rigorosa.

### 🎯 Objetivo

Avaliar e comparar a eficácia de duas ferramentas de detecção de testes flaky (NonDex para Java e pytest-rerun para Python) através de métricas estatísticas robustas, identificando padrões e características dos testes flaky em diferentes ecossistemas de linguagens.

### ✨ Características

- 📊 **Análise Estatística Rigorosa**: Wilson Score CI (95%), teste binomial com α = 0.05
- 🔄 **Execuções Múltiplas**: 20 rodadas para projetos Python, detecção automatizada para Java
- 📈 **Dashboard Interativo**: Visualização em tempo real com Streamlit (3 modos de escala)
- 📋 **Relatórios Completos**: CSV, JSON, Markdown e HTML exportáveis
- 🎨 **Métricas Avançadas**: Taxa de falha, p-value, severidade, evolução temporal
- 🔧 **Automação Total**: Makefile com comandos simples para todas as operações

### Ferramentas de Detecção
- **NonDex** (Java): Detecta não-determinismo através de múltiplas execuções com diferentes ordenações de coleções e APIs
- **pytest-rerun** (Python): Detecta testes flaky através de 20 execuções repetidas com análise estatística (p-value, IC 95%)

### Projetos Analisados

**Java (4 projetos - Apache Commons):**
- `commons-lang` (57,778 testes) - Utilidades para Java
- `commons-codec` (18,549 testes) - Codificadores/decodificadores
- `commons-collections` (8,428 testes) - Estruturas de dados
- `guava` - Core libraries do Google

**Python (4 projetos):**
- `httpie` - Cliente HTTP moderno
- `flask` - Framework web
- `black` - Formatador de código
- `httpx` - Cliente HTTP assíncrono

### Métricas Estatísticas

O sistema calcula **métricas rigorosas** para cada teste:
- Taxa de falha e intervalos de confiança (95%)
- P-value e significância estatística (α = 0.05)
- Classificação de severidade (low/medium/high)
- Variância e desvio padrão

**Resultados atuais**: 680 testes flaky detectados em 3/8 projetos, com taxa variando de 0.07% a 1.16%.

---

## 🚀 Quick Start

```bash
# 1. Clone o repositório
git clone https://github.com/PedroCLins/flaky-tests-comparative-study.git
cd flaky-tests-comparative-study

# 2. Configure o ambiente
make setup

# 3. Execute todos os testes e visualize
make all

# 4. Abra o dashboard interativo
make dashboard
```

O dashboard estará disponível em `http://localhost:8501`

---

## 🚀 Setup Inicial

### 1. Clone este repositório

```bash
git clone https://github.com/PedroCLins/flaky-tests-comparative-study.git
cd flaky-tests-comparative-study
```

### 2. Crie o diretório de experimentos

Crie um diretório separado para os projetos que serão testados:

```bash
cd ..
mkdir flaky-tests-experiments
cd flaky-tests-experiments
```

### 3. Clone os projetos a serem analisados

Clone os repositórios dos projetos que você deseja analisar:

**Projetos Java (Apache Commons):**
```bash
git clone https://github.com/apache/commons-lang.git
git clone https://github.com/apache/commons-codec.git
git clone https://github.com/apache/commons-collections.git
git clone https://github.com/google/guava.git
```

**Projetos Python:**
```bash
git clone https://github.com/httpie/cli.git httpie
git clone https://github.com/pallets/flask.git
git clone https://github.com/psf/black.git
git clone https://github.com/encode/httpx.git
```

Estrutura esperada:
```
.
├── flaky-tests-comparative-study/    # Este repositório
└── flaky-tests-experiments/          # Projetos a serem analisados
    ├── commons-lang/
    ├── commons-codec/
    ├── commons-collections/
    ├── guava/
    ├── httpie/
    ├── flask/
    ├── black/
    └── httpx/
```

### 4. Configure o arquivo `.env`

Volte para o diretório do projeto e crie um arquivo `.env`:

```bash
cd ../flaky-tests-comparative-study
```

Crie o arquivo `.env` com o seguinte conteúdo:

```bash
# Directory paths
EXPERIMENT_DIR=../flaky-tests-experiments
SCRIPTS_DIR=./scripts
RESULTS_DIR=./results

# Project names
JAVA_PROJECTS=commons-lang commons-codec commons-collections guava
PYTHON_PROJECTS=httpie flask black httpx

# Test configuration
PYTEST_ROUNDS=20  # Número de execuções para análise estatística
```

**Nota:** O número de rodadas (20) foi escolhido para fornecer poder estatístico adequado (>90%) para detectar testes flaky com taxa de falha ≥ 10%.

### 5. Instale as dependências

Execute o setup para instalar todas as dependências necessárias:

```bash
make setup
```

Isso irá:
- Verificar instalação de Java e Maven
- Criar um ambiente virtual Python (`.venv`)
- Instalar pacotes pytest e visualização necessários

## 🏃 Executando os Testes

### Executar tudo

Para executar todas as ferramentas em todos os projetos:

```bash
make all
```

### Executar ferramentas específicas

**NonDex (apenas projetos Java):**
```bash
make nondex
```

**pytest-rerun (apenas projetos Python):**
```bash
make python
```

### Execução em Background

Para processos longos, recomenda-se usar `tmux`:

```bash
# Cria uma sessão tmux
tmux new -s flaky-tests

# Execute os testes
make all

# Desanexar: Pressione Ctrl+b, depois d
# Reanexar depois: tmux attach -t flaky-tests
```

Ou execute em background simples:

```bash
nohup make all > output.log 2>&1 &
tail -f output.log
```

Veja o arquivo [RUN_GUIDE.md](RUN_GUIDE.md) para mais opções de execução em background.

## 📊 Resultados

Os resultados são salvos em `results/` organizados por projeto e ferramenta:

```
results/
├── commons-lang/
│   └── nondex/
│       └── 2025-12-10_16-21-10/
│           ├── commit.txt
│           ├── nondex.log          # Log completo do NonDex
│           ├── summary.txt         # Resumo de erros e warnings
│           └── metadata.json       # Metadados da execução
├── httpie/
│   └── pytest-rerun/
│       └── 2025-12-10_16-21-10/
│           ├── commit.txt
│           ├── runs.csv            # Dados por rodada (para métricas)
│           ├── summary.txt         # Resumo de testes flaky
│           ├── run_1.log
│           ├── run_2.log
│           ├── ...
│           ├── run_20.log
│           └── metadata.json
└── ...
```

### Visualização e Análise

Após executar os testes, analise os resultados:

```bash
# Gerar relatórios e CSVs com métricas
make visualize

# Abrir dashboard interativo (Streamlit)
make dashboard
```

#### 🎨 Dashboard Interativo

O dashboard Streamlit oferece uma interface completa para análise:

**Visão Geral**
- 📊 Métricas agregadas por projeto (total de testes, flaky detectados, taxa %)
- 📈 Gráficos comparativos com 3 modos de visualização:
  - **Separado por Projeto**: Gráficos individuais para melhor análise
  - **Escala Logarítmica**: Visualização simultânea de projetos com escalas muito diferentes
  - **Todos Juntos**: Comparação direta em escala linear
- 🎯 Indicadores visuais de severidade (baixo/médio/alto)

**Análise Detalhada Python (pytest-rerun)**
- 🔬 Métricas individuais por teste com estatísticas completas
- 📉 Taxa de falha com Intervalo de Confiança Wilson (95%)
- 🧪 P-valor e significância estatística (α = 0.05)
- 📊 Gráficos de distribuição de falhas por rodada
- ⏰ Evolução temporal das detecções

**Análise Java (NonDex)**
- ⚠️ Lista de testes com não-determinismo detectado
- 📋 Logs completos de warnings do NonDex
- 📊 Contagem agregada por projeto

**Exportação**
- 📋 Tabelas filtráveis e ordenáveis interativamente
- 💾 Download em CSV/JSON para análise posterior
- 📄 Relatório HTML completo com todos os dados

**Relatórios gerados** em `visualization/reports/`:
- `project_summary.csv` - Métricas agregadas por projeto
- `test_metrics_detailed.csv` - Métricas individuais de cada teste
- `flaky_tests_metrics.csv` - Apenas testes com p < 0.05
- `summary_report.md` - Relatório em markdown

### Exemplo de Resultados Reais

Baseado nas execuções realizadas:

| Projeto | Total Testes | Flaky Detectados | Taxa | Severidade |
|---------|--------------|------------------|------|------------|
| commons-lang | 57,778 | 673 | 1.16% | Crítico |
| commons-collections | 8,428 | 6 | 0.07% | Baixo |
| commons-codec | 18,549 | 0 | 0% | - |
| httpie | 3 | 1 | 33% | Baixo (5% falha) |
| flask | 1 | 0 | 0% | - |

## 🛠️ Estrutura do Projeto

```
.
├── Makefile                      # Comandos principais
├── README.md                     # Este arquivo
├── RUN_GUIDE.md                  # Guia de execução em background
├── METRICS.md                    # Documentação das métricas
├── RELATORIO_METRICAS.md         # Relatório acadêmico completo
├── .env                          # Configuração (criar manualmente)
├── .gitignore                    # Arquivos ignorados
│
├── scripts/
│   ├── setup_dependencies.sh     # Setup de dependências
│   ├── run_nondex.sh             # Script NonDex
│   ├── run_py_flaky_detection.sh # Script pytest (20 rodadas)
│   ├── run_visualization.sh      # Script de visualização
│   ├── cleanup.sh                # Limpeza de resultados
│   └── monitor_tests.sh          # Monitoramento de execução
│
├── visualization/
│   ├── analyze_results.py        # Analisador principal
│   ├── dashboard.py              # Dashboard Streamlit
│   ├── metrics.py                # Cálculo de métricas estatísticas
│   ├── html_report.py            # Gerador de relatórios HTML
│   ├── requirements.txt          # Dependências Python
│   ├── activate.sh               # Script de ativação do venv
│   └── reports/                  # Relatórios gerados
│       ├── project_summary.csv
│       ├── test_metrics_detailed.csv
│       ├── flaky_tests_metrics.csv
│       └── summary_report.md
│
└── results/                      # Resultados dos experimentos
    ├── commons-lang/nondex/
    ├── commons-collections/nondex/
    ├── httpie/pytest-rerun/
    └── ...
```

## 📝 Comandos Makefile

| Comando | Descrição |
|---------|-----------|
| `make all` | Executa setup + todos os testes + visualização |
| `make setup` | Instala dependências (Java, Maven, Python, venv) |
| `make java` | Executa NonDex em todos os projetos Java |
| `make nondex` | Alias para `make java` |
| `make python` | Executa pytest-rerun (20 rodadas) em projetos Python |
| `make visualize` | Gera relatórios CSV, JSON e markdown |
| `make dashboard` | Abre dashboard interativo Streamlit (porta 8501) |
| `make clean` | Remove resultados e arquivos temporários |
| `make help` | Lista todos os comandos disponíveis |

### Comandos Avançados

```bash
# Executar apenas um projeto específico
RUN_PROJECT=commons-lang make nondex

# Alterar número de rodadas pytest (padrão: 20)
PYTEST_ROUNDS=50 make python

# Executar em background com tmux
tmux new -s flaky-tests
make all
# Ctrl+b, d para desanexar

# Monitorar progresso
tail -f results/*/*/summary.txt
```

## 📖 Documentação Completa

Para informações detalhadas sobre as métricas utilizadas e metodologia estatística:

- **[METRICS.md](METRICS.md)** - Documentação técnica das métricas implementadas
- **[RELATORIO_METRICAS.md](RELATORIO_METRICAS.md)** - Relatório acadêmico completo com fundamentação estatística
- **[RUN_GUIDE.md](RUN_GUIDE.md)** - Guia detalhado de execução e monitoramento
- **[TEST_STATUS.md](TEST_STATUS.md)** - Status atual dos testes por projeto
- **[FINAL_STATUS.md](FINAL_STATUS.md)** - Status final da execução experimental

### Métricas Estatísticas Implementadas

**Para projetos Python (pytest-rerun):**
- Taxa de falha individual por teste
- Intervalo de Confiança Wilson Score (95%)
- P-valor (teste binomial, α = 0.05)
- Classificação de severidade baseada na taxa de falha
- Evolução temporal das detecções

**Para projetos Java (NonDex):**
- Detecção agregada de não-determinismo
- Contagem de testes flaky detectados
- Logs completos de warnings e erros

## 🎯 Principais Conclusões

Baseado em 24 execuções completas (3 rodadas × 8 projetos):

1. **Detecção Eficaz**: 680 testes flaky identificados em 3 dos 8 projetos analisados
2. **Projeto Mais Crítico**: commons-lang com 673 testes flaky (1.16% da base de testes)
3. **Ferramentas Complementares**: NonDex e pytest-rerun detectam tipos diferentes de flakiness
4. **Distribuição Desigual**: Concentração de problemas em poucos projetos indica fatores específicos

## ❓ FAQ e Troubleshooting

<details>
<summary><b>Por que 20 rodadas para pytest?</b></summary>

O número de 20 rodadas foi escolhido para fornecer **poder estatístico > 90%** para detectar testes com taxa de falha ≥ 10%, conforme análise estatística detalhada em [RELATORIO_METRICAS.md](RELATORIO_METRICAS.md).
</details>

<details>
<summary><b>Como interpretar o p-value?</b></summary>

Um p-value < 0.05 indica que a probabilidade de observar aquele padrão de falhas por acaso é menor que 5%, sugerindo **forte evidência estatística** de flakiness. Veja explicação completa em [METRICS.md](METRICS.md).
</details>

<details>
<summary><b>Por que alguns projetos não têm métricas detalhadas?</b></summary>

- **Projetos Java (NonDex)**: Fornecem apenas detecção agregada, sem dados por rodada individual
- **Projetos Python (pytest-rerun)**: Fornecem dados de todas as 20 rodadas, permitindo cálculo completo de métricas estatísticas
</details>

<details>
<summary><b>Os testes estão travados/muito lentos</b></summary>

Alguns projetos Java (especialmente commons-lang com 57k testes) podem levar várias horas. Use:
```bash
# Monitorar progresso
tail -f results/*/*/summary.txt

# Executar em background com tmux
tmux new -s flaky-tests
make all
# Ctrl+b, d para desanexar
```
</details>

<details>
<summary><b>Como limpar resultados antigos?</b></summary>

```bash
make clean  # Remove todos os resultados e temporários
```
</details>

## 🔧 Requisitos

- **Java**: JDK 8 ou 11+
- **Maven**: 3.6+
- **Python**: 3.8+
- **Git**: Para clonar repositórios

## 📚 Referências

### Ferramentas de Detecção
- **NonDex** - [GitHub](https://github.com/TestingResearchIllinois/NonDex) | Bell, J., et al. "DeFlaker: Automatically Detecting Flaky Tests." ICSE 2018.
- **pytest-rerunfailures** - [GitHub](https://github.com/pytest-dev/pytest-rerunfailures) | Plugin para re-execução de testes pytest

### Projetos Analisados
- **Apache Commons Lang** - [GitHub](https://github.com/apache/commons-lang)
- **Apache Commons Collections** - [GitHub](https://github.com/apache/commons-collections)
- **Apache Commons Codec** - [GitHub](https://github.com/apache/commons-codec)
- **Google Guava** - [GitHub](https://github.com/google/guava)
- **HTTPie** - [GitHub](https://github.com/httpie/httpie)
- **Flask** - [GitHub](https://github.com/pallets/flask)
- **Black** - [GitHub](https://github.com/psf/black)
- **HTTPX** - [GitHub](https://github.com/encode/httpx)

### Literatura Relacionada
- Luo, Q., et al. "An Empirical Analysis of Flaky Tests." FSE 2014.
- Thorve, S., et al. "An Empirical Study of Flaky Tests in Android Apps." ICSME 2018.
- Eck, M., et al. "Understanding Flaky Tests: The Developer's Perspective." ESEC/FSE 2019.

## 👥 Equipe

**CIn - UFPE | Testes e Validação de Software**

- Áriston Aragão \<aaa10@cin.ufpe.br>
- Fabriely Luana \<flps@cin.ufpe.br>
- Pedro Campelo \<pcl@cin.ufpe.br>

## 📄 Licença

Este projeto foi desenvolvido para fins acadêmicos como parte da disciplina de Testes e Validação de Software do Centro de Informática da UFPE.

Os projetos analisados mantêm suas respectivas licenças originais (Apache 2.0, MIT, etc.).
