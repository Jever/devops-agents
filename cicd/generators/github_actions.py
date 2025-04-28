"""
Gerador de pipeline para GitHub Actions.
"""
import os
import logging
from typing import Dict, Any, List, Optional
import yaml
import jinja2

from config import Config, logger

class GitHubActionsGenerator:
    """
    Classe para gerar pipelines CI/CD para GitHub Actions.
    """
    
    def __init__(self):
        """
        Inicializa o gerador de pipeline para GitHub Actions.
        """
        self.logger = logging.getLogger("cicd_agent.github_actions_generator")
        self.template_dir = os.path.join(Config.TEMPLATE_DIR, "github_actions")
        
        # Configurar ambiente Jinja2
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.template_dir),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True
        )
    
    def generate_pipeline(self, repo_analysis: Dict[str, Any]) -> Dict[str, str]:
        """
        Gera um pipeline CI/CD para GitHub Actions com base na análise do repositório.
        
        Args:
            repo_analysis: Resultado da análise do repositório.
            
        Returns:
            Dicionário com nomes de arquivos e conteúdos gerados.
        """
        self.logger.info("Gerando pipeline para GitHub Actions")
        
        # Determinar quais workflows gerar com base na análise
        workflows = {}
        
        # Workflow principal (CI)
        ci_workflow = self._generate_ci_workflow(repo_analysis)
        if ci_workflow:
            workflows["ci.yml"] = ci_workflow
        
        # Workflow de deploy (CD)
        if self._should_generate_cd_workflow(repo_analysis):
            cd_workflow = self._generate_cd_workflow(repo_analysis)
            if cd_workflow:
                workflows["cd.yml"] = cd_workflow
        
        # Workflow de análise de código
        if self._should_generate_code_analysis_workflow(repo_analysis):
            code_analysis_workflow = self._generate_code_analysis_workflow(repo_analysis)
            if code_analysis_workflow:
                workflows["code-analysis.yml"] = code_analysis_workflow
        
        # Workflow de release
        if self._should_generate_release_workflow(repo_analysis):
            release_workflow = self._generate_release_workflow(repo_analysis)
            if release_workflow:
                workflows["release.yml"] = release_workflow
        
        self.logger.info(f"Gerados {len(workflows)} workflows para GitHub Actions")
        return workflows
    
    def _generate_ci_workflow(self, repo_analysis: Dict[str, Any]) -> Optional[str]:
        """Gera um workflow de CI para GitHub Actions."""
        try:
            # Determinar a linguagem principal
            languages = repo_analysis.get("languages", {})
            if not languages:
                self.logger.warning("Não foi possível determinar a linguagem principal")
                return None
            
            primary_language = next(iter(languages))
            
            # Selecionar o template apropriado com base na linguagem
            template_name = self._get_template_for_language(primary_language, "ci")
            if not template_name:
                self.logger.warning(f"Não há template de CI disponível para {primary_language}")
                return None
            
            # Preparar dados para o template
            template_data = self._prepare_template_data(repo_analysis)
            
            # Renderizar o template
            template = self.jinja_env.get_template(template_name)
            return template.render(**template_data)
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar workflow de CI: {str(e)}")
            return None
    
    def _generate_cd_workflow(self, repo_analysis: Dict[str, Any]) -> Optional[str]:
        """
        Gera um workflow de CD para GitHub Actions.
        
        Args:
            repo_analysis: Resultado da análise do repositório.
            
        Returns:
            Conteúdo do workflow gerado ou None se não for possível gerar.
        """
        try:
            # Determinar a linguagem principal
            languages = repo_analysis.get("languages", {})
            if not languages:
                self.logger.warning("Não foi possível determinar a linguagem principal")
                return None
            
            primary_language = next(iter(languages))
            
            # Selecionar o template apropriado com base na linguagem
            template_name = self._get_template_for_language(primary_language, "cd")
            if not template_name:
                self.logger.warning(f"Não há template de CD disponível para {primary_language}")
                return None
            
            # Preparar dados para o template
            template_data = self._prepare_template_data(repo_analysis)
            
            # Adicionar dados específicos para CD
            template_data["deployment_environments"] = self._determine_deployment_environments(repo_analysis)
            
            # Renderizar o template
            template = self.jinja_env.get_template(template_name)
            return template.render(**template_data)
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar workflow de CD: {str(e)}")
            return None
    
    def _generate_code_analysis_workflow(self, repo_analysis: Dict[str, Any]) -> Optional[str]:
        """
        Gera um workflow de análise de código para GitHub Actions.
        
        Args:
            repo_analysis: Resultado da análise do repositório.
            
        Returns:
            Conteúdo do workflow gerado ou None se não for possível gerar.
        """
        try:
            # Determinar a linguagem principal
            languages = repo_analysis.get("languages", {})
            if not languages:
                self.logger.warning("Não foi possível determinar a linguagem principal")
                return None
            
            primary_language = next(iter(languages))
            
            # Selecionar o template apropriado com base na linguagem
            template_name = self._get_template_for_language(primary_language, "code-analysis")
            if not template_name:
                self.logger.warning(f"Não há template de análise de código disponível para {primary_language}")
                return None
            
            # Preparar dados para o template
            template_data = self._prepare_template_data(repo_analysis)
            
            # Adicionar dados específicos para análise de código
            tech_data = repo_analysis.get("tech_data", {})
            template_data["linters"] = tech_data.get("linters_formatters", [])
            
            # Renderizar o template
            template = self.jinja_env.get_template(template_name)
            return template.render(**template_data)
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar workflow de análise de código: {str(e)}")
            return None
    
    def _generate_release_workflow(self, repo_analysis: Dict[str, Any]) -> Optional[str]:
        """
        Gera um workflow de release para GitHub Actions.
        
        Args:
            repo_analysis: Resultado da análise do repositório.
            
        Returns:
            Conteúdo do workflow gerado ou None se não for possível gerar.
        """
        try:
            # Determinar a linguagem principal
            languages = repo_analysis.get("languages", {})
            if not languages:
                self.logger.warning("Não foi possível determinar a linguagem principal")
                return None
            
            primary_language = next(iter(languages))
            
            # Selecionar o template apropriado com base na linguagem
            template_name = self._get_template_for_language(primary_language, "release")
            if not template_name:
                self.logger.warning(f"Não há template de release disponível para {primary_language}")
                return None
            
            # Preparar dados para o template
            template_data = self._prepare_template_data(repo_analysis)
            
            # Renderizar o template
            template = self.jinja_env.get_template(template_name)
            return template.render(**template_data)
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar workflow de release: {str(e)}")
            return None
    
    def _get_template_for_language(self, language: str, workflow_type: str) -> Optional[str]:
        """
        Retorna o nome do template apropriado para a linguagem e tipo de workflow.
        
        Args:
            language: Linguagem de programação.
            workflow_type: Tipo de workflow (ci, cd, code-analysis, release).
            
        Returns:
            Nome do template ou None se não houver template disponível.
        """
        # Mapeamento de linguagens para templates
        templates = {
            "Python": {
                "ci": "python-ci.yml.j2",
                "cd": "python-cd.yml.j2",
                "code-analysis": "python-code-analysis.yml.j2",
                "release": "python-release.yml.j2"
            },
            "JavaScript": {
                "ci": "javascript-ci.yml.j2",
                "cd": "javascript-cd.yml.j2",
                "code-analysis": "javascript-code-analysis.yml.j2",
                "release": "javascript-release.yml.j2"
            },
            "TypeScript": {
                "ci": "typescript-ci.yml.j2",
                "cd": "typescript-cd.yml.j2",
                "code-analysis": "typescript-code-analysis.yml.j2",
                "release": "typescript-release.yml.j2"
            },
            "Java": {
                "ci": "java-ci.yml.j2",
                "cd": "java-cd.yml.j2",
                "code-analysis": "java-code-analysis.yml.j2",
                "release": "java-release.yml.j2"
            },
            "Go": {
                "ci": "go-ci.yml.j2",
                "cd": "go-cd.yml.j2",
                "code-analysis": "go-code-analysis.yml.j2",
                "release": "go-release.yml.j2"
            },
            "Ruby": {
                "ci": "ruby-ci.yml.j2",
                "cd": "ruby-cd.yml.j2",
                "code-analysis": "ruby-code-analysis.yml.j2",
                "release": "ruby-release.yml.j2"
            },
            "PHP": {
                "ci": "php-ci.yml.j2",
                "cd": "php-cd.yml.j2",
                "code-analysis": "php-code-analysis.yml.j2",
                "release": "php-release.yml.j2"
            },
            "C#": {
                "ci": "dotnet-ci.yml.j2",
                "cd": "dotnet-cd.yml.j2",
                "code-analysis": "dotnet-code-analysis.yml.j2",
                "release": "dotnet-release.yml.j2"
            }
        }
        
        # Verificar se há template para a linguagem
        if language in templates and workflow_type in templates[language]:
            template_path = templates[language][workflow_type]
            if os.path.exists(os.path.join(self.template_dir, template_path)):
                return template_path
        
        # Fallback para template genérico
        generic_template = f"generic-{workflow_type}.yml.j2"
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
            "repo_analysis": repo_analysis  # Incluir análise completa para acesso a todos os dados
        }
    
    def _should_generate_cd_workflow(self, repo_analysis: Dict[str, Any]) -> bool:
        """
        Determina se deve gerar um workflow de CD.
        
        Args:
            repo_analysis: Resultado da análise do repositório.
            
        Returns:
            True se deve gerar um workflow de CD, False caso contrário.
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
    
    def _should_generate_code_analysis_workflow(self, repo_analysis: Dict[str, Any]) -> bool:
        """
        Determina se deve gerar um workflow de análise de código.
        
        Args:
            repo_analysis: Resultado da análise do repositório.
            
        Returns:
            True se deve gerar um workflow de análise de código, False caso contrário.
        """
        # Verificar se há linters ou formatadores
        tech_data = repo_analysis.get("tech_data", {})
        linters_formatters = tech_data.get("linters_formatters", [])
        return bool(linters_formatters)
    
    def _should_generate_release_workflow(self, repo_analysis: Dict[str, Any]) -> bool:
        """
        Determina se deve gerar um workflow de release.
        
        Args:
            repo_analysis: Resultado da análise do repositório.
            
        Returns:
            True se deve gerar um workflow de release, False caso contrário.
        """
        # Por padrão, gerar workflow de release para a maioria dos projetos
        return True
    
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
