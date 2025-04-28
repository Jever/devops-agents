"""
Gerador de código Terraform.
"""
import os
import logging
from typing import Dict, Any, List, Optional
import jinja2

from config import Config, logger
from models import LLMConfig

class TerraformGenerator:
    """
    Classe para gerar código Terraform com base na análise de infraestrutura.
    """
    
    def __init__(self, llm_config: Optional[LLMConfig] = None):
        """
        Inicializa o gerador de código Terraform.
        
        Args:
            llm_config: Configuração do modelo de linguagem.
        """
        self.logger = logging.getLogger("iac_agent.terraform_generator")
        self.template_dir = os.path.join(Config.TEMPLATE_DIR, "terraform")
        self.llm_config = llm_config or LLMConfig()
        
        # Configurar ambiente Jinja2
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.template_dir),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True
        )
    
    def generate(self, infra_analysis: Dict[str, Any], output_dir: str) -> Dict[str, str]:
        """
        Gera código Terraform com base na análise de infraestrutura.
        
        Args:
            infra_analysis: Resultado da análise de infraestrutura.
            output_dir: Diretório de saída para os arquivos gerados.
            
        Returns:
            Dicionário com nomes de arquivos e conteúdos gerados.
        """
        self.logger.info("Gerando código Terraform")
        
        # Criar diretório de saída se não existir
        os.makedirs(output_dir, exist_ok=True)
        
        # Inicializar dicionário de arquivos gerados
        generated_files = {}
        
        # Gerar arquivos principais
        main_tf = self._generate_main_tf(infra_analysis)
        if main_tf:
            generated_files["main.tf"] = main_tf
            with open(os.path.join(output_dir, "main.tf"), "w") as f:
                f.write(main_tf)
        
        variables_tf = self._generate_variables_tf(infra_analysis)
        if variables_tf:
            generated_files["variables.tf"] = variables_tf
            with open(os.path.join(output_dir, "variables.tf"), "w") as f:
                f.write(variables_tf)
        
        outputs_tf = self._generate_outputs_tf(infra_analysis)
        if outputs_tf:
            generated_files["outputs.tf"] = outputs_tf
            with open(os.path.join(output_dir, "outputs.tf"), "w") as f:
                f.write(outputs_tf)
        
        providers_tf = self._generate_providers_tf(infra_analysis)
        if providers_tf:
            generated_files["providers.tf"] = providers_tf
            with open(os.path.join(output_dir, "providers.tf"), "w") as f:
                f.write(providers_tf)
        
        # Gerar arquivos de ambiente
        for env in infra_analysis.get("environments", []):
            env_dir = os.path.join(output_dir, env)
            os.makedirs(env_dir, exist_ok=True)
            
            terraform_tfvars = self._generate_terraform_tfvars(infra_analysis, env)
            if terraform_tfvars:
                file_path = os.path.join(env, "terraform.tfvars")
                generated_files[file_path] = terraform_tfvars
                with open(os.path.join(output_dir, file_path), "w") as f:
                    f.write(terraform_tfvars)
            
            backend_tf = self._generate_backend_tf(infra_analysis, env)
            if backend_tf:
                file_path = os.path.join(env, "backend.tf")
                generated_files[file_path] = backend_tf
                with open(os.path.join(output_dir, file_path), "w") as f:
                    f.write(backend_tf)
        
        # Gerar arquivos de módulos
        if infra_analysis.get("modules"):
            modules_dir = os.path.join(output_dir, "modules")
            os.makedirs(modules_dir, exist_ok=True)
            
            for module in infra_analysis.get("modules", []):
                module_dir = os.path.join(modules_dir, module)
                os.makedirs(module_dir, exist_ok=True)
                
                module_files = self._generate_module(infra_analysis, module)
                for file_name, content in module_files.items():
                    file_path = os.path.join("modules", module, file_name)
                    generated_files[file_path] = content
                    with open(os.path.join(output_dir, file_path), "w") as f:
                        f.write(content)
        
        return generated_files
    
    def _generate_main_tf(self, infra_analysis: Dict[str, Any]) -> str:
        """
        Gera o arquivo main.tf.
        
        Args:
            infra_analysis: Resultado da análise de infraestrutura.
            
        Returns:
            Conteúdo do arquivo main.tf.
        """
        # Verificar se há template disponível
        if os.path.exists(os.path.join(self.template_dir, "main.tf.j2")):
            template = self.jinja_env.get_template("main.tf.j2")
            return template.render(infra=infra_analysis)
        
        # Gerar com base na análise
        resources = infra_analysis.get("resources", {})
        providers = infra_analysis.get("providers", {})
        modules = infra_analysis.get("modules", [])
        
        # Usar LLM para gerar o conteúdo
        prompt = f"""
        Gere um arquivo main.tf do Terraform com base na seguinte análise de infraestrutura:
        
        Recursos: {resources}
        Provedores: {providers}
        Módulos: {modules}
        
        O arquivo deve incluir:
        1. Recursos identificados na análise
        2. Referências a módulos, se houver
        3. Configurações adequadas para cada recurso
        4. Variáveis para valores configuráveis
        
        Formate o código de acordo com as melhores práticas do Terraform.
        Não inclua comentários explicativos, apenas o código Terraform.
        """
        
        main_tf = self.llm_config.generate_text(prompt)
        if not main_tf:
            # Fallback: gerar conteúdo básico
            main_tf = self._generate_basic_main_tf(infra_analysis)
        
        return main_tf
    
    def _generate_basic_main_tf(self, infra_analysis: Dict[str, Any]) -> str:
        """
        Gera um arquivo main.tf básico.
        
        Args:
            infra_analysis: Resultado da análise de infraestrutura.
            
        Returns:
            Conteúdo básico do arquivo main.tf.
        """
        content = "# Arquivo main.tf gerado automaticamente\n\n"
        
        # Adicionar módulos
        for module in infra_analysis.get("modules", []):
            content += f"""
module "{module}" {{
  source = "./modules/{module}"
  
  # Variáveis do módulo
  # var1 = var.var1
  # var2 = var.var2
}}
"""
        
        # Adicionar recursos
        for resource_type, resources in infra_analysis.get("resources", {}).items():
            if resource_type.startswith("aws_") or resource_type.startswith("azurerm_") or resource_type.startswith("google_"):
                for resource_name in resources:
                    content += f"""
resource "{resource_type}" "{resource_name}" {{
  # Configurações do recurso
  # name = "{resource_name}"
  # ...
}}
"""
        
        return content
    
    def _generate_variables_tf(self, infra_analysis: Dict[str, Any]) -> str:
        """
        Gera o arquivo variables.tf.
        
        Args:
            infra_analysis: Resultado da análise de infraestrutura.
            
        Returns:
            Conteúdo do arquivo variables.tf.
        """
        # Verificar se há template disponível
        if os.path.exists(os.path.join(self.template_dir, "variables.tf.j2")):
            template = self.jinja_env.get_template("variables.tf.j2")
            return template.render(infra=infra_analysis)
        
        # Gerar com base na análise
        variables = infra_analysis.get("variables", {})
        
        # Usar LLM para gerar o conteúdo
        prompt = f"""
        Gere um arquivo variables.tf do Terraform com base na seguinte análise de infraestrutura:
        
        Variáveis: {variables}
        
        O arquivo deve incluir:
        1. Declarações de variáveis identificadas na análise
        2. Tipos apropriados para cada variável
        3. Descrições claras para cada variável
        4. Valores padrão quando apropriado
        
        Formate o código de acordo com as melhores práticas do Terraform.
        Não inclua comentários explicativos, apenas o código Terraform.
        """
        
        variables_tf = self.llm_config.generate_text(prompt)
        if not variables_tf:
            # Fallback: gerar conteúdo básico
            variables_tf = self._generate_basic_variables_tf(infra_analysis)
        
        return variables_tf
    
    def _generate_basic_variables_tf(self, infra_analysis: Dict[str, Any]) -> str:
        """
        Gera um arquivo variables.tf básico.
        
        Args:
            infra_analysis: Resultado da análise de infraestrutura.
            
        Returns:
            Conteúdo básico do arquivo variables.tf.
        """
        content = "# Arquivo variables.tf gerado automaticamente\n\n"
        
        # Adicionar variáveis comuns
        content += """
variable "environment" {
  description = "Ambiente de implantação (development, staging, production)"
  type        = string
}

variable "region" {
  description = "Região de implantação"
  type        = string
  default     = "us-east-1"
}
"""
        
        # Adicionar variáveis da análise
        for var_name in infra_analysis.get("variables", {}).keys():
            content += f"""
variable "{var_name}" {{
  description = "Descrição da variável {var_name}"
  type        = string
  # default     = ""
}}
"""
        
        return content
    
    def _generate_outputs_tf(self, infra_analysis: Dict[str, Any]) -> str:
        """
        Gera o arquivo outputs.tf.
        
        Args:
            infra_analysis: Resultado da análise de infraestrutura.
            
        Returns:
            Conteúdo do arquivo outputs.tf.
        """
        # Verificar se há template disponível
        if os.path.exists(os.path.join(self.template_dir, "outputs.tf.j2")):
            template = self.jinja_env.get_template("outputs.tf.j2")
            return template.render(infra=infra_analysis)
        
        # Gerar com base na análise
        resources = infra_analysis.get("resources", {})
        
        # Usar LLM para gerar o conteúdo
        prompt = f"""
        Gere um arquivo outputs.tf do Terraform com base na seguinte análise de infraestrutura:
        
        Recursos: {resources}
        
        O arquivo deve incluir:
        1. Outputs para recursos importantes identificados na análise
        2. Descrições claras para cada output
        
        Formate o código de acordo com as melhores práticas do Terraform.
        Não inclua comentários explicativos, apenas o código Terraform.
        """
        
        outputs_tf = self.llm_config.generate_text(prompt)
        if not outputs_tf:
            # Fallback: gerar conteúdo básico
            outputs_tf = self._generate_basic_outputs_tf(infra_analysis)
        
        return outputs_tf
    
    def _generate_basic_outputs_tf(self, infra_analysis: Dict[str, Any]) -> str:
        """
        Gera um arquivo outputs.tf básico.
        
        Args:
            infra_analysis: Resultado da análise de infraestrutura.
            
        Returns:
            Conteúdo básico do arquivo outputs.tf.
        """
        content = "# Arquivo outputs.tf gerado automaticamente\n\n"
        
        # Adicionar outputs para recursos comuns
        for resource_type, resources in infra_analysis.get("resources", {}).items():
            if resource_type == "aws_instance" or resource_type == "azurerm_virtual_machine" or resource_type == "google_compute_instance":
                for resource_name in resources:
                    content += f"""
output "{resource_name}_id" {{
  description = "ID da instância {resource_name}"
  value       = {resource_type}.{resource_name}.id
}}
"""
            elif resource_type == "aws_db_instance" or resource_type == "azurerm_mysql_server" or resource_type == "google_sql_database_instance":
                for resource_name in resources:
                    content += f"""
output "{resource_name}_endpoint" {{
  description = "Endpoint do banco de dados {resource_name}"
  value       = {resource_type}.{resource_name}.endpoint
}}
"""
        
        return content
    
    def _generate_providers_tf(self, infra_analysis: Dict[str, Any]) -> str:
        """
        Gera o arquivo providers.tf.
        
        Args:
            infra_analysis: Resultado da análise de infraestrutura.
            
        Returns:
            Conteúdo do arquivo providers.tf.
        """
        # Verificar se há template disponível
        if os.path.exists(os.path.join(self.template_dir, "providers.tf.j2")):
            template = self.jinja_env.get_template("providers.tf.j2")
            return template.render(infra=infra_analysis)
        
        # Gerar com base na análise
        providers = infra_analysis.get("providers", {})
        
        # Usar LLM para gerar o conteúdo
        prompt = f"""
        Gere um arquivo providers.tf do Terraform com base na seguinte análise de infraestrutura:
        
        Provedores: {providers}
        
        O arquivo deve incluir:
        1. Configurações para cada provedor identificado na análise
        2. Versões recomendadas para cada provedor
        3. Configurações de autenticação usando variáveis
        
        Formate o código de acordo com as melhores práticas do Terraform.
        Não inclua comentários explicativos, apenas o código Terraform.
        """
        
        providers_tf = self.llm_config.generate_text(prompt)
        if not providers_tf:
            # Fallback: gerar conteúdo básico
            providers_tf = self._generate_basic_providers_tf(infra_analysis)
        
        return providers_tf
    
    def _generate_basic_providers_tf(self, infra_analysis: Dict[str, Any]) -> str:
        """
        Gera um arquivo providers.tf básico.
        
        Args:
            infra_analysis: Resultado da análise de infraestrutura.
            
        Returns:
            Conteúdo básico do arquivo providers.tf.
        """
        content = "# Arquivo providers.tf gerado automaticamente\n\n"
        
        # Configuração do Terraform
        content += """
terraform {
  required_version = ">= 1.0.0"
  
  required_providers {
"""
        
        # Adicionar provedores
        for provider_name in infra_analysis.get("providers", {}).keys():
            if provider_name == "aws":
                content += """    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
"""
            elif provider_name == "azurerm":
                content += """    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
"""
            elif provider_name == "google":
                content += """    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
"""
        
        content += """  }
}
"""
        
        # Configuração de provedores
        for provider_name in infra_analysis.get("providers", {}).keys():
            if provider_name == "aws":
                content += """
provider "aws" {
  region = var.region
  
  # Configurações adicionais
  # access_key = var.aws_access_key
  # secret_key = var.aws_secret_key
}
"""
            elif provider_name == "azurerm":
                content += """
provider "azurerm" {
  features {}
  
  # Configurações adicionais
  # subscription_id = var.azure_subscription_id
  # tenant_id       = var.azure_tenant_id
  # client_id       = var.azure_client_id
  # client_secret   = var.azure_client_secret
}
"""
            elif provider_name == "google":
                content += """
provider "google" {
  project = var.project_id
  region  = var.region
  
  # Configurações adicionais
  # credentials = file(var.gcp_credentials_file)
}
"""
        
        return content
    
    def _generate_terraform_tfvars(self, infra_analysis: Dict[str, Any], environment: str) -> str:
        """
        Gera o arquivo terraform.tfvars para um ambiente específico.
        
        Args:
            infra_analysis: Resultado da análise de infraestrutura.
            environment: Ambiente (development, staging, production).
            
        Returns:
            Conteúdo do arquivo terraform.tfvars.
        """
        # Verificar se há template disponível
        template_name = f"{environment}.tfvars.j2"
        if os.path.exists(os.path.join(self.template_dir, template_name)):
            template = self.jinja_env.get_template(template_name)
            return template.render(infra=infra_analysis)
        
        # Gerar com base na análise
        variables = infra_analysis.get("variables", {})
        
        # Usar LLM para gerar o conteúdo
        prompt = f"""
        Gere um arquivo terraform.tfvars do Terraform para o ambiente {environment} com base na seguinte análise de infraestrutura:
        
        Variáveis: {variables}
        
        O arquivo deve incluir:
        1. Valores para as variáveis identificadas na análise
        2. Valores específicos para o ambiente {environment}
        
        Formate o código de acordo com as melhores práticas do Terraform.
        Não inclua comentários explicativos, apenas o código Terraform.
        """
        
        terraform_tfvars = self.llm_config.generate_text(prompt)
        if not terraform_tfvars:
            # Fallback: gerar conteúdo básico
            terraform_tfvars = self._generate_basic_terraform_tfvars(infra_analysis, environment)
        
        return terraform_tfvars
    
    def _generate_basic_terraform_tfvars(self, infra_analysis: Dict[str, Any], environment: str) -> str:
        """
        Gera um arquivo terraform.tfvars básico para um ambiente específico.
        
        Args:
            infra_analysis: Resultado da análise de infraestrutura.
            environment: Ambiente (development, staging, production).
            
        Returns:
            Conteúdo básico do arquivo terraform.tfvars.
        """
        content = f"# Arquivo terraform.tfvars para ambiente {environment}\n\n"
        
        # Adicionar variáveis comuns
        content += f"""
environment = "{environment}"
region      = "us-east-1"
"""
        
        # Adicionar variáveis da análise
        for var_name in infra_analysis.get("variables", {}).keys():
            content += f"""
{var_name} = "valor_para_{var_name}_{environment}"
"""
        
        return content
    
    def _generate_backend_tf(self, infra_analysis: Dict[str, Any], environment: str) -> str:
        """
        Gera o arquivo backend.tf para um ambiente específico.
        
        Args:
            infra_analysis: Resultado da análise de infraestrutura.
            environment: Ambiente (development, staging, production).
            
        Returns:
            Conteúdo do arquivo backend.tf.
        """
        # Verificar se há template disponível
        template_name = "backend.tf.j2"
        if os.path.exists(os.path.join(self.template_dir, template_name)):
            template = self.jinja_env.get_template(template_name)
            return template.render(infra=infra_analysis, environment=environment)
        
        # Gerar com base na análise
        providers = infra_analysis.get("providers", {})
        
        # Determinar o tipo de backend com base nos provedores
        backend_type = "local"
        if "aws" in providers:
            backend_type = "s3"
        elif "azurerm" in providers:
            backend_type = "azurerm"
        elif "google" in providers:
            backend_type = "gcs"
        
        # Gerar conteúdo do backend
        content = f"# Arquivo backend.tf para ambiente {environment}\n\n"
        content += "terraform {\n  backend \""
        
        if backend_type == "s3":
            content += f"""s3" {{
    bucket         = "terraform-state-{environment}"
    key            = "terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }}
}}
"""
        elif backend_type == "azurerm":
            content += f"""azurerm" {{
    resource_group_name  = "terraform-state-rg"
    storage_account_name = "terraformstate{environment}"
    container_name       = "tfstate"
    key                  = "terraform.tfstate"
  }}
}}
"""
        elif backend_type == "gcs":
            content += f"""gcs" {{
    bucket = "terraform-state-{environment}"
    prefix = "terraform/state"
  }}
}}
"""
        else:
            content += f"""local" {{
    path = "terraform.tfstate"
  }}
}}
"""
        
        return content
    
    def _generate_module(self, infra_analysis: Dict[str, Any], module_name: str) -> Dict[str, str]:
        """
        Gera arquivos para um módulo específico.
        
        Args:
            infra_analysis: Resultado da análise de infraestrutura.
            module_name: Nome do módulo.
            
        Returns:
            Dicionário com nomes de arquivos e conteúdos gerados.
        """
        module_files = {}
        
        # Gerar arquivos principais do módulo
        module_files["main.tf"] = self._generate_module_main_tf(infra_analysis, module_name)
        module_files["variables.tf"] = self._generate_module_variables_tf(infra_analysis, module_name)
        module_files["outputs.tf"] = self._generate_module_outputs_tf(infra_analysis, module_name)
        
        return module_files
    
    def _generate_module_main_tf(self, infra_analysis: Dict[str, Any], module_name: str) -> str:
        """
        Gera o arquivo main.tf para um módulo específico.
        
        Args:
            infra_analysis: Resultado da análise de infraestrutura.
            module_name: Nome do módulo.
            
        Returns:
            Conteúdo do arquivo main.tf do módulo.
        """
        # Verificar se há template disponível
        template_name = f"modules/{module_name}/main.tf.j2"
        if os.path.exists(os.path.join(self.template_dir, template_name)):
            template = self.jinja_env.get_template(template_name)
            return template.render(infra=infra_analysis)
        
        # Usar LLM para gerar o conteúdo
        prompt = f"""
        Gere um arquivo main.tf do Terraform para o módulo '{module_name}' com base na seguinte análise de infraestrutura:
        
        Recursos: {infra_analysis.get("resources", {})}
        Provedores: {infra_analysis.get("providers", {})}
        
        O arquivo deve incluir:
        1. Recursos relacionados ao módulo '{module_name}'
        2. Configurações adequadas para cada recurso
        3. Referências a variáveis do módulo
        
        Formate o código de acordo com as melhores práticas do Terraform.
        Não inclua comentários explicativos, apenas o código Terraform.
        """
        
        main_tf = self.llm_config.generate_text(prompt)
        if not main_tf:
            # Fallback: gerar conteúdo básico
            main_tf = f"# Arquivo main.tf para o módulo {module_name}\n\n"
            main_tf += f"""
# Exemplo de recurso para o módulo {module_name}
resource "aws_example" "example" {{
  name = var.name
  # Outras configurações
}}
"""
        
        return main_tf
    
    def _generate_module_variables_tf(self, infra_analysis: Dict[str, Any], module_name: str) -> str:
        """
        Gera o arquivo variables.tf para um módulo específico.
        
        Args:
            infra_analysis: Resultado da análise de infraestrutura.
            module_name: Nome do módulo.
            
        Returns:
            Conteúdo do arquivo variables.tf do módulo.
        """
        # Verificar se há template disponível
        template_name = f"modules/{module_name}/variables.tf.j2"
        if os.path.exists(os.path.join(self.template_dir, template_name)):
            template = self.jinja_env.get_template(template_name)
            return template.render(infra=infra_analysis)
        
        # Usar LLM para gerar o conteúdo
        prompt = f"""
        Gere um arquivo variables.tf do Terraform para o módulo '{module_name}' com base na seguinte análise de infraestrutura:
        
        Variáveis: {infra_analysis.get("variables", {})}
        
        O arquivo deve incluir:
        1. Declarações de variáveis necessárias para o módulo '{module_name}'
        2. Tipos apropriados para cada variável
        3. Descrições claras para cada variável
        4. Valores padrão quando apropriado
        
        Formate o código de acordo com as melhores práticas do Terraform.
        Não inclua comentários explicativos, apenas o código Terraform.
        """
        
        variables_tf = self.llm_config.generate_text(prompt)
        if not variables_tf:
            # Fallback: gerar conteúdo básico
            variables_tf = f"# Arquivo variables.tf para o módulo {module_name}\n\n"
            variables_tf += """
variable "name" {
  description = "Nome do recurso"
  type        = string
}

variable "environment" {
  description = "Ambiente de implantação"
  type        = string
}
"""
        
        return variables_tf
    
    def _generate_module_outputs_tf(self, infra_analysis: Dict[str, Any], module_name: str) -> str:
        """
        Gera o arquivo outputs.tf para um módulo específico.
        
        Args:
            infra_analysis: Resultado da análise de infraestrutura.
            module_name: Nome do módulo.
            
        Returns:
            Conteúdo do arquivo outputs.tf do módulo.
        """
        # Verificar se há template disponível
        template_name = f"modules/{module_name}/outputs.tf.j2"
        if os.path.exists(os.path.join(self.template_dir, template_name)):
            template = self.jinja_env.get_template(template_name)
            return template.render(infra=infra_analysis)
        
        # Usar LLM para gerar o conteúdo
        prompt = f"""
        Gere um arquivo outputs.tf do Terraform para o módulo '{module_name}' com base na seguinte análise de infraestrutura:
        
        Recursos: {infra_analysis.get("resources", {})}
        
        O arquivo deve incluir:
        1. Outputs para recursos importantes do módulo '{module_name}'
        2. Descrições claras para cada output
        
        Formate o código de acordo com as melhores práticas do Terraform.
        Não inclua comentários explicativos, apenas o código Terraform.
        """
        
        outputs_tf = self.llm_config.generate_text(prompt)
        if not outputs_tf:
            # Fallback: gerar conteúdo básico
            outputs_tf = f"# Arquivo outputs.tf para o módulo {module_name}\n\n"
            outputs_tf += """
output "id" {
  description = "ID do recurso criado"
  value       = aws_example.example.id
}

output "name" {
  description = "Nome do recurso criado"
  value       = aws_example.example.name
}
"""
        
        return outputs_tf
