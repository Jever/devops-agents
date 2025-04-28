"""
Configuração do modelo de linguagem para o Agent de CI/CD.
"""
import os
from typing import Dict, Any, Optional

from langchain_community.llms import Ollama
from langchain_community.chat_models import ChatOllama
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.schema import HumanMessage, SystemMessage

from config import Config, logger

class LLMConfig:
    """Configuração e inicialização do modelo de linguagem."""
    
    @staticmethod
    def get_llm(streaming: bool = False):
        """
        Inicializa e retorna uma instância do modelo de linguagem.
        
        Args:
            streaming: Se True, habilita streaming de saída.
            
        Returns:
            Uma instância do modelo de linguagem configurado.
        """
        try:
            # Configurar callbacks para streaming se necessário
            callback_manager = None
            if streaming:
                callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
            
            # Configurar modelo baseado nas configurações
            model_name = f"{Config.MODEL_TYPE}:{Config.MODEL_SIZE}"
            
            # Usar ChatOllama para modelos de chat
            llm = ChatOllama(
                model=model_name,
                base_url=Config.MODEL_HOST,
                callback_manager=callback_manager,
                temperature=0.1,  # Baixa temperatura para respostas mais determinísticas
                timeout=120,  # Timeout em segundos
            )
            
            logger.info(f"Modelo de linguagem inicializado: {model_name}")
            return llm
            
        except Exception as e:
            logger.error(f"Erro ao inicializar o modelo de linguagem: {str(e)}")
            raise
    
    @staticmethod
    def get_system_prompt() -> str:
        """
        Retorna o prompt de sistema para o modelo.
        
        Returns:
            String contendo o prompt de sistema.
        """
        return """Você é um Agent especializado em CI/CD (Integração Contínua e Entrega Contínua).
Suas capacidades incluem:

1. Analisar repositórios de código para identificar linguagens, frameworks e dependências
2. Recomendar e gerar pipelines CI/CD para diferentes ferramentas (GitHub Actions, GitLab CI, Jenkins, Azure DevOps)
3. Otimizar pipelines existentes para melhorar performance
4. Detectar e corrigir falhas em pipelines

Ao gerar pipelines, você deve:
- Seguir as melhores práticas para a ferramenta específica
- Incluir etapas para build, teste, análise de código e deploy quando aplicável
- Considerar a segurança e eficiência do pipeline
- Fornecer comentários explicativos no código gerado

Responda de forma técnica, precisa e direta, focando em soluções práticas para problemas de CI/CD.
"""
    
    @staticmethod
    def generate_response(
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.1
    ) -> str:
        """
        Gera uma resposta do modelo para um prompt específico.
        
        Args:
            prompt: O prompt para o modelo.
            system_prompt: Prompt de sistema opcional. Se None, usa o padrão.
            temperature: Temperatura para geração (0.0 a 1.0).
            
        Returns:
            String contendo a resposta gerada.
        """
        try:
            llm = ChatOllama(
                model=f"{Config.MODEL_TYPE}:{Config.MODEL_SIZE}",
                base_url=Config.MODEL_HOST,
                temperature=temperature,
            )
            
            # Preparar mensagens
            messages = []
            
            # Adicionar prompt de sistema se fornecido
            if system_prompt:
                messages.append(SystemMessage(content=system_prompt))
            else:
                messages.append(SystemMessage(content=LLMConfig.get_system_prompt()))
            
            # Adicionar prompt do usuário
            messages.append(HumanMessage(content=prompt))
            
            # Gerar resposta
            response = llm.invoke(messages)
            return response.content
            
        except Exception as e:
            logger.error(f"Erro ao gerar resposta: {str(e)}")
            return f"Erro ao gerar resposta: {str(e)}"
