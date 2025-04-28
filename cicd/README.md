# Agent para Criação e Manutenção de Pipelines CI/CD

Este diretório contém o código e a documentação para o Agent de Criação e Manutenção de Pipelines CI/CD, que é capaz de:

- Analisar automaticamente a estrutura do repositório de código
- Identificar a ferramenta de CI/CD mais adequada (Jenkins, GitHub Actions, GitLab CI, etc.)
- Gerar pipelines CI/CD baseados no tipo de projeto e tecnologias utilizadas
- Otimizar pipelines existentes para melhorar performance
- Detectar e corrigir falhas em pipelines

## Arquitetura

O agent utiliza o framework LangChain para orquestração e um modelo de linguagem local (Llama 3) para análise e geração de código. A arquitetura é composta por:

1. **Analisador de Repositório**: Analisa a estrutura do repositório para identificar linguagens, frameworks e dependências
2. **Seletor de Ferramenta CI/CD**: Determina a ferramenta de CI/CD mais adequada com base no projeto
3. **Gerador de Pipeline**: Cria arquivos de configuração de pipeline para a ferramenta selecionada
4. **Otimizador de Pipeline**: Analisa e otimiza pipelines existentes
5. **Detector de Falhas**: Identifica e sugere correções para falhas em pipelines

## Requisitos

- Python 3.10+
- LangChain
- Llama 3 (8B ou 70B)
- Ollama (para execução local do modelo)
- Bibliotecas de integração com ferramentas de CI/CD

## Estrutura de Arquivos

```
cicd/
├── README.md                    # Documentação do agent
├── requirements.txt             # Dependências Python
├── main.py                      # Ponto de entrada principal
├── config.py                    # Configurações do agent
├── models/                      # Configurações de modelos
│   ├── __init__.py
│   └── llm.py                   # Configuração do modelo de linguagem
├── analyzers/                   # Analisadores de repositório
│   ├── __init__.py
│   ├── repo_analyzer.py         # Analisador de estrutura de repositório
│   └── tech_detector.py         # Detector de tecnologias
├── generators/                  # Geradores de pipeline
│   ├── __init__.py
│   ├── github_actions.py        # Gerador para GitHub Actions
│   ├── gitlab_ci.py             # Gerador para GitLab CI
│   ├── jenkins.py               # Gerador para Jenkins
│   └── azure_devops.py          # Gerador para Azure DevOps
├── optimizers/                  # Otimizadores de pipeline
│   ├── __init__.py
│   └── pipeline_optimizer.py    # Otimizador de pipeline
├── detectors/                   # Detectores de falhas
│   ├── __init__.py
│   └── failure_detector.py      # Detector de falhas em pipeline
├── utils/                       # Utilitários
│   ├── __init__.py
│   └── file_utils.py            # Utilitários para manipulação de arquivos
└── templates/                   # Templates de pipeline
    ├── github_actions/          # Templates para GitHub Actions
    ├── gitlab_ci/               # Templates para GitLab CI
    ├── jenkins/                 # Templates para Jenkins
    └── azure_devops/            # Templates para Azure DevOps
```

## Implementação

A seguir, implementaremos os principais componentes do agent.
