"""
Analisador de repositório para identificar estrutura, linguagens e tecnologias.
"""
import os
import re
from typing import Dict, List, Any, Optional
import logging
import git
import yaml
import json

from config import Config, logger

class RepoAnalyzer:
    def __init__(self, repo_path: str):
        """Inicializa o analisador de repositório."""
        if not repo_path or not os.path.exists(repo_path):
            raise ValueError("Caminho do repositório inválido ou não fornecido.")
        self.repo_path = repo_path
        self.logger = logging.getLogger("cicd_agent.repo_analyzer")
        self.is_git_repo = os.path.exists(os.path.join(self.repo_path, ".git"))
        if self.is_git_repo:
            try:
                self.repo = git.Repo(self.repo_path)
                self.logger.info(f"Repositório Git encontrado em: {self.repo_path}")
            except git.InvalidGitRepositoryError:
                self.is_git_repo = False
                self.logger.warning(f"Diretório .git encontrado, mas não é um repositório Git válido: {self.repo_path}")
        else:
            self.logger.info(f"Analisando diretório não-Git: {self.repo_path}")
    
    def analyze(self) -> Dict[str, Any]:
        self.logger.info(f"Iniciando análise do repositório: {self.repo_path}")
        
        result = {
            "repo_path": self.repo_path,
            "is_git_repo": self.is_git_repo,
            "languages": self.detect_languages(),
            "frameworks": self.detect_frameworks(),
            "build_tools": self.detect_build_tools(),
            "ci_cd_files": self.find_existing_ci_cd_files(),
            "package_managers": self.detect_package_managers(),
            "has_tests": self.has_tests(),
            "has_docker": self.has_docker(),
            "recommended_ci_tool": None
        }

        result["recommended_ci_tool"] = self._recommend_ci_tool(result)
        
        self.logger.info(f"Análise do repositório concluída: {self.repo_path}")
        return result
    
    def detect_languages(self) -> Dict[str, float]:
        """
        Detecta as linguagens de programação usadas no repositório.
        
        Returns:
            Dicionário com linguagens e suas porcentagens no repositório.
        """
        extensions_count = {}
        total_files = 0
        
        # Extensões comuns e suas linguagens
        ext_to_lang = {
            ".py": "Python",
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".jsx": "JavaScript/React",
            ".tsx": "TypeScript/React",
            ".java": "Java",
            ".c": "C",
            ".cpp": "C++",
            ".cs": "C#",
            ".go": "Go",
            ".rb": "Ruby",
            ".php": "PHP",
            ".swift": "Swift",
            ".kt": "Kotlin",
            ".rs": "Rust",
            ".scala": "Scala",
            ".html": "HTML",
            ".css": "CSS",
            ".scss": "SCSS",
            ".sass": "Sass",
            ".sh": "Shell",
            ".bat": "Batch",
            ".ps1": "PowerShell",
            ".md": "Markdown",
            ".json": "JSON",
            ".xml": "XML",
            ".yaml": "YAML",
            ".yml": "YAML",
            ".toml": "TOML",
            ".sql": "SQL",
            ".r": "R",
            ".dart": "Dart",
            ".lua": "Lua",
            ".ex": "Elixir",
            ".exs": "Elixir",
            ".erl": "Erlang",
            ".fs": "F#",
            ".hs": "Haskell",
            ".pl": "Perl",
            ".groovy": "Groovy",
            ".clj": "Clojure",
        }
        
        # Percorrer todos os arquivos no repositório
        for root, _, files in os.walk(self.repo_path):
            # Ignorar diretórios ocultos e node_modules, venv, etc.
            if any(part.startswith(".") for part in root.split(os.sep)) or \
               any(part in ["node_modules", "venv", "env", "__pycache__", "dist", "build", "target"] 
                   for part in root.split(os.sep)):
                continue
                
            for file in files:
                # Ignorar arquivos ocultos
                if file.startswith("."):
                    continue
                    
                # Obter extensão
                _, ext = os.path.splitext(file)
                if ext in ext_to_lang:
                    lang = ext_to_lang[ext]
                    extensions_count[lang] = extensions_count.get(lang, 0) + 1
                    total_files += 1
        
        # Calcular porcentagens
        languages = {}
        if total_files > 0:
            for lang, count in extensions_count.items():
                languages[lang] = round(count / total_files * 100, 2)
        
        # Ordenar por porcentagem (decrescente)
        languages = dict(sorted(languages.items(), key=lambda x: x[1], reverse=True))
        
        self.logger.info(f"Linguagens detectadas: {languages}")
        return languages
    
    def detect_frameworks(self) -> Dict[str, str]:
        """
        Detecta frameworks utilizados no repositório.
        
        Returns:
            Dicionário com frameworks detectados por linguagem.
        """
        frameworks = {}
        
        # Verificar frameworks Python
        if self._has_file("requirements.txt") or self._has_file("setup.py") or self._has_file("pyproject.toml"):
            if self._has_file_content_match("django"):
                frameworks["Python"] = "Django"
            elif self._has_file_content_match("flask"):
                frameworks["Python"] = "Flask"
            elif self._has_file_content_match("fastapi"):
                frameworks["Python"] = "FastAPI"
            elif self._has_file_content_match("tornado"):
                frameworks["Python"] = "Tornado"
            elif self._has_file_content_match("pyramid"):
                frameworks["Python"] = "Pyramid"
        
        # Verificar frameworks JavaScript/TypeScript
        if self._has_file("package.json"):
            package_json = self._read_json_file("package.json")
            if package_json:
                dependencies = {**package_json.get("dependencies", {}), **package_json.get("devDependencies", {})}
                
                if "react" in dependencies:
                    if "next" in dependencies:
                        frameworks["JavaScript"] = "Next.js"
                    else:
                        frameworks["JavaScript"] = "React"
                elif "vue" in dependencies:
                    if "nuxt" in dependencies:
                        frameworks["JavaScript"] = "Nuxt.js"
                    else:
                        frameworks["JavaScript"] = "Vue.js"
                elif "angular" in dependencies or "@angular/core" in dependencies:
                    frameworks["JavaScript"] = "Angular"
                elif "svelte" in dependencies:
                    frameworks["JavaScript"] = "Svelte"
                elif "express" in dependencies:
                    frameworks["JavaScript"] = "Express"
                elif "koa" in dependencies:
                    frameworks["JavaScript"] = "Koa"
                elif "nest" in dependencies or "@nestjs/core" in dependencies:
                    frameworks["JavaScript"] = "NestJS"
        
        # Verificar frameworks Java
        if self._has_file("pom.xml"):
            if self._has_file_content_match("springframework"):
                frameworks["Java"] = "Spring"
            elif self._has_file_content_match("quarkus"):
                frameworks["Java"] = "Quarkus"
            elif self._has_file_content_match("micronaut"):
                frameworks["Java"] = "Micronaut"
        elif self._has_file("build.gradle") or self._has_file("build.gradle.kts"):
            if self._has_file_content_match("springframework"):
                frameworks["Java"] = "Spring"
            elif self._has_file_content_match("quarkus"):
                frameworks["Java"] = "Quarkus"
            elif self._has_file_content_match("micronaut"):
                frameworks["Java"] = "Micronaut"
        
        # Verificar frameworks .NET
        if self._has_file_with_extension(".csproj") or self._has_file_with_extension(".sln"):
            if self._has_file_content_match("Microsoft.AspNetCore"):
                frameworks["C#"] = "ASP.NET Core"
            elif self._has_file_content_match("Microsoft.AspNet"):
                frameworks["C#"] = "ASP.NET"
        
        # Verificar frameworks Go
        if self._has_file("go.mod") or self._has_file_with_extension(".go"):
            if self._has_file_content_match("github.com/gin-gonic/gin"):
                frameworks["Go"] = "Gin"
            elif self._has_file_content_match("github.com/gorilla/mux"):
                frameworks["Go"] = "Gorilla"
            elif self._has_file_content_match("github.com/labstack/echo"):
                frameworks["Go"] = "Echo"
        
        self.logger.info(f"Frameworks detectados: {frameworks}")
        return frameworks
    
    def detect_build_tools(self) -> List[str]:
        """
        Detecta ferramentas de build utilizadas no repositório.
        
        Returns:
            Lista de ferramentas de build detectadas.
        """
        build_tools = []
        
        # Maven (Java)
        if self._has_file("pom.xml"):
            build_tools.append("Maven")
        
        # Gradle (Java)
        if self._has_file("build.gradle") or self._has_file("build.gradle.kts"):
            build_tools.append("Gradle")
        
        # npm/Yarn (JavaScript/TypeScript)
        if self._has_file("package.json"):
            if self._has_file("yarn.lock"):
                build_tools.append("Yarn")
            else:
                build_tools.append("npm")
        
        # pip/Poetry (Python)
        if self._has_file("requirements.txt"):
            build_tools.append("pip")
        if self._has_file("pyproject.toml"):
            if self._has_file_content_match("poetry"):
                build_tools.append("Poetry")
            elif self._has_file_content_match("flit"):
                build_tools.append("Flit")
        
        # Make
        if self._has_file("Makefile"):
            build_tools.append("Make")
        
        # CMake
        if self._has_file("CMakeLists.txt"):
            build_tools.append("CMake")
        
        # Bazel
        if self._has_file("WORKSPACE") or self._has_file("BUILD"):
            build_tools.append("Bazel")
        
        # Cargo (Rust)
        if self._has_file("Cargo.toml"):
            build_tools.append("Cargo")
        
        # Go
        if self._has_file("go.mod"):
            build_tools.append("Go Modules")
        
        # .NET
        if self._has_file_with_extension(".csproj") or self._has_file_with_extension(".sln"):
            build_tools.append("MSBuild/.NET CLI")
        
        self.logger.info(f"Ferramentas de build detectadas: {build_tools}")
        return build_tools
    
    def find_existing_ci_cd_files(self) -> Dict[str, List[str]]:
        """
        Encontra arquivos de CI/CD existentes no repositório.
        
        Returns:
            Dicionário com ferramentas de CI/CD e seus arquivos.
        """
        ci_cd_files = {
            "github_actions": [],
            "gitlab_ci": [],
            "jenkins": [],
            "azure_devops": [],
            "travis": [],
            "circle_ci": [],
            "other": []
        }
        
        # GitHub Actions
        github_workflows_dir = os.path.join(self.repo_path, ".github", "workflows")
        if os.path.exists(github_workflows_dir) and os.path.isdir(github_workflows_dir):
            for file in os.listdir(github_workflows_dir):
                if file.endswith((".yml", ".yaml")):
                    ci_cd_files["github_actions"].append(os.path.join(".github", "workflows", file))
        
        # GitLab CI
        gitlab_ci_file = os.path.join(self.repo_path, ".gitlab-ci.yml")
        if os.path.exists(gitlab_ci_file):
            ci_cd_files["gitlab_ci"].append(".gitlab-ci.yml")
        
        # Jenkins
        jenkins_files = ["Jenkinsfile", "jenkins.yml", "jenkins.yaml", "jenkins.json", "jenkins.xml"]
        for file in jenkins_files:
            if os.path.exists(os.path.join(self.repo_path, file)):
                ci_cd_files["jenkins"].append(file)
        
        # Azure DevOps
        azure_pipelines_file = os.path.join(self.repo_path, "azure-pipelines.yml")
        if os.path.exists(azure_pipelines_file):
            ci_cd_files["azure_devops"].append("azure-pipelines.yml")
        
        # Travis CI
        travis_file = os.path.join(self.repo_path, ".travis.yml")
        if os.path.exists(travis_file):
            ci_cd_files["travis"].append(".travis.yml")
        
        # Circle CI
        circle_ci_file = os.path.join(self.repo_path, ".circleci", "config.yml")
        if os.path.exists(circle_ci_file):
            ci_cd_files["circle_ci"].append(os.path.join(".circleci", "config.yml"))
        
        # Outros arquivos de CI/CD
        other_ci_files = ["bitbucket-pipelines.yml", "cloudbuild.yaml", "cloudbuild.yml", "buildspec.yml", "appveyor.yml"]
        for file in other_ci_files:
            if os.path.exists(os.path.join(self.repo_path, file)):
                ci_cd_files["other"].append(file)
        
        # Remover ferramentas sem arquivos
        ci_cd_files = {k: v for k, v in ci_cd_files.items() if v}
        
        self.logger.info(f"Arquivos de CI/CD encontrados: {ci_cd_files}")
        return ci_cd_files
    
    def detect_package_managers(self) -> List[str]:
        """
        Detecta gerenciadores de pacotes utilizados no repositório.
        
        Returns:
            Lista de gerenciadores de pacotes detectados.
        """
        package_managers = []
        
        # npm/Yarn (JavaScript/TypeScript)
        if self._has_file("package.json"):
            if self._has_file("yarn.lock"):
                package_managers.append("Yarn")
            elif self._has_file("package-lock.json"):
                package_managers.append("npm")
            else:
                package_managers.append("npm")
        
        # pip/Poetry/Pipenv (Python)
        if self._has_file("requirements.txt"):
            package_managers.append("pip")
        if self._has_file("Pipfile") or self._has_file("Pipfile.lock"):
            package_managers.append("Pipenv")
        if self._has_file("pyproject.toml"):
            if self._has_file_content_match("poetry"):
                package_managers.append("Poetry")
        
        # Maven/Gradle (Java)
        if self._has_file("pom.xml"):
            package_managers.append("Maven")
        if self._has_file("build.gradle") or self._has_file("build.gradle.kts"):
            package_managers.append("Gradle")
        
        # NuGet (.NET)
        if self._has_file_with_extension(".csproj") or self._has_file("packages.config"):
            package_managers.append("NuGet")
        
        # Cargo (Rust)
        if self._has_file("Cargo.toml"):
            package_managers.append("Cargo")
        
        # Go Modules
        if self._has_file("go.mod"):
            package_managers.append("Go Modules")
        
        # Composer (PHP)
        if self._has_file("composer.json"):
            package_managers.append("Composer")
        
        # Bundler (Ruby)
        if self._has_file("Gemfile"):
            package_managers.append("Bundler")
        
        # CocoaPods (Swift/Objective-C)
        if self._has_file("Podfile"):
            package_managers.append("CocoaPods")
        
        self.logger.info(f"Gerenciadores de pacotes detectados: {package_managers}")
        return package_managers
    
    def has_tests(self) -> bool:
        """
        Verifica se o repositório contém testes.
        
        Returns:
            True se o repositório contém testes, False caso contrário.
        """
        test_dirs = ["test", "tests", "spec", "specs", "__tests__", "Testing", "unittest"]
        test_files_patterns = ["test_*.py", "*_test.py", "*Test.java", "*Tests.java", "*.test.js", "*.spec.js", "*_test.go"]
        
        # Verificar diretórios de teste
        for test_dir in test_dirs:
            if os.path.exists(os.path.join(self.repo_path, test_dir)) and os.path.isdir(os.path.join(self.repo_path, test_dir)):
                return True
        
        # Verificar arquivos de teste
        for root, _, files in os.walk(self.repo_path):
            # Ignorar diretórios ocultos e node_modules, venv, etc.
            if any(part.startswith(".") for part in root.split(os.sep)) or \
               any(part in ["node_modules", "venv", "env", "__pycache__", "dist", "build", "target"] 
                   for part in root.split(os.sep)):
                continue
                
            for file in files:
                for pattern in test_files_patterns:
                    if self._match_pattern(file, pattern):
                        return True
        
        # Verificar configurações de teste em package.json
        if self._has_file("package.json"):
            package_json = self._read_json_file("package.json")
            if package_json and "scripts" in package_json and any("test" in script for script in package_json["scripts"]):
                return True
        
        return False
    
    def has_docker(self) -> bool:
        """
        Verifica se o repositório contém arquivos Docker.
        
        Returns:
            True se o repositório contém arquivos Docker, False caso contrário.
        """
        docker_files = ["Dockerfile", "docker-compose.yml", "docker-compose.yaml"]
        
        for file in docker_files:
            if os.path.exists(os.path.join(self.repo_path, file)):
                return True
        
        # Verificar diretório .docker
        if os.path.exists(os.path.join(self.repo_path, ".docker")) and os.path.isdir(os.path.join(self.repo_path, ".docker")):
            return True
        
        return False
    
    def _recommend_ci_tool(self, analysis: Dict[str, Any]) -> str:
        """
        Recomenda uma ferramenta de CI/CD com base na análise do repositório.
        
        Args:
            analysis: Resultado da análise do repositório.
            
        Returns:
            Nome da ferramenta de CI/CD recomendada.
        """
        # Se já existir uma ferramenta de CI/CD, recomendá-la
        existing_ci_cd = analysis.get("ci_cd_files", {})
        if existing_ci_cd:
            # Retornar a primeira ferramenta encontrada
            return next(iter(existing_ci_cd.keys()))
        
        # Se for um repositório GitHub, recomendar GitHub Actions
        if self.is_git_repo:
            try:
                remote_url = self.repo.remotes.origin.url
                if "github.com" in remote_url:
                    return "github_actions"
                elif "gitlab" in remote_url:
                    return "gitlab_ci"
                elif "dev.azure.com" in remote_url or "visualstudio.com" in remote_url:
                    return "azure_devops"
            except (git.GitError, AttributeError):
                pass
        
        # Recomendar com base nas linguagens e frameworks
        languages = analysis.get("languages", {})
        if not languages:
            return "github_actions"  # Padrão se não houver linguagens detectadas
        
        primary_language = next(iter(languages))
        
        # Recomendações específicas por linguagem
        if primary_language in ["Java", "Kotlin"]:
            return "jenkins"
        elif primary_language in ["C#", "F#"]:
            return "azure_devops"
        elif primary_language in ["Python", "JavaScript", "TypeScript", "Go", "Ruby"]:
            return "github_actions"
        else:
            return "github_actions"  # Padrão para outras linguagens
    
    def _has_file(self, filename: str) -> bool:
        """
        Verifica se um arquivo existe no repositório.
        
        Args:
            filename: Nome do arquivo a ser verificado.
            
        Returns:
            True se o arquivo existe, False caso contrário.
        """
        return os.path.exists(os.path.join(self.repo_path, filename))
    
    def _has_file_with_extension(self, extension: str) -> bool:
        """
        Verifica se existe algum arquivo com a extensão especificada.
        
        Args:
            extension: Extensão a ser verificada.
            
        Returns:
            True se existe algum arquivo com a extensão, False caso contrário.
        """
        for root, _, files in os.walk(self.repo_path):
            # Ignorar diretórios ocultos e node_modules, venv, etc.
            if any(part.startswith(".") for part in root.split(os.sep)) or \
               any(part in ["node_modules", "venv", "env", "__pycache__", "dist", "build", "target"] 
                   for part in root.split(os.sep)):
                continue
                
            for file in files:
                if file.endswith(extension):
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
