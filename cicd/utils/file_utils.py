"""
Utilitários para o agent de CI/CD.
"""
import os
import logging
import json
import yaml
from typing import Dict, Any, List, Optional

from config import Config, logger

def load_yaml_file(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Carrega um arquivo YAML.
    
    Args:
        file_path: Caminho do arquivo YAML.
        
    Returns:
        Conteúdo do arquivo YAML ou None se não for possível carregar.
    """
    try:
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Erro ao carregar arquivo YAML {file_path}: {str(e)}")
        return None

def save_yaml_file(file_path: str, content: Dict[str, Any]) -> bool:
    """
    Salva um dicionário em um arquivo YAML.
    
    Args:
        file_path: Caminho do arquivo YAML.
        content: Conteúdo a ser salvo.
        
    Returns:
        True se o arquivo foi salvo com sucesso, False caso contrário.
    """
    try:
        with open(file_path, 'w') as f:
            yaml.dump(content, f, sort_keys=False)
        return True
    except Exception as e:
        logger.error(f"Erro ao salvar arquivo YAML {file_path}: {str(e)}")
        return False

def load_json_file(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Carrega um arquivo JSON.
    
    Args:
        file_path: Caminho do arquivo JSON.
        
    Returns:
        Conteúdo do arquivo JSON ou None se não for possível carregar.
    """
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Erro ao carregar arquivo JSON {file_path}: {str(e)}")
        return None

def save_json_file(file_path: str, content: Dict[str, Any]) -> bool:
    """
    Salva um dicionário em um arquivo JSON.
    
    Args:
        file_path: Caminho do arquivo JSON.
        content: Conteúdo a ser salvo.
        
    Returns:
        True se o arquivo foi salvo com sucesso, False caso contrário.
    """
    try:
        with open(file_path, 'w') as f:
            json.dump(content, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Erro ao salvar arquivo JSON {file_path}: {str(e)}")
        return False

def read_file(file_path: str) -> Optional[str]:
    """
    Lê o conteúdo de um arquivo.
    
    Args:
        file_path: Caminho do arquivo.
        
    Returns:
        Conteúdo do arquivo ou None se não for possível ler.
    """
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Erro ao ler arquivo {file_path}: {str(e)}")
        return None

def write_file(file_path: str, content: str) -> bool:
    """
    Escreve conteúdo em um arquivo.
    
    Args:
        file_path: Caminho do arquivo.
        content: Conteúdo a ser escrito.
        
    Returns:
        True se o arquivo foi escrito com sucesso, False caso contrário.
    """
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            f.write(content)
        return True
    except Exception as e:
        logger.error(f"Erro ao escrever arquivo {file_path}: {str(e)}")
        return False

def ensure_directory(directory: str) -> bool:
    """
    Garante que um diretório existe.
    
    Args:
        directory: Caminho do diretório.
        
    Returns:
        True se o diretório existe ou foi criado com sucesso, False caso contrário.
    """
    try:
        os.makedirs(directory, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Erro ao criar diretório {directory}: {str(e)}")
        return False

def list_files(directory: str, extension: Optional[str] = None) -> List[str]:
    """
    Lista arquivos em um diretório.
    
    Args:
        directory: Caminho do diretório.
        extension: Extensão dos arquivos a serem listados.
        
    Returns:
        Lista de caminhos de arquivos.
    """
    try:
        if not os.path.exists(directory):
            return []
        
        files = []
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path):
                if extension is None or file.endswith(extension):
                    files.append(file_path)
        return files
    except Exception as e:
        logger.error(f"Erro ao listar arquivos em {directory}: {str(e)}")
        return []

def get_pipeline_type(file_path: str) -> Optional[str]:
    """
    Determina o tipo de pipeline com base no nome do arquivo.
    
    Args:
        file_path: Caminho do arquivo de pipeline.
        
    Returns:
        Tipo de pipeline ou None se não for possível determinar.
    """
    file_name = os.path.basename(file_path)
    
    if file_name.endswith('.yml') or file_name.endswith('.yaml'):
        if file_name.startswith('azure-pipelines'):
            return "azure_devops"
        elif file_name == '.gitlab-ci.yml':
            return "gitlab_ci"
        else:
            # Verificar conteúdo para determinar se é GitHub Actions
            content = read_file(file_path)
            if content and ('actions/' in content or 'github.' in content):
                return "github_actions"
            return None
    elif file_name == 'Jenkinsfile':
        return "jenkins"
    
    return None
