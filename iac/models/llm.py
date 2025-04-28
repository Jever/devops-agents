"""
Configuração do modelo de linguagem para o agent de IaC.
"""
import os
import logging
import requests
from typing import Dict, Any, List, Optional

from config import Config, logger

class LLMConfig:
    """
    Classe para configuração e interação com o modelo de linguagem.
    """
    
    def __init__(self):
        """
        Inicializa a configuração do modelo de linguagem.
        """
        self.logger = logging.getLogger("iac_agent.llm")
        self.provider = Config.LLM_PROVIDER
        self.model = Config.LLM_MODEL
        self.api_key = Config.LLM_API_KEY
        self.api_base = Config.LLM_API_BASE
    
    def generate_text(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.2) -> Optional[str]:
        """
        Gera texto usando o modelo de linguagem.
        
        Args:
            prompt: Texto de entrada para o modelo.
            max_tokens: Número máximo de tokens a serem gerados.
            temperature: Temperatura para geração de texto (0.0 a 1.0).
            
        Returns:
            Texto gerado ou None se ocorrer um erro.
        """
        try:
            if self.provider == "ollama":
                return self._generate_text_ollama(prompt, max_tokens, temperature)
            elif self.provider == "openai":
                return self._generate_text_openai(prompt, max_tokens, temperature)
            elif self.provider == "azure":
                return self._generate_text_azure(prompt, max_tokens, temperature)
            else:
                self.logger.error(f"Provedor de LLM não suportado: {self.provider}")
                return None
        except Exception as e:
            self.logger.error(f"Erro ao gerar texto: {str(e)}")
            return None
    
    def _generate_text_ollama(self, prompt: str, max_tokens: int, temperature: float) -> Optional[str]:
        """
        Gera texto usando o Ollama.
        
        Args:
            prompt: Texto de entrada para o modelo.
            max_tokens: Número máximo de tokens a serem gerados.
            temperature: Temperatura para geração de texto (0.0 a 1.0).
            
        Returns:
            Texto gerado ou None se ocorrer um erro.
        """
        try:
            url = f"{self.api_base}/generate"
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": temperature
                }
            }
            
            response = requests.post(url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            return result.get("response")
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar texto com Ollama: {str(e)}")
            return None
    
    def _generate_text_openai(self, prompt: str, max_tokens: int, temperature: float) -> Optional[str]:
        """
        Gera texto usando a API da OpenAI.
        
        Args:
            prompt: Texto de entrada para o modelo.
            max_tokens: Número máximo de tokens a serem gerados.
            temperature: Temperatura para geração de texto (0.0 a 1.0).
            
        Returns:
            Texto gerado ou None se ocorrer um erro.
        """
        try:
            import openai
            
            openai.api_key = self.api_key
            if self.api_base:
                openai.api_base = self.api_base
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar texto com OpenAI: {str(e)}")
            return None
    
    def _generate_text_azure(self, prompt: str, max_tokens: int, temperature: float) -> Optional[str]:
        """
        Gera texto usando a API da Azure OpenAI.
        
        Args:
            prompt: Texto de entrada para o modelo.
            max_tokens: Número máximo de tokens a serem gerados.
            temperature: Temperatura para geração de texto (0.0 a 1.0).
            
        Returns:
            Texto gerado ou None se ocorrer um erro.
        """
        try:
            import openai
            
            openai.api_type = "azure"
            openai.api_key = self.api_key
            openai.api_base = self.api_base
            openai.api_version = "2023-05-15"
            
            response = openai.ChatCompletion.create(
                engine=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar texto com Azure OpenAI: {str(e)}")
            return None
