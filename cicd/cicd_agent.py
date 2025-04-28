"""
Classe principal do Agent de CI/CD.
"""
import os
import logging
import argparse
from typing import Dict, Any, List, Optional, Tuple

from config import Config, logger
from models import LLMConfig
from analyzers import RepoAnalyzer, TechDetector
from generators import (
    GitHubActionsGenerator,
    GitLabCIGenerator,
    JenkinsGenerator,
    AzureDevOpsGenerator
)
from optimizers import PipelineOptimizer
from detectors import FailureDetector
from utils import (
    load_yaml_file, save_yaml_file, load_json_file, save_json_file,
    read_file, write_file, ensure_directory, list_files, get_pipeline_type
)

class CICDAgent:
    def __init__(self, repo_path: str):
        self.logger = logging.getLogger("cicd_agent")  
        if not repo_path or not os.path.exists(repo_path):
            raise ValueError("Caminho do repositório inválido ou não fornecido.")
        self.repo_path = repo_path
        self.repo_analyzer = RepoAnalyzer(self.repo_path)
        self.tech_detector = TechDetector(self.repo_path)
        self.generators = {
            "github_actions": GitHubActionsGenerator(),
            "gitlab_ci": GitLabCIGenerator(),
            "jenkins": JenkinsGenerator(),
            "azure_devops": AzureDevOpsGenerator()
        }
        self.optimizer = PipelineOptimizer()
        self.failure_detector = FailureDetector()
    
    def analyze_repository(self, repo_path: str) -> Dict[str, Any]:
        """Analisa um repositório para identificar tecnologias e estrutura.
        Args:
            repo_path: Caminho para o repositório.
        Returns:
            Resultado da análise.
        """
        self.logger.info(f"Analisando repositório: {repo_path}")
        
        # Criar diretório .cicd_agent
        cicd_dir = os.path.join(repo_path, ".cicd_agent")
        os.makedirs(cicd_dir, exist_ok=True)
        
        # Analisar estrutura do repositório
        repo_analysis = self.repo_analyzer.analyze()  # Removido o argumento repo_path
        
        # Detectar tecnologias
        tech_data = self.tech_detector.detect_technologies()
        
        # Adicionar dados de tecnologia à análise
        repo_analysis["tech_data"] = tech_data
        
        # Salvar análise em arquivo
        analysis_path = os.path.join(cicd_dir, "repo_analysis.json")
        save_json_file(analysis_path, repo_analysis)
        
        return repo_analysis
        
    def generate_pipeline(self, repo_path: str, platform: str, output_dir: Optional[str] = None) -> Dict[str, str]:
        self.logger.info(f"Gerando pipeline do tipo {platform} para {repo_path}")
        
        # Verificar se o tipo de pipeline é suportado
        if platform not in self.generators:
            self.logger.error(f"Tipo de pipeline não suportado: {platform}")
            return {}
        
        # Carregar análise existente ou analisar repositório
        analysis_path = os.path.join(repo_path, ".cicd_agent", "repo_analysis.json")
        if os.path.exists(analysis_path):
            repo_analysis = load_json_file(analysis_path)
            if not repo_analysis:
                repo_analysis = self.analyze_repository(repo_path)
        else:
            repo_analysis = self.analyze_repository(repo_path)
        
        # Gerar pipeline
        generator = self.generators[platform]
        pipelines = generator.generate_pipeline(repo_analysis)
        
        # Salvar pipelines gerados
        if output_dir:
            target_dir = output_dir
        else:
            target_dir = os.path.join(repo_path, ".cicd_agent", "generated", platform)
        
        ensure_directory(target_dir)
        
        for file_name, content in pipelines.items():
            file_path = os.path.join(target_dir, file_name)
            write_file(file_path, content)
        
        return pipelines
    
    def optimize_pipeline(self, pipeline_path: str, repo_path: Optional[str] = None) -> Optional[str]:
        """
        Otimiza um pipeline CI/CD existente.
        
        Args:
            pipeline_path: Caminho para o arquivo de pipeline.
            repo_path: Caminho para o repositório.
            
        Returns:
            Conteúdo otimizado do pipeline ou None se não for possível otimizar.
        """
        self.logger.info(f"Otimizando pipeline: {pipeline_path}")
        
        # Determinar o tipo de pipeline
        pipeline_type = get_pipeline_type(pipeline_path)
        if not pipeline_type:
            self.logger.error(f"Não foi possível determinar o tipo de pipeline: {pipeline_path}")
            return None
        
        # Ler conteúdo do pipeline
        pipeline_content = read_file(pipeline_path)
        if not pipeline_content:
            return None
        
        # Carregar análise existente ou analisar repositório
        if repo_path:
            analysis_path = os.path.join(repo_path, ".cicd_agent", "repo_analysis.json")
            if os.path.exists(analysis_path):
                repo_analysis = load_json_file(analysis_path)
                if not repo_analysis:
                    repo_analysis = self.analyze_repository(repo_path)
            else:
                repo_analysis = self.analyze_repository(repo_path)
        else:
            # Usar o diretório do pipeline como repositório
            repo_path = os.path.dirname(pipeline_path)
            analysis_path = os.path.join(repo_path, ".cicd_agent", "repo_analysis.json")
            if os.path.exists(analysis_path):
                repo_analysis = load_json_file(analysis_path)
                if not repo_analysis:
                    repo_analysis = self.analyze_repository(repo_path)
            else:
                repo_analysis = self.analyze_repository(repo_path)
        
        # Otimizar pipeline
        optimized_content = self.optimizer.optimize_pipeline(pipeline_content, pipeline_type, repo_analysis)
        
        # Salvar pipeline otimizado
        if optimized_content:
            optimized_path = os.path.join(os.path.dirname(pipeline_path), f"{os.path.basename(pipeline_path)}.optimized")
            write_file(optimized_path, optimized_content)
        
        return optimized_content
    
    def detect_failures(self, pipeline_path: str, error_logs_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Detecta falhas em um pipeline CI/CD.
        
        Args:
            pipeline_path: Caminho para o arquivo de pipeline.
            error_logs_path: Caminho para o arquivo de logs de erro.
            
        Returns:
            Dicionário com falhas detectadas e sugestões de correção.
        """
        self.logger.info(f"Detectando falhas em pipeline: {pipeline_path}")
        
        # Determinar o tipo de pipeline
        pipeline_type = get_pipeline_type(pipeline_path)
        if not pipeline_type:
            self.logger.error(f"Não foi possível determinar o tipo de pipeline: {pipeline_path}")
            return {"status": "error", "message": f"Não foi possível determinar o tipo de pipeline: {pipeline_path}"}
        
        # Ler conteúdo do pipeline
        pipeline_content = read_file(pipeline_path)
        if not pipeline_content:
            return {"status": "error", "message": f"Não foi possível ler o arquivo de pipeline: {pipeline_path}"}
        
        # Ler logs de erro, se fornecidos
        error_logs = None
        if error_logs_path:
            error_logs = read_file(error_logs_path)
        
        # Detectar falhas
        failures = self.failure_detector.detect_failures(pipeline_content, pipeline_type, error_logs)
        
        # Salvar relatório de falhas
        failures_path = os.path.join(os.path.dirname(pipeline_path), f"{os.path.basename(pipeline_path)}.failures.json")
        save_json_file(failures_path, failures)
        
        return failures
    
    def fix_failures(self, pipeline_path: str, failures_path: Optional[str] = None) -> Optional[str]:
        """
        Corrige falhas detectadas em um pipeline CI/CD.
        
        Args:
            pipeline_path: Caminho para o arquivo de pipeline.
            failures_path: Caminho para o arquivo de falhas detectadas.
            
        Returns:
            Conteúdo corrigido do pipeline ou None se não for possível corrigir.
        """
        self.logger.info(f"Corrigindo falhas em pipeline: {pipeline_path}")
        
        # Determinar o tipo de pipeline
        pipeline_type = get_pipeline_type(pipeline_path)
        if not pipeline_type:
            self.logger.error(f"Não foi possível determinar o tipo de pipeline: {pipeline_path}")
            return None
        
        # Ler conteúdo do pipeline
        pipeline_content = read_file(pipeline_path)
        if not pipeline_content:
            return None
        
        # Carregar falhas detectadas
        failures = None
        if failures_path:
            failures = load_json_file(failures_path)
        
        if not failures:
            # Detectar falhas
            failures = self.failure_detector.detect_failures(pipeline_content, pipeline_type)
        
        # Corrigir falhas
        fixed_content = self.failure_detector.fix_failures(pipeline_content, pipeline_type, failures)
        
        # Salvar pipeline corrigido
        if fixed_content:
            fixed_path = os.path.join(os.path.dirname(pipeline_path), f"{os.path.basename(pipeline_path)}.fixed")
            write_file(fixed_path, fixed_content)
        
        return fixed_content
    
    def run_cli(self, args):
        """Executa o agent de CI/CD via linha de comando."""
        # Executar comando
        if args.command == "analyze":
            result = self.analyze_repository(args.repo_path)
            print(f"Análise concluída. Resultado salvo em {os.path.join(args.repo_path, '.cicd_agent', 'repo_analysis.json')}")
        elif args.command == "generate":
            output_dir = args.output_path or os.path.join(args.repo_path, ".cicd_agent", "generated", args.platform)
            pipelines = self.generate_pipeline(args.repo_path, args.platform, output_dir)
            if pipelines:
                print(f"Pipelines gerados com sucesso em {output_dir}:")
                for file_name in pipelines.keys():
                    print(f" - {file_name}")
            else:
                print("Falha ao gerar pipelines.")
        elif args.command == "optimize":
            optimized_content = self.optimize_pipeline(args.pipeline_path, args.repo_path)
            if optimized_content:
                optimized_path = os.path.join(os.path.dirname(args.pipeline_path), f"{os.path.basename(args.pipeline_path)}.optimized")
                write_file(optimized_path, optimized_content)
                print(f"Pipeline otimizado com sucesso. Resultado salvo em {optimized_path}")
            else:
                print("Falha ao otimizar pipeline.")
        elif args.command == "detect":
            failures = self.detect_failures(args.pipeline_path, args.logs)
            failures_path = os.path.join(os.path.dirname(args.pipeline_path), "failures.json")
            save_json_file(failures_path, failures)
            print(f"Falhas detectadas. Resultado salvo em {failures_path}")
        elif args.command == "fix":
            fixed_content = self.fix_failures(args.pipeline_path, args.failures)
            if fixed_content:
                fixed_path = os.path.join(os.path.dirname(args.pipeline_path), f"{os.path.basename(args.pipeline_path)}.fixed")
                write_file(fixed_path, fixed_content)
                print(f"Pipeline corrigido com sucesso. Resultado salvo em {fixed_path}")
            else:
                print("Falha ao corrigir pipeline.")

def main():
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Configurar parser de argumentos
    parser = argparse.ArgumentParser(description="Agent de CI/CD para criação e manutenção de pipelines")
    subparsers = parser.add_subparsers(dest="command", help="Comando a ser executado")

    # Comando analyze
    analyze_parser = subparsers.add_parser("analyze", help="Analisar repositório")
    analyze_parser.add_argument("--repo-path", dest="repo_path", required=True, help="Caminho para o repositório")

    # Comando generate
    generate_parser = subparsers.add_parser("generate", help="Gerar pipeline CI/CD")
    generate_parser.add_argument("--repo-path", dest="repo_path", required=True, help="Caminho para o repositório")
    generate_parser.add_argument("--platform", choices=["github_actions", "gitlab_ci", "jenkins", "azure_devops"], required=True, help="Tipo de pipeline")
    generate_parser.add_argument("--output-path", dest="output_path", help="Diretório de saída para os arquivos gerados")

    # Comando optimize
    optimize_parser = subparsers.add_parser("optimize", help="Otimizar pipeline CI/CD existente")
    optimize_parser.add_argument("pipeline_path", help="Caminho para o arquivo de pipeline")
    optimize_parser.add_argument("--repo-path", help="Caminho para o repositório")

    # Comando detect
    detect_parser = subparsers.add_parser("detect", help="Detectar falhas em pipeline CI/CD")
    detect_parser.add_argument("pipeline_path", help="Caminho para o arquivo de pipeline")
    detect_parser.add_argument("--logs", help="Caminho para o arquivo de logs de erro")

    # Comando fix
    fix_parser = subparsers.add_parser("fix", help="Corrigir falhas em pipeline CI/CD")
    fix_parser.add_argument("pipeline_path", help="Caminho para o arquivo de pipeline")
    fix_parser.add_argument("--failures", help="Caminho para o arquivo de falhas detectadas")

    # Analisar argumentos
    args = parser.parse_args()

    # Verificar se o comando foi fornecido
    if not args.command:
        parser.print_help()
        return

    # Inicializar e executar agent
    agent = CICDAgent(repo_path=getattr(args, "repo_path", None))
    agent.run_cli(args)

if __name__ == "__main__":
    main()
