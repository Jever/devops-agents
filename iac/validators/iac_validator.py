"""
Validador de infraestrutura como código.
"""
import os
import logging
import re
import json
import yaml
from typing import Dict, Any, List, Optional, Tuple

from config import Config, logger
from models import LLMConfig

class IaCValidator:
    """
    Classe para validar código de infraestrutura.
    """
    
    def __init__(self, llm_config: Optional[LLMConfig] = None):
        """
        Inicializa o validador de infraestrutura.
        
        Args:
            llm_config: Configuração do modelo de linguagem.
        """
        self.logger = logging.getLogger("iac_agent.validator")
        self.llm_config = llm_config or LLMConfig()
    
    def validate(self, file_path: str, file_content: str, iac_type: str) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Valida o código de infraestrutura.
        
        Args:
            file_path: Caminho do arquivo.
            file_content: Conteúdo do arquivo.
            iac_type: Tipo de IaC (terraform, cloudformation, ansible, kubernetes).
            
        Returns:
            Tupla com flag de validade e lista de problemas encontrados.
        """
        self.logger.info(f"Validando arquivo {file_path} do tipo {iac_type}")
        
        # Verificar tipo de IaC
        if iac_type.lower() == "terraform":
            return self._validate_terraform(file_path, file_content)
        elif iac_type.lower() == "cloudformation":
            return self._validate_cloudformation(file_path, file_content)
        elif iac_type.lower() == "ansible":
            return self._validate_ansible(file_path, file_content)
        elif iac_type.lower() == "kubernetes":
            return self._validate_kubernetes(file_path, file_content)
        else:
            self.logger.warning(f"Tipo de IaC não suportado: {iac_type}")
            return False, [{"severity": "error", "message": f"Tipo de IaC não suportado: {iac_type}"}]
    
    def _validate_terraform(self, file_path: str, file_content: str) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Valida código Terraform.
        
        Args:
            file_path: Caminho do arquivo.
            file_content: Conteúdo do arquivo.
            
        Returns:
            Tupla com flag de validade e lista de problemas encontrados.
        """
        issues = []
        
        # Verificar sintaxe básica
        if not self._is_valid_terraform_syntax(file_content):
            issues.append({
                "severity": "error",
                "message": "Erro de sintaxe no arquivo Terraform",
                "file": file_path,
                "line": 0
            })
            return False, issues
        
        # Verificar problemas comuns
        issues.extend(self._check_terraform_common_issues(file_path, file_content))
        
        # Verificar boas práticas
        issues.extend(self._check_terraform_best_practices(file_path, file_content))
        
        # Determinar se o arquivo é válido (sem erros críticos)
        is_valid = not any(issue["severity"] == "error" for issue in issues)
        
        return is_valid, issues
    
    def _is_valid_terraform_syntax(self, content: str) -> bool:
        """
        Verifica se o conteúdo tem sintaxe Terraform válida.
        
        Args:
            content: Conteúdo do arquivo Terraform.
            
        Returns:
            True se a sintaxe for válida, False caso contrário.
        """
        # Verificação básica de sintaxe (chaves balanceadas, etc.)
        open_braces = content.count("{")
        close_braces = content.count("}")
        
        if open_braces != close_braces:
            return False
        
        # Verificar aspas não fechadas
        if content.count('"') % 2 != 0:
            return False
        
        return True
    
    def _check_terraform_common_issues(self, file_path: str, content: str) -> List[Dict[str, Any]]:
        """
        Verifica problemas comuns em código Terraform.
        
        Args:
            file_path: Caminho do arquivo.
            content: Conteúdo do arquivo Terraform.
            
        Returns:
            Lista de problemas encontrados.
        """
        issues = []
        
        # Verificar recursos sem tags
        if re.search(r'resource\s+"aws_', content) and not re.search(r'tags\s*=', content):
            issues.append({
                "severity": "warning",
                "message": "Recursos AWS sem tags",
                "file": file_path,
                "line": self._find_line_number(content, r'resource\s+"aws_')
            })
        
        # Verificar variáveis sem descrição
        var_matches = re.finditer(r'variable\s+"([^"]+)"\s*{', content)
        for match in var_matches:
            var_name = match.group(1)
            var_block_start = match.start()
            var_block_end = self._find_closing_brace(content, var_block_start)
            var_block = content[var_block_start:var_block_end]
            
            if not re.search(r'description\s*=', var_block):
                issues.append({
                    "severity": "warning",
                    "message": f"Variável '{var_name}' sem descrição",
                    "file": file_path,
                    "line": content[:var_block_start].count('\n') + 1
                })
        
        # Verificar hardcoded values
        sensitive_patterns = [
            (r'(access_key|secret_key)\s*=\s*"[^"]+"', "Credenciais AWS hardcoded", "error"),
            (r'(password|token)\s*=\s*"[^"]+"', "Senha ou token hardcoded", "error"),
            (r'(private_key|ssh_key)\s*=\s*"[^"]+"', "Chave privada hardcoded", "error")
        ]
        
        for pattern, message, severity in sensitive_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                issues.append({
                    "severity": severity,
                    "message": message,
                    "file": file_path,
                    "line": content[:match.start()].count('\n') + 1
                })
        
        return issues
    
    def _check_terraform_best_practices(self, file_path: str, content: str) -> List[Dict[str, Any]]:
        """
        Verifica boas práticas em código Terraform.
        
        Args:
            file_path: Caminho do arquivo.
            content: Conteúdo do arquivo Terraform.
            
        Returns:
            Lista de problemas encontrados.
        """
        issues = []
        
        # Verificar uso de versões específicas de providers
        if re.search(r'provider\s+"', content) and not re.search(r'version\s*=', content) and not re.search(r'required_providers', content):
            issues.append({
                "severity": "info",
                "message": "Providers sem versão especificada",
                "file": file_path,
                "line": self._find_line_number(content, r'provider\s+"')
            })
        
        # Verificar uso de latest/master
        latest_matches = re.finditer(r'(latest|master)', content)
        for match in latest_matches:
            issues.append({
                "severity": "warning",
                "message": "Uso de 'latest' ou 'master' em vez de versões específicas",
                "file": file_path,
                "line": content[:match.start()].count('\n') + 1
            })
        
        # Verificar recursos sem count ou for_each para múltiplos recursos similares
        resource_count = len(re.findall(r'resource\s+"[^"]+"\s+"[^"]+"', content))
        if resource_count > 3 and not re.search(r'(count|for_each)\s*=', content):
            issues.append({
                "severity": "info",
                "message": "Múltiplos recursos similares sem uso de count ou for_each",
                "file": file_path,
                "line": 0
            })
        
        return issues
    
    def _validate_cloudformation(self, file_path: str, file_content: str) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Valida código CloudFormation.
        
        Args:
            file_path: Caminho do arquivo.
            file_content: Conteúdo do arquivo.
            
        Returns:
            Tupla com flag de validade e lista de problemas encontrados.
        """
        issues = []
        
        # Verificar sintaxe básica
        is_valid_syntax, syntax_error = self._is_valid_cloudformation_syntax(file_content)
        if not is_valid_syntax:
            issues.append({
                "severity": "error",
                "message": f"Erro de sintaxe no arquivo CloudFormation: {syntax_error}",
                "file": file_path,
                "line": 0
            })
            return False, issues
        
        # Carregar o template
        try:
            if file_path.endswith('.json'):
                template = json.loads(file_content)
            else:
                template = yaml.safe_load(file_content)
        except Exception as e:
            issues.append({
                "severity": "error",
                "message": f"Erro ao carregar template CloudFormation: {str(e)}",
                "file": file_path,
                "line": 0
            })
            return False, issues
        
        # Verificar estrutura básica
        if not isinstance(template, dict):
            issues.append({
                "severity": "error",
                "message": "Template CloudFormation inválido: deve ser um objeto",
                "file": file_path,
                "line": 0
            })
            return False, issues
        
        # Verificar seção Resources
        if "Resources" not in template:
            issues.append({
                "severity": "error",
                "message": "Template CloudFormation sem seção Resources",
                "file": file_path,
                "line": 0
            })
            return False, issues
        
        # Verificar problemas comuns
        issues.extend(self._check_cloudformation_common_issues(file_path, file_content, template))
        
        # Verificar boas práticas
        issues.extend(self._check_cloudformation_best_practices(file_path, file_content, template))
        
        # Determinar se o arquivo é válido (sem erros críticos)
        is_valid = not any(issue["severity"] == "error" for issue in issues)
        
        return is_valid, issues
    
    def _is_valid_cloudformation_syntax(self, content: str) -> Tuple[bool, str]:
        """
        Verifica se o conteúdo tem sintaxe CloudFormation válida.
        
        Args:
            content: Conteúdo do arquivo CloudFormation.
            
        Returns:
            Tupla com flag de validade e mensagem de erro.
        """
        try:
            # Tentar carregar como JSON
            if content.strip().startswith('{'):
                json.loads(content)
            # Tentar carregar como YAML
            else:
                yaml.safe_load(content)
            return True, ""
        except Exception as e:
            return False, str(e)
    
    def _check_cloudformation_common_issues(self, file_path: str, content: str, template: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Verifica problemas comuns em código CloudFormation.
        
        Args:
            file_path: Caminho do arquivo.
            content: Conteúdo do arquivo CloudFormation.
            template: Template CloudFormation carregado.
            
        Returns:
            Lista de problemas encontrados.
        """
        issues = []
        
        # Verificar recursos sem Type
        resources = template.get("Resources", {})
        for resource_id, resource in resources.items():
            if not isinstance(resource, dict):
                issues.append({
                    "severity": "error",
                    "message": f"Recurso '{resource_id}' inválido: deve ser um objeto",
                    "file": file_path,
                    "line": self._find_line_number(content, resource_id)
                })
                continue
            
            if "Type" not in resource:
                issues.append({
                    "severity": "error",
                    "message": f"Recurso '{resource_id}' sem Type",
                    "file": file_path,
                    "line": self._find_line_number(content, resource_id)
                })
        
        # Verificar parâmetros sem Type
        parameters = template.get("Parameters", {})
        for param_id, param in parameters.items():
            if not isinstance(param, dict):
                issues.append({
                    "severity": "error",
                    "message": f"Parâmetro '{param_id}' inválido: deve ser um objeto",
                    "file": file_path,
                    "line": self._find_line_number(content, param_id)
                })
                continue
            
            if "Type" not in param:
                issues.append({
                    "severity": "error",
                    "message": f"Parâmetro '{param_id}' sem Type",
                    "file": file_path,
                    "line": self._find_line_number(content, param_id)
                })
        
        # Verificar hardcoded values
        sensitive_patterns = [
            (r'(AccessKey|SecretKey):\s*[^\s{]', "Credenciais AWS hardcoded", "error"),
            (r'(Password|Token):\s*[^\s{]', "Senha ou token hardcoded", "error"),
            (r'(PrivateKey|SSHKey):\s*[^\s{]', "Chave privada hardcoded", "error")
        ]
        
        for pattern, message, severity in sensitive_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                issues.append({
                    "severity": severity,
                    "message": message,
                    "file": file_path,
                    "line": content[:match.start()].count('\n') + 1
                })
        
        return issues
    
    def _check_cloudformation_best_practices(self, file_path: str, content: str, template: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Verifica boas práticas em código CloudFormation.
        
        Args:
            file_path: Caminho do arquivo.
            content: Conteúdo do arquivo CloudFormation.
            template: Template CloudFormation carregado.
            
        Returns:
            Lista de problemas encontrados.
        """
        issues = []
        
        # Verificar parâmetros sem Description
        parameters = template.get("Parameters", {})
        for param_id, param in parameters.items():
            if isinstance(param, dict) and "Description" not in param:
                issues.append({
                    "severity": "warning",
                    "message": f"Parâmetro '{param_id}' sem Description",
                    "file": file_path,
                    "line": self._find_line_number(content, param_id)
                })
        
        # Verificar outputs sem Description
        outputs = template.get("Outputs", {})
        for output_id, output in outputs.items():
            if isinstance(output, dict) and "Description" not in output:
                issues.append({
                    "severity": "warning",
                    "message": f"Output '{output_id}' sem Description",
                    "file": file_path,
                    "line": self._find_line_number(content, output_id)
                })
        
        # Verificar recursos AWS sem Tags
        resources = template.get("Resources", {})
        for resource_id, resource in resources.items():
            if isinstance(resource, dict) and isinstance(resource.get("Type"), str) and resource.get("Type").startswith("AWS::"):
                properties = resource.get("Properties", {})
                if isinstance(properties, dict) and "Tags" not in properties:
                    # Alguns recursos não suportam tags
                    non_taggable_resources = ["AWS::CloudFormation::", "AWS::IAM::Policy"]
                    if not any(resource.get("Type").startswith(prefix) for prefix in non_taggable_resources):
                        issues.append({
                            "severity": "warning",
                            "message": f"Recurso AWS '{resource_id}' sem Tags",
                            "file": file_path,
                            "line": self._find_line_number(content, resource_id)
                        })
        
        return issues
    
    def _validate_ansible(self, file_path: str, file_content: str) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Valida código Ansible.
        
        Args:
            file_path: Caminho do arquivo.
            file_content: Conteúdo do arquivo.
            
        Returns:
            Tupla com flag de validade e lista de problemas encontrados.
        """
        issues = []
        
        # Verificar sintaxe básica
        is_valid_syntax, syntax_error = self._is_valid_ansible_syntax(file_content)
        if not is_valid_syntax:
            issues.append({
                "severity": "error",
                "message": f"Erro de sintaxe no arquivo Ansible: {syntax_error}",
                "file": file_path,
                "line": 0
            })
            return False, issues
        
        # Carregar o conteúdo
        try:
            content_obj = yaml.safe_load(file_content)
        except Exception as e:
            issues.append({
                "severity": "error",
                "message": f"Erro ao carregar arquivo Ansible: {str(e)}",
                "file": file_path,
                "line": 0
            })
            return False, issues
        
        # Verificar estrutura básica
        if not isinstance(content_obj, list) and not isinstance(content_obj, dict):
            issues.append({
                "severity": "error",
                "message": "Arquivo Ansible inválido: deve ser uma lista ou um dicionário",
                "file": file_path,
                "line": 0
            })
            return False, issues
        
        # Verificar problemas comuns
        issues.extend(self._check_ansible_common_issues(file_path, file_content, content_obj))
        
        # Verificar boas práticas
        issues.extend(self._check_ansible_best_practices(file_path, file_content, content_obj))
        
        # Determinar se o arquivo é válido (sem erros críticos)
        is_valid = not any(issue["severity"] == "error" for issue in issues)
        
        return is_valid, issues
    
    def _is_valid_ansible_syntax(self, content: str) -> Tuple[bool, str]:
        """
        Verifica se o conteúdo tem sintaxe Ansible válida.
        
        Args:
            content: Conteúdo do arquivo Ansible.
            
        Returns:
            Tupla com flag de validade e mensagem de erro.
        """
        try:
            yaml.safe_load(content)
            return True, ""
        except Exception as e:
            return False, str(e)
    
    def _check_ansible_common_issues(self, file_path: str, content: str, content_obj: Any) -> List[Dict[str, Any]]:
        """
        Verifica problemas comuns em código Ansible.
        
        Args:
            file_path: Caminho do arquivo.
            content: Conteúdo do arquivo Ansible.
            content_obj: Conteúdo Ansible carregado.
            
        Returns:
            Lista de problemas encontrados.
        """
        issues = []
        
        # Verificar tarefas sem nome
        if isinstance(content_obj, list):
            for i, item in enumerate(content_obj):
                if isinstance(item, dict):
                    # Verificar plays
                    if "tasks" in item and isinstance(item["tasks"], list):
                        for j, task in enumerate(item["tasks"]):
                            if isinstance(task, dict) and "name" not in task:
                                task_line = self._find_task_line(content, i, j)
                                issues.append({
                                    "severity": "warning",
                                    "message": f"Tarefa sem nome no play {i+1}, tarefa {j+1}",
                                    "file": file_path,
                                    "line": task_line
                                })
        
        # Verificar uso de comandos shell/command sem controle de idempotência
        shell_pattern = r'(shell|command):\s*'
        idempotence_pattern = r'(creates|removes|changed_when|failed_when):'
        
        shell_matches = re.finditer(shell_pattern, content)
        for match in shell_matches:
            # Verificar se há controle de idempotência nas proximidades
            start_pos = match.start()
            end_pos = self._find_next_task(content, start_pos)
            task_content = content[start_pos:end_pos]
            
            if not re.search(idempotence_pattern, task_content):
                issues.append({
                    "severity": "warning",
                    "message": "Uso de shell/command sem controle de idempotência",
                    "file": file_path,
                    "line": content[:start_pos].count('\n') + 1
                })
        
        # Verificar hardcoded values
        sensitive_patterns = [
            (r'(password|token):\s*[^\s{]', "Senha ou token hardcoded", "error"),
            (r'(private_key|ssh_key):\s*[^\s{]', "Chave privada hardcoded", "error")
        ]
        
        for pattern, message, severity in sensitive_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                # Ignorar se estiver dentro de vars_prompt
                start_pos = match.start()
                if "vars_prompt:" in content[:start_pos] and "vars:" not in content[content.rfind("\n", 0, start_pos):start_pos]:
                    continue
                
                issues.append({
                    "severity": severity,
                    "message": message,
                    "file": file_path,
                    "line": content[:start_pos].count('\n') + 1
                })
        
        return issues
    
    def _check_ansible_best_practices(self, file_path: str, content: str, content_obj: Any) -> List[Dict[str, Any]]:
        """
        Verifica boas práticas em código Ansible.
        
        Args:
            file_path: Caminho do arquivo.
            content: Conteúdo do arquivo Ansible.
            content_obj: Conteúdo Ansible carregado.
            
        Returns:
            Lista de problemas encontrados.
        """
        issues = []
        
        # Verificar handlers sem notify
        if "handlers:" in content and not "notify:" in content:
            issues.append({
                "severity": "warning",
                "message": "Handlers definidos mas não notificados",
                "file": file_path,
                "line": self._find_line_number(content, "handlers:")
            })
        
        # Verificar falta de tags
        if "tasks:" in content and not "tags:" in content:
            issues.append({
                "severity": "info",
                "message": "Tarefas sem tags",
                "file": file_path,
                "line": self._find_line_number(content, "tasks:")
            })
        
        # Verificar uso de become sem become_user
        if "become: true" in content or "become: yes" in content:
            if not "become_user:" in content:
                issues.append({
                    "severity": "warning",
                    "message": "Uso de become sem become_user",
                    "file": file_path,
                    "line": self._find_line_number(content, "become:")
                })
        
        return issues
    
    def _validate_kubernetes(self, file_path: str, file_content: str) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Valida código Kubernetes.
        
        Args:
            file_path: Caminho do arquivo.
            file_content: Conteúdo do arquivo.
            
        Returns:
            Tupla com flag de validade e lista de problemas encontrados.
        """
        issues = []
        
        # Verificar sintaxe básica
        is_valid_syntax, syntax_error = self._is_valid_kubernetes_syntax(file_content)
        if not is_valid_syntax:
            issues.append({
                "severity": "error",
                "message": f"Erro de sintaxe no arquivo Kubernetes: {syntax_error}",
                "file": file_path,
                "line": 0
            })
            return False, issues
        
        # Carregar o conteúdo
        try:
            # Lidar com documentos YAML múltiplos
            documents = list(yaml.safe_load_all(file_content))
        except Exception as e:
            issues.append({
                "severity": "error",
                "message": f"Erro ao carregar arquivo Kubernetes: {str(e)}",
                "file": file_path,
                "line": 0
            })
            return False, issues
        
        # Verificar cada documento
        for i, doc in enumerate(documents):
            if not isinstance(doc, dict):
                issues.append({
                    "severity": "error",
                    "message": f"Documento Kubernetes {i+1} inválido: deve ser um objeto",
                    "file": file_path,
                    "line": 0
                })
                continue
            
            # Verificar campos obrigatórios
            for field in ["apiVersion", "kind", "metadata"]:
                if field not in doc:
                    issues.append({
                        "severity": "error",
                        "message": f"Documento Kubernetes {i+1} sem campo obrigatório: {field}",
                        "file": file_path,
                        "line": self._find_document_line(file_content, i)
                    })
            
            # Verificar problemas comuns
            issues.extend(self._check_kubernetes_common_issues(file_path, file_content, doc, i))
        
        # Verificar boas práticas
        issues.extend(self._check_kubernetes_best_practices(file_path, file_content, documents))
        
        # Determinar se o arquivo é válido (sem erros críticos)
        is_valid = not any(issue["severity"] == "error" for issue in issues)
        
        return is_valid, issues
    
    def _is_valid_kubernetes_syntax(self, content: str) -> Tuple[bool, str]:
        """
        Verifica se o conteúdo tem sintaxe Kubernetes válida.
        
        Args:
            content: Conteúdo do arquivo Kubernetes.
            
        Returns:
            Tupla com flag de validade e mensagem de erro.
        """
        try:
            list(yaml.safe_load_all(content))
            return True, ""
        except Exception as e:
            return False, str(e)
    
    def _check_kubernetes_common_issues(self, file_path: str, content: str, doc: Dict[str, Any], doc_index: int) -> List[Dict[str, Any]]:
        """
        Verifica problemas comuns em código Kubernetes.
        
        Args:
            file_path: Caminho do arquivo.
            content: Conteúdo do arquivo Kubernetes.
            doc: Documento Kubernetes carregado.
            doc_index: Índice do documento.
            
        Returns:
            Lista de problemas encontrados.
        """
        issues = []
        
        # Verificar metadata
        metadata = doc.get("metadata", {})
        if not isinstance(metadata, dict):
            issues.append({
                "severity": "error",
                "message": f"Documento Kubernetes {doc_index+1}: metadata inválido",
                "file": file_path,
                "line": self._find_line_number(content, "metadata:")
            })
        else:
            # Verificar nome
            if "name" not in metadata:
                issues.append({
                    "severity": "error",
                    "message": f"Documento Kubernetes {doc_index+1}: metadata sem name",
                    "file": file_path,
                    "line": self._find_line_number(content, "metadata:")
                })
        
        # Verificar recursos sem limites
        if doc.get("kind") in ["Deployment", "StatefulSet", "DaemonSet", "Job", "CronJob"]:
            spec = doc.get("spec", {})
            template = spec.get("template", {})
            template_spec = template.get("spec", {})
            containers = template_spec.get("containers", [])
            
            for i, container in enumerate(containers):
                if not isinstance(container, dict):
                    continue
                
                if "resources" not in container:
                    issues.append({
                        "severity": "warning",
                        "message": f"Container {i+1} sem recursos definidos",
                        "file": file_path,
                        "line": self._find_container_line(content, doc_index, i)
                    })
                elif "limits" not in container.get("resources", {}):
                    issues.append({
                        "severity": "warning",
                        "message": f"Container {i+1} sem limites de recursos",
                        "file": file_path,
                        "line": self._find_container_line(content, doc_index, i)
                    })
        
        # Verificar uso de latest tag
        if doc.get("kind") in ["Deployment", "StatefulSet", "DaemonSet", "Job", "CronJob", "Pod"]:
            containers = []
            
            if "spec" in doc and "containers" in doc["spec"]:
                containers = doc["spec"]["containers"]
            elif "spec" in doc and "template" in doc["spec"] and "spec" in doc["spec"]["template"] and "containers" in doc["spec"]["template"]["spec"]:
                containers = doc["spec"]["template"]["spec"]["containers"]
            
            for i, container in enumerate(containers):
                if not isinstance(container, dict):
                    continue
                
                image = container.get("image", "")
                if image.endswith(":latest") or ":" not in image:
                    issues.append({
                        "severity": "warning",
                        "message": f"Container {i+1} usa tag 'latest' ou não especifica tag",
                        "file": file_path,
                        "line": self._find_container_line(content, doc_index, i)
                    })
        
        return issues
    
    def _check_kubernetes_best_practices(self, file_path: str, content: str, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Verifica boas práticas em código Kubernetes.
        
        Args:
            file_path: Caminho do arquivo.
            content: Conteúdo do arquivo Kubernetes.
            documents: Lista de documentos Kubernetes carregados.
            
        Returns:
            Lista de problemas encontrados.
        """
        issues = []
        
        for i, doc in enumerate(documents):
            if not isinstance(doc, dict):
                continue
            
            # Verificar recursos sem labels
            metadata = doc.get("metadata", {})
            if isinstance(metadata, dict) and "labels" not in metadata:
                issues.append({
                    "severity": "warning",
                    "message": f"Documento Kubernetes {i+1}: recurso sem labels",
                    "file": file_path,
                    "line": self._find_line_number(content, "metadata:")
                })
            
            # Verificar falta de health checks
            if doc.get("kind") in ["Deployment", "StatefulSet", "DaemonSet"]:
                spec = doc.get("spec", {})
                template = spec.get("template", {})
                template_spec = template.get("spec", {})
                containers = template_spec.get("containers", [])
                
                for j, container in enumerate(containers):
                    if not isinstance(container, dict):
                        continue
                    
                    if "livenessProbe" not in container and "readinessProbe" not in container:
                        issues.append({
                            "severity": "warning",
                            "message": f"Container {j+1} sem health checks (livenessProbe/readinessProbe)",
                            "file": file_path,
                            "line": self._find_container_line(content, i, j)
                        })
            
            # Verificar falta de namespace
            if isinstance(metadata, dict) and "namespace" not in metadata and doc.get("kind") != "Namespace":
                issues.append({
                    "severity": "warning",
                    "message": f"Documento Kubernetes {i+1}: recurso sem namespace especificado",
                    "file": file_path,
                    "line": self._find_line_number(content, "metadata:")
                })
            
            # Verificar secrets não criptografados
            if doc.get("kind") == "Secret" and "stringData" in doc and "data" not in doc:
                issues.append({
                    "severity": "warning",
                    "message": "Secret usando stringData em vez de data (valores não codificados em base64)",
                    "file": file_path,
                    "line": self._find_line_number(content, "stringData:")
                })
            
            # Verificar falta de seletores em serviços
            if doc.get("kind") == "Service":
                spec = doc.get("spec", {})
                if "selector" not in spec:
                    issues.append({
                        "severity": "warning",
                        "message": "Serviço sem seletores",
                        "file": file_path,
                        "line": self._find_line_number(content, "spec:")
                    })
        
        return issues
    
    def _find_line_number(self, content: str, pattern: str) -> int:
        """
        Encontra o número da linha de um padrão no conteúdo.
        
        Args:
            content: Conteúdo do arquivo.
            pattern: Padrão a ser encontrado.
            
        Returns:
            Número da linha (1-based).
        """
        match = re.search(pattern, content)
        if match:
            return content[:match.start()].count('\n') + 1
        return 0
    
    def _find_closing_brace(self, content: str, start_pos: int) -> int:
        """
        Encontra a posição da chave de fechamento correspondente.
        
        Args:
            content: Conteúdo do arquivo.
            start_pos: Posição inicial.
            
        Returns:
            Posição da chave de fechamento.
        """
        open_count = 0
        for i in range(start_pos, len(content)):
            if content[i] == '{':
                open_count += 1
            elif content[i] == '}':
                open_count -= 1
                if open_count == 0:
                    return i + 1
        return len(content)
    
    def _find_task_line(self, content: str, play_index: int, task_index: int) -> int:
        """
        Encontra o número da linha de uma tarefa específica.
        
        Args:
            content: Conteúdo do arquivo.
            play_index: Índice do play.
            task_index: Índice da tarefa.
            
        Returns:
            Número da linha (1-based).
        """
        lines = content.split('\n')
        play_count = -1
        task_count = -1
        
        for i, line in enumerate(lines):
            if re.match(r'^\s*-\s+\w+:', line) and not re.match(r'^\s*-\s+\w+:\s*\[', line):
                play_count += 1
                task_count = -1
            
            if play_count == play_index and re.match(r'^\s+\s*-\s+\w+:', line):
                task_count += 1
                if task_count == task_index:
                    return i + 1
        
        return 0
    
    def _find_next_task(self, content: str, start_pos: int) -> int:
        """
        Encontra a posição da próxima tarefa.
        
        Args:
            content: Conteúdo do arquivo.
            start_pos: Posição inicial.
            
        Returns:
            Posição da próxima tarefa.
        """
        lines = content[start_pos:].split('\n')
        current_indent = None
        
        for i, line in enumerate(lines):
            if i == 0:
                # Determinar indentação da tarefa atual
                match = re.match(r'^(\s*)', line)
                if match:
                    current_indent = len(match.group(1))
                continue
            
            # Procurar por linha com mesma indentação ou menor
            match = re.match(r'^(\s*)-', line)
            if match and (current_indent is None or len(match.group(1)) <= current_indent):
                return start_pos + content[start_pos:].find(line)
        
        return len(content)
    
    def _find_document_line(self, content: str, doc_index: int) -> int:
        """
        Encontra o número da linha de um documento YAML específico.
        
        Args:
            content: Conteúdo do arquivo.
            doc_index: Índice do documento.
            
        Returns:
            Número da linha (1-based).
        """
        doc_separators = [m.start() for m in re.finditer(r'^---', content, re.MULTILINE)]
        
        if doc_index == 0 and not doc_separators:
            return 1
        
        if doc_index == 0 and doc_separators:
            return 1
        
        if doc_index < len(doc_separators):
            return content[:doc_separators[doc_index]].count('\n') + 1
        
        return 0
    
    def _find_container_line(self, content: str, doc_index: int, container_index: int) -> int:
        """
        Encontra o número da linha de um container específico.
        
        Args:
            content: Conteúdo do arquivo.
            doc_index: Índice do documento.
            container_index: Índice do container.
            
        Returns:
            Número da linha (1-based).
        """
        # Encontrar o documento
        doc_start = 0
        doc_separators = [m.start() for m in re.finditer(r'^---', content, re.MULTILINE)]
        
        if doc_index > 0 and doc_index - 1 < len(doc_separators):
            doc_start = doc_separators[doc_index - 1]
        
        # Encontrar a seção de containers
        containers_match = re.search(r'containers:', content[doc_start:])
        if not containers_match:
            return 0
        
        containers_pos = doc_start + containers_match.start()
        containers_line = content[:containers_pos].count('\n') + 1
        
        # Encontrar o container específico
        container_count = -1
        lines = content[containers_pos:].split('\n')
        
        for i, line in enumerate(lines):
            if re.match(r'^\s*-\s+\w+:', line):
                container_count += 1
                if container_count == container_index:
                    return containers_line + i
        
        return containers_line
