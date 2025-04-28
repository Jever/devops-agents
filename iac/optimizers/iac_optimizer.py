"""
Otimizador de infraestrutura como código.
"""
import os
import logging
import re
from typing import Dict, Any, List, Optional, Tuple

from config import Config, logger
from models import LLMConfig

class IaCOptimizer:
    """
    Classe para otimizar código de infraestrutura.
    """
    
    def __init__(self, llm_config: Optional[LLMConfig] = None):
        """
        Inicializa o otimizador de infraestrutura.
        
        Args:
            llm_config: Configuração do modelo de linguagem.
        """
        self.logger = logging.getLogger("iac_agent.optimizer")
        self.llm_config = llm_config or LLMConfig()
    
    def optimize(self, file_path: str, file_content: str, iac_type: str) -> Tuple[bool, str]:
        """
        Otimiza o código de infraestrutura.
        
        Args:
            file_path: Caminho do arquivo.
            file_content: Conteúdo do arquivo.
            iac_type: Tipo de IaC (terraform, cloudformation, ansible, kubernetes).
            
        Returns:
            Tupla com flag de sucesso e conteúdo otimizado.
        """
        self.logger.info(f"Otimizando arquivo {file_path} do tipo {iac_type}")
        
        # Verificar tipo de IaC
        if iac_type.lower() == "terraform":
            return self._optimize_terraform(file_path, file_content)
        elif iac_type.lower() == "cloudformation":
            return self._optimize_cloudformation(file_path, file_content)
        elif iac_type.lower() == "ansible":
            return self._optimize_ansible(file_path, file_content)
        elif iac_type.lower() == "kubernetes":
            return self._optimize_kubernetes(file_path, file_content)
        else:
            self.logger.warning(f"Tipo de IaC não suportado: {iac_type}")
            return False, file_content
    
    def _optimize_terraform(self, file_path: str, file_content: str) -> Tuple[bool, str]:
        """
        Otimiza código Terraform.
        
        Args:
            file_path: Caminho do arquivo.
            file_content: Conteúdo do arquivo.
            
        Returns:
            Tupla com flag de sucesso e conteúdo otimizado.
        """
        # Verificar se há problemas comuns
        issues = self._identify_terraform_issues(file_content)
        
        if not issues:
            self.logger.info("Nenhum problema encontrado no código Terraform")
            return False, file_content
        
        # Usar LLM para otimizar o código
        prompt = f"""
        Otimize o seguinte código Terraform, corrigindo os problemas identificados:
        
        Problemas encontrados:
        {issues}
        
        Código original:
        ```hcl
        {file_content}
        ```
        
        Por favor, forneça apenas o código Terraform otimizado, sem explicações adicionais.
        """
        
        optimized_content = self.llm_config.generate_text(prompt)
        if not optimized_content:
            self.logger.warning("Falha ao otimizar código Terraform com LLM")
            return False, file_content
        
        # Limpar o resultado
        optimized_content = self._clean_code_from_llm(optimized_content)
        
        self.logger.info("Código Terraform otimizado com sucesso")
        return True, optimized_content
    
    def _identify_terraform_issues(self, content: str) -> List[str]:
        """
        Identifica problemas comuns em código Terraform.
        
        Args:
            content: Conteúdo do arquivo Terraform.
            
        Returns:
            Lista de problemas identificados.
        """
        issues = []
        
        # Verificar recursos sem tags
        if re.search(r'resource\s+"aws_', content) and not re.search(r'tags\s*=', content):
            issues.append("Recursos AWS sem tags")
        
        # Verificar variáveis sem descrição
        if re.search(r'variable\s+"[^"]+"\s*{[^}]*}', content) and not re.search(r'description\s*=', content):
            issues.append("Variáveis sem descrição")
        
        # Verificar variáveis sem tipo
        if re.search(r'variable\s+"[^"]+"\s*{[^}]*}', content) and not re.search(r'type\s*=', content):
            issues.append("Variáveis sem tipo definido")
        
        # Verificar outputs sem descrição
        if re.search(r'output\s+"[^"]+"\s*{[^}]*}', content) and not re.search(r'description\s*=', content):
            issues.append("Outputs sem descrição")
        
        # Verificar hardcoded values
        if re.search(r'(access_key|secret_key|password|token)\s*=\s*"[^"]+"', content):
            issues.append("Credenciais hardcoded no código")
        
        # Verificar recursos sem count ou for_each
        if len(re.findall(r'resource\s+"[^"]+"\s+"[^"]+"', content)) > 3 and not re.search(r'(count|for_each)\s*=', content):
            issues.append("Múltiplos recursos similares sem uso de count ou for_each")
        
        # Verificar uso de latest/master
        if re.search(r'(latest|master)', content):
            issues.append("Uso de 'latest' ou 'master' em vez de versões específicas")
        
        return issues
    
    def _optimize_cloudformation(self, file_path: str, file_content: str) -> Tuple[bool, str]:
        """
        Otimiza código CloudFormation.
        
        Args:
            file_path: Caminho do arquivo.
            file_content: Conteúdo do arquivo.
            
        Returns:
            Tupla com flag de sucesso e conteúdo otimizado.
        """
        # Verificar se há problemas comuns
        issues = self._identify_cloudformation_issues(file_content)
        
        if not issues:
            self.logger.info("Nenhum problema encontrado no código CloudFormation")
            return False, file_content
        
        # Usar LLM para otimizar o código
        prompt = f"""
        Otimize o seguinte código CloudFormation, corrigindo os problemas identificados:
        
        Problemas encontrados:
        {issues}
        
        Código original:
        ```yaml
        {file_content}
        ```
        
        Por favor, forneça apenas o código CloudFormation otimizado, sem explicações adicionais.
        """
        
        optimized_content = self.llm_config.generate_text(prompt)
        if not optimized_content:
            self.logger.warning("Falha ao otimizar código CloudFormation com LLM")
            return False, file_content
        
        # Limpar o resultado
        optimized_content = self._clean_code_from_llm(optimized_content)
        
        self.logger.info("Código CloudFormation otimizado com sucesso")
        return True, optimized_content
    
    def _identify_cloudformation_issues(self, content: str) -> List[str]:
        """
        Identifica problemas comuns em código CloudFormation.
        
        Args:
            content: Conteúdo do arquivo CloudFormation.
            
        Returns:
            Lista de problemas identificados.
        """
        issues = []
        
        # Verificar recursos sem tags
        if "Resources:" in content and "AWS::" in content and not "Tags:" in content:
            issues.append("Recursos AWS sem tags")
        
        # Verificar parâmetros sem descrição
        if "Parameters:" in content and not "Description:" in content:
            issues.append("Parâmetros sem descrição")
        
        # Verificar outputs sem descrição
        if "Outputs:" in content and not re.search(r'Description:', content):
            issues.append("Outputs sem descrição")
        
        # Verificar hardcoded values
        if re.search(r'(AccessKey|SecretKey|Password|Token):\s*[^\s{]', content):
            issues.append("Credenciais hardcoded no código")
        
        # Verificar uso de !Ref para valores dinâmicos
        if "Resources:" in content and not "!Ref" in content:
            issues.append("Falta de referências dinâmicas (!Ref) para parâmetros")
        
        # Verificar uso de !GetAtt para atributos
        if "Resources:" in content and not "!GetAtt" in content:
            issues.append("Falta de uso de !GetAtt para obter atributos de recursos")
        
        return issues
    
    def _optimize_ansible(self, file_path: str, file_content: str) -> Tuple[bool, str]:
        """
        Otimiza código Ansible.
        
        Args:
            file_path: Caminho do arquivo.
            file_content: Conteúdo do arquivo.
            
        Returns:
            Tupla com flag de sucesso e conteúdo otimizado.
        """
        # Verificar se há problemas comuns
        issues = self._identify_ansible_issues(file_content)
        
        if not issues:
            self.logger.info("Nenhum problema encontrado no código Ansible")
            return False, file_content
        
        # Usar LLM para otimizar o código
        prompt = f"""
        Otimize o seguinte código Ansible, corrigindo os problemas identificados:
        
        Problemas encontrados:
        {issues}
        
        Código original:
        ```yaml
        {file_content}
        ```
        
        Por favor, forneça apenas o código Ansible otimizado, sem explicações adicionais.
        """
        
        optimized_content = self.llm_config.generate_text(prompt)
        if not optimized_content:
            self.logger.warning("Falha ao otimizar código Ansible com LLM")
            return False, file_content
        
        # Limpar o resultado
        optimized_content = self._clean_code_from_llm(optimized_content)
        
        self.logger.info("Código Ansible otimizado com sucesso")
        return True, optimized_content
    
    def _identify_ansible_issues(self, content: str) -> List[str]:
        """
        Identifica problemas comuns em código Ansible.
        
        Args:
            content: Conteúdo do arquivo Ansible.
            
        Returns:
            Lista de problemas identificados.
        """
        issues = []
        
        # Verificar tarefas sem nome
        if re.search(r'^\s*-\s+\w+:', content, re.MULTILINE) and not re.search(r'^\s*-\s+name:', content, re.MULTILINE):
            issues.append("Tarefas sem nome")
        
        # Verificar uso de comandos shell/command em vez de módulos
        if re.search(r'(shell|command):', content) and not "creates:" in content and not "removes:" in content:
            issues.append("Uso de shell/command sem controle de idempotência (creates/removes)")
        
        # Verificar handlers sem notify
        if "handlers:" in content and not "notify:" in content:
            issues.append("Handlers definidos mas não notificados")
        
        # Verificar variáveis hardcoded
        if re.search(r'(password|token|secret|key):\s*[^\s{]', content, re.IGNORECASE):
            issues.append("Credenciais hardcoded no código")
        
        # Verificar falta de tags
        if "tasks:" in content and not "tags:" in content:
            issues.append("Tarefas sem tags")
        
        # Verificar falta de condicionais
        if "tasks:" in content and not "when:" in content:
            issues.append("Falta de condicionais (when) para controle de execução")
        
        return issues
    
    def _optimize_kubernetes(self, file_path: str, file_content: str) -> Tuple[bool, str]:
        """
        Otimiza código Kubernetes.
        
        Args:
            file_path: Caminho do arquivo.
            file_content: Conteúdo do arquivo.
            
        Returns:
            Tupla com flag de sucesso e conteúdo otimizado.
        """
        # Verificar se há problemas comuns
        issues = self._identify_kubernetes_issues(file_content)
        
        if not issues:
            self.logger.info("Nenhum problema encontrado no código Kubernetes")
            return False, file_content
        
        # Usar LLM para otimizar o código
        prompt = f"""
        Otimize o seguinte código Kubernetes, corrigindo os problemas identificados:
        
        Problemas encontrados:
        {issues}
        
        Código original:
        ```yaml
        {file_content}
        ```
        
        Por favor, forneça apenas o código Kubernetes otimizado, sem explicações adicionais.
        """
        
        optimized_content = self.llm_config.generate_text(prompt)
        if not optimized_content:
            self.logger.warning("Falha ao otimizar código Kubernetes com LLM")
            return False, file_content
        
        # Limpar o resultado
        optimized_content = self._clean_code_from_llm(optimized_content)
        
        self.logger.info("Código Kubernetes otimizado com sucesso")
        return True, optimized_content
    
    def _identify_kubernetes_issues(self, content: str) -> List[str]:
        """
        Identifica problemas comuns em código Kubernetes.
        
        Args:
            content: Conteúdo do arquivo Kubernetes.
            
        Returns:
            Lista de problemas identificados.
        """
        issues = []
        
        # Verificar recursos sem labels
        if "kind:" in content and not "labels:" in content:
            issues.append("Recursos sem labels")
        
        # Verificar recursos sem limites de recursos
        if "containers:" in content and not "resources:" in content:
            issues.append("Containers sem limites de recursos")
        
        # Verificar uso de latest tag
        if re.search(r'image:\s*[^:]+:latest', content):
            issues.append("Uso de tag 'latest' em imagens")
        
        # Verificar falta de health checks
        if "containers:" in content and not re.search(r'(livenessProbe|readinessProbe):', content):
            issues.append("Containers sem health checks (livenessProbe/readinessProbe)")
        
        # Verificar falta de namespace
        if "kind:" in content and not "namespace:" in content:
            issues.append("Recursos sem namespace especificado")
        
        # Verificar secrets não criptografados
        if "kind: Secret" in content and "stringData:" in content:
            issues.append("Secrets usando stringData em vez de data (valores não codificados em base64)")
        
        # Verificar falta de seletores em serviços
        if "kind: Service" in content and not "selector:" in content:
            issues.append("Serviços sem seletores")
        
        return issues
    
    def _clean_code_from_llm(self, content: str) -> str:
        """
        Limpa o código gerado pelo LLM.
        
        Args:
            content: Conteúdo gerado pelo LLM.
            
        Returns:
            Conteúdo limpo.
        """
        # Remover blocos de código
        content = re.sub(r'```[a-z]*\n', '', content)
        content = re.sub(r'```\n?$', '', content)
        
        # Remover explicações
        if "Aqui está o código otimizado:" in content:
            content = content.split("Aqui está o código otimizado:")[1].strip()
        
        # Remover linhas em branco extras
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        return content
