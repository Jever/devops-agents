"""
Classe principal do agent de IaC.
"""
import os
import logging
import argparse
from typing import Dict, Any, List, Optional

from config import Config, logger
from models import LLMConfig
from analyzers import InfrastructureAnalyzer
from generators import (
    TerraformGenerator,
    CloudFormationGenerator,
    AnsibleGenerator,
    KubernetesGenerator
)
from optimizers import IaCOptimizer
from validators import IaCValidator
from utils import FileUtils

class IaCAgent:
    """
    Agent para Infraestrutura como Código (IaC).
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Inicializa o agent de IaC.
        
        Args:
            config_path: Caminho para o arquivo de configuração.
        """
        # Configurar logger
        self.logger = logging.getLogger("iac_agent")
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        
        # Carregar configurações
        if config_path and os.path.exists(config_path):
            Config.load_config(config_path)
        
        # Inicializar componentes
        self.llm_config = LLMConfig()
        self.analyzer = InfrastructureAnalyzer()
        self.terraform_generator = TerraformGenerator(self.llm_config)
        self.cloudformation_generator = CloudFormationGenerator(self.llm_config)
        self.ansible_generator = AnsibleGenerator(self.llm_config)
        self.kubernetes_generator = KubernetesGenerator(self.llm_config)
        self.optimizer = IaCOptimizer(self.llm_config)
        self.validator = IaCValidator(self.llm_config)
    
    def analyze(self, infra_path: str) -> Dict[str, Any]:
        """
        Analisa a infraestrutura em um diretório.
        
        Args:
            infra_path: Caminho para o diretório contendo a infraestrutura.
            
        Returns:
            Resultado da análise.
        """
        self.logger.info(f"Analisando infraestrutura em: {infra_path}")
        return self.analyzer.analyze(infra_path)
    
    def generate(self, infra_analysis: Dict[str, Any], output_dir: str, iac_type: str) -> Dict[str, str]:
        """
        Gera código de infraestrutura com base na análise.
        
        Args:
            infra_analysis: Resultado da análise de infraestrutura.
            output_dir: Diretório de saída para os arquivos gerados.
            iac_type: Tipo de IaC (terraform, cloudformation, ansible, kubernetes).
            
        Returns:
            Dicionário com nomes de arquivos e conteúdos gerados.
        """
        self.logger.info(f"Gerando código {iac_type} em: {output_dir}")
        
        if iac_type.lower() == "terraform":
            return self.terraform_generator.generate(infra_analysis, output_dir)
        elif iac_type.lower() == "cloudformation":
            return self.cloudformation_generator.generate(infra_analysis, output_dir)
        elif iac_type.lower() == "ansible":
            return self.ansible_generator.generate(infra_analysis, output_dir)
        elif iac_type.lower() == "kubernetes":
            return self.kubernetes_generator.generate(infra_analysis, output_dir)
        else:
            self.logger.error(f"Tipo de IaC não suportado: {iac_type}")
            return {}
    
    def optimize(self, directory: str, iac_type: str) -> Dict[str, Any]:
        """
        Otimiza código de infraestrutura.
        
        Args:
            directory: Diretório contendo os arquivos a serem otimizados.
            iac_type: Tipo de IaC (terraform, cloudformation, ansible, kubernetes).
            
        Returns:
            Resultado da otimização.
        """
        self.logger.info(f"Otimizando código {iac_type} em: {directory}")
        
        result = {
            "optimized_files": 0,
            "total_files": 0,
            "details": []
        }
        
        # Determinar extensões de arquivo com base no tipo de IaC
        extensions = []
        if iac_type.lower() == "terraform":
            extensions = [".tf", ".tfvars"]
        elif iac_type.lower() == "cloudformation":
            extensions = [".yaml", ".yml", ".json"]
        elif iac_type.lower() == "ansible":
            extensions = [".yaml", ".yml"]
        elif iac_type.lower() == "kubernetes":
            extensions = [".yaml", ".yml"]
        else:
            self.logger.error(f"Tipo de IaC não suportado: {iac_type}")
            return result
        
        # Listar arquivos
        files = FileUtils.list_files(directory, extensions)
        result["total_files"] = len(files)
        
        # Otimizar cada arquivo
        for file_path in files:
            content = FileUtils.read_file(file_path)
            if not content:
                continue
            
            success, optimized_content = self.optimizer.optimize(file_path, content, iac_type)
            if success:
                FileUtils.write_file(file_path, optimized_content)
                result["optimized_files"] += 1
                result["details"].append({
                    "file": file_path,
                    "status": "optimized"
                })
            else:
                result["details"].append({
                    "file": file_path,
                    "status": "no_changes"
                })
        
        return result
    
    def validate(self, directory: str, iac_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Valida código de infraestrutura.
        
        Args:
            directory: Diretório contendo os arquivos a serem validados.
            iac_type: Tipo de IaC (terraform, cloudformation, ansible, kubernetes).
                      Se None, o tipo será determinado automaticamente para cada arquivo.
            
        Returns:
            Resultado da validação.
        """
        self.logger.info(f"Validando código em: {directory}")
        
        result = {
            "valid_files": 0,
            "invalid_files": 0,
            "total_files": 0,
            "details": []
        }
        
        # Determinar extensões de arquivo
        extensions = [".tf", ".tfvars", ".yaml", ".yml", ".json"]
        
        # Listar arquivos
        files = FileUtils.list_files(directory, extensions)
        result["total_files"] = len(files)
        
        # Validar cada arquivo
        for file_path in files:
            content = FileUtils.read_file(file_path)
            if not content:
                continue
            
            # Determinar tipo de IaC
            file_iac_type = iac_type
            if not file_iac_type:
                file_iac_type = FileUtils.get_file_type(file_path)
            
            if not file_iac_type:
                result["details"].append({
                    "file": file_path,
                    "status": "skipped",
                    "message": "Tipo de IaC não determinado"
                })
                continue
            
            is_valid, issues = self.validator.validate(file_path, content, file_iac_type)
            
            if is_valid:
                result["valid_files"] += 1
                result["details"].append({
                    "file": file_path,
                    "status": "valid",
                    "issues": issues
                })
            else:
                result["invalid_files"] += 1
                result["details"].append({
                    "file": file_path,
                    "status": "invalid",
                    "issues": issues
                })
        
        return result
    
    def convert(self, infra_path: str, output_dir: str, source_type: str, target_type: str) -> Dict[str, Any]:
        """
        Converte código de infraestrutura de um tipo para outro.
        
        Args:
            infra_path: Caminho para o diretório contendo a infraestrutura.
            output_dir: Diretório de saída para os arquivos gerados.
            source_type: Tipo de IaC de origem (terraform, cloudformation, ansible, kubernetes).
            target_type: Tipo de IaC de destino (terraform, cloudformation, ansible, kubernetes).
            
        Returns:
            Resultado da conversão.
        """
        self.logger.info(f"Convertendo código de {source_type} para {target_type}")
        
        # Analisar infraestrutura
        infra_analysis = self.analyze(infra_path)
        
        # Gerar código no formato de destino
        generated_files = self.generate(infra_analysis, output_dir, target_type)
        
        return {
            "source_type": source_type,
            "target_type": target_type,
            "analysis": infra_analysis,
            "generated_files": len(generated_files),
            "output_dir": output_dir
        }

def main():
    """
    Função principal para execução via linha de comando.
    """
    parser = argparse.ArgumentParser(description='Agent para Infraestrutura como Código (IaC)')
    parser.add_argument('--config', help='Caminho para o arquivo de configuração')
    
    subparsers = parser.add_subparsers(dest='command', help='Comando a ser executado')
    
    # Comando analyze
    analyze_parser = subparsers.add_parser('analyze', help='Analisar infraestrutura')
    analyze_parser.add_argument('path', help='Caminho para o diretório contendo a infraestrutura')
    analyze_parser.add_argument('--output', help='Caminho para o arquivo de saída (JSON)')
    
    # Comando generate
    generate_parser = subparsers.add_parser('generate', help='Gerar código de infraestrutura')
    generate_parser.add_argument('path', help='Caminho para o diretório contendo a infraestrutura')
    generate_parser.add_argument('--output', required=True, help='Diretório de saída para os arquivos gerados')
    generate_parser.add_argument('--type', required=True, choices=['terraform', 'cloudformation', 'ansible', 'kubernetes'], help='Tipo de IaC a ser gerado')
    
    # Comando optimize
    optimize_parser = subparsers.add_parser('optimize', help='Otimizar código de infraestrutura')
    optimize_parser.add_argument('path', help='Caminho para o diretório contendo os arquivos a serem otimizados')
    optimize_parser.add_argument('--type', required=True, choices=['terraform', 'cloudformation', 'ansible', 'kubernetes'], help='Tipo de IaC a ser otimizado')
    
    # Comando validate
    validate_parser = subparsers.add_parser('validate', help='Validar código de infraestrutura')
    validate_parser.add_argument('path', help='Caminho para o diretório contendo os arquivos a serem validados')
    validate_parser.add_argument('--type', choices=['terraform', 'cloudformation', 'ansible', 'kubernetes'], help='Tipo de IaC a ser validado')
    
    # Comando convert
    convert_parser = subparsers.add_parser('convert', help='Converter código de infraestrutura')
    convert_parser.add_argument('path', help='Caminho para o diretório contendo a infraestrutura')
    convert_parser.add_argument('--output', required=True, help='Diretório de saída para os arquivos gerados')
    convert_parser.add_argument('--source', required=True, choices=['terraform', 'cloudformation', 'ansible', 'kubernetes'], help='Tipo de IaC de origem')
    convert_parser.add_argument('--target', required=True, choices=['terraform', 'cloudformation', 'ansible', 'kubernetes'], help='Tipo de IaC de destino')
    
    args = parser.parse_args()
    
    # Inicializar agent
    agent = IaCAgent(args.config)
    
    # Executar comando
    if args.command == 'analyze':
        result = agent.analyze(args.path)
        if args.output:
            import json
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
        else:
            import json
            print(json.dumps(result, indent=2))
    
    elif args.command == 'generate':
        # Analisar infraestrutura
        infra_analysis = agent.analyze(args.path)
        
        # Gerar código
        agent.generate(infra_analysis, args.output, args.type)
        print(f"Código gerado em: {args.output}")
    
    elif args.command == 'optimize':
        result = agent.optimize(args.path, args.type)
        print(f"Arquivos otimizados: {result['optimized_files']}/{result['total_files']}")
    
    elif args.command == 'validate':
        result = agent.validate(args.path, args.type)
        print(f"Arquivos válidos: {result['valid_files']}/{result['total_files']}")
        print(f"Arquivos inválidos: {result['invalid_files']}/{result['total_files']}")
    
    elif args.command == 'convert':
        result = agent.convert(args.path, args.output, args.source, args.target)
        print(f"Código convertido de {args.source} para {args.target}")
        print(f"Arquivos gerados: {result['generated_files']}")
        print(f"Diretório de saída: {result['output_dir']}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
