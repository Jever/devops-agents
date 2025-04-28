"""
Configurações para o agent de Infraestrutura como Código (IaC).
"""
import os
import logging
from typing import Dict, Any, Optional

# Configurar logger
logger = logging.getLogger("iac_agent")

class Config:
    """
    Configurações globais para o agent de IaC.
    """
    
    # Diretórios
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
    
    # Configurações de ferramentas de IaC
    TERRAFORM_VERSION = "1.5.0"
    ANSIBLE_VERSION = "2.15.0"
    KUBERNETES_VERSION = "1.27.0"
    
    # Configurações de LLM
    LLM_PROVIDER = "ollama"  # ollama, openai, azure, etc.
    LLM_MODEL = "llama3"     # llama3, mistral, gpt-4, etc.
    LLM_API_KEY = os.environ.get("LLM_API_KEY", "")
    LLM_API_BASE = os.environ.get("LLM_API_BASE", "http://localhost:11434/api")
    
    # Configurações de análise
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
    IGNORE_DIRS = [".git", "node_modules", "__pycache__", ".terraform"]
    
    # Configurações de geração
    GENERATION_TIMEOUT = 60  # segundos
    
    @classmethod
    def load_config(cls, config_path: str) -> None:
        """
        Carrega configurações de um arquivo.
        
        Args:
            config_path: Caminho para o arquivo de configuração.
        """
        import yaml
        
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            # Atualizar configurações
            for key, value in config.items():
                if hasattr(cls, key):
                    setattr(cls, key, value)
            
            logger.info(f"Configurações carregadas de {config_path}")
        except Exception as e:
            logger.error(f"Erro ao carregar configurações de {config_path}: {str(e)}")
