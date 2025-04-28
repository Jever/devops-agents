import os
import logging
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações do agent
class Config:
    # Configurações gerais
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Configurações do modelo
    MODEL_TYPE = os.getenv("MODEL_TYPE", "llama3")  # llama3, mistral, etc.
    MODEL_SIZE = os.getenv("MODEL_SIZE", "8b")      # 8b, 70b, etc.
    MODEL_HOST = os.getenv("MODEL_HOST", "http://localhost:11434")  # Para Ollama
    
    # Configurações de análise
    #REPO_PATH = os.getenv("REPO_PATH")
    REPO_PATH = None
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "1000000"))  # 1MB
    
    # Configurações de geração
    TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")
    
    # Configurações de ferramentas CI/CD suportadas
    SUPPORTED_TOOLS = ["github_actions", "gitlab_ci", "jenkins", "azure_devops"]
    
    # Configurações de logging
    @staticmethod
    def setup_logging():
        logging.basicConfig(
            level=getattr(logging, Config.LOG_LEVEL),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler("cicd_agent.log")
            ]
        )
        
        # Reduzir verbosidade de bibliotecas de terceiros
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("langchain").setLevel(logging.WARNING)
        
        return logging.getLogger("cicd_agent")

# Inicializar logger
logger = Config.setup_logging()
