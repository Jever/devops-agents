"""
Módulo de inicialização para o pacote analyzers.
"""
from .repo_analyzer import RepoAnalyzer
from .tech_detector import TechDetector

__all__ = ["RepoAnalyzer", "TechDetector"]
