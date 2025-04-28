# Guia do Agent de IaC

Este guia fornece informações detalhadas sobre o Agent de Infraestrutura como Código (IaC), suas funcionalidades e como utilizá-lo efetivamente.

## Índice

1. [Introdução](#introdução)
2. [Arquitetura](#arquitetura)
3. [Funcionalidades Detalhadas](#funcionalidades-detalhadas)
4. [Comandos e Opções](#comandos-e-opções)
5. [Exemplos Práticos](#exemplos-práticos)
6. [Personalização](#personalização)
7. [Integração com Outras Ferramentas](#integração-com-outras-ferramentas)

## Introdução

O Agent de IaC é uma ferramenta de IA projetada para automatizar a criação, validação, otimização e manutenção de código de infraestrutura como código. Ele suporta múltiplas ferramentas de IaC, incluindo Terraform, CloudFormation, Ansible e Kubernetes, permitindo que equipes de DevOps acelerem o desenvolvimento e manutenção de sua infraestrutura.

### Benefícios

- **Economia de tempo**: Reduz significativamente o tempo gasto na criação manual de código de infraestrutura
- **Padronização**: Garante que o código de infraestrutura siga as melhores práticas e padrões da organização
- **Otimização**: Identifica e corrige ineficiências em código existente
- **Validação**: Detecta problemas de segurança, conformidade e desempenho
- **Conversão**: Facilita a migração entre diferentes ferramentas de IaC

## Arquitetura

O Agent de IaC é composto por vários módulos que trabalham em conjunto:

```
iac/
├── analyzers/         # Módulos para análise de infraestrutura
├── generators/        # Geradores de código para diferentes ferramentas
├── models/            # Configuração e interface com modelos de IA
├── optimizers/        # Otimizadores de código de infraestrutura
├── validators/        # Validadores de código de infraestrutura
├── templates/         # Templates para diferentes ferramentas de IaC
├── utils/             # Utilitários diversos
├── iac_agent.py       # Ponto de entrada principal
└── config.py          # Configurações do agent
```

### Fluxo de Trabalho

1. **Análise**: A infraestrutura existente é analisada para identificar recursos, configurações e dependências
2. **Geração**: Com base na análise, código de infraestrutura é gerado para a ferramenta escolhida
3. **Validação**: O código gerado é validado para garantir que siga as melhores práticas e não contenha problemas
4. **Otimização**: O código é otimizado para eficiência, segurança e conformidade

## Funcionalidades Detalhadas

### Análise de Infraestrutura

O módulo de análise examina a infraestrutura existente para identificar:

- Recursos de computação, rede e armazenamento
- Configurações de segurança
- Dependências entre recursos
- Padrões de arquitetura
- Configurações específicas de provedores de nuvem

### Geração de Código

O agent pode gerar código para as seguintes ferramentas:

- **Terraform**: Arquivos .tf para diversos provedores (AWS, Azure, GCP, etc.)
- **CloudFormation**: Templates YAML/JSON para AWS
- **Ansible**: Playbooks e roles para configuração de sistemas
- **Kubernetes**: Manifestos YAML para orquestração de contêineres

Para cada ferramenta, o agent gera código que inclui:

- Definição de recursos
- Configurações de segurança
- Variáveis e parâmetros
- Outputs e saídas
- Módulos e componentes reutilizáveis

### Validação de Código

O módulo de validação verifica o código de infraestrutura para identificar:

- Problemas de segurança
- Configurações incorretas
- Violações de melhores práticas
- Problemas de conformidade
- Ineficiências de recursos

### Otimização de Código

O módulo de otimização melhora o código de infraestrutura:

- Redução de custos
- Melhoria de segurança
- Aumento de resiliência
- Implementação de melhores práticas
- Refatoração para melhor manutenibilidade

### Conversão entre Formatos

O agent pode converter código entre diferentes ferramentas de IaC:

- De Terraform para CloudFormation
- De CloudFormation para Terraform
- De configurações manuais para código IaC
- Entre diferentes versões da mesma ferramenta

## Comandos e Opções

O Agent de IaC é controlado através da linha de comando:

### Comando `analyze`

Analisa a infraestrutura em um diretório e exibe informações sobre ela.

```bash
python iac/iac_agent.py analyze /caminho/para/infraestrutura [--output resultado.json]
```

Opções:
- `path`: Caminho para o diretório contendo a infraestrutura (obrigatório)
- `--output`: Arquivo para salvar o resultado da análise em formato JSON (opcional)

### Comando `generate`

Gera código de infraestrutura para a ferramenta especificada.

```bash
python iac/iac_agent.py generate /caminho/para/infraestrutura --output ./output --type terraform
```

Opções:
- `path`: Caminho para o diretório contendo a infraestrutura (obrigatório)
- `--output`: Diretório onde os arquivos gerados serão salvos (obrigatório)
- `--type`: Tipo de IaC (terraform, cloudformation, ansible, kubernetes) (obrigatório)

### Comando `optimize`

Otimiza código de infraestrutura existente.

```bash
python iac/iac_agent.py optimize /caminho/para/infraestrutura --type terraform
```

Opções:
- `path`: Caminho para o diretório contendo os arquivos a serem otimizados (obrigatório)
- `--type`: Tipo de IaC (terraform, cloudformation, ansible, kubernetes) (obrigatório)

### Comando `validate`

Valida código de infraestrutura existente.

```bash
python iac/iac_agent.py validate /caminho/para/infraestrutura [--type terraform]
```

Opções:
- `path`: Caminho para o diretório contendo os arquivos a serem validados (obrigatório)
- `--type`: Tipo de IaC (opcional, se não especificado, o tipo será determinado automaticamente)

### Comando `convert`

Converte código de infraestrutura de um tipo para outro.

```bash
python iac/iac_agent.py convert /caminho/para/infraestrutura --output ./output --source terraform --target ansible
```

Opções:
- `path`: Caminho para o diretório contendo a infraestrutura (obrigatório)
- `--output`: Diretório onde os arquivos convertidos serão salvos (obrigatório)
- `--source`: Tipo de IaC de origem (obrigatório)
- `--target`: Tipo de IaC de destino (obrigatório)

## Exemplos Práticos

### Exemplo 1: Infraestrutura AWS com Terraform

```bash
# Analisar a infraestrutura
python iac/iac_agent.py analyze ./aws-infra

# Gerar código Terraform
python iac/iac_agent.py generate ./aws-infra --output ./terraform-output --type terraform
```

O código gerado incluirá:
- Definição de VPC, subnets e grupos de segurança
- Instâncias EC2, balanceadores de carga e grupos de auto-scaling
- Bancos de dados RDS e caches ElastiCache
- Buckets S3 e distribuições CloudFront
- Funções Lambda e APIs Gateway

### Exemplo 2: Infraestrutura Kubernetes

```bash
# Analisar a infraestrutura
python iac/iac_agent.py analyze ./k8s-infra

# Gerar manifestos Kubernetes
python iac/iac_agent.py generate ./k8s-infra --output ./k8s-output --type kubernetes
```

Os manifestos gerados incluirão:
- Deployments, StatefulSets e DaemonSets
- Services, Ingresses e NetworkPolicies
- ConfigMaps e Secrets
- PersistentVolumes e PersistentVolumeClaims
- RBAC (Role-Based Access Control)

### Exemplo 3: Validar Infraestrutura Existente

```bash
# Validar código Terraform
python iac/iac_agent.py validate ./terraform-code --type terraform
```

### Exemplo 4: Converter de Terraform para CloudFormation

```bash
# Converter de Terraform para CloudFormation
python iac/iac_agent.py convert ./terraform-code --output ./cloudformation-output --source terraform --target cloudformation
```

## Personalização

### Configuração do Modelo de IA

Você pode configurar o modelo de IA usado pelo agent no arquivo `config.py`:

```python
# Configurações de LLM
LLM_PROVIDER = "ollama"  # ollama, openai, azure, etc.
LLM_MODEL = "llama3"     # llama3, mistral, gpt-4, etc.
LLM_API_KEY = ""         # Não necessário para Ollama local
LLM_API_BASE = "http://localhost:11434/api"

# Parâmetros de geração
LLM_TEMPERATURE = 0.2    # Valores mais baixos = mais determinístico
LLM_MAX_TOKENS = 4000    # Limite de tokens na resposta
```

### Templates Personalizados

Você pode adicionar seus próprios templates na pasta `templates/`:

```
iac/templates/
├── terraform/
│   ├── aws/
│   ├── azure/
│   └── gcp/
├── cloudformation/
├── ansible/
└── kubernetes/
```

### Extensão para Outras Ferramentas

Para adicionar suporte a uma nova ferramenta de IaC:

1. Crie uma nova classe geradora em `generators/`
2. Adicione templates na pasta `templates/`
3. Atualize o arquivo `generators/__init__.py`
4. Adicione a nova ferramenta nas opções de linha de comando em `iac_agent.py`

## Integração com Outras Ferramentas

### Integração com Ferramentas de CI/CD

O Agent de IaC pode ser integrado com pipelines de CI/CD para automatizar a validação, otimização e implantação de infraestrutura.

### Integração com Ferramentas de Segurança

O agent pode ser configurado para incluir verificações de segurança com ferramentas como Checkov, TFSec e Terrascan.

### Integração com Ferramentas de Monitoramento

O agent pode gerar código que inclui configurações para ferramentas de monitoramento como Prometheus, Grafana e CloudWatch.

### Integração com Ferramentas de Gerenciamento de Custos

O agent pode otimizar infraestrutura para redução de custos e integrar com ferramentas como AWS Cost Explorer, Azure Cost Management e Infracost.

---

Para mais informações sobre a instalação e configuração geral, consulte a [Documentação de Implantação](implantacao.md).

© 2025 Sua Organização. Todos os direitos reservados.
