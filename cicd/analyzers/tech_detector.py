import os
import re
from typing import Dict, List, Any, Optional
import logging
import json
import yaml

from config import Config, logger

class TechDetector:

    def __init__(self, repo_path: str = None):
        self.repo_path = repo_path
        self.logger = logging.getLogger("cicd_agent.tech_detector")
        if not os.path.exists(self.repo_path):
            self.logger.error(f"Caminho do repositório não encontrado: {self.repo_path}")
            raise FileNotFoundError(f"Caminho do repositório não encontrado: {self.repo_path}")
    
    def detect_technologies(self) -> Dict[str, Any]:
        self.logger.info(f"Iniciando detecção de tecnologias: {self.repo_path}")
        
        result = {
            "testing_frameworks": self.detect_testing_frameworks(),
            "linters_formatters": self.detect_linters_formatters(),
            "containerization": self.detect_containerization(),
            "cloud_providers": self.detect_cloud_providers(),
            "databases": self.detect_databases(),
            "frontend_libraries": self.detect_frontend_libraries(),
            "deployment_tools": self.detect_deployment_tools(),
            "monitoring_tools": self.detect_monitoring_tools(),
        }
        
        self.logger.info(f"Detecção de tecnologias concluída: {self.repo_path}")
        return result
    
    def detect_testing_frameworks(self) -> Dict[str, List[str]]:
        testing_frameworks = {}
        
        # Python
        python_frameworks = []
        if self._has_file_content_match("pytest"):
            python_frameworks.append("pytest")
        if self._has_file_content_match("unittest"):
            python_frameworks.append("unittest")
        if self._has_file_content_match("nose"):
            python_frameworks.append("nose")
        if python_frameworks:
            testing_frameworks["Python"] = python_frameworks
        
        # JavaScript/TypeScript
        js_frameworks = []
        if self._has_file_content_match("jest"):
            js_frameworks.append("Jest")
        if self._has_file_content_match("mocha"):
            js_frameworks.append("Mocha")
        if self._has_file_content_match("jasmine"):
            js_frameworks.append("Jasmine")
        if self._has_file_content_match("cypress"):
            js_frameworks.append("Cypress")
        if self._has_file_content_match("selenium"):
            js_frameworks.append("Selenium")
        if js_frameworks:
            testing_frameworks["JavaScript/TypeScript"] = js_frameworks
        
        # Java
        java_frameworks = []
        if self._has_file_content_match("junit"):
            java_frameworks.append("JUnit")
        if self._has_file_content_match("testng"):
            java_frameworks.append("TestNG")
        if self._has_file_content_match("mockito"):
            java_frameworks.append("Mockito")
        if java_frameworks:
            testing_frameworks["Java"] = java_frameworks
        
        # Go
        go_frameworks = []
        if self._has_file_content_match("testing.T"):
            go_frameworks.append("Go Testing")
        if self._has_file_content_match("testify"):
            go_frameworks.append("Testify")
        if go_frameworks:
            testing_frameworks["Go"] = go_frameworks
        
        # .NET
        dotnet_frameworks = []
        if self._has_file_content_match("xunit"):
            dotnet_frameworks.append("xUnit")
        if self._has_file_content_match("nunit"):
            dotnet_frameworks.append("NUnit")
        if self._has_file_content_match("mstest"):
            dotnet_frameworks.append("MSTest")
        if dotnet_frameworks:
            testing_frameworks["C#"] = dotnet_frameworks
        
        self.logger.info(f"Frameworks de teste detectados: {testing_frameworks}")
        return testing_frameworks
    
    def detect_linters_formatters(self) -> List[str]:
        linters_formatters = []
        
        # Verificar arquivos de configuração comuns
        linter_configs = {
            ".eslintrc": "ESLint",
            ".eslintrc.js": "ESLint",
            ".eslintrc.json": "ESLint",
            ".eslintrc.yml": "ESLint",
            ".eslintrc.yaml": "ESLint",
            ".prettierrc": "Prettier",
            ".prettierrc.js": "Prettier",
            ".prettierrc.json": "Prettier",
            ".prettierrc.yml": "Prettier",
            ".prettierrc.yaml": "Prettier",
            ".stylelintrc": "Stylelint",
            ".stylelintrc.js": "Stylelint",
            ".stylelintrc.json": "Stylelint",
            ".stylelintrc.yml": "Stylelint",
            ".stylelintrc.yaml": "Stylelint",
            "pylintrc": "Pylint",
            ".pylintrc": "Pylint",
            "pyproject.toml": None,  # Verificar conteúdo
            "setup.cfg": None,  # Verificar conteúdo
            ".flake8": "Flake8",
            "tslint.json": "TSLint",
            ".jshintrc": "JSHint",
            ".golangci.yml": "GolangCI-Lint",
            ".golangci.yaml": "GolangCI-Lint",
            ".rubocop.yml": "RuboCop",
            ".checkstyle.xml": "Checkstyle",
            "checkstyle.xml": "Checkstyle",
            ".scalafmt.conf": "Scalafmt",
            ".ktlint.yml": "ktlint",
            ".editorconfig": "EditorConfig",
        }
        
        for config_file, linter in linter_configs.items():
            if self._has_file(config_file):
                if linter:
                    if linter not in linters_formatters:
                        linters_formatters.append(linter)
                else:
                    # Verificar conteúdo para arquivos como pyproject.toml
                    if config_file == "pyproject.toml":
                        content = self._read_file_content(config_file)
                        if content:
                            if "black" in content.lower():
                                linters_formatters.append("Black")
                            if "isort" in content.lower():
                                linters_formatters.append("isort")
                            if "flake8" in content.lower():
                                linters_formatters.append("Flake8")
                            if "pylint" in content.lower():
                                linters_formatters.append("Pylint")
                            if "mypy" in content.lower():
                                linters_formatters.append("mypy")
                    elif config_file == "setup.cfg":
                        content = self._read_file_content(config_file)
                        if content:
                            if "flake8" in content.lower():
                                linters_formatters.append("Flake8")
                            if "pylint" in content.lower():
                                linters_formatters.append("Pylint")
                            if "isort" in content.lower():
                                linters_formatters.append("isort")
        
        # Verificar package.json para linters JavaScript
        if self._has_file("package.json"):
            package_json = self._read_json_file("package.json")
            if package_json:
                dependencies = {**package_json.get("dependencies", {}), **package_json.get("devDependencies", {})}
                
                if "eslint" in dependencies and "ESLint" not in linters_formatters:
                    linters_formatters.append("ESLint")
                if "prettier" in dependencies and "Prettier" not in linters_formatters:
                    linters_formatters.append("Prettier")
                if "stylelint" in dependencies and "Stylelint" not in linters_formatters:
                    linters_formatters.append("Stylelint")
                if "tslint" in dependencies and "TSLint" not in linters_formatters:
                    linters_formatters.append("TSLint")
                if "jshint" in dependencies and "JSHint" not in linters_formatters:
                    linters_formatters.append("JSHint")
        
        # Verificar requirements.txt para linters Python
        if self._has_file("requirements.txt") or self._has_file("requirements-dev.txt"):
            files_to_check = ["requirements.txt", "requirements-dev.txt"]
            for file in files_to_check:
                if self._has_file(file):
                    content = self._read_file_content(file)
                    if content:
                        if "black" in content.lower() and "Black" not in linters_formatters:
                            linters_formatters.append("Black")
                        if "flake8" in content.lower() and "Flake8" not in linters_formatters:
                            linters_formatters.append("Flake8")
                        if "pylint" in content.lower() and "Pylint" not in linters_formatters:
                            linters_formatters.append("Pylint")
                        if "isort" in content.lower() and "isort" not in linters_formatters:
                            linters_formatters.append("isort")
                        if "mypy" in content.lower() and "mypy" not in linters_formatters:
                            linters_formatters.append("mypy")
        
        self.logger.info(f"Linters e formatadores detectados: {linters_formatters}")
        return linters_formatters
    
    def detect_containerization(self) -> Dict[str, bool]:
        """
        Detecta tecnologias de containerização utilizadas no repositório.
        
        Returns:
            Dicionário com tecnologias de containerização detectadas.
        """
        containerization = {
            "docker": False,
            "docker_compose": False,
            "kubernetes": False,
            "helm": False,
        }
        
        # Docker
        if self._has_file("Dockerfile") or self._has_file_with_pattern("Dockerfile.*"):
            containerization["docker"] = True
        
        # Docker Compose
        if self._has_file("docker-compose.yml") or self._has_file("docker-compose.yaml"):
            containerization["docker_compose"] = True
        
        # Kubernetes
        k8s_patterns = ["*.yaml", "*.yml", "*.json"]
        for root, _, files in os.walk(self.repo_path):
            # Ignorar diretórios ocultos e node_modules, venv, etc.
            if any(part.startswith(".") for part in root.split(os.sep)) or \
               any(part in ["node_modules", "venv", "env", "__pycache__", "dist", "build", "target"] 
                   for part in root.split(os.sep)):
                continue
                
            for file in files:
                file_path = os.path.join(root, file)
                
                # Verificar se é um arquivo YAML ou JSON
                if any(self._match_pattern(file, pattern) for pattern in k8s_patterns):
                    try:
                        content = self._read_file_content(file_path)
                        if content and ("kind:" in content or "apiVersion:" in content):
                            containerization["kubernetes"] = True
                            break
                    except Exception:
                        pass
            
            if containerization["kubernetes"]:
                break
        
        # Helm
        if os.path.exists(os.path.join(self.repo_path, "Chart.yaml")) or \
           os.path.exists(os.path.join(self.repo_path, "charts")) and os.path.isdir(os.path.join(self.repo_path, "charts")):
            containerization["helm"] = True
        
        self.logger.info(f"Tecnologias de containerização detectadas: {containerization}")
        return containerization
    
    def detect_cloud_providers(self) -> Dict[str, bool]:
        """
        Detecta provedores de nuvem utilizados no repositório.
        
        Returns:
            Dicionário com provedores de nuvem detectados.
        """
        cloud_providers = {
            "aws": False,
            "azure": False,
            "gcp": False,
            "alibaba": False,
            "digitalocean": False,
            "heroku": False,
        }
        
        # AWS
        aws_patterns = ["aws", "amazon", "s3", "ec2", "lambda", "cloudformation", "cloudfront", "dynamodb", "rds"]
        if any(self._has_file_content_match(pattern) for pattern in aws_patterns):
            cloud_providers["aws"] = True
        
        # Azure
        azure_patterns = ["azure", "microsoft.azure", "azurerm", "app service", "cosmos db", "azure functions"]
        if any(self._has_file_content_match(pattern) for pattern in azure_patterns):
            cloud_providers["azure"] = True
        
        # GCP
        gcp_patterns = ["gcp", "google cloud", "gke", "cloud run", "cloud functions", "bigquery", "firestore"]
        if any(self._has_file_content_match(pattern) for pattern in gcp_patterns):
            cloud_providers["gcp"] = True
        
        # Alibaba Cloud
        alibaba_patterns = ["alibaba", "aliyun", "alicloud"]
        if any(self._has_file_content_match(pattern) for pattern in alibaba_patterns):
            cloud_providers["alibaba"] = True
        
        # DigitalOcean
        do_patterns = ["digitalocean", "digital ocean", "droplet"]
        if any(self._has_file_content_match(pattern) for pattern in do_patterns):
            cloud_providers["digitalocean"] = True
        
        # Heroku
        if self._has_file("Procfile") or self._has_file_content_match("heroku"):
            cloud_providers["heroku"] = True
        
        self.logger.info(f"Provedores de nuvem detectados: {cloud_providers}")
        return cloud_providers
    
    def detect_databases(self) -> List[str]:
        """
        Detecta bancos de dados utilizados no repositório.
        
        Returns:
            Lista de bancos de dados detectados.
        """
        databases = []
        
        # Padrões para diferentes bancos de dados
        db_patterns = {
            "mysql": ["mysql", "mariadb"],
            "postgresql": ["postgresql", "postgres"],
            "mongodb": ["mongodb", "mongo"],
            "redis": ["redis"],
            "elasticsearch": ["elasticsearch", "elastic"],
            "cassandra": ["cassandra"],
            "sqlite": ["sqlite"],
            "oracle": ["oracle", "oracledb"],
            "sqlserver": ["sqlserver", "mssql"],
            "dynamodb": ["dynamodb"],
            "cosmosdb": ["cosmosdb", "cosmos db"],
            "firestore": ["firestore"],
            "neo4j": ["neo4j"],
        }
        
        for db, patterns in db_patterns.items():
            if any(self._has_file_content_match(pattern) for pattern in patterns):
                databases.append(db)
        
        self.logger.info(f"Bancos de dados detectados: {databases}")
        return databases
    
    def detect_frontend_libraries(self) -> List[str]:
        """
        Detecta bibliotecas frontend utilizadas no repositório.
        
        Returns:
            Lista de bibliotecas frontend detectadas.
        """
        frontend_libraries = []
        
        # Verificar package.json
        if self._has_file("package.json"):
            package_json = self._read_json_file("package.json")
            if package_json:
                dependencies = {**package_json.get("dependencies", {}), **package_json.get("devDependencies", {})}
                
                # UI Libraries
                if "react" in dependencies:
                    frontend_libraries.append("React")
                if "vue" in dependencies:
                    frontend_libraries.append("Vue.js")
                if "angular" in dependencies or "@angular/core" in dependencies:
                    frontend_libraries.append("Angular")
                if "svelte" in dependencies:
                    frontend_libraries.append("Svelte")
                
                # CSS Frameworks
                if "bootstrap" in dependencies:
                    frontend_libraries.append("Bootstrap")
                if "tailwindcss" in dependencies:
                    frontend_libraries.append("Tailwind CSS")
                if "material-ui" in dependencies or "@mui/material" in dependencies:
                    frontend_libraries.append("Material UI")
                if "antd" in dependencies:
                    frontend_libraries.append("Ant Design")
                if "chakra-ui" in dependencies or "@chakra-ui/react" in dependencies:
                    frontend_libraries.append("Chakra UI")
                
                # State Management
                if "redux" in dependencies:
                    frontend_libraries.append("Redux")
                if "mobx" in dependencies:
                    frontend_libraries.append("MobX")
                if "recoil" in dependencies:
                    frontend_libraries.append("Recoil")
                if "vuex" in dependencies:
                    frontend_libraries.append("Vuex")
                if "pinia" in dependencies:
                    frontend_libraries.append("Pinia")
                
                # Testing
                if "jest" in dependencies:
                    frontend_libraries.append("Jest")
                if "cypress" in dependencies:
                    frontend_libraries.append("Cypress")
                if "testing-library" in " ".join(dependencies.keys()):
                    frontend_libraries.append("Testing Library")
        
        self.logger.info(f"Bibliotecas frontend detectadas: {frontend_libraries}")
        return frontend_libraries
    
    def detect_deployment_tools(self) -> List[str]:
        """
        Detecta ferramentas de deploy utilizadas no repositório.
        
        Returns:
            Lista de ferramentas de deploy detectadas.
        """
        deployment_tools = []
        
        # Verificar arquivos de configuração comuns
        deployment_configs = {
            "vercel.json": "Vercel",
            "netlify.toml": "Netlify",
            "firebase.json": "Firebase",
            "serverless.yml": "Serverless Framework",
            "serverless.yaml": "Serverless Framework",
            "terraform.tf": "Terraform",
            "main.tf": "Terraform",
            "cloudformation.yml": "CloudFormation",
            "cloudformation.yaml": "CloudFormation",
            "template.yml": "CloudFormation",
            "template.yaml": "CloudFormation",
            "ansible.yml": "Ansible",
            "ansible.yaml": "Ansible",
            "playbook.yml": "Ansible",
            "playbook.yaml": "Ansible",
            "pulumi.yaml": "Pulumi",
            "pulumi.yml": "Pulumi",
            "Procfile": "Heroku",
            "app.yaml": "Google App Engine",
            "app.yml": "Google App Engine",
            "appspec.yml": "AWS CodeDeploy",
            "appspec.yaml": "AWS CodeDeploy",
            "buildspec.yml": "AWS CodeBuild",
            "buildspec.yaml": "AWS CodeBuild",
            "cloudbuild.yml": "Google Cloud Build",
            "cloudbuild.yaml": "Google Cloud Build",
        }
        
        for config_file, tool in deployment_configs.items():
            if self._has_file(config_file) or self._has_file_with_pattern(config_file):
                if tool not in deployment_tools:
                    deployment_tools.append(tool)
        
        # Verificar diretórios específicos
        if os.path.exists(os.path.join(self.repo_path, "terraform")) and os.path.isdir(os.path.join(self.repo_path, "terraform")):
            if "Terraform" not in deployment_tools:
                deployment_tools.append("Terraform")
        
        if os.path.exists(os.path.join(self.repo_path, "ansible")) and os.path.isdir(os.path.join(self.repo_path, "ansible")):
            if "Ansible" not in deployment_tools:
                deployment_tools.append("Ansible")
        
        # Verificar conteúdo de arquivos para padrões específicos
        if self._has_file_content_match("terraform"):
            if "Terraform" not in deployment_tools:
                deployment_tools.append("Terraform")
        
        if self._has_file_content_match("ansible"):
            if "Ansible" not in deployment_tools:
                deployment_tools.append("Ansible")
        
        if self._has_file_content_match("pulumi"):
            if "Pulumi" not in deployment_tools:
                deployment_tools.append("Pulumi")
        
        if self._has_file_content_match("cloudformation"):
            if "CloudFormation" not in deployment_tools:
                deployment_tools.append("CloudFormation")
        
        self.logger.info(f"Ferramentas de deploy detectadas: {deployment_tools}")
        return deployment_tools
    
    def detect_monitoring_tools(self) -> List[str]:
        """
        Detecta ferramentas de monitoramento utilizadas no repositório.
        
        Returns:
            Lista de ferramentas de monitoramento detectadas.
        """
        monitoring_tools = []
        
        # Padrões para diferentes ferramentas de monitoramento
        monitoring_patterns = {
            "Prometheus": ["prometheus"],
            "Grafana": ["grafana"],
            "Datadog": ["datadog"],
            "New Relic": ["newrelic", "new relic"],
            "Sentry": ["sentry"],
            "ELK Stack": ["elasticsearch", "logstash", "kibana"],
            "Jaeger": ["jaeger"],
            "Zipkin": ["zipkin"],
            "Nagios": ["nagios"],
            "Zabbix": ["zabbix"],
            "AppDynamics": ["appdynamics"],
            "Dynatrace": ["dynatrace"],
            "CloudWatch": ["cloudwatch"],
            "Stackdriver": ["stackdriver"],
            "Application Insights": ["application insights"],
        }
        
        for tool, patterns in monitoring_patterns.items():
            if any(self._has_file_content_match(pattern) for pattern in patterns):
                monitoring_tools.append(tool)
        
        self.logger.info(f"Ferramentas de monitoramento detectadas: {monitoring_tools}")
        return monitoring_tools
    
    def _has_file(self, filename: str) -> bool:
        """
        Verifica se um arquivo existe no repositório.
        
        Args:
            filename: Nome do arquivo a ser verificado.
            
        Returns:
            True se o arquivo existe, False caso contrário.
        """
        return os.path.exists(os.path.join(self.repo_path, filename))
    
    def _has_file_with_pattern(self, pattern: str) -> bool:
        """
        Verifica se existe algum arquivo que corresponda ao padrão especificado.
        
        Args:
            pattern: Padrão a ser verificado.
            
        Returns:
            True se existe algum arquivo que corresponda ao padrão, False caso contrário.
        """
        for root, _, files in os.walk(self.repo_path):
            # Ignorar diretórios ocultos e node_modules, venv, etc.
            if any(part.startswith(".") for part in root.split(os.sep)) or \
               any(part in ["node_modules", "venv", "env", "__pycache__", "dist", "build", "target"] 
                   for part in root.split(os.sep)):
                continue
                
            for file in files:
                if self._match_pattern(file, pattern):
                    return True
        
        return False
    
    def _has_file_content_match(self, pattern: str) -> bool:
        """
        Verifica se algum arquivo contém o padrão especificado.
        
        Args:
            pattern: Padrão a ser verificado.
            
        Returns:
            True se algum arquivo contém o padrão, False caso contrário.
        """
        for root, _, files in os.walk(self.repo_path):
            # Ignorar diretórios ocultos e node_modules, venv, etc.
            if any(part.startswith(".") for part in root.split(os.sep)) or \
               any(part in ["node_modules", "venv", "env", "__pycache__", "dist", "build", "target"] 
                   for part in root.split(os.sep)):
                continue
                
            for file in files:
                # Ignorar arquivos binários e muito grandes
                file_path = os.path.join(root, file)
                if not self._is_text_file(file_path) or os.path.getsize(file_path) > Config.MAX_FILE_SIZE:
                    continue
                    
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        if pattern.lower() in content.lower():
                            return True
                except Exception as e:
                    self.logger.warning(f"Erro ao ler arquivo {file_path}: {str(e)}")
        
        return False
    
    def _read_json_file(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        Lê um arquivo JSON.
        
        Args:
            filename: Nome do arquivo a ser lido.
            
        Returns:
            Conteúdo do arquivo JSON ou None se ocorrer um erro.
        """
        file_path = os.path.join(self.repo_path, filename)
        if not os.path.exists(file_path):
            return None
            
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            self.logger.warning(f"Erro ao ler arquivo JSON {file_path}: {str(e)}")
            return None
    
    def _read_file_content(self, file_path: str) -> Optional[str]:
        """
        Lê o conteúdo de um arquivo.
        
        Args:
            file_path: Caminho do arquivo a ser lido.
            
        Returns:
            Conteúdo do arquivo ou None se ocorrer um erro.
        """
        if not os.path.exists(file_path):
            return None
            
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception as e:
            self.logger.warning(f"Erro ao ler arquivo {file_path}: {str(e)}")
            return None
    
    def _is_text_file(self, file_path: str) -> bool:
        """
        Verifica se um arquivo é de texto.
        
        Args:
            file_path: Caminho do arquivo.
            
        Returns:
            True se o arquivo é de texto, False caso contrário.
        """
        # Verificar extensão
        _, ext = os.path.splitext(file_path)
        text_extensions = [
            ".txt", ".md", ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".c", ".cpp", ".cs", ".go",
            ".rb", ".php", ".swift", ".kt", ".rs", ".scala", ".html", ".css", ".scss", ".sass",
            ".sh", ".bat", ".ps1", ".json", ".xml", ".yaml", ".yml", ".toml", ".sql", ".r",
            ".dart", ".lua", ".ex", ".exs", ".erl", ".fs", ".hs", ".pl", ".groovy", ".clj"
        ]
        if ext.lower() in text_extensions:
            return True
        
        # Verificar conteúdo
        try:
            with open(file_path, "rb") as f:
                chunk = f.read(1024)
                return b"\0" not in chunk  # Arquivos de texto geralmente não contêm bytes nulos
        except Exception:
            return False
    
    def _match_pattern(self, filename: str, pattern: str) -> bool:
        """
        Verifica se um nome de arquivo corresponde a um padrão.
        
        Args:
            filename: Nome do arquivo.
            pattern: Padrão a ser verificado.
            
        Returns:
            True se o nome do arquivo corresponde ao padrão, False caso contrário.
        """
        # Converter padrão para regex
        regex_pattern = pattern.replace(".", "\\.").replace("*", ".*")
        return bool(re.match(f"^{regex_pattern}$", filename))
