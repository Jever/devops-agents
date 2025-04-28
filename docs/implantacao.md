# Documentação de Implantação - DevOps Agents

Este documento fornece instruções detalhadas para a implantação e utilização dos agents de DevOps desenvolvidos para acelerar o trabalho da equipe de DevOps.

## Índice

1. [Visão Geral](#visão-geral)
2. [Requisitos do Sistema](#requisitos-do-sistema)
3. [Instalação](#instalação)
4. [Agent de CI/CD](#agent-de-cicd)
5. [Agent de IaC](#agent-de-iac)
6. [Solução de Problemas](#solução-de-problemas)
7. [Perguntas Frequentes](#perguntas-frequentes)

## Visão Geral

Os DevOps Agents são ferramentas de IA projetadas para automatizar tarefas comuns de DevOps. Esta versão inclui dois agents principais:

1. **Agent de CI/CD**: Analisa repositórios, gera e otimiza pipelines de CI/CD para diferentes plataformas.
2. **Agent de IaC**: Analisa, gera, valida e otimiza código de infraestrutura como código para várias ferramentas.

Ambos os agents podem ser executados localmente, sem necessidade de conexão com serviços externos de IA, utilizando modelos de linguagem locais como Llama 3 ou Mistral AI.

## Requisitos do Sistema

### Requisitos Mínimos

- **Sistema Operacional**: Linux, macOS ou Windows com WSL
- **Python**: Versão 3.8 ou superior
- **RAM**: 8GB (16GB recomendado para melhor desempenho)
- **Espaço em Disco**: 10GB para instalação completa com modelos de IA locais
- **CPU**: 4 núcleos (8 recomendado)
- **GPU**: Opcional, mas recomendado para melhor desempenho dos modelos de IA

### Dependências de Software

- Python 3.8+
- pip (gerenciador de pacotes Python)
- git
- Docker (opcional, para execução em contêineres)

## Instalação

### 1. Clonar o Repositório

```bash
git clone https://github.com/sua-organizacao/devops-agents.git
cd devops-agents
```

### 2. Configurar Ambiente Virtual

```bash
python3 -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

### 3. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar Modelo de IA Local

#### Opção 1: Ollama (Recomendado)

1. Instale o Ollama seguindo as instruções em [ollama.ai](https://ollama.ai)
2. Baixe o modelo Llama 3:

```bash
ollama pull llama3
```

#### Opção 2: Outros Modelos Locais

Você pode configurar outros modelos como Mistral AI. Consulte a seção de configuração para mais detalhes.

### 5. Configurar os Agents

Copie os arquivos de configuração de exemplo:

```bash
cp cicd/config.example.py cicd/config.py
cp iac/config.example.py iac/config.py
```

Edite os arquivos de configuração conforme necessário, especialmente as configurações do modelo de IA.

## Agent de CI/CD

O Agent de CI/CD analisa repositórios de código e gera pipelines de CI/CD otimizados para diferentes plataformas.

### Funcionalidades

- Análise de repositórios para identificar linguagens, frameworks e tecnologias
- Geração de pipelines para GitHub Actions, GitLab CI, Jenkins e Azure DevOps
- Otimização de pipelines existentes
- Detecção e correção de falhas em pipelines

### Uso Básico

#### Analisar um Repositório

```bash
python cicd/cicd_agent.py analyze --repo-path /caminho/para/repositorio
```

#### Gerar Pipeline CI/CD

```bash
python cicd/cicd_agent.py generate --repo-path /caminho/para/repositorio --output-path ./output --platform github-actions
```

Plataformas suportadas:
- `github-actions`: GitHub Actions
- `gitlab-ci`: GitLab CI/CD
- `jenkins`: Jenkins
- `azure-devops`: Azure DevOps

#### Otimizar Pipeline Existente

```bash
python cicd/cicd_agent.py optimize --pipeline-path /caminho/para/pipeline.yml --platform github-actions
```

#### Detectar Falhas em Pipeline

```bash
python cicd/cicd_agent.py detect --pipeline-path /caminho/para/pipeline.yml --platform github-actions
```

### Exemplos de Uso

#### Exemplo 1: Gerar Pipeline para Aplicação Node.js

```bash
python cicd/cicd_agent.py generate --repo-path ./minha-app-nodejs --output-path ./output --platform github-actions
```

#### Exemplo 2: Otimizar Pipeline Existente do GitLab

```bash
python cicd/cicd_agent.py optimize --pipeline-path ./gitlab-ci.yml --platform gitlab-ci
```

## Agent de IaC

O Agent de IaC (Infraestrutura como Código) analisa, gera, valida e otimiza código de infraestrutura para diferentes ferramentas.

### Funcionalidades

- Análise de infraestrutura existente
- Geração de código para Terraform, CloudFormation, Ansible e Kubernetes
- Otimização de código de infraestrutura
- Validação de código de infraestrutura
- Conversão entre diferentes formatos de IaC

### Uso Básico

#### Analisar Infraestrutura

```bash
python iac/iac_agent.py analyze /caminho/para/infraestrutura
```

#### Gerar Código de Infraestrutura

```bash
python iac/iac_agent.py generate /caminho/para/infraestrutura --output ./output --type terraform
```

Tipos suportados:
- `terraform`: Terraform
- `cloudformation`: AWS CloudFormation
- `ansible`: Ansible
- `kubernetes`: Kubernetes

#### Otimizar Código de Infraestrutura

```bash
python iac/iac_agent.py optimize /caminho/para/infraestrutura --type terraform
```

#### Validar Código de Infraestrutura

```bash
python iac/iac_agent.py validate /caminho/para/infraestrutura --type terraform
```

#### Converter entre Formatos

```bash
python iac/iac_agent.py convert /caminho/para/infraestrutura --output ./output --source terraform --target ansible
```

### Exemplos de Uso

#### Exemplo 1: Gerar Código Terraform a partir de Infraestrutura Existente

```bash
python iac/iac_agent.py generate ./minha-infra --output ./terraform-output --type terraform
```

#### Exemplo 2: Validar Código CloudFormation

```bash
python iac/iac_agent.py validate ./cloudformation-templates --type cloudformation
```

## Configuração Avançada

### Configuração do Modelo de IA

Ambos os agents utilizam modelos de IA para análise e geração de código. Você pode configurar o modelo nos arquivos `config.py` de cada agent:

```python
# Configurações de LLM
LLM_PROVIDER = "ollama"  # ollama, openai, azure, etc.
LLM_MODEL = "llama3"     # llama3, mistral, gpt-4, etc.
LLM_API_KEY = ""         # Não necessário para Ollama local
LLM_API_BASE = "http://localhost:11434/api"
```

### Configuração de Proxy

Se você estiver atrás de um proxy corporativo, configure as variáveis de ambiente:

```bash
export HTTP_PROXY="http://proxy.example.com:8080"
export HTTPS_PROXY="http://proxy.example.com:8080"
```

### Configuração de Logging

O nível de logging pode ser configurado nos arquivos `config.py`:

```python
import logging
LOGGING_LEVEL = logging.INFO  # Pode ser DEBUG, INFO, WARNING, ERROR
```

## Solução de Problemas

### Problemas Comuns

#### O Agent não Consegue Conectar ao Modelo de IA Local

**Problema**: Erro de conexão ao tentar usar o Ollama ou outro modelo local.

**Solução**:
1. Verifique se o serviço Ollama está em execução: `ollama ps`
2. Verifique se a URL da API está correta no arquivo de configuração
3. Verifique se o modelo foi baixado corretamente: `ollama list`

#### Erros de Memória ao Executar os Agents

**Problema**: Erros de falta de memória ao executar os agents com modelos grandes.

**Solução**:
1. Feche aplicativos que consomem muita memória
2. Configure o modelo para usar menos memória no arquivo de configuração
3. Use um modelo menor ou mais eficiente

#### Erros na Geração de Código

**Problema**: O código gerado contém erros ou não compila.

**Solução**:
1. Verifique se o repositório ou infraestrutura de origem está completo e válido
2. Tente usar um modelo de IA diferente ou mais capaz
3. Ajuste os parâmetros de geração no arquivo de configuração

## Perguntas Frequentes

### Geral

**P: Os agents precisam de conexão com a internet para funcionar?**

R: Não, uma vez que os modelos de IA estejam instalados localmente (como Ollama com Llama 3), os agents podem funcionar completamente offline.

**P: Posso usar os agents em um ambiente de produção?**

R: Os agents são primariamente ferramentas de assistência para equipes de DevOps. Recomendamos revisar e testar todo o código gerado antes de usá-lo em produção.

### Agent de CI/CD

**P: O agent pode integrar com sistemas de CI/CD personalizados?**

R: Atualmente, o agent suporta GitHub Actions, GitLab CI, Jenkins e Azure DevOps. Suporte para sistemas personalizados pode ser adicionado estendendo as classes geradoras.

**P: Como o agent lida com segredos e credenciais em pipelines?**

R: O agent é projetado para usar variáveis de ambiente ou sistemas de gerenciamento de segredos da plataforma de CI/CD, nunca incluindo credenciais diretamente no código.

### Agent de IaC

**P: O agent pode gerar código para provedores de nuvem específicos?**

R: Sim, o agent pode gerar código Terraform e CloudFormation otimizado para AWS, Azure e GCP, dependendo da análise da infraestrutura.

**P: É possível converter completamente entre diferentes formatos de IaC?**

R: A conversão entre formatos é possível, mas pode não ser 100% perfeita para todos os recursos, especialmente para recursos específicos de plataforma. Recomendamos revisar o código convertido.

## Suporte e Contribuição

Para obter suporte ou contribuir com o desenvolvimento dos DevOps Agents, entre em contato com a equipe de DevOps ou abra uma issue no repositório do projeto.

---

© 2025 Sua Organização. Todos os direitos reservados.
