"""
Utilitários para manipulação de arquivos.
"""
import os
import logging
import shutil
from typing import List, Optional, Dict, Any

from config import Config, logger

class FileUtils:
    """
    Classe com utilitários para manipulação de arquivos.
    """
    
    @staticmethod
    def list_files(directory: str, extensions: Optional[List[str]] = None, recursive: bool = True) -> List[str]:
        """
        Lista arquivos em um diretório.
        
        Args:
            directory: Diretório a ser listado.
            extensions: Lista de extensões para filtrar (ex: ['.tf', '.yaml']).
            recursive: Se deve listar arquivos recursivamente.
            
        Returns:
            Lista de caminhos de arquivos.
        """
        files = []
        
        if not os.path.exists(directory):
            logger.warning(f"Diretório não encontrado: {directory}")
            return files
        
        if recursive:
            for root, dirs, filenames in os.walk(directory):
                # Ignorar diretórios específicos
                dirs[:] = [d for d in dirs if d not in Config.IGNORE_DIRS]
                
                for filename in filenames:
                    file_path = os.path.join(root, filename)
                    
                    # Verificar tamanho do arquivo
                    if os.path.getsize(file_path) > Config.MAX_FILE_SIZE:
                        continue
                    
                    # Filtrar por extensão
                    if extensions is None or any(filename.endswith(ext) for ext in extensions):
                        files.append(file_path)
        else:
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                
                if os.path.isfile(file_path):
                    # Verificar tamanho do arquivo
                    if os.path.getsize(file_path) > Config.MAX_FILE_SIZE:
                        continue
                    
                    # Filtrar por extensão
                    if extensions is None or any(filename.endswith(ext) for ext in extensions):
                        files.append(file_path)
        
        return files
    
    @staticmethod
    def read_file(file_path: str) -> Optional[str]:
        """
        Lê o conteúdo de um arquivo.
        
        Args:
            file_path: Caminho do arquivo.
            
        Returns:
            Conteúdo do arquivo ou None se ocorrer um erro.
        """
        if not os.path.exists(file_path):
            logger.warning(f"Arquivo não encontrado: {file_path}")
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Erro ao ler arquivo {file_path}: {str(e)}")
            return None
    
    @staticmethod
    def write_file(file_path: str, content: str) -> bool:
        """
        Escreve conteúdo em um arquivo.
        
        Args:
            file_path: Caminho do arquivo.
            content: Conteúdo a ser escrito.
            
        Returns:
            True se a operação for bem-sucedida, False caso contrário.
        """
        try:
            # Criar diretório se não existir
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
        except Exception as e:
            logger.error(f"Erro ao escrever arquivo {file_path}: {str(e)}")
            return False
    
    @staticmethod
    def copy_file(source: str, destination: str) -> bool:
        """
        Copia um arquivo.
        
        Args:
            source: Caminho do arquivo de origem.
            destination: Caminho do arquivo de destino.
            
        Returns:
            True se a operação for bem-sucedida, False caso contrário.
        """
        try:
            # Criar diretório de destino se não existir
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            
            shutil.copy2(source, destination)
            return True
        except Exception as e:
            logger.error(f"Erro ao copiar arquivo de {source} para {destination}: {str(e)}")
            return False
    
    @staticmethod
    def delete_file(file_path: str) -> bool:
        """
        Exclui um arquivo.
        
        Args:
            file_path: Caminho do arquivo.
            
        Returns:
            True se a operação for bem-sucedida, False caso contrário.
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            return True
        except Exception as e:
            logger.error(f"Erro ao excluir arquivo {file_path}: {str(e)}")
            return False
    
    @staticmethod
    def create_directory(directory: str) -> bool:
        """
        Cria um diretório.
        
        Args:
            directory: Caminho do diretório.
            
        Returns:
            True se a operação for bem-sucedida, False caso contrário.
        """
        try:
            os.makedirs(directory, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"Erro ao criar diretório {directory}: {str(e)}")
            return False
    
    @staticmethod
    def delete_directory(directory: str) -> bool:
        """
        Exclui um diretório.
        
        Args:
            directory: Caminho do diretório.
            
        Returns:
            True se a operação for bem-sucedida, False caso contrário.
        """
        try:
            if os.path.exists(directory):
                shutil.rmtree(directory)
            return True
        except Exception as e:
            logger.error(f"Erro ao excluir diretório {directory}: {str(e)}")
            return False
    
    @staticmethod
    def get_file_type(file_path: str) -> Optional[str]:
        """
        Determina o tipo de arquivo de IaC.
        
        Args:
            file_path: Caminho do arquivo.
            
        Returns:
            Tipo de arquivo (terraform, cloudformation, ansible, kubernetes) ou None.
        """
        if not os.path.exists(file_path):
            return None
        
        # Verificar por extensão
        if file_path.endswith('.tf') or file_path.endswith('.tfvars'):
            return "terraform"
        
        # Verificar conteúdo para YAML/JSON
        try:
            content = FileUtils.read_file(file_path)
            if not content:
                return None
            
            # CloudFormation
            if 'AWSTemplateFormatVersion' in content or '"AWSTemplateFormatVersion"' in content:
                return "cloudformation"
            
            if ('Resources:' in content and 'Type: AWS::' in content) or ('"Resources"' in content and '"Type": "AWS::' in content):
                return "cloudformation"
            
            # Kubernetes
            if 'apiVersion:' in content and ('kind:' in content or 'Kind:' in content):
                return "kubernetes"
            
            # Ansible
            if 'hosts:' in content and ('tasks:' in content or 'roles:' in content):
                return "ansible"
            
            # Verificar por nome de arquivo
            filename = os.path.basename(file_path)
            if filename == 'playbook.yml' or filename.endswith('.playbook.yml'):
                return "ansible"
            
        except Exception as e:
            logger.warning(f"Erro ao determinar tipo de arquivo {file_path}: {str(e)}")
        
        return None
