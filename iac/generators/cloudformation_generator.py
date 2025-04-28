"""
Gerador de código CloudFormation.
"""
import os
import logging
import json
import yaml
from typing import Dict, Any, List, Optional
import jinja2

from config import Config, logger
from models import LLMConfig

class CloudFormationGenerator:
    """
    Classe para gerar código CloudFormation com base na análise de infraestrutura.
    """
    
    def __init__(self, llm_config: Optional[LLMConfig] = None):
        """
        Inicializa o gerador de código CloudFormation.
        
        Args:
            llm_config: Configuração do modelo de linguagem.
        """
        self.logger = logging.getLogger("iac_agent.cloudformation_generator")
        self.template_dir = os.path.join(Config.TEMPLATE_DIR, "cloudformation")
        self.llm_config = llm_config or LLMConfig()
        
        # Configurar ambiente Jinja2
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.template_dir),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True
        )
    
    def generate(self, infra_analysis: Dict[str, Any], output_dir: str, format: str = "yaml") -> Dict[str, str]:
        """
        Gera código CloudFormation com base na análise de infraestrutura.
        
        Args:
            infra_analysis: Resultado da análise de infraestrutura.
            output_dir: Diretório de saída para os arquivos gerados.
            format: Formato dos arquivos (yaml ou json).
            
        Returns:
            Dicionário com nomes de arquivos e conteúdos gerados.
        """
        self.logger.info(f"Gerando código CloudFormation no formato {format}")
        
        # Criar diretório de saída se não existir
        os.makedirs(output_dir, exist_ok=True)
        
        # Inicializar dicionário de arquivos gerados
        generated_files = {}
        
        # Gerar template principal
        main_template = self._generate_main_template(infra_analysis)
        
        # Salvar template no formato especificado
        if format.lower() == "json":
            main_file = "template.json"
            main_content = json.dumps(main_template, indent=2)
        else:
            main_file = "template.yaml"
            main_content = yaml.dump(main_template, default_flow_style=False)
        
        generated_files[main_file] = main_content
        with open(os.path.join(output_dir, main_file), "w") as f:
            f.write(main_content)
        
        # Gerar templates para cada ambiente
        for env in infra_analysis.get("environments", []):
            env_dir = os.path.join(output_dir, env)
            os.makedirs(env_dir, exist_ok=True)
            
            env_template = self._generate_environment_template(infra_analysis, env)
            
            # Salvar template no formato especificado
            if format.lower() == "json":
                env_file = f"{env}/template.json"
                env_content = json.dumps(env_template, indent=2)
            else:
                env_file = f"{env}/template.yaml"
                env_content = yaml.dump(env_template, default_flow_style=False)
            
            generated_files[env_file] = env_content
            with open(os.path.join(output_dir, env_file), "w") as f:
                f.write(env_content)
            
            # Gerar arquivo de parâmetros para o ambiente
            params_template = self._generate_parameters_file(infra_analysis, env)
            
            # Salvar parâmetros no formato especificado
            if format.lower() == "json":
                params_file = f"{env}/parameters.json"
                params_content = json.dumps(params_template, indent=2)
            else:
                params_file = f"{env}/parameters.yaml"
                params_content = yaml.dump(params_template, default_flow_style=False)
            
            generated_files[params_file] = params_content
            with open(os.path.join(output_dir, params_file), "w") as f:
                f.write(params_content)
        
        # Gerar templates para recursos específicos
        resource_types = self._identify_resource_groups(infra_analysis)
        for resource_type in resource_types:
            resource_dir = os.path.join(output_dir, "resources", resource_type)
            os.makedirs(resource_dir, exist_ok=True)
            
            resource_template = self._generate_resource_template(infra_analysis, resource_type)
            
            # Salvar template no formato especificado
            if format.lower() == "json":
                resource_file = f"resources/{resource_type}/template.json"
                resource_content = json.dumps(resource_template, indent=2)
            else:
                resource_file = f"resources/{resource_type}/template.yaml"
                resource_content = yaml.dump(resource_template, default_flow_style=False)
            
            generated_files[resource_file] = resource_content
            with open(os.path.join(output_dir, resource_file), "w") as f:
                f.write(resource_content)
        
        return generated_files
    
    def _generate_main_template(self, infra_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera o template principal do CloudFormation.
        
        Args:
            infra_analysis: Resultado da análise de infraestrutura.
            
        Returns:
            Template CloudFormation.
        """
        # Verificar se há template disponível
        if os.path.exists(os.path.join(self.template_dir, "main.yaml.j2")):
            template = self.jinja_env.get_template("main.yaml.j2")
            rendered = template.render(infra=infra_analysis)
            return yaml.safe_load(rendered)
        
        # Gerar com base na análise
        resources = infra_analysis.get("resources", {})
        
        # Usar LLM para gerar o conteúdo
        prompt = f"""
        Gere um template CloudFormation com base na seguinte análise de infraestrutura:
        
        Recursos: {resources}
        
        O template deve incluir:
        1. AWSTemplateFormatVersion e Description
        2. Parâmetros para valores configuráveis
        3. Recursos identificados na análise
        4. Outputs para recursos importantes
        
        Formate o template como um dicionário Python que pode ser convertido para YAML ou JSON.
        Não inclua comentários explicativos, apenas o código CloudFormation.
        """
        
        template_str = self.llm_config.generate_text(prompt)
        if template_str:
            try:
                # Tentar converter a string para dicionário
                import ast
                template = ast.literal_eval(template_str)
                if isinstance(template, dict):
                    return template
            except:
                # Se falhar, tentar carregar como YAML
                try:
                    template = yaml.safe_load(template_str)
                    if isinstance(template, dict):
                        return template
                except:
                    pass
        
        # Fallback: gerar template básico
        return self._generate_basic_template(infra_analysis)
    
    def _generate_basic_template(self, infra_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera um template CloudFormation básico.
        
        Args:
            infra_analysis: Resultado da análise de infraestrutura.
            
        Returns:
            Template CloudFormation básico.
        """
        template = {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Description": "Template CloudFormation gerado automaticamente",
            "Parameters": {
                "Environment": {
                    "Type": "String",
                    "Default": "development",
                    "AllowedValues": infra_analysis.get("environments", ["development", "production"]),
                    "Description": "Ambiente de implantação"
                }
            },
            "Resources": {},
            "Outputs": {}
        }
        
        # Adicionar recursos básicos
        for resource_type, resources in infra_analysis.get("resources", {}).items():
            if resource_type.startswith("AWS::"):
                for resource_name in resources:
                    logical_id = resource_name.replace("-", "").replace("_", "")
                    template["Resources"][logical_id] = {
                        "Type": resource_type,
                        "Properties": {
                            "Name": resource_name
                        }
                    }
                    
                    # Adicionar output para o recurso
                    template["Outputs"][f"{logical_id}Id"] = {
                        "Description": f"ID do recurso {resource_name}",
                        "Value": {"Ref": logical_id}
                    }
        
        return template
    
    def _generate_environment_template(self, infra_analysis: Dict[str, Any], environment: str) -> Dict[str, Any]:
        """
        Gera um template CloudFormation para um ambiente específico.
        
        Args:
            infra_analysis: Resultado da análise de infraestrutura.
            environment: Ambiente (development, staging, production).
            
        Returns:
            Template CloudFormation para o ambiente.
        """
        # Verificar se há template disponível
        template_name = f"{environment}.yaml.j2"
        if os.path.exists(os.path.join(self.template_dir, template_name)):
            template = self.jinja_env.get_template(template_name)
            rendered = template.render(infra=infra_analysis, environment=environment)
            return yaml.safe_load(rendered)
        
        # Usar LLM para gerar o conteúdo
        prompt = f"""
        Gere um template CloudFormation para o ambiente {environment} com base na seguinte análise de infraestrutura:
        
        Recursos: {infra_analysis.get("resources", {})}
        
        O template deve incluir:
        1. AWSTemplateFormatVersion e Description
        2. Parâmetros específicos para o ambiente {environment}
        3. Recursos com configurações apropriadas para {environment}
        4. Outputs para recursos importantes
        
        Formate o template como um dicionário Python que pode ser convertido para YAML ou JSON.
        Não inclua comentários explicativos, apenas o código CloudFormation.
        """
        
        template_str = self.llm_config.generate_text(prompt)
        if template_str:
            try:
                # Tentar converter a string para dicionário
                import ast
                template = ast.literal_eval(template_str)
                if isinstance(template, dict):
                    return template
            except:
                # Se falhar, tentar carregar como YAML
                try:
                    template = yaml.safe_load(template_str)
                    if isinstance(template, dict):
                        return template
                except:
                    pass
        
        # Fallback: gerar template básico para o ambiente
        return self._generate_basic_environment_template(infra_analysis, environment)
    
    def _generate_basic_environment_template(self, infra_analysis: Dict[str, Any], environment: str) -> Dict[str, Any]:
        """
        Gera um template CloudFormation básico para um ambiente específico.
        
        Args:
            infra_analysis: Resultado da análise de infraestrutura.
            environment: Ambiente (development, staging, production).
            
        Returns:
            Template CloudFormation básico para o ambiente.
        """
        template = {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Description": f"Template CloudFormation para ambiente {environment}",
            "Parameters": {
                "Environment": {
                    "Type": "String",
                    "Default": environment,
                    "Description": "Ambiente de implantação"
                }
            },
            "Resources": {},
            "Outputs": {}
        }
        
        # Adicionar recursos com configurações específicas para o ambiente
        for resource_type, resources in infra_analysis.get("resources", {}).items():
            if resource_type.startswith("AWS::"):
                for resource_name in resources:
                    logical_id = resource_name.replace("-", "").replace("_", "")
                    
                    # Configurações específicas por ambiente
                    if environment == "development":
                        template["Resources"][logical_id] = {
                            "Type": resource_type,
                            "Properties": {
                                "Name": f"{resource_name}-dev",
                                "Environment": "development"
                            }
                        }
                    elif environment == "staging":
                        template["Resources"][logical_id] = {
                            "Type": resource_type,
                            "Properties": {
                                "Name": f"{resource_name}-staging",
                                "Environment": "staging"
                            }
                        }
                    elif environment == "production":
                        template["Resources"][logical_id] = {
                            "Type": resource_type,
                            "Properties": {
                                "Name": f"{resource_name}-prod",
                                "Environment": "production"
                            }
                        }
                    else:
                        template["Resources"][logical_id] = {
                            "Type": resource_type,
                            "Properties": {
                                "Name": f"{resource_name}-{environment}",
                                "Environment": environment
                            }
                        }
                    
                    # Adicionar output para o recurso
                    template["Outputs"][f"{logical_id}Id"] = {
                        "Description": f"ID do recurso {resource_name} no ambiente {environment}",
                        "Value": {"Ref": logical_id}
                    }
        
        return template
    
    def _generate_parameters_file(self, infra_analysis: Dict[str, Any], environment: str) -> Dict[str, Any]:
        """
        Gera um arquivo de parâmetros CloudFormation para um ambiente específico.
        
        Args:
            infra_analysis: Resultado da análise de infraestrutura.
            environment: Ambiente (development, staging, production).
            
        Returns:
            Arquivo de parâmetros CloudFormation para o ambiente.
        """
        # Verificar se há template disponível
        template_name = f"{environment}-parameters.yaml.j2"
        if os.path.exists(os.path.join(self.template_dir, template_name)):
            template = self.jinja_env.get_template(template_name)
            rendered = template.render(infra=infra_analysis, environment=environment)
            return yaml.safe_load(rendered)
        
        # Gerar parâmetros básicos
        parameters = {
            "Parameters": [
                {
                    "ParameterKey": "Environment",
                    "ParameterValue": environment
                }
            ]
        }
        
        # Adicionar parâmetros para variáveis identificadas
        for var_name in infra_analysis.get("variables", {}).keys():
            parameters["Parameters"].append({
                "ParameterKey": var_name,
                "ParameterValue": f"valor-para-{var_name}-{environment}"
            })
        
        return parameters
    
    def _identify_resource_groups(self, infra_analysis: Dict[str, Any]) -> List[str]:
        """
        Identifica grupos de recursos para templates separados.
        
        Args:
            infra_analysis: Resultado da análise de infraestrutura.
            
        Returns:
            Lista de grupos de recursos.
        """
        resource_groups = []
        
        # Agrupar por tipo de recurso
        for resource_type in infra_analysis.get("resources", {}).keys():
            if resource_type.startswith("AWS::"):
                # Extrair categoria do recurso (ex: AWS::EC2 de AWS::EC2::Instance)
                parts = resource_type.split("::")
                if len(parts) >= 2:
                    category = parts[1].lower()
                    if category not in resource_groups:
                        resource_groups.append(category)
        
        # Se não houver grupos, adicionar um grupo padrão
        if not resource_groups:
            resource_groups.append("resources")
        
        return resource_groups
    
    def _generate_resource_template(self, infra_analysis: Dict[str, Any], resource_group: str) -> Dict[str, Any]:
        """
        Gera um template CloudFormation para um grupo de recursos específico.
        
        Args:
            infra_analysis: Resultado da análise de infraestrutura.
            resource_group: Grupo de recursos.
            
        Returns:
            Template CloudFormation para o grupo de recursos.
        """
        # Verificar se há template disponível
        template_name = f"resources/{resource_group}.yaml.j2"
        if os.path.exists(os.path.join(self.template_dir, template_name)):
            template = self.jinja_env.get_template(template_name)
            rendered = template.render(infra=infra_analysis, resource_group=resource_group)
            return yaml.safe_load(rendered)
        
        # Gerar template básico para o grupo de recursos
        template = {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Description": f"Template CloudFormation para recursos {resource_group}",
            "Parameters": {
                "Environment": {
                    "Type": "String",
                    "Default": "development",
                    "AllowedValues": infra_analysis.get("environments", ["development", "production"]),
                    "Description": "Ambiente de implantação"
                }
            },
            "Resources": {},
            "Outputs": {}
        }
        
        # Adicionar recursos do grupo
        for resource_type, resources in infra_analysis.get("resources", {}).items():
            if resource_type.startswith("AWS::"):
                # Verificar se o recurso pertence ao grupo
                parts = resource_type.split("::")
                if len(parts) >= 2 and parts[1].lower() == resource_group:
                    for resource_name in resources:
                        logical_id = resource_name.replace("-", "").replace("_", "")
                        template["Resources"][logical_id] = {
                            "Type": resource_type,
                            "Properties": {
                                "Name": {"Fn::Sub": f"{resource_name}-${{Environment}}"},
                                "Environment": {"Ref": "Environment"}
                            }
                        }
                        
                        # Adicionar output para o recurso
                        template["Outputs"][f"{logical_id}Id"] = {
                            "Description": f"ID do recurso {resource_name}",
                            "Value": {"Ref": logical_id}
                        }
        
        return template
