"""
Analisador de infraestrutura para identificar recursos e configurações existentes.
"""
import os
import logging
import json
import re
from typing import Dict, Any, List, Optional, Set, Tuple

from config import Config, logger

class InfrastructureAnalyzer:
    """
    Classe para analisar infraestrutura existente e identificar recursos e configurações.
    """
    
    def __init__(self):
        """
        Inicializa o analisador de infraestrutura.
        """
        self.logger = logging.getLogger("iac_agent.infrastructure_analyzer")
    
    def analyze(self, infra_path: str) -> Dict[str, Any]:
        """
        Analisa a infraestrutura em um diretório.
        
        Args:
            infra_path: Caminho para o diretório contendo a infraestrutura.
            
        Returns:
            Resultado da análise.
        """
        self.logger.info(f"Analisando infraestrutura em: {infra_path}")
        
        # Verificar se o diretório existe
        if not os.path.exists(infra_path):
            self.logger.error(f"Diretório não encontrado: {infra_path}")
            return {"error": f"Diretório não encontrado: {infra_path}"}
        
        # Inicializar resultado da análise
        analysis = {
            "iac_tools": {},
            "resources": {},
            "providers": {},
            "environments": [],
            "dependencies": {},
            "variables": {},
            "modules": [],
            "files": []
        }
        
        # Identificar ferramentas de IaC
        analysis["iac_tools"] = self._identify_iac_tools(infra_path)
        
        # Analisar arquivos por tipo de ferramenta
        if analysis["iac_tools"].get("terraform", 0) > 0:
            terraform_analysis = self._analyze_terraform(infra_path)
            self._merge_analysis(analysis, terraform_analysis)
        
        if analysis["iac_tools"].get("cloudformation", 0) > 0:
            cloudformation_analysis = self._analyze_cloudformation(infra_path)
            self._merge_analysis(analysis, cloudformation_analysis)
        
        if analysis["iac_tools"].get("ansible", 0) > 0:
            ansible_analysis = self._analyze_ansible(infra_path)
            self._merge_analysis(analysis, ansible_analysis)
        
        if analysis["iac_tools"].get("kubernetes", 0) > 0:
            kubernetes_analysis = self._analyze_kubernetes(infra_path)
            self._merge_analysis(analysis, kubernetes_analysis)
        
        # Identificar ambientes
        analysis["environments"] = self._identify_environments(infra_path, analysis)
        
        return analysis
    
    def _identify_iac_tools(self, infra_path: str) -> Dict[str, int]:
        """
        Identifica ferramentas de IaC utilizadas no diretório.
        
        Args:
            infra_path: Caminho para o diretório contendo a infraestrutura.
            
        Returns:
            Dicionário com ferramentas de IaC e contagem de arquivos.
        """
        iac_tools = {
            "terraform": 0,
            "cloudformation": 0,
            "ansible": 0,
            "kubernetes": 0,
            "pulumi": 0,
            "chef": 0,
            "puppet": 0,
            "salt": 0
        }
        
        # Percorrer diretórios e arquivos
        for root, dirs, files in os.walk(infra_path):
            # Ignorar diretórios específicos
            dirs[:] = [d for d in dirs if d not in Config.IGNORE_DIRS]
            
            for file in files:
                file_path = os.path.join(root, file)
                
                # Verificar tamanho do arquivo
                if os.path.getsize(file_path) > Config.MAX_FILE_SIZE:
                    continue
                
                # Identificar por extensão e nome de arquivo
                if file.endswith('.tf') or file.endswith('.tfvars') or file == 'terraform.tfstate':
                    iac_tools["terraform"] += 1
                elif file.endswith('.yaml') or file.endswith('.yml'):
                    # Verificar conteúdo para diferenciar CloudFormation, Kubernetes e Ansible
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        try:
                            content = f.read()
                            if 'AWSTemplateFormatVersion' in content or 'Resources:' in content and 'Type: AWS::' in content:
                                iac_tools["cloudformation"] += 1
                            elif 'apiVersion:' in content and ('kind:' in content or 'Kind:' in content):
                                iac_tools["kubernetes"] += 1
                            elif 'hosts:' in content and ('tasks:' in content or 'roles:' in content):
                                iac_tools["ansible"] += 1
                        except Exception as e:
                            self.logger.warning(f"Erro ao ler arquivo {file_path}: {str(e)}")
                elif file.endswith('.json'):
                    # Verificar se é CloudFormation
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        try:
                            content = f.read()
                            if 'AWSTemplateFormatVersion' in content or '"Resources"' in content and '"Type": "AWS::' in content:
                                iac_tools["cloudformation"] += 1
                        except Exception as e:
                            self.logger.warning(f"Erro ao ler arquivo {file_path}: {str(e)}")
                elif file == 'playbook.yml' or file.endswith('.playbook.yml'):
                    iac_tools["ansible"] += 1
                elif file == 'Puppetfile':
                    iac_tools["puppet"] += 1
                elif file.endswith('.pp'):
                    iac_tools["puppet"] += 1
                elif file.endswith('.rb') and ('cookbook' in file_path or 'recipe' in file_path):
                    iac_tools["chef"] += 1
                elif file.endswith('.sls'):
                    iac_tools["salt"] += 1
        
        return iac_tools
    
    def _analyze_terraform(self, infra_path: str) -> Dict[str, Any]:
        """
        Analisa arquivos Terraform.
        
        Args:
            infra_path: Caminho para o diretório contendo a infraestrutura.
            
        Returns:
            Resultado da análise.
        """
        analysis = {
            "resources": {},
            "providers": {},
            "variables": {},
            "modules": [],
            "files": []
        }
        
        # Padrões para identificar recursos, providers, variáveis e módulos
        resource_pattern = re.compile(r'resource\s+"([^"]+)"\s+"([^"]+)"')
        provider_pattern = re.compile(r'provider\s+"([^"]+)"')
        variable_pattern = re.compile(r'variable\s+"([^"]+)"')
        module_pattern = re.compile(r'module\s+"([^"]+)"')
        
        # Percorrer diretórios e arquivos
        for root, dirs, files in os.walk(infra_path):
            # Ignorar diretórios específicos
            dirs[:] = [d for d in dirs if d not in Config.IGNORE_DIRS]
            
            for file in files:
                if file.endswith('.tf'):
                    file_path = os.path.join(root, file)
                    analysis["files"].append(file_path)
                    
                    # Verificar tamanho do arquivo
                    if os.path.getsize(file_path) > Config.MAX_FILE_SIZE:
                        continue
                    
                    # Analisar conteúdo
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        try:
                            content = f.read()
                            
                            # Identificar recursos
                            for resource_type, resource_name in resource_pattern.findall(content):
                                if resource_type not in analysis["resources"]:
                                    analysis["resources"][resource_type] = []
                                analysis["resources"][resource_type].append(resource_name)
                            
                            # Identificar providers
                            for provider in provider_pattern.findall(content):
                                analysis["providers"][provider] = analysis["providers"].get(provider, 0) + 1
                            
                            # Identificar variáveis
                            for variable in variable_pattern.findall(content):
                                analysis["variables"][variable] = None
                            
                            # Identificar módulos
                            for module in module_pattern.findall(content):
                                if module not in analysis["modules"]:
                                    analysis["modules"].append(module)
                        except Exception as e:
                            self.logger.warning(f"Erro ao analisar arquivo {file_path}: {str(e)}")
        
        return analysis
    
    def _analyze_cloudformation(self, infra_path: str) -> Dict[str, Any]:
        """
        Analisa arquivos CloudFormation.
        
        Args:
            infra_path: Caminho para o diretório contendo a infraestrutura.
            
        Returns:
            Resultado da análise.
        """
        analysis = {
            "resources": {},
            "providers": {"aws": 0},
            "variables": {},
            "files": []
        }
        
        # Percorrer diretórios e arquivos
        for root, dirs, files in os.walk(infra_path):
            # Ignorar diretórios específicos
            dirs[:] = [d for d in dirs if d not in Config.IGNORE_DIRS]
            
            for file in files:
                if (file.endswith('.yaml') or file.endswith('.yml') or file.endswith('.json')) and not file.startswith('.'):
                    file_path = os.path.join(root, file)
                    
                    # Verificar tamanho do arquivo
                    if os.path.getsize(file_path) > Config.MAX_FILE_SIZE:
                        continue
                    
                    # Verificar se é CloudFormation
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        try:
                            content = f.read()
                            if 'AWSTemplateFormatVersion' in content or (('Resources:' in content or '"Resources"' in content) and ('Type: AWS::' in content or '"Type": "AWS::' in content)):
                                analysis["files"].append(file_path)
                                analysis["providers"]["aws"] += 1
                                
                                # Analisar como YAML ou JSON
                                try:
                                    if file.endswith('.json'):
                                        template = json.loads(content)
                                    else:
                                        import yaml
                                        template = yaml.safe_load(content)
                                    
                                    # Identificar recursos
                                    if 'Resources' in template and isinstance(template['Resources'], dict):
                                        for resource_name, resource_data in template['Resources'].items():
                                            if 'Type' in resource_data:
                                                resource_type = resource_data['Type']
                                                if resource_type not in analysis["resources"]:
                                                    analysis["resources"][resource_type] = []
                                                analysis["resources"][resource_type].append(resource_name)
                                    
                                    # Identificar parâmetros (variáveis)
                                    if 'Parameters' in template and isinstance(template['Parameters'], dict):
                                        for param_name, param_data in template['Parameters'].items():
                                            analysis["variables"][param_name] = None
                                except Exception as e:
                                    self.logger.warning(f"Erro ao analisar template CloudFormation {file_path}: {str(e)}")
                        except Exception as e:
                            self.logger.warning(f"Erro ao ler arquivo {file_path}: {str(e)}")
        
        return analysis
    
    def _analyze_ansible(self, infra_path: str) -> Dict[str, Any]:
        """
        Analisa arquivos Ansible.
        
        Args:
            infra_path: Caminho para o diretório contendo a infraestrutura.
            
        Returns:
            Resultado da análise.
        """
        analysis = {
            "resources": {},
            "providers": {},
            "variables": {},
            "files": []
        }
        
        # Percorrer diretórios e arquivos
        for root, dirs, files in os.walk(infra_path):
            # Ignorar diretórios específicos
            dirs[:] = [d for d in dirs if d not in Config.IGNORE_DIRS]
            
            for file in files:
                if (file.endswith('.yaml') or file.endswith('.yml')) and not file.startswith('.'):
                    file_path = os.path.join(root, file)
                    
                    # Verificar tamanho do arquivo
                    if os.path.getsize(file_path) > Config.MAX_FILE_SIZE:
                        continue
                    
                    # Verificar se é Ansible
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        try:
                            content = f.read()
                            if ('hosts:' in content and ('tasks:' in content or 'roles:' in content)) or file == 'playbook.yml' or file.endswith('.playbook.yml'):
                                analysis["files"].append(file_path)
                                
                                # Analisar como YAML
                                try:
                                    import yaml
                                    playbook = yaml.safe_load(content)
                                    
                                    if isinstance(playbook, list):
                                        for play in playbook:
                                            if isinstance(play, dict):
                                                # Identificar hosts
                                                if 'hosts' in play:
                                                    host = play['hosts']
                                                    if 'ansible_host' not in analysis["resources"]:
                                                        analysis["resources"]["ansible_host"] = []
                                                    if host not in analysis["resources"]["ansible_host"]:
                                                        analysis["resources"]["ansible_host"].append(host)
                                                
                                                # Identificar tarefas e módulos
                                                if 'tasks' in play and isinstance(play['tasks'], list):
                                                    for task in play['tasks']:
                                                        if isinstance(task, dict):
                                                            for key, value in task.items():
                                                                if key not in ['name', 'when', 'register', 'tags', 'become', 'become_user']:
                                                                    if key not in analysis["resources"]:
                                                                        analysis["resources"][key] = []
                                                                    if isinstance(value, dict) and 'name' in value:
                                                                        if value['name'] not in analysis["resources"][key]:
                                                                            analysis["resources"][key].append(value['name'])
                                                                    else:
                                                                        if str(value) not in analysis["resources"][key]:
                                                                            analysis["resources"][key].append(str(value))
                                                
                                                # Identificar variáveis
                                                if 'vars' in play and isinstance(play['vars'], dict):
                                                    for var_name, var_value in play['vars'].items():
                                                        analysis["variables"][var_name] = None
                                except Exception as e:
                                    self.logger.warning(f"Erro ao analisar playbook Ansible {file_path}: {str(e)}")
                        except Exception as e:
                            self.logger.warning(f"Erro ao ler arquivo {file_path}: {str(e)}")
        
        return analysis
    
    def _analyze_kubernetes(self, infra_path: str) -> Dict[str, Any]:
        """
        Analisa arquivos Kubernetes.
        
        Args:
            infra_path: Caminho para o diretório contendo a infraestrutura.
            
        Returns:
            Resultado da análise.
        """
        analysis = {
            "resources": {},
            "providers": {"kubernetes": 0},
            "variables": {},
            "files": []
        }
        
        # Percorrer diretórios e arquivos
        for root, dirs, files in os.walk(infra_path):
            # Ignorar diretórios específicos
            dirs[:] = [d for d in dirs if d not in Config.IGNORE_DIRS]
            
            for file in files:
                if (file.endswith('.yaml') or file.endswith('.yml')) and not file.startswith('.'):
                    file_path = os.path.join(root, file)
                    
                    # Verificar tamanho do arquivo
                    if os.path.getsize(file_path) > Config.MAX_FILE_SIZE:
                        continue
                    
                    # Verificar se é Kubernetes
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        try:
                            content = f.read()
                            if 'apiVersion:' in content and ('kind:' in content or 'Kind:' in content):
                                analysis["files"].append(file_path)
                                analysis["providers"]["kubernetes"] += 1
                                
                                # Analisar como YAML
                                try:
                                    import yaml
                                    
                                    # Lidar com documentos YAML múltiplos
                                    documents = list(yaml.safe_load_all(content))
                                    
                                    for doc in documents:
                                        if isinstance(doc, dict):
                                            # Identificar recursos
                                            if 'kind' in doc and 'apiVersion' in doc:
                                                kind = doc['kind']
                                                api_version = doc['apiVersion']
                                                resource_type = f"{api_version}/{kind}"
                                                
                                                if resource_type not in analysis["resources"]:
                                                    analysis["resources"][resource_type] = []
                                                
                                                if 'metadata' in doc and isinstance(doc['metadata'], dict) and 'name' in doc['metadata']:
                                                    resource_name = doc['metadata']['name']
                                                    if resource_name not in analysis["resources"][resource_type]:
                                                        analysis["resources"][resource_type].append(resource_name)
                                except Exception as e:
                                    self.logger.warning(f"Erro ao analisar manifesto Kubernetes {file_path}: {str(e)}")
                        except Exception as e:
                            self.logger.warning(f"Erro ao ler arquivo {file_path}: {str(e)}")
        
        return analysis
    
    def _merge_analysis(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """
        Mescla resultados de análise.
        
        Args:
            target: Dicionário de destino.
            source: Dicionário de origem.
        """
        # Mesclar recursos
        for resource_type, resources in source.get("resources", {}).items():
            if resource_type not in target["resources"]:
                target["resources"][resource_type] = []
            for resource in resources:
                if resource not in target["resources"][resource_type]:
                    target["resources"][resource_type].append(resource)
        
        # Mesclar providers
        for provider, count in source.get("providers", {}).items():
            target["providers"][provider] = target["providers"].get(provider, 0) + count
        
        # Mesclar variáveis
        for var_name, var_value in source.get("variables", {}).items():
            if var_name not in target["variables"]:
                target["variables"][var_name] = var_value
        
        # Mesclar módulos
        for module in source.get("modules", []):
            if module not in target["modules"]:
                target["modules"].append(module)
        
        # Mesclar arquivos
        for file_path in source.get("files", []):
            if file_path not in target["files"]:
                target["files"].append(file_path)
    
    def _identify_environments(self, infra_path: str, analysis: Dict[str, Any]) -> List[str]:
        """
        Identifica ambientes de infraestrutura.
        
        Args:
            infra_path: Caminho para o diretório contendo a infraestrutura.
            analysis: Resultado da análise.
            
        Returns:
            Lista de ambientes identificados.
        """
        environments = set()
        
        # Identificar por nomes de diretórios
        env_dirs = ['dev', 'development', 'test', 'testing', 'staging', 'prod', 'production', 'qa', 'homolog', 'sandbox']
        
        for root, dirs, files in os.walk(infra_path):
            for dir_name in dirs:
                if dir_name.lower() in env_dirs:
                    environments.add(dir_name.lower())
                elif dir_name.lower().startswith(tuple(env + '-' for env in env_dirs)):
                    environments.add(dir_name.split('-')[0].lower())
        
        # Identificar por nomes de arquivos
        for file_path in analysis.get("files", []):
            file_name = os.path.basename(file_path)
            for env in env_dirs:
                if env in file_name.lower():
                    environments.add(env)
        
        # Identificar por variáveis
        for var_name in analysis.get("variables", {}).keys():
            for env in env_dirs:
                if env in var_name.lower():
                    environments.add(env)
        
        # Normalizar nomes de ambientes
        normalized_environments = []
        if 'dev' in environments or 'development' in environments:
            normalized_environments.append('development')
        if 'test' in environments or 'testing' in environments:
            normalized_environments.append('testing')
        if 'staging' in environments or 'homolog' in environments:
            normalized_environments.append('staging')
        if 'prod' in environments or 'production' in environments:
            normalized_environments.append('production')
        if 'qa' in environments:
            normalized_environments.append('qa')
        if 'sandbox' in environments:
            normalized_environments.append('sandbox')
        
        # Se nenhum ambiente foi identificado, assumir pelo menos desenvolvimento e produção
        if not normalized_environments:
            normalized_environments = ['development', 'production']
        
        return normalized_environments
