# Guia do Agent de CI/CD

Este guia fornece informações detalhadas sobre o Agent de CI/CD, suas funcionalidades e como utilizá-lo efetivamente.

## Índice

1. [Introdução](#introdução)
2. [Arquitetura](#arquitetura)
3. [Funcionalidades Detalhadas](#funcionalidades-detalhadas)
4. [Comandos e Opções](#comandos-e-opções)
5. [Exemplos Práticos](#exemplos-práticos)
6. [Personalização](#personalização)
7. [Integração com Outras Ferramentas](#integração-com-outras-ferramentas)

## Introdução

O Agent de CI/CD é uma ferramenta de IA projetada para automatizar a criação, manutenção e otimização de pipelines de integração e entrega contínua. Ele analisa repositórios de código para identificar linguagens, frameworks e tecnologias utilizadas, e gera pipelines otimizados para diferentes plataformas de CI/CD.

### Benefícios

- **Economia de tempo**: Reduz significativamente o tempo gasto na criação manual de pipelines
- **Padronização**: Garante que os pipelines sigam as melhores práticas e padrões da organização
- **Otimização**: Identifica e corrige ineficiências em pipelines existentes
- **Detecção de falhas**: Identifica problemas comuns em pipelines antes que causem falhas

## Arquitetura

O Agent de CI/CD é composto por vários módulos que trabalham em conjunto:

```
cicd/
├── analyzers/         # Módulos para análise de repositórios
├── detectors/         # Módulos para detecção de falhas
├── generators/        # Geradores de pipeline para diferentes plataformas
├── models/            # Configuração e interface com modelos de IA
├── optimizers/        # Otimizadores de pipeline
├── templates/         # Templates para diferentes plataformas de CI/CD
├── utils/             # Utilitários diversos
├── cicd_agent.py      # Ponto de entrada principal
└── config.py          # Configurações do agent
```

### Fluxo de Trabalho

1. **Análise**: O repositório é analisado para identificar linguagens, frameworks, dependências e padrões de projeto
2. **Geração**: Com base na análise, um pipeline é gerado para a plataforma escolhida
3. **Otimização**: O pipeline gerado é otimizado para eficiência e desempenho
4. **Validação**: O pipeline é validado para garantir que funcione corretamente

## Funcionalidades Detalhadas

### Análise de Repositórios

O módulo de análise examina o repositório para identificar:

- Linguagens de programação utilizadas
- Frameworks e bibliotecas
- Ferramentas de build e teste
- Padrões de projeto
- Estrutura do projeto
- Dependências e suas versões

### Geração de Pipelines

O agent pode gerar pipelines para as seguintes plataformas:

- **GitHub Actions**: Workflows YAML para GitHub
- **GitLab CI/CD**: Arquivos .gitlab-ci.yml
- **Jenkins**: Jenkinsfile em formato declarativo ou script
- **Azure DevOps**: Pipelines YAML para Azure DevOps

Para cada plataforma, o agent gera pipelines que incluem:

- Etapas de build
- Testes unitários e de integração
- Análise de código estática
- Verificação de segurança
- Implantação em diferentes ambientes

### Otimização de Pipelines

O módulo de otimização melhora pipelines existentes:

- Paralelização de tarefas quando possível
- Uso eficiente de cache
- Redução de tempos de execução
- Eliminação de etapas redundantes
- Implementação de melhores práticas específicas da plataforma

### Detecção de Falhas

O detector de falhas identifica problemas comuns em pipelines:

- Configurações incorretas
- Dependências ausentes
- Problemas de segurança
- Ineficiências de desempenho
- Incompatibilidades entre ferramentas

## Comandos e Opções

O Agent de CI/CD é controlado através da linha de comando:

### Comando `analyze`

Analisa um repositório e exibe informações sobre ele.

```bash
python cicd/cicd_agent.py analyze --repo-path /caminho/para/repositorio [--output-file resultado.json]
```

Opções:
- `--repo-path`: Caminho para o repositório a ser analisado (obrigatório)
- `--output-file`: Arquivo para salvar o resultado da análise em formato JSON (opcional)

### Comando `generate`

Gera um pipeline CI/CD para a plataforma especificada.

```bash
python cicd/cicd_agent.py generate --repo-path /caminho/para/repositorio --output-path ./output --platform github-actions [--template basic|complete]
```

Opções:
- `--repo-path`: Caminho para o repositório (obrigatório)
- `--output-path`: Diretório onde os arquivos do pipeline serão salvos (obrigatório)
- `--platform`: Plataforma de CI/CD (github-actions, gitlab-ci, jenkins, azure-devops) (obrigatório)
- `--template`: Template a ser usado (basic, complete) (opcional, padrão: complete)

### Comando `optimize`

Otimiza um pipeline existente.

```bash
python cicd/cicd_agent.py optimize --pipeline-path /caminho/para/pipeline.yml --platform github-actions [--output-path ./output]
```

Opções:
- `--pipeline-path`: Caminho para o arquivo de pipeline existente (obrigatório)
- `--platform`: Plataforma de CI/CD (obrigatório)
- `--output-path`: Diretório para salvar o pipeline otimizado (opcional, padrão: sobrescreve o original)

### Comando `detect`

Detecta problemas em um pipeline existente.

```bash
python cicd/cicd_agent.py detect --pipeline-path /caminho/para/pipeline.yml --platform github-actions [--output-file issues.json]
```

Opções:
- `--pipeline-path`: Caminho para o arquivo de pipeline existente (obrigatório)
- `--platform`: Plataforma de CI/CD (obrigatório)
- `--output-file`: Arquivo para salvar os problemas detectados em formato JSON (opcional)

## Exemplos Práticos

### Exemplo 1: Aplicação Node.js com React

```bash
# Analisar o repositório
python cicd/cicd_agent.py analyze --repo-path ./minha-app-react

# Gerar pipeline para GitHub Actions
python cicd/cicd_agent.py generate --repo-path ./minha-app-react --output-path ./output --platform github-actions
```

O pipeline gerado incluirá:
- Instalação de dependências com npm/yarn
- Execução de testes com Jest
- Build da aplicação
- Análise de código com ESLint
- Implantação em ambiente de staging/produção

### Exemplo 2: Aplicação Java Spring Boot

```bash
# Analisar o repositório
python cicd/cicd_agent.py analyze --repo-path ./spring-boot-app

# Gerar pipeline para Jenkins
python cicd/cicd_agent.py generate --repo-path ./spring-boot-app --output-path ./output --platform jenkins
```

O pipeline gerado incluirá:
- Build com Maven/Gradle
- Execução de testes unitários e de integração
- Análise de código com SonarQube
- Geração de artefatos JAR/WAR
- Implantação em servidores de aplicação

### Exemplo 3: Otimizar Pipeline Existente

```bash
# Otimizar pipeline do GitLab CI
python cicd/cicd_agent.py optimize --pipeline-path ./gitlab-ci.yml --platform gitlab-ci --output-path ./optimized
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
cicd/templates/
├── github_actions/
│   ├── basic.yml.template
│   └── complete.yml.template
├── gitlab_ci/
│   ├── basic.yml.template
│   └── complete.yml.template
└── ...
```

### Extensão para Outras Plataformas

Para adicionar suporte a uma nova plataforma de CI/CD:

1. Crie uma nova classe geradora em `generators/`
2. Adicione templates na pasta `templates/`
3. Atualize o arquivo `generators/__init__.py`
4. Adicione a nova plataforma nas opções de linha de comando em `cicd_agent.py`

## Integração com Outras Ferramentas

### Integração com Sistemas de Controle de Versão

O Agent de CI/CD pode ser integrado com sistemas de controle de versão como GitHub, GitLab e Bitbucket para automatizar a criação e atualização de pipelines.

### Integração com Ferramentas de Qualidade de Código

O agent pode ser configurado para incluir ferramentas de qualidade de código como SonarQube, CodeClimate e Codacy nos pipelines gerados.

### Integração com Ferramentas de Segurança

O agent pode incluir verificações de segurança com ferramentas como OWASP Dependency Check, Snyk e Trivy nos pipelines gerados.

---

Para mais informações sobre a instalação e configuração geral, consulte a [Documentação de Implantação](implantacao.md).
