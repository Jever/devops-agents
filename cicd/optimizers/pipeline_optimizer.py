"""
Otimizador de pipeline para melhorar performance e eficiência.
"""
import os
import logging
from typing import Dict, Any, List, Optional
import yaml
import json
import re

from config import Config, logger

class PipelineOptimizer:
    """
    Classe para otimizar pipelines CI/CD existentes.
    """
    
    def __init__(self):
        """
        Inicializa o otimizador de pipeline.
        """
        self.logger = logging.getLogger("cicd_agent.pipeline_optimizer")
    
    def optimize_pipeline(self, pipeline_content: str, pipeline_type: str, repo_analysis: Dict[str, Any]) -> Optional[str]:
        """
        Otimiza um pipeline CI/CD existente.
        
        Args:
            pipeline_content: Conteúdo do arquivo de pipeline.
            pipeline_type: Tipo de pipeline (github_actions, gitlab_ci, jenkins, azure_devops).
            repo_analysis: Resultado da análise do repositório.
            
        Returns:
            Conteúdo otimizado do pipeline ou None se não for possível otimizar.
        """
        self.logger.info(f"Otimizando pipeline do tipo {pipeline_type}")
        
        try:
            # Selecionar o método de otimização apropriado com base no tipo de pipeline
            if pipeline_type == "github_actions":
                return self._optimize_github_actions(pipeline_content, repo_analysis)
            elif pipeline_type == "gitlab_ci":
                return self._optimize_gitlab_ci(pipeline_content, repo_analysis)
            elif pipeline_type == "jenkins":
                return self._optimize_jenkins(pipeline_content, repo_analysis)
            elif pipeline_type == "azure_devops":
                return self._optimize_azure_devops(pipeline_content, repo_analysis)
            else:
                self.logger.warning(f"Tipo de pipeline não suportado: {pipeline_type}")
                return None
                
        except Exception as e:
            self.logger.error(f"Erro ao otimizar pipeline: {str(e)}")
            return None
    
    def _optimize_github_actions(self, pipeline_content: str, repo_analysis: Dict[str, Any]) -> Optional[str]:
        """
        Otimiza um pipeline GitHub Actions.
        
        Args:
            pipeline_content: Conteúdo do arquivo de pipeline.
            repo_analysis: Resultado da análise do repositório.
            
        Returns:
            Conteúdo otimizado do pipeline ou None se não for possível otimizar.
        """
        try:
            # Carregar o pipeline como YAML
            pipeline = yaml.safe_load(pipeline_content)
            if not pipeline:
                return None
            
            # Aplicar otimizações
            pipeline = self._add_caching(pipeline, "github_actions", repo_analysis)
            pipeline = self._optimize_job_dependencies(pipeline, "github_actions")
            pipeline = self._optimize_triggers(pipeline, "github_actions", repo_analysis)
            pipeline = self._add_parallel_execution(pipeline, "github_actions")
            
            # Converter de volta para YAML
            return yaml.dump(pipeline, sort_keys=False)
            
        except Exception as e:
            self.logger.error(f"Erro ao otimizar pipeline GitHub Actions: {str(e)}")
            return None
    
    def _optimize_gitlab_ci(self, pipeline_content: str, repo_analysis: Dict[str, Any]) -> Optional[str]:
        """
        Otimiza um pipeline GitLab CI.
        
        Args:
            pipeline_content: Conteúdo do arquivo de pipeline.
            repo_analysis: Resultado da análise do repositório.
            
        Returns:
            Conteúdo otimizado do pipeline ou None se não for possível otimizar.
        """
        try:
            # Carregar o pipeline como YAML
            pipeline = yaml.safe_load(pipeline_content)
            if not pipeline:
                return None
            
            # Aplicar otimizações
            pipeline = self._add_caching(pipeline, "gitlab_ci", repo_analysis)
            pipeline = self._optimize_job_dependencies(pipeline, "gitlab_ci")
            pipeline = self._optimize_triggers(pipeline, "gitlab_ci", repo_analysis)
            pipeline = self._add_parallel_execution(pipeline, "gitlab_ci")
            
            # Converter de volta para YAML
            return yaml.dump(pipeline, sort_keys=False)
            
        except Exception as e:
            self.logger.error(f"Erro ao otimizar pipeline GitLab CI: {str(e)}")
            return None
    
    def _optimize_jenkins(self, pipeline_content: str, repo_analysis: Dict[str, Any]) -> Optional[str]:
        """
        Otimiza um pipeline Jenkins.
        
        Args:
            pipeline_content: Conteúdo do arquivo de pipeline.
            repo_analysis: Resultado da análise do repositório.
            
        Returns:
            Conteúdo otimizado do pipeline ou None se não for possível otimizar.
        """
        try:
            # Para Jenkins, usamos expressões regulares para modificar o Jenkinsfile
            
            # Adicionar caching
            pipeline_content = self._add_jenkins_caching(pipeline_content, repo_analysis)
            
            # Otimizar paralelismo
            pipeline_content = self._add_jenkins_parallel(pipeline_content)
            
            # Otimizar triggers
            pipeline_content = self._optimize_jenkins_triggers(pipeline_content, repo_analysis)
            
            return pipeline_content
            
        except Exception as e:
            self.logger.error(f"Erro ao otimizar pipeline Jenkins: {str(e)}")
            return None
    
    def _optimize_azure_devops(self, pipeline_content: str, repo_analysis: Dict[str, Any]) -> Optional[str]:
        """
        Otimiza um pipeline Azure DevOps.
        
        Args:
            pipeline_content: Conteúdo do arquivo de pipeline.
            repo_analysis: Resultado da análise do repositório.
            
        Returns:
            Conteúdo otimizado do pipeline ou None se não for possível otimizar.
        """
        try:
            # Carregar o pipeline como YAML
            pipeline = yaml.safe_load(pipeline_content)
            if not pipeline:
                return None
            
            # Aplicar otimizações
            pipeline = self._add_caching(pipeline, "azure_devops", repo_analysis)
            pipeline = self._optimize_job_dependencies(pipeline, "azure_devops")
            pipeline = self._optimize_triggers(pipeline, "azure_devops", repo_analysis)
            pipeline = self._add_parallel_execution(pipeline, "azure_devops")
            
            # Converter de volta para YAML
            return yaml.dump(pipeline, sort_keys=False)
            
        except Exception as e:
            self.logger.error(f"Erro ao otimizar pipeline Azure DevOps: {str(e)}")
            return None
    
    def _add_caching(self, pipeline: Dict[str, Any], pipeline_type: str, repo_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adiciona configurações de cache ao pipeline.
        
        Args:
            pipeline: Pipeline a ser otimizado.
            pipeline_type: Tipo de pipeline.
            repo_analysis: Resultado da análise do repositório.
            
        Returns:
            Pipeline otimizado.
        """
        # Determinar a linguagem principal
        languages = repo_analysis.get("languages", {})
        if not languages:
            return pipeline
        
        primary_language = next(iter(languages))
        
        # Adicionar cache com base no tipo de pipeline e linguagem
        if pipeline_type == "github_actions":
            # Verificar se já existe configuração de cache
            if "jobs" in pipeline:
                for job_name, job in pipeline["jobs"].items():
                    if "steps" in job:
                        # Verificar se já existe step de cache
                        has_cache = any("cache" in str(step).lower() for step in job["steps"])
                        if not has_cache:
                            # Adicionar step de cache apropriado para a linguagem
                            cache_step = self._get_cache_step_for_language(primary_language, "github_actions")
                            if cache_step:
                                # Inserir após o checkout
                                checkout_index = next((i for i, step in enumerate(job["steps"]) if "checkout" in str(step).lower()), 0)
                                job["steps"].insert(checkout_index + 1, cache_step)
        
        elif pipeline_type == "gitlab_ci":
            # Verificar se já existe configuração de cache
            if "cache" not in pipeline:
                # Adicionar configuração de cache apropriada para a linguagem
                cache_config = self._get_cache_config_for_language(primary_language, "gitlab_ci")
                if cache_config:
                    pipeline["cache"] = cache_config
        
        elif pipeline_type == "azure_devops":
            # Verificar se já existe configuração de cache
            if "jobs" in pipeline:
                for job in pipeline["jobs"]:
                    if "steps" in job:
                        # Verificar se já existe step de cache
                        has_cache = any("cache" in str(step).lower() for step in job["steps"])
                        if not has_cache:
                            # Adicionar step de cache apropriado para a linguagem
                            cache_step = self._get_cache_step_for_language(primary_language, "azure_devops")
                            if cache_step:
                                # Inserir no início dos steps
                                job["steps"].insert(0, cache_step)
        
        return pipeline
    
    def _get_cache_step_for_language(self, language: str, pipeline_type: str) -> Optional[Dict[str, Any]]:
        """
        Retorna um step de cache apropriado para a linguagem e tipo de pipeline.
        
        Args:
            language: Linguagem de programação.
            pipeline_type: Tipo de pipeline.
            
        Returns:
            Step de cache ou None se não houver step disponível.
        """
        if pipeline_type == "github_actions":
            if language == "Python":
                return {
                    "name": "Cache pip dependencies",
                    "uses": "actions/cache@v3",
                    "with": {
                        "path": "~/.cache/pip",
                        "key": "${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}",
                        "restore-keys": "${{ runner.os }}-pip-"
                    }
                }
            elif language in ["JavaScript", "TypeScript"]:
                return {
                    "name": "Cache node modules",
                    "uses": "actions/cache@v3",
                    "with": {
                        "path": "node_modules",
                        "key": "${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}",
                        "restore-keys": "${{ runner.os }}-node-"
                    }
                }
            elif language == "Java":
                return {
                    "name": "Cache Maven packages",
                    "uses": "actions/cache@v3",
                    "with": {
                        "path": "~/.m2",
                        "key": "${{ runner.os }}-m2-${{ hashFiles('**/pom.xml') }}",
                        "restore-keys": "${{ runner.os }}-m2"
                    }
                }
            elif language == "Go":
                return {
                    "name": "Cache Go modules",
                    "uses": "actions/cache@v3",
                    "with": {
                        "path": "~/go/pkg/mod",
                        "key": "${{ runner.os }}-go-${{ hashFiles('**/go.sum') }}",
                        "restore-keys": "${{ runner.os }}-go-"
                    }
                }
        
        elif pipeline_type == "azure_devops":
            if language == "Python":
                return {
                    "task": "Cache@2",
                    "inputs": {
                        "key": "pip | $(Agent.OS) | requirements.txt",
                        "restoreKeys": "pip | $(Agent.OS)",
                        "path": "$(PIP_CACHE_DIR)"
                    },
                    "displayName": "Cache pip dependencies"
                }
            elif language in ["JavaScript", "TypeScript"]:
                return {
                    "task": "Cache@2",
                    "inputs": {
                        "key": "npm | $(Agent.OS) | package-lock.json",
                        "restoreKeys": "npm | $(Agent.OS)",
                        "path": "$(System.DefaultWorkingDirectory)/node_modules"
                    },
                    "displayName": "Cache node modules"
                }
            elif language == "Java":
                return {
                    "task": "Cache@2",
                    "inputs": {
                        "key": "maven | $(Agent.OS) | **/pom.xml",
                        "restoreKeys": "maven | $(Agent.OS)",
                        "path": "$(MAVEN_CACHE_FOLDER)"
                    },
                    "displayName": "Cache Maven packages"
                }
        
        return None
    
    def _get_cache_config_for_language(self, language: str, pipeline_type: str) -> Optional[Dict[str, Any]]:
        """
        Retorna uma configuração de cache apropriada para a linguagem e tipo de pipeline.
        
        Args:
            language: Linguagem de programação.
            pipeline_type: Tipo de pipeline.
            
        Returns:
            Configuração de cache ou None se não houver configuração disponível.
        """
        if pipeline_type == "gitlab_ci":
            if language == "Python":
                return {
                    "key": "$CI_COMMIT_REF_SLUG",
                    "paths": [".pip-cache/"],
                    "policy": "pull-push"
                }
            elif language in ["JavaScript", "TypeScript"]:
                return {
                    "key": "$CI_COMMIT_REF_SLUG",
                    "paths": ["node_modules/"],
                    "policy": "pull-push"
                }
            elif language == "Java":
                return {
                    "key": "$CI_COMMIT_REF_SLUG",
                    "paths": [".m2/repository/"],
                    "policy": "pull-push"
                }
            elif language == "Go":
                return {
                    "key": "$CI_COMMIT_REF_SLUG",
                    "paths": [".go/"],
                    "policy": "pull-push"
                }
        
        return None
    
    def _optimize_job_dependencies(self, pipeline: Dict[str, Any], pipeline_type: str) -> Dict[str, Any]:
        """
        Otimiza as dependências entre jobs no pipeline.
        
        Args:
            pipeline: Pipeline a ser otimizado.
            pipeline_type: Tipo de pipeline.
            
        Returns:
            Pipeline otimizado.
        """
        # Implementação específica para cada tipo de pipeline
        if pipeline_type == "github_actions":
            if "jobs" in pipeline:
                # Identificar jobs que podem ser executados em paralelo
                # e ajustar as dependências needs
                pass
        
        elif pipeline_type == "gitlab_ci":
            # Otimizar dependências needs
            pass
        
        elif pipeline_type == "azure_devops":
            if "jobs" in pipeline:
                # Otimizar dependências dependsOn
                pass
        
        return pipeline
    
    def _optimize_triggers(self, pipeline: Dict[str, Any], pipeline_type: str, repo_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Otimiza os triggers do pipeline.
        
        Args:
            pipeline: Pipeline a ser otimizado.
            pipeline_type: Tipo de pipeline.
            repo_analysis: Resultado da análise do repositório.
            
        Returns:
            Pipeline otimizado.
        """
        # Implementação específica para cada tipo de pipeline
        if pipeline_type == "github_actions":
            # Otimizar triggers on
            if "on" in pipeline:
                # Se não houver path filters, adicionar
                if "push" in pipeline["on"] and isinstance(pipeline["on"]["push"], dict) and "paths" not in pipeline["on"]["push"]:
                    # Determinar paths relevantes com base na linguagem
                    languages = repo_analysis.get("languages", {})
                    if languages:
                        primary_language = next(iter(languages))
                        paths = self._get_relevant_paths_for_language(primary_language)
                        if paths:
                            pipeline["on"]["push"]["paths"] = paths
        
        elif pipeline_type == "gitlab_ci":
            # Otimizar only/except
            pass
        
        elif pipeline_type == "azure_devops":
            # Otimizar trigger/pr
            pass
        
        return pipeline
    
    def _get_relevant_paths_for_language(self, language: str) -> List[str]:
        """
        Retorna paths relevantes para a linguagem.
        
        Args:
            language: Linguagem de programação.
            
        Returns:
            Lista de paths relevantes.
        """
        if language == "Python":
            return ["**/*.py", "requirements.txt", "setup.py", "pyproject.toml"]
        elif language == "JavaScript":
            return ["**/*.js", "**/*.jsx", "package.json", "package-lock.json"]
        elif language == "TypeScript":
            return ["**/*.ts", "**/*.tsx", "package.json", "package-lock.json", "tsconfig.json"]
        elif language == "Java":
            return ["**/*.java", "pom.xml", "build.gradle", "build.gradle.kts"]
        elif language == "Go":
            return ["**/*.go", "go.mod", "go.sum"]
        elif language == "Ruby":
            return ["**/*.rb", "Gemfile", "Gemfile.lock"]
        elif language == "PHP":
            return ["**/*.php", "composer.json", "composer.lock"]
        elif language == "C#":
            return ["**/*.cs", "**/*.csproj", "**/*.sln"]
        else:
            return ["**/*"]
    
    def _add_parallel_execution(self, pipeline: Dict[str, Any], pipeline_type: str) -> Dict[str, Any]:
        """
        Adiciona execução paralela ao pipeline quando possível.
        
        Args:
            pipeline: Pipeline a ser otimizado.
            pipeline_type: Tipo de pipeline.
            
        Returns:
            Pipeline otimizado.
        """
        # Implementação específica para cada tipo de pipeline
        if pipeline_type == "github_actions":
            # Identificar jobs que podem ser executados em paralelo
            pass
        
        elif pipeline_type == "gitlab_ci":
            # Adicionar parallel quando possível
            pass
        
        elif pipeline_type == "azure_devops":
            # Otimizar paralelismo
            pass
        
        return pipeline
    
    def _add_jenkins_caching(self, pipeline_content: str, repo_analysis: Dict[str, Any]) -> str:
        """
        Adiciona configurações de cache a um Jenkinsfile.
        
        Args:
            pipeline_content: Conteúdo do Jenkinsfile.
            repo_analysis: Resultado da análise do repositório.
            
        Returns:
            Jenkinsfile otimizado.
        """
        # Determinar a linguagem principal
        languages = repo_analysis.get("languages", {})
        if not languages:
            return pipeline_content
        
        primary_language = next(iter(languages))
        
        # Adicionar configuração de cache com base na linguagem
        if primary_language == "Java":
            # Verificar se já existe configuração de cache
            if "stash" not in pipeline_content:
                # Adicionar stash/unstash para Maven/Gradle
                pipeline_content = re.sub(
                    r'(stage\s*\(\s*[\'"]Build[\'"]\s*\)\s*\{[^\}]*\})',
                    r'\1\n        stage("Cache") {\n            steps {\n                stash includes: "**/target/**", name: "build-cache"\n            }\n        }',
                    pipeline_content
                )
                pipeline_content = re.sub(
                    r'(stage\s*\(\s*[\'"]Test[\'"]\s*\)\s*\{)',
                    r'        stage("Restore Cache") {\n            steps {\n                unstash "build-cache"\n            }\n        }\n\1',
                    pipeline_content
                )
        
        elif primary_language in ["JavaScript", "TypeScript"]:
            # Verificar se já existe configuração de cache
            if "stash" not in pipeline_content:
                # Adicionar stash/unstash para node_modules
                pipeline_content = re.sub(
                    r'(stage\s*\(\s*[\'"]Build[\'"]\s*\)\s*\{[^\}]*\})',
                    r'\1\n        stage("Cache") {\n            steps {\n                stash includes: "node_modules/**", name: "node-modules"\n            }\n        }',
                    pipeline_content
                )
                pipeline_content = re.sub(
                    r'(stage\s*\(\s*[\'"]Test[\'"]\s*\)\s*\{)',
                    r'        stage("Restore Cache") {\n            steps {\n                unstash "node-modules"\n            }\n        }\n\1',
                    pipeline_content
                )
        
        return pipeline_content
    
    def _add_jenkins_parallel(self, pipeline_content: str) -> str:
        """
        Adiciona execução paralela a um Jenkinsfile.
        
        Args:
            pipeline_content: Conteúdo do Jenkinsfile.
            
        Returns:
            Jenkinsfile otimizado.
        """
        # Verificar se já existe configuração de paralelismo
        if "parallel" not in pipeline_content and "stage('Test')" in pipeline_content:
            # Adicionar execução paralela para testes
            pipeline_content = re.sub(
                r'stage\s*\(\s*[\'"]Test[\'"]\s*\)\s*\{\s*steps\s*\{([^\}]*)\}\s*\}',
                r'stage("Test") {\n            parallel {\n                stage("Unit Tests") {\n                    steps {\1}\n                }\n                stage("Integration Tests") {\n                    steps {\n                        echo "Running integration tests..."\n                    }\n                }\n            }\n        }',
                pipeline_content
            )
        
        return pipeline_content
    
    def _optimize_jenkins_triggers(self, pipeline_content: str, repo_analysis: Dict[str, Any]) -> str:
        """
        Otimiza os triggers de um Jenkinsfile.
        
        Args:
            pipeline_content: Conteúdo do Jenkinsfile.
            repo_analysis: Resultado da análise do repositório.
            
        Returns:
            Jenkinsfile otimizado.
        """
        # Verificar se já existe configuração de triggers
        if "triggers" not in pipeline_content:
            # Adicionar triggers
            pipeline_content = re.sub(
                r'(pipeline\s*\{)',
                r'\1\n    triggers {\n        pollSCM("H/15 * * * *")\n    }',
                pipeline_content
            )
        
        return pipeline_content
