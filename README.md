# DevOps Agents

## Visão Geral

DevOps Agents é uma solução baseada em IA para automatizar tarefas comuns de DevOps, permitindo que equipes técnicas acelerem seu trabalho e reduzam tarefas repetitivas. Esta solução inclui agents inteligentes que podem ser executados localmente, sem necessidade de conexão com serviços externos de IA.

## Agents Disponíveis

Esta versão inclui dois agents principais:

1. **Agent de CI/CD**: Analisa repositórios, gera e otimiza pipelines de CI/CD para diferentes plataformas (GitHub Actions, GitLab CI, Jenkins, Azure DevOps).

2. **Agent de IaC (Infraestrutura como Código)**: Analisa, gera, valida e otimiza código de infraestrutura para várias ferramentas (Terraform, CloudFormation, Ansible, Kubernetes).

## Funcionalidades Principais

### Agent de CI/CD
- Análise automática de repositórios para identificar linguagens, frameworks e tecnologias
- Geração de pipelines otimizados para diferentes plataformas
- Otimização de pipelines existentes para melhorar performance e eficiência
- Detecção e correção de falhas em pipelines

### Agent de IaC
- Análise de infraestrutura existente para identificar recursos e configurações
- Geração de código para diferentes ferramentas de IaC
- Validação de código de infraestrutura para identificar problemas e vulnerabilidades
- Otimização de código de infraestrutura para seguir boas práticas
- Conversão entre diferentes formatos de IaC

## Instalação Rápida

```bash
# Clonar o repositório
git clone https://github.com/Jever/devops-agents.git
cd devops-agents

# Configurar ambiente virtual
python3 -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Configurar modelo de IA local (Ollama com Llama 3)
# Primeiro, instale o Ollama de https://ollama.ai
ollama pull llama3

# Copiar arquivos de configuração
cp cicd/config.example.py cicd/config.py
cp iac/config.example.py iac/config.py
```

## Documentação

Para instruções detalhadas de instalação, configuração e uso, consulte:

- [Documentação de Implantação](docs/implantacao.md)
- [Guia do Agent de CI/CD](docs/cicd_guide.md)
- [Guia do Agent de IaC](docs/iac_guide.md)

## Requisitos do Sistema

- **Sistema Operacional**: Linux, macOS ou Windows com WSL
- **Python**: Versão 3.8 ou superior
- **RAM**: 8GB (16GB recomendado)
- **Espaço em Disco**: 10GB para instalação completa
- **CPU**: 4 núcleos (8 recomendado)
- **GPU**: Opcional, mas recomendado para melhor desempenho

## Exemplos de Uso

### Agent de CI/CD

```bash
# Analisar um repositório
python cicd/cicd_agent.py analyze --repo-path /caminho/para/repositorio

# Gerar pipeline para GitHub Actions
python cicd/cicd_agent.py generate --repo-path /caminho/para/repositorio --output-path ./output --platform github-actions
```

### Agent de IaC

```bash
# Analisar infraestrutura existente
python iac/iac_agent.py analyze /caminho/para/infraestrutura

# Gerar código Terraform
python iac/iac_agent.py generate /caminho/para/infraestrutura --output ./output --type terraform
```
