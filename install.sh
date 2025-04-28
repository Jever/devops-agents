#!/bin/bash

# Script de instalação para DevOps Agents
# Este script configura o ambiente necessário para executar os DevOps Agents

echo "Iniciando instalação dos DevOps Agents..."

# Verificar se Python 3.8+ está instalado
python3 --version >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Erro: Python 3.8 ou superior é necessário."
    exit 1
fi

# Verificar versão do Python
python_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
python_major=$(echo $python_version | cut -d. -f1)
python_minor=$(echo $python_version | cut -d. -f2)

if [ $python_major -lt 3 ] || ([ $python_major -eq 3 ] && [ $python_minor -lt 8 ]); then
    echo "Erro: Python 3.8 ou superior é necessário. Versão atual: $python_version"
    exit 1
fi

echo "Python $python_version detectado."

# Criar ambiente virtual
echo "Criando ambiente virtual..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "Erro ao criar ambiente virtual."
    exit 1
fi

# Ativar ambiente virtual
echo "Ativando ambiente virtual..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "Erro ao ativar ambiente virtual."
    exit 1
fi

# Instalar dependências
echo "Instalando dependências..."
pip install --upgrade pip
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Erro ao instalar dependências."
    exit 1
fi

# Verificar se Ollama está instalado (opcional)
echo "Verificando instalação do Ollama..."
ollama_installed=false
if command -v ollama >/dev/null 2>&1; then
    echo "Ollama já está instalado."
    ollama_installed=true
else
    echo "Ollama não está instalado. Recomendamos instalar para execução local dos modelos de IA."
    echo "Visite https://ollama.ai para instruções de instalação."
    
    read -p "Deseja continuar sem instalar o Ollama? (y/n): " continue_without_ollama
    if [ "$continue_without_ollama" != "y" ]; then
        echo "Instalação interrompida. Por favor, instale o Ollama e execute este script novamente."
        exit 1
    fi
fi

# Criar arquivos de configuração
echo "Criando arquivos de configuração..."
if [ ! -f cicd/config.py ]; then
    cp cicd/config.example.py cicd/config.py 2>/dev/null || echo "# Configuração do Agent CI/CD" > cicd/config.py
    echo "Arquivo de configuração cicd/config.py criado."
fi

if [ ! -f iac/config.py ]; then
    cp iac/config.example.py iac/config.py 2>/dev/null || echo "# Configuração do Agent IaC" > iac/config.py
    echo "Arquivo de configuração iac/config.py criado."
fi

# Baixar modelo Llama 3 se Ollama estiver instalado
if [ "$ollama_installed" = true ]; then
    echo "Verificando se o modelo Llama 3 está disponível..."
    if ! ollama list | grep -q "llama3"; then
        echo "Baixando modelo Llama 3..."
        ollama pull llama3
        if [ $? -ne 0 ]; then
            echo "Aviso: Não foi possível baixar o modelo Llama 3. Você precisará configurar um modelo alternativo."
        else
            echo "Modelo Llama 3 baixado com sucesso."
        fi
    else
        echo "Modelo Llama 3 já está disponível."
    fi
fi

echo ""
echo "Instalação concluída com sucesso!"
echo ""
echo "Para usar os agents, ative o ambiente virtual:"
echo "  source venv/bin/activate"
echo ""
echo "Exemplos de uso:"
echo "  Agent CI/CD: python cicd/cicd_agent.py analyze --repo-path /caminho/para/repositorio"
echo "  Agent IaC: python iac/iac_agent.py analyze /caminho/para/infraestrutura"
echo ""
echo "Consulte a documentação em docs/ para mais informações."
