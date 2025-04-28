"""
Detector de falhas em pipelines CI/CD.
"""
import os
import logging
from typing import Dict, Any, List, Optional
import yaml
import json
import re

from config import Config, logger

class FailureDetector:
    """
    Classe para detectar e corrigir falhas em pipelines CI/CD.
    """
    
    def __init__(self):
        """
        Inicializa o detector de falhas.
        """
        self.logger = logging.getLogger("cicd_agent.failure_detector")
    
    def detect_failures(self, pipeline_content: str, pipeline_type: str, error_logs: Optional[str] = None) -> Dict[str, Any]:
        """
        Detecta falhas em um pipeline CI/CD.
        
        Args:
            pipeline_content: Conteúdo do arquivo de pipeline.
            pipeline_type: Tipo de pipeline (github_actions, gitlab_ci, jenkins, azure_devops).
            error_logs: Logs de erro opcionais para análise adicional.
            
        Returns:
            Dicionário com falhas detectadas e sugestões de correção.
        """
        self.logger.info(f"Detectando falhas em pipeline do tipo {pipeline_type}")
        
        try:
            # Selecionar o método de detecção apropriado com base no tipo de pipeline
            if pipeline_type == "github_actions":
                return self._detect_github_actions_failures(pipeline_content, error_logs)
            elif pipeline_type == "gitlab_ci":
                return self._detect_gitlab_ci_failures(pipeline_content, error_logs)
            elif pipeline_type == "jenkins":
                return self._detect_jenkins_failures(pipeline_content, error_logs)
            elif pipeline_type == "azure_devops":
                return self._detect_azure_devops_failures(pipeline_content, error_logs)
            else:
                self.logger.warning(f"Tipo de pipeline não suportado: {pipeline_type}")
                return {"status": "error", "message": f"Tipo de pipeline não suportado: {pipeline_type}"}
                
        except Exception as e:
            self.logger.error(f"Erro ao detectar falhas no pipeline: {str(e)}")
            return {"status": "error", "message": f"Erro ao detectar falhas: {str(e)}"}
    
    def fix_failures(self, pipeline_content: str, pipeline_type: str, failures: Dict[str, Any]) -> Optional[str]:
        """
        Corrige falhas detectadas em um pipeline CI/CD.
        
        Args:
            pipeline_content: Conteúdo do arquivo de pipeline.
            pipeline_type: Tipo de pipeline (github_actions, gitlab_ci, jenkins, azure_devops).
            failures: Dicionário com falhas detectadas.
            
        Returns:
            Conteúdo corrigido do pipeline ou None se não for possível corrigir.
        """
        self.logger.info(f"Corrigindo falhas em pipeline do tipo {pipeline_type}")
        
        try:
            # Selecionar o método de correção apropriado com base no tipo de pipeline
            if pipeline_type == "github_actions":
                return self._fix_github_actions_failures(pipeline_content, failures)
            elif pipeline_type == "gitlab_ci":
                return self._fix_gitlab_ci_failures(pipeline_content, failures)
            elif pipeline_type == "jenkins":
                return self._fix_jenkins_failures(pipeline_content, failures)
            elif pipeline_type == "azure_devops":
                return self._fix_azure_devops_failures(pipeline_content, failures)
            else:
                self.logger.warning(f"Tipo de pipeline não suportado: {pipeline_type}")
                return None
                
        except Exception as e:
            self.logger.error(f"Erro ao corrigir falhas no pipeline: {str(e)}")
            return None
    
    def _detect_github_actions_failures(self, pipeline_content: str, error_logs: Optional[str] = None) -> Dict[str, Any]:
        """
        Detecta falhas em um pipeline GitHub Actions.
        
        Args:
            pipeline_content: Conteúdo do arquivo de pipeline.
            error_logs: Logs de erro opcionais para análise adicional.
            
        Returns:
            Dicionário com falhas detectadas e sugestões de correção.
        """
        failures = {
            "status": "success",
            "failures": [],
            "warnings": []
        }
        
        try:
            # Carregar o pipeline como YAML
            pipeline = yaml.safe_load(pipeline_content)
            if not pipeline:
                failures["status"] = "error"
                failures["message"] = "Não foi possível carregar o pipeline como YAML válido"
                return failures
            
            # Verificar problemas comuns
            
            # 1. Verificar se há jobs definidos
            if "jobs" not in pipeline:
                failures["failures"].append({
                    "type": "missing_jobs",
                    "message": "Não há jobs definidos no pipeline",
                    "fix": "Adicionar seção 'jobs' com pelo menos um job"
                })
            
            # 2. Verificar se há triggers (on) definidos
            if "on" not in pipeline:
                failures["failures"].append({
                    "type": "missing_triggers",
                    "message": "Não há triggers (on) definidos no pipeline",
                    "fix": "Adicionar seção 'on' com pelo menos um trigger (push, pull_request, etc.)"
                })
            
            # 3. Verificar jobs sem steps
            if "jobs" in pipeline:
                for job_name, job in pipeline["jobs"].items():
                    if "steps" not in job or not job["steps"]:
                        failures["failures"].append({
                            "type": "missing_steps",
                            "message": f"Job '{job_name}' não tem steps definidos",
                            "job": job_name,
                            "fix": f"Adicionar pelo menos um step ao job '{job_name}'"
                        })
            
            # 4. Verificar referências a secrets não definidos
            if "jobs" in pipeline:
                for job_name, job in pipeline["jobs"].items():
                    if "steps" in job:
                        for step_index, step in enumerate(job["steps"]):
                            step_str = str(step)
                            secret_refs = re.findall(r'\$\{\{\s*secrets\.([a-zA-Z0-9_-]+)\s*\}\}', step_str)
                            for secret in secret_refs:
                                # Avisar sobre possíveis secrets não definidos
                                failures["warnings"].append({
                                    "type": "undefined_secret",
                                    "message": f"Possível referência a secret não definido: '{secret}' no job '{job_name}', step {step_index + 1}",
                                    "job": job_name,
                                    "step": step_index,
                                    "secret": secret,
                                    "fix": f"Verificar se o secret '{secret}' está definido nas configurações do repositório"
                                })
            
            # 5. Verificar dependências de jobs (needs) inválidas
            if "jobs" in pipeline:
                job_names = set(pipeline["jobs"].keys())
                for job_name, job in pipeline["jobs"].items():
                    if "needs" in job:
                        needs = job["needs"]
                        if isinstance(needs, str) and needs not in job_names:
                            failures["failures"].append({
                                "type": "invalid_needs",
                                "message": f"Job '{job_name}' depende de job inexistente: '{needs}'",
                                "job": job_name,
                                "dependency": needs,
                                "fix": f"Corrigir a dependência 'needs' para um job existente ou remover"
                            })
                        elif isinstance(needs, list):
                            for need in needs:
                                if need not in job_names:
                                    failures["failures"].append({
                                        "type": "invalid_needs",
                                        "message": f"Job '{job_name}' depende de job inexistente: '{need}'",
                                        "job": job_name,
                                        "dependency": need,
                                        "fix": f"Corrigir a dependência 'needs' para um job existente ou remover"
                                    })
            
            # 6. Verificar runners inválidos
            if "jobs" in pipeline:
                for job_name, job in pipeline["jobs"].items():
                    if "runs-on" not in job:
                        failures["failures"].append({
                            "type": "missing_runner",
                            "message": f"Job '{job_name}' não tem runner (runs-on) definido",
                            "job": job_name,
                            "fix": f"Adicionar 'runs-on' ao job '{job_name}'"
                        })
            
            # 7. Analisar logs de erro, se fornecidos
            if error_logs:
                # Procurar por erros comuns nos logs
                if "No such file or directory" in error_logs:
                    failures["warnings"].append({
                        "type": "file_not_found",
                        "message": "Possível erro de arquivo não encontrado",
                        "fix": "Verificar caminhos de arquivos no pipeline"
                    })
                
                if "Permission denied" in error_logs:
                    failures["warnings"].append({
                        "type": "permission_denied",
                        "message": "Possível erro de permissão negada",
                        "fix": "Verificar permissões de arquivos ou adicionar 'chmod +x' para scripts"
                    })
                
                if "Error: Process completed with exit code" in error_logs:
                    failures["warnings"].append({
                        "type": "exit_code_error",
                        "message": "Processo completou com código de erro",
                        "fix": "Verificar comandos e scripts executados no pipeline"
                    })
            
            return failures
            
        except Exception as e:
            self.logger.error(f"Erro ao detectar falhas no pipeline GitHub Actions: {str(e)}")
            failures["status"] = "error"
            failures["message"] = f"Erro ao analisar pipeline: {str(e)}"
            return failures
    
    def _detect_gitlab_ci_failures(self, pipeline_content: str, error_logs: Optional[str] = None) -> Dict[str, Any]:
        """
        Detecta falhas em um pipeline GitLab CI.
        
        Args:
            pipeline_content: Conteúdo do arquivo de pipeline.
            error_logs: Logs de erro opcionais para análise adicional.
            
        Returns:
            Dicionário com falhas detectadas e sugestões de correção.
        """
        failures = {
            "status": "success",
            "failures": [],
            "warnings": []
        }
        
        try:
            # Carregar o pipeline como YAML
            pipeline = yaml.safe_load(pipeline_content)
            if not pipeline:
                failures["status"] = "error"
                failures["message"] = "Não foi possível carregar o pipeline como YAML válido"
                return failures
            
            # Verificar problemas comuns
            
            # 1. Verificar se há stages definidos
            if "stages" not in pipeline:
                failures["warnings"].append({
                    "type": "missing_stages",
                    "message": "Não há stages definidos no pipeline",
                    "fix": "Adicionar seção 'stages' com os estágios do pipeline"
                })
            
            # 2. Verificar se há jobs definidos
            job_count = 0
            for key, value in pipeline.items():
                if isinstance(value, dict) and ("script" in value or "extends" in value):
                    job_count += 1
            
            if job_count == 0:
                failures["failures"].append({
                    "type": "missing_jobs",
                    "message": "Não há jobs definidos no pipeline",
                    "fix": "Adicionar pelo menos um job com script ou extends"
                })
            
            # 3. Verificar jobs sem script ou extends
            for key, value in pipeline.items():
                if isinstance(value, dict) and key not in ["stages", "variables", "default", "include"]:
                    if "script" not in value and "extends" not in value:
                        failures["failures"].append({
                            "type": "missing_script",
                            "message": f"Job '{key}' não tem script ou extends definido",
                            "job": key,
                            "fix": f"Adicionar 'script' ou 'extends' ao job '{key}'"
                        })
            
            # 4. Verificar referências a variáveis não definidas
            if "variables" in pipeline:
                defined_vars = set(pipeline["variables"].keys())
                
                for key, value in pipeline.items():
                    if isinstance(value, dict) and key not in ["stages", "variables", "default", "include"]:
                        job_str = str(value)
                        var_refs = re.findall(r'\$([A-Z0-9_]+)', job_str)
                        for var in var_refs:
                            if var not in defined_vars and not var.startswith("CI_"):
                                failures["warnings"].append({
                                    "type": "undefined_variable",
                                    "message": f"Possível referência a variável não definida: '{var}' no job '{key}'",
                                    "job": key,
                                    "variable": var,
                                    "fix": f"Definir a variável '{var}' na seção 'variables'"
                                })
            
            # 5. Verificar stages inválidos
            if "stages" in pipeline:
                defined_stages = set(pipeline["stages"])
                
                for key, value in pipeline.items():
                    if isinstance(value, dict) and key not in ["stages", "variables", "default", "include"]:
                        if "stage" in value and value["stage"] not in defined_stages:
                            failures["failures"].append({
                                "type": "invalid_stage",
                                "message": f"Job '{key}' usa stage inexistente: '{value['stage']}'",
                                "job": key,
                                "stage": value["stage"],
                                "fix": f"Adicionar '{value['stage']}' à lista de stages ou corrigir o nome"
                            })
            
            # 6. Analisar logs de erro, se fornecidos
            if error_logs:
                # Procurar por erros comuns nos logs
                if "No such file or directory" in error_logs:
                    failures["warnings"].append({
                        "type": "file_not_found",
                        "message": "Possível erro de arquivo não encontrado",
                        "fix": "Verificar caminhos de arquivos no pipeline"
                    })
                
                if "Permission denied" in error_logs:
                    failures["warnings"].append({
                        "type": "permission_denied",
                        "message": "Possível erro de permissão negada",
                        "fix": "Verificar permissões de arquivos ou adicionar 'chmod +x' para scripts"
                    })
                
                if "Job failed" in error_logs:
                    failures["warnings"].append({
                        "type": "job_failed",
                        "message": "Job falhou durante a execução",
                        "fix": "Verificar comandos e scripts executados no pipeline"
                    })
            
            return failures
            
        except Exception as e:
            self.logger.error(f"Erro ao detectar falhas no pipeline GitLab CI: {str(e)}")
            failures["status"] = "error"
            failures["message"] = f"Erro ao analisar pipeline: {str(e)}"
            return failures
    
    def _detect_jenkins_failures(self, pipeline_content: str, error_logs: Optional[str] = None) -> Dict[str, Any]:
        """
        Detecta falhas em um pipeline Jenkins.
        
        Args:
            pipeline_content: Conteúdo do arquivo de pipeline.
            error_logs: Logs de erro opcionais para análise adicional.
            
        Returns:
            Dicionário com falhas detectadas e sugestões de correção.
        """
        failures = {
            "status": "success",
            "failures": [],
            "warnings": []
        }
        
        try:
            # Verificar problemas comuns usando expressões regulares
            
            # 1. Verificar se há pipeline definido
            if not re.search(r'pipeline\s*\{', pipeline_content):
                failures["failures"].append({
                    "type": "missing_pipeline",
                    "message": "Não há bloco 'pipeline' definido",
                    "fix": "Adicionar bloco 'pipeline { ... }'"
                })
            
            # 2. Verificar se há agent definido
            if not re.search(r'agent\s*\{', pipeline_content) and not re.search(r'agent\s+any', pipeline_content):
                failures["failures"].append({
                    "type": "missing_agent",
                    "message": "Não há 'agent' definido",
                    "fix": "Adicionar 'agent any' ou 'agent { ... }'"
                })
            
            # 3. Verificar se há stages definidos
            if not re.search(r'stages\s*\{', pipeline_content):
                failures["failures"].append({
                    "type": "missing_stages",
                    "message": "Não há bloco 'stages' definido",
                    "fix": "Adicionar bloco 'stages { ... }'"
                })
            
            # 4. Verificar se há pelo menos um stage
            if not re.search(r'stage\s*\(', pipeline_content):
                failures["failures"].append({
                    "type": "missing_stage",
                    "message": "Não há nenhum 'stage' definido",
                    "fix": "Adicionar pelo menos um 'stage(...)'"
                })
            
            # 5. Verificar se há steps em cada stage
            stages = re.findall(r'stage\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)\s*\{([^\}]*)\}', pipeline_content)
            for stage_name, stage_content in stages:
                if not re.search(r'steps\s*\{', stage_content):
                    failures["failures"].append({
                        "type": "missing_steps",
                        "message": f"Stage '{stage_name}' não tem bloco 'steps' definido",
                        "stage": stage_name,
                        "fix": f"Adicionar bloco 'steps {{ ... }}' ao stage '{stage_name}'"
                    })
            
            # 6. Verificar referências a variáveis não definidas
            var_refs = re.findall(r'\$\{([a-zA-Z0-9_]+)\}', pipeline_content)
            defined_vars = set()
            
            # Procurar variáveis definidas
            env_block = re.search(r'environment\s*\{([^\}]*)\}', pipeline_content)
            if env_block:
                env_vars = re.findall(r'([a-zA-Z0-9_]+)\s*=', env_block.group(1))
                defined_vars.update(env_vars)
            
            # Procurar parâmetros definidos
            params_block = re.search(r'parameters\s*\{([^\}]*)\}', pipeline_content)
            if params_block:
                param_vars = re.findall(r'([a-zA-Z0-9_]+)\s*\(', params_block.group(1))
                defined_vars.update(param_vars)
            
            # Verificar variáveis não definidas
            for var in var_refs:
                if var not in defined_vars and not var.startswith("env.") and var not in ["BUILD_NUMBER", "JOB_NAME", "WORKSPACE"]:
                    failures["warnings"].append({
                        "type": "undefined_variable",
                        "message": f"Possível referência a variável não definida: '{var}'",
                        "variable": var,
                        "fix": f"Definir a variável '{var}' na seção 'environment' ou como parâmetro"
                    })
            
            # 7. Analisar logs de erro, se fornecidos
            if error_logs:
                # Procurar por erros comuns nos logs
                if "No such file or directory" in error_logs:
                    failures["warnings"].append({
                        "type": "file_not_found",
                        "message": "Possível erro de arquivo não encontrado",
                        "fix": "Verificar caminhos de arquivos no pipeline"
                    })
                
                if "Permission denied" in error_logs:
                    failures["warnings"].append({
                        "type": "permission_denied",
                        "message": "Possível erro de permissão negada",
                        "fix": "Verificar permissões de arquivos ou adicionar 'sh \"chmod +x ...\"' para scripts"
                    })
                
                if "groovy.lang.MissingPropertyException" in error_logs:
                    failures["warnings"].append({
                        "type": "missing_property",
                        "message": "Possível erro de propriedade não definida",
                        "fix": "Verificar variáveis e propriedades usadas no pipeline"
                    })
            
            return failures
            
        except Exception as e:
            self.logger.error(f"Erro ao detectar falhas no pipeline Jenkins: {str(e)}")
            failures["status"] = "error"
            failures["message"] = f"Erro ao analisar pipeline: {str(e)}"
            return failures
    
    def _detect_azure_devops_failures(self, pipeline_content: str, error_logs: Optional[str] = None) -> Dict[str, Any]:
        """
        Detecta falhas em um pipeline Azure DevOps.
        
        Args:
            pipeline_content: Conteúdo do arquivo de pipeline.
            error_logs: Logs de erro opcionais para análise adicional.
            
        Returns:
            Dicionário com falhas detectadas e sugestões de correção.
        """
        failures = {
            "status": "success",
            "failures": [],
            "warnings": []
        }
        
        try:
            # Carregar o pipeline como YAML
            pipeline = yaml.safe_load(pipeline_content)
            if not pipeline:
                failures["status"] = "error"
                failures["message"] = "Não foi possível carregar o pipeline como YAML válido"
                return failures
            
            # Verificar problemas comuns
            
            # 1. Verificar se há trigger ou pr definidos
            if "trigger" not in pipeline and "pr" not in pipeline:
                failures["warnings"].append({
                    "type": "missing_triggers",
                    "message": "Não há triggers (trigger/pr) definidos no pipeline",
                    "fix": "Adicionar seção 'trigger' ou 'pr'"
                })
            
            # 2. Verificar se há pool definido
            if "pool" not in pipeline:
                failures["warnings"].append({
                    "type": "missing_pool",
                    "message": "Não há 'pool' definido no pipeline",
                    "fix": "Adicionar seção 'pool' com o agente a ser usado"
                })
            
            # 3. Verificar se há stages, jobs ou steps definidos
            if "stages" not in pipeline and "jobs" not in pipeline and "steps" not in pipeline:
                failures["failures"].append({
                    "type": "missing_pipeline_structure",
                    "message": "Não há 'stages', 'jobs' ou 'steps' definidos no pipeline",
                    "fix": "Adicionar pelo menos uma das seções: 'stages', 'jobs' ou 'steps'"
                })
            
            # 4. Verificar jobs sem steps
            if "jobs" in pipeline:
                for job_index, job in enumerate(pipeline["jobs"]):
                    if "steps" not in job or not job["steps"]:
                        failures["failures"].append({
                            "type": "missing_steps",
                            "message": f"Job {job_index + 1} não tem steps definidos",
                            "job_index": job_index,
                            "fix": f"Adicionar pelo menos um step ao job {job_index + 1}"
                        })
            
            # 5. Verificar stages sem jobs
            if "stages" in pipeline:
                for stage_index, stage in enumerate(pipeline["stages"]):
                    if "jobs" not in stage or not stage["jobs"]:
                        failures["failures"].append({
                            "type": "missing_jobs",
                            "message": f"Stage '{stage.get('name', f'Stage {stage_index + 1}')}' não tem jobs definidos",
                            "stage_index": stage_index,
                            "fix": f"Adicionar pelo menos um job ao stage '{stage.get('name', f'Stage {stage_index + 1}')}'"
                        })
            
            # 6. Verificar referências a variáveis não definidas
            pipeline_str = str(pipeline)
            var_refs = re.findall(r'\$\(([a-zA-Z0-9_.-]+)\)', pipeline_str)
            defined_vars = set()
            
            # Procurar variáveis definidas
            if "variables" in pipeline:
                if isinstance(pipeline["variables"], list):
                    for var in pipeline["variables"]:
                        if isinstance(var, dict) and "name" in var:
                            defined_vars.add(var["name"])
                elif isinstance(pipeline["variables"], dict):
                    defined_vars.update(pipeline["variables"].keys())
            
            # Verificar variáveis não definidas
            for var in var_refs:
                if var not in defined_vars and not var.startswith("System.") and not var.startswith("Build."):
                    failures["warnings"].append({
                        "type": "undefined_variable",
                        "message": f"Possível referência a variável não definida: '{var}'",
                        "variable": var,
                        "fix": f"Definir a variável '{var}' na seção 'variables'"
                    })
            
            # 7. Verificar dependências de jobs (dependsOn) inválidas
            if "stages" in pipeline:
                stage_names = [stage.get("name", f"stage_{i}") for i, stage in enumerate(pipeline["stages"])]
                
                for stage_index, stage in enumerate(pipeline["stages"]):
                    if "dependsOn" in stage:
                        depends_on = stage["dependsOn"]
                        if isinstance(depends_on, str) and depends_on not in stage_names:
                            failures["failures"].append({
                                "type": "invalid_depends_on",
                                "message": f"Stage '{stage.get('name', f'Stage {stage_index + 1}')}' depende de stage inexistente: '{depends_on}'",
                                "stage_index": stage_index,
                                "dependency": depends_on,
                                "fix": f"Corrigir a dependência 'dependsOn' para um stage existente ou remover"
                            })
                        elif isinstance(depends_on, list):
                            for depend in depends_on:
                                if depend not in stage_names:
                                    failures["failures"].append({
                                        "type": "invalid_depends_on",
                                        "message": f"Stage '{stage.get('name', f'Stage {stage_index + 1}')}' depende de stage inexistente: '{depend}'",
                                        "stage_index": stage_index,
                                        "dependency": depend,
                                        "fix": f"Corrigir a dependência 'dependsOn' para um stage existente ou remover"
                                    })
            
            # 8. Analisar logs de erro, se fornecidos
            if error_logs:
                # Procurar por erros comuns nos logs
                if "No such file or directory" in error_logs:
                    failures["warnings"].append({
                        "type": "file_not_found",
                        "message": "Possível erro de arquivo não encontrado",
                        "fix": "Verificar caminhos de arquivos no pipeline"
                    })
                
                if "Permission denied" in error_logs:
                    failures["warnings"].append({
                        "type": "permission_denied",
                        "message": "Possível erro de permissão negada",
                        "fix": "Verificar permissões de arquivos ou adicionar 'chmod +x' para scripts"
                    })
                
                if "Task failed" in error_logs:
                    failures["warnings"].append({
                        "type": "task_failed",
                        "message": "Task falhou durante a execução",
                        "fix": "Verificar configurações das tasks no pipeline"
                    })
            
            return failures
            
        except Exception as e:
            self.logger.error(f"Erro ao detectar falhas no pipeline Azure DevOps: {str(e)}")
            failures["status"] = "error"
            failures["message"] = f"Erro ao analisar pipeline: {str(e)}"
            return failures
    
    def _fix_github_actions_failures(self, pipeline_content: str, failures: Dict[str, Any]) -> Optional[str]:
        """
        Corrige falhas detectadas em um pipeline GitHub Actions.
        
        Args:
            pipeline_content: Conteúdo do arquivo de pipeline.
            failures: Dicionário com falhas detectadas.
            
        Returns:
            Conteúdo corrigido do pipeline ou None se não for possível corrigir.
        """
        try:
            # Carregar o pipeline como YAML
            pipeline = yaml.safe_load(pipeline_content)
            if not pipeline:
                return None
            
            # Aplicar correções com base nas falhas detectadas
            for failure in failures.get("failures", []):
                failure_type = failure.get("type")
                
                if failure_type == "missing_jobs":
                    # Adicionar seção jobs com um job básico
                    pipeline["jobs"] = {
                        "build": {
                            "runs-on": "ubuntu-latest",
                            "steps": [
                                {"uses": "actions/checkout@v3"},
                                {"name": "Run a one-line script", "run": "echo Hello, world!"}
                            ]
                        }
                    }
                
                elif failure_type == "missing_triggers":
                    # Adicionar trigger básico
                    pipeline["on"] = {"push": {"branches": ["main"]}, "pull_request": {"branches": ["main"]}}
                
                elif failure_type == "missing_steps":
                    # Adicionar steps básicos ao job
                    job_name = failure.get("job")
                    if job_name and job_name in pipeline.get("jobs", {}):
                        pipeline["jobs"][job_name]["steps"] = [
                            {"uses": "actions/checkout@v3"},
                            {"name": "Run a one-line script", "run": "echo Hello, world!"}
                        ]
                
                elif failure_type == "invalid_needs":
                    # Corrigir ou remover dependência inválida
                    job_name = failure.get("job")
                    dependency = failure.get("dependency")
                    if job_name and dependency and job_name in pipeline.get("jobs", {}):
                        if "needs" in pipeline["jobs"][job_name]:
                            if isinstance(pipeline["jobs"][job_name]["needs"], str):
                                # Remover dependência inválida
                                del pipeline["jobs"][job_name]["needs"]
                            elif isinstance(pipeline["jobs"][job_name]["needs"], list):
                                # Remover dependência inválida da lista
                                pipeline["jobs"][job_name]["needs"] = [
                                    need for need in pipeline["jobs"][job_name]["needs"] if need != dependency
                                ]
                                if not pipeline["jobs"][job_name]["needs"]:
                                    del pipeline["jobs"][job_name]["needs"]
                
                elif failure_type == "missing_runner":
                    # Adicionar runner ao job
                    job_name = failure.get("job")
                    if job_name and job_name in pipeline.get("jobs", {}):
                        pipeline["jobs"][job_name]["runs-on"] = "ubuntu-latest"
            
            # Converter de volta para YAML
            return yaml.dump(pipeline, sort_keys=False)
            
        except Exception as e:
            self.logger.error(f"Erro ao corrigir falhas no pipeline GitHub Actions: {str(e)}")
            return None
    
    def _fix_gitlab_ci_failures(self, pipeline_content: str, failures: Dict[str, Any]) -> Optional[str]:
        """
        Corrige falhas detectadas em um pipeline GitLab CI.
        
        Args:
            pipeline_content: Conteúdo do arquivo de pipeline.
            failures: Dicionário com falhas detectadas.
            
        Returns:
            Conteúdo corrigido do pipeline ou None se não for possível corrigir.
        """
        try:
            # Carregar o pipeline como YAML
            pipeline = yaml.safe_load(pipeline_content)
            if not pipeline:
                return None
            
            # Aplicar correções com base nas falhas detectadas
            for failure in failures.get("failures", []):
                failure_type = failure.get("type")
                
                if failure_type == "missing_stages":
                    # Adicionar seção stages básica
                    pipeline["stages"] = ["build", "test", "deploy"]
                
                elif failure_type == "missing_jobs":
                    # Adicionar job básico
                    pipeline["build"] = {
                        "stage": "build",
                        "script": ["echo 'Building...'"]
                    }
                
                elif failure_type == "missing_script":
                    # Adicionar script básico ao job
                    job_name = failure.get("job")
                    if job_name and job_name in pipeline:
                        pipeline[job_name]["script"] = ["echo 'Running...'"]
                
                elif failure_type == "invalid_stage":
                    # Corrigir stage inválido
                    job_name = failure.get("job")
                    stage = failure.get("stage")
                    if job_name and stage and job_name in pipeline:
                        # Adicionar stage à lista de stages se não existir
                        if "stages" not in pipeline:
                            pipeline["stages"] = ["build", "test", "deploy"]
                        elif stage not in pipeline["stages"]:
                            pipeline["stages"].append(stage)
            
            # Converter de volta para YAML
            return yaml.dump(pipeline, sort_keys=False)
            
        except Exception as e:
            self.logger.error(f"Erro ao corrigir falhas no pipeline GitLab CI: {str(e)}")
            return None
    
    def _fix_jenkins_failures(self, pipeline_content: str, failures: Dict[str, Any]) -> Optional[str]:
        """
        Corrige falhas detectadas em um pipeline Jenkins.
        
        Args:
            pipeline_content: Conteúdo do arquivo de pipeline.
            failures: Dicionário com falhas detectadas.
            
        Returns:
            Conteúdo corrigido do pipeline ou None se não for possível corrigir.
        """
        try:
            # Aplicar correções com base nas falhas detectadas
            for failure in failures.get("failures", []):
                failure_type = failure.get("type")
                
                if failure_type == "missing_pipeline":
                    # Adicionar bloco pipeline básico
                    pipeline_content = "pipeline {\n    agent any\n    stages {\n        stage('Build') {\n            steps {\n                echo 'Building...'\n            }\n        }\n    }\n}"
                
                elif failure_type == "missing_agent":
                    # Adicionar agent básico
                    pipeline_content = re.sub(
                        r'(pipeline\s*\{)',
                        r'\1\n    agent any',
                        pipeline_content
                    )
                
                elif failure_type == "missing_stages":
                    # Adicionar bloco stages básico
                    pipeline_content = re.sub(
                        r'(pipeline\s*\{[^\}]*)',
                        r'\1\n    stages {\n        stage(\'Build\') {\n            steps {\n                echo \'Building...\'\n            }\n        }\n    }',
                        pipeline_content
                    )
                
                elif failure_type == "missing_stage":
                    # Adicionar stage básico
                    pipeline_content = re.sub(
                        r'(stages\s*\{[^\}]*)',
                        r'\1\n        stage(\'Build\') {\n            steps {\n                echo \'Building...\'\n            }\n        }',
                        pipeline_content
                    )
                
                elif failure_type == "missing_steps":
                    # Adicionar steps básicos ao stage
                    stage_name = failure.get("stage")
                    if stage_name:
                        pipeline_content = re.sub(
                            r'(stage\s*\(\s*[\'"]{0}[\'"]\s*\)\s*\{[^\}]*)',
                            r'\1\n            steps {\n                echo \'Running...\'\n            }',
                            pipeline_content.replace(stage_name, "{0}")
                        ).replace("{0}", stage_name)
            
            return pipeline_content
            
        except Exception as e:
            self.logger.error(f"Erro ao corrigir falhas no pipeline Jenkins: {str(e)}")
            return None
    
    def _fix_azure_devops_failures(self, pipeline_content: str, failures: Dict[str, Any]) -> Optional[str]:
        """
        Corrige falhas detectadas em um pipeline Azure DevOps.
        
        Args:
            pipeline_content: Conteúdo do arquivo de pipeline.
            failures: Dicionário com falhas detectadas.
            
        Returns:
            Conteúdo corrigido do pipeline ou None se não for possível corrigir.
        """
        try:
            # Carregar o pipeline como YAML
            pipeline = yaml.safe_load(pipeline_content)
            if not pipeline:
                return None
            
            # Aplicar correções com base nas falhas detectadas
            for failure in failures.get("failures", []):
                failure_type = failure.get("type")
                
                if failure_type == "missing_triggers":
                    # Adicionar trigger básico
                    pipeline["trigger"] = ["main"]
                
                elif failure_type == "missing_pool":
                    # Adicionar pool básico
                    pipeline["pool"] = {"vmImage": "ubuntu-latest"}
                
                elif failure_type == "missing_pipeline_structure":
                    # Adicionar estrutura básica
                    if "stages" not in pipeline and "jobs" not in pipeline and "steps" not in pipeline:
                        pipeline["jobs"] = [
                            {
                                "job": "build",
                                "steps": [
                                    {"checkout": "self"},
                                    {"script": "echo Hello, world!", "displayName": "Run a one-line script"}
                                ]
                            }
                        ]
                
                elif failure_type == "missing_steps":
                    # Adicionar steps básicos ao job
                    job_index = failure.get("job_index")
                    if job_index is not None and job_index < len(pipeline.get("jobs", [])):
                        pipeline["jobs"][job_index]["steps"] = [
                            {"checkout": "self"},
                            {"script": "echo Hello, world!", "displayName": "Run a one-line script"}
                        ]
                
                elif failure_type == "missing_jobs":
                    # Adicionar jobs básicos ao stage
                    stage_index = failure.get("stage_index")
                    if stage_index is not None and stage_index < len(pipeline.get("stages", [])):
                        pipeline["stages"][stage_index]["jobs"] = [
                            {
                                "job": "build",
                                "steps": [
                                    {"checkout": "self"},
                                    {"script": "echo Hello, world!", "displayName": "Run a one-line script"}
                                ]
                            }
                        ]
                
                elif failure_type == "invalid_depends_on":
                    # Corrigir ou remover dependência inválida
                    stage_index = failure.get("stage_index")
                    dependency = failure.get("dependency")
                    if stage_index is not None and dependency and stage_index < len(pipeline.get("stages", [])):
                        if "dependsOn" in pipeline["stages"][stage_index]:
                            if isinstance(pipeline["stages"][stage_index]["dependsOn"], str):
                                # Remover dependência inválida
                                del pipeline["stages"][stage_index]["dependsOn"]
                            elif isinstance(pipeline["stages"][stage_index]["dependsOn"], list):
                                # Remover dependência inválida da lista
                                pipeline["stages"][stage_index]["dependsOn"] = [
                                    depend for depend in pipeline["stages"][stage_index]["dependsOn"] if depend != dependency
                                ]
                                if not pipeline["stages"][stage_index]["dependsOn"]:
                                    del pipeline["stages"][stage_index]["dependsOn"]
            
            # Converter de volta para YAML
            return yaml.dump(pipeline, sort_keys=False)
            
        except Exception as e:
            self.logger.error(f"Erro ao corrigir falhas no pipeline Azure DevOps: {str(e)}")
            return None
