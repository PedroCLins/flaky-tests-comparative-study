# flaky-tests-comparative-study

Projeto da cadeira IF1009 - Testes e Validação de Software. O objetivo deste projeto é conduzir estudos empíricos comparativos e exploratórios em detecção e mitigação de testes flaky em projetos reais.

## 📋 Visão Geral

Este projeto executa três ferramentas de detecção de testes flaky em projetos Java e Python:
- **NonDex**: Detecta testes não-determinísticos em projetos Java (Maven/Gradle)
- **iDFlakies**: Detecta testes flaky através de reordenação em projetos Java
- **pytest-rerun**: Detecta testes flaky em projetos Python através de múltiplas execuções

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

**Projetos Java:**
```bash
git clone https://github.com/apache/commons-lang.git
git clone https://github.com/mockito/mockito.git
```

**Projetos Python:**
```bash
git clone https://github.com/pandas-dev/pandas.git
git clone https://github.com/psf/requests.git
```

Estrutura esperada:
```
.
├── flaky-tests-comparative-study/    # Este repositório
└── flaky-tests-experiments/          # Projetos a serem analisados
    ├── commons-lang/
    ├── mockito/
    ├── pandas/
    └── requests/
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
JAVA_PROJECTS=commons-lang mockito
PYTHON_PROJECTS=pandas requests
```

**Nota:** Ajuste os nomes dos projetos em `JAVA_PROJECTS` e `PYTHON_PROJECTS` conforme os repositórios que você clonou.

### 5. Instale as dependências

Execute o setup para instalar todas as dependências necessárias:

```bash
make setup
```

Isso irá:
- Verificar instalação de Java e Maven
- Criar um ambiente virtual Python (`.venv`)
- Instalar pacotes pytest necessários
- Clonar e configurar iDFlakies

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

**iDFlakies (apenas projetos Java):**
```bash
make idflakies
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
│   ├── nondex/
│   │   └── 2025-12-08_11-30-15/
│   │       ├── commit.txt
│   │       ├── nondex.log
│   │       └── metadata.json
│   └── idflakies/
│       └── ...
├── mockito/
│   └── ...
├── pandas/
│   └── pytest-rerun/
│       └── 2025-12-08_11-30-15/
│           ├── commit.txt
│           ├── runs.csv
│           ├── run_1.log
│           ├── run_2.log
│           └── metadata.json
└── requests/
    └── ...
```

## 🛠️ Estrutura do Projeto

```
.
├── Makefile                    # Comandos principais
├── README.md                   # Este arquivo
├── RUN_GUIDE.md               # Guia de execução em background
├── .env                       # Configuração (criar manualmente)
├── .gitignore                 # Arquivos ignorados
├── scripts/
│   ├── setup_dependencies.sh  # Setup de dependências
│   ├── run_nondex.sh         # Script NonDex
│   ├── run_idflakies.sh      # Script iDFlakies
│   └── run_py_flaky_detection.sh  # Script pytest
├── tools/
│   └── iDFlakies/            # Clone do iDFlakies (criado no setup)
└── results/                   # Resultados dos experimentos
```

## 📝 Comandos Makefile

| Comando | Descrição |
|---------|-----------|
| `make all` | Executa setup + todos os testes |
| `make setup` | Instala dependências |
| `make java` | Executa NonDex + iDFlakies |
| `make nondex` | Executa apenas NonDex |
| `make idflakies` | Executa apenas iDFlakies |
| `make python` | Executa detecção pytest |

## 🔧 Requisitos

- **Java**: JDK 8 ou 11+
- **Maven**: 3.6+
- **Python**: 3.8+
- **Git**: Para clonar repositórios

## 📚 Referências

- [NonDex](https://github.com/TestingResearchIllinois/NonDex)
- [iDFlakies](https://github.com/idflakies/iDFlakies)
- [pytest-rerunfailures](https://github.com/pytest-dev/pytest-rerunfailures)

## 👥 Equipe

Áriston Aragão \<aaa10>
Fabriely Luana \<flps>
Pedro Campelo \<pcl>
