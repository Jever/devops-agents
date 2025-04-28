"""
Gerador de pipeline para GitLab CI.
"""
import os
import logging
from typing import Dict, Any, List, Optional
import yaml
import jinja2

from config import Config, logger

class GitLabCIGenerator:
    """
    Classe para gerar pipelines CI/CD para GitLab CI.
    """
    
    def __init__(self):
        """
        Inicializa o gerador de pipeline para GitLab CI.
        """
        self.logger = logging.getLogger("cicd_agent.gitlab_ci_generator")
        self.template_dir = os.path.join(Config.TEMPLATE_DIR, "gitlab_ci")
        
        # Configurar ambiente Jinja2
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.template_dir),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True
        )
    
    def generate_pipeline(self, repo_analysis: Dict[str, Any]) -> Dict[str, str]:
        """
        Gera um pipeline CI/CD para GitLab CI com base na análise do repositório.
        
        Args:
            repo_analysis: Resultado da análise do repositório.
            
        Returns:
            Dicionário com nomes de arquivos e conteúdos gerados.
        """
        self.logger.info("Gerando pipeline para GitLab CI")
        
        # No GitLab CI, geralmente temos apenas um arquivo .gitlab-ci.yml
        pipeline = self._generate_gitlab_ci_yml(repo_analysis)
        
        if pipeline:
            return {".gitlab-ci.yml": pipeline}
        else:
            return {}
    
    def _generate_gitlab_ci_yml(self, repo_analysis: Dict[str, Any]) -> Optional[str]:
        """
        Gera o arquivo .gitlab-ci.yml com base na análise do repositório.
        
        Args:
            repo_analysis: Resultado da análise do repositório.
            
        Returns:
            Conteúdo do arquivo .gitlab-ci.yml ou None se não for possível gerar.
        """
        try:
            # Determinar a linguagem principal
            languages = repo_analysis.get("languages", {})
            if not languages:
                self.logger.warning("Não foi possível determinar a linguagem principal")
                return None
            
            primary_language = next(iter(languages))
            
            # Selecionar o template apropriado com base na linguagem
            template_name = self._get_template_for_language(primary_language)
            if not template_name:
                self.logger.warning(f"Não há template disponível para {primary_language}")
                return None
            
            # Preparar dados para o template
            template_data = self._prepare_template_data(repo_analysis)
            
            # Renderizar o template
            template = self.jinja_env.get_template(template_name)
            return template.render(**template_data)
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar arquivo .gitlab-ci.yml: {str(e)}")
            return None
    
    def _get_template_for_language(self, language: str) -> Optional[str]:
        """
        Retorna o nome do template apropriado para a linguagem.
        
        Args:
            language: Linguagem de programação.
            
        Returns:
            Nome do template ou None se não houver template disponível.
        """
        # Mapeamento de linguagens para templates
        templates = {
            "Python": "python.yml.j2",
            "JavaScript": "javascript.yml.j2",
            "TypeScript": "typescript.yml.j2",
            "Java": "java.yml.j2",
            "Go": "go.yml.j2",
            "Ruby": "ruby.yml.j2",
            "PHP": "php.yml.j2",
            "C#": "dotnet.yml.j2"
        }
        
        # Verificar se há template para a linguagem
        if language in templates:
            template_path = templates[language]
            if os.path.exists(os.path.join(self.template_dir, template_path)):
                return template_path
        
        # Fallback para template genérico
        generic_template = "generic.yml.j2"
        if os.path.exists(os.path.join(self.template_dir, generic_template)):
            return generic_template
        
        return None
    
    def _prepare_template_data(self, repo_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepara os dados para o template.
        
        Args:
            repo_analysis: Resultado da análise do repositório.
            
        Returns:
            Dicionário com dados para o template.
        """
        languages = repo_analysis.get("languages", {})
        primary_language = next(iter(languages)) if languages else "Unknown"
        
        frameworks = repo_analysis.get("frameworks", {})
        primary_framework = frameworks.get(primary_language, "None")
        
        build_tools = repo_analysis.get("build_tools", [])
        package_managers = repo_analysis.get("package_managers", [])
        has_tests = repo_analysis.get("has_tests", False)
        has_docker = repo_analysis.get("has_docker", False)
        
        # Obter dados de tecnologia, se disponíveis
        tech_data = repo_analysis.get("tech_data", {})
        testing_frameworks = tech_data.get("testing_frameworks", {})
        containerization = tech_data.get("containerization", {})
        cloud_providers = tech_data.get("cloud_providers", {})
        databases = tech_data.get("databases", [])
        linters_formatters = tech_data.get("linters_formatters", [])
        
        # Determinar os estágios do pipeline
        stages = self._determine_pipeline_stages(repo_analysis)
        
        # Determinar as variáveis de ambiente
        variables = self._determine_environment_variables(repo_analysis)
        
        # Determinar os ambientes de deploy
        deployment_environments = self._determine_deployment_environments(repo_analysis)
        
        return {
            "primary_language": primary_language,
            "languages": languages,
            "primary_framework": primary_framework,
            "frameworks": frameworks,
            "build_tools": build_tools,
            "package_managers": package_managers,
            "has_tests": has_tests,
            "has_docker": has_docker,
            "testing_frameworks": testing_frameworks,
            "containerization": containerization,
            "cloud_providers": cloud_providers,
            "databases": databases,
            "linters_formatters": linters_formatters,
            "stages": stages,
            "variables": variables,
            "deployment_environments": deployment_environments,
            "repo_analysis": repo_analysis  # Incluir análise completa para acesso a todos os dados
        }
    
    def _determine_pipeline_stages(self, repo_analysis: Dict[str, Any]) -> List[str]:
        """
        Determina os estágios do pipeline com base na análise do repositório.
        
        Args:
            repo_analysis: Resultado da análise do repositório.
            
        Returns:
            Lista de estágios do pipeline.
        """
        stages = ["build", "test"]
        
        # Adicionar estágio de lint se houver linters
        tech_data = repo_analysis.get("tech_data", {})
        linters_formatters = tech_data.get("linters_formatters", [])
        if linters_formatters:
            stages.insert(0, "lint")
        
        # Adicionar estágio de deploy se necessário
        if self._should_have_deploy_stage(repo_analysis):
            stages.append("deploy")
        
        # Adicionar estágio de release se necessário
        if self._should_have_release_stage(repo_analysis):
            stages.append("release")
        
        return stages
    
    def _should_have_deploy_stage(self, repo_analysis: Dict[str, Any]) -> bool:
        """
        Determina se o pipeline deve ter um estágio de deploy.
        
        Args:
            repo_analysis: Resultado da análise do repositório.
            
        Returns:
            True se o pipeline deve ter um estágio de deploy, False caso contrário.
        """
        # Verificar se há Docker
        if repo_analysis.get("has_docker", False):
            return True
        
        # Verificar se há configurações de deploy
        tech_data = repo_analysis.get("tech_data", {})
        deployment_tools = tech_data.get("deployment_tools", [])
        if deployment_tools:
            return True
        
        # Verificar se há provedores de nuvem
        cloud_providers = tech_data.get("cloud_providers", {})
        if any(cloud_providers.values()):
            return True
        
        return False
    
    def _should_have_release_stage(self, repo_analysis: Dict[str, Any]) -> bool:
        """
        Determina se o pipeline deve ter um estágio de release.
        
        Args:
            repo_analysis: Resultado da análise do repositório.
            
        Returns:
            True se o pipeline deve ter um estágio de release, False caso contrário.
        """
        # Por padrão, incluir estágio de release para a maioria dos projetos
        return True
    
    def _determine_environment_variables(self, repo_analysis: Dict[str, Any]) -> Dict[str, str]:
        """
        Determina as variáveis de ambiente para o pipeline.
        
        Args:
            repo_analysis: Resultado da análise do repositório.
            
        Returns:
            Dicionário com variáveis de ambiente.
        """
        variables = {}
        
        # Variáveis comuns
        variables["CI_DEBUG_TRACE"] = "false"
        
        # Variáveis específicas por linguagem
        languages = repo_analysis.get("languages", {})
        if not languages:
            return variables
        
        primary_language = next(iter(languages))
        
        if primary_language == "Python":
            variables["PIP_CACHE_DIR"] = "$CI_PROJECT_DIR/.pip-cache"
            variables["PYTHONUNBUFFERED"] = "1"
        elif primary_language in ["JavaScript", "TypeScript"]:
            variables["NODE_ENV"] = "development"
        elif primary_language == "Java":
            variables["MAVEN_OPTS"] = "-Dmaven.repo.local=$CI_PROJECT_DIR/.m2/repository"
        elif primary_language == "Go":
            variables["GOPATH"] = "$CI_PROJECT_DIR/.go"
        
        return variables
    
    def _determine_deployment_environments(self, repo_analysis: Dict[str, Any]) -> List[str]:
        """
        Determina os ambientes de deploy com base na análise do repositório.
        
        Args:
            repo_analysis: Resultado da análise do repositório.
            
        Returns:
            Lista de ambientes de deploy.
        """
        # Por padrão, usar staging e production
        environments = ["staging", "production"]
        
        # Verificar se há configurações específicas de ambiente
        # (Isso poderia ser expandido com base em mais análises)
        
        return environments
