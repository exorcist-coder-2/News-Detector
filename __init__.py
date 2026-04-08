"""
News Detector - AI-Powered News Credibility Analyzer

A modular news analysis system with:
- Real-time credibility scoring
- Sentiment analysis
- AI-powered summarization
- Fact-checking capabilities
"""

from .app import NewsAnalyzerApp
from .config import Config, SourceTiers
from .api import (
    NewsAPIClient,
    GeminiSummarizer,
    SentimentAnalyzer,
    FactChecker,
    ArticleProcessor
)
from .credibility import CredibilityAnalyzer
from .ui import UITheme, ArticleCard, StatsPanel, SearchPanel, FactCheckPanel

__version__ = "2.0.0"
__author__ = "News Detector Team"

__all__ = [
    # Main app
    "NewsAnalyzerApp",
    # Config
    "Config",
    "SourceTiers",
    # API clients
    "NewsAPIClient",
    "GeminiSummarizer",
    "SentimentAnalyzer",
    "FactChecker",
    "ArticleProcessor",
    # Analysis
    "CredibilityAnalyzer",
    # UI
    "UITheme",
    "ArticleCard",
    "StatsPanel",
    "SearchPanel",
    "FactCheckPanel",
]
