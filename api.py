import os
import requests
import time
from datetime import datetime, timedelta
from textblob import TextBlob
from config import Config
from credibility import CredibilityAnalyzer


class NewsAPIClient:
    """Client for fetching news from NewsAPI"""
    
    def __init__(self, config=None):
        self.config = config or Config()
        self.base_url = "https://newsapi.org/v2/everything"
    
    def fetch_news(self, query, days=2):
        """Fetch news articles from NewsAPI"""
        if not self.config.is_newsapi_configured():
            return None, "❌ NewsAPI key not found! Please set NEWSAPI_KEY environment variable."
        
        try:
            from_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            params = {
                "q": query,
                "from": from_date,
                "sortBy": "publishedAt",
                "language": "en",
                "pageSize": 10,
                "apiKey": self.config.NEWSAPI_KEY
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "ok":
                return data["articles"], None
            return None, f"API Error: {data.get('message', 'Unknown error')}"
        except requests.exceptions.RequestException as e:
            return None, f"❌ Network error: {str(e)}"


class GeminiSummarizer:
    """AI-powered article summarizer using Gemini"""
    
    def __init__(self, config=None):
        self.config = config or Config()
    
    def summarize(self, content, title):
        """Summarize article content using Gemini"""
        if not self.config.is_gemini_configured():
            return None
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.config.GEMINI_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"""Summarize this news article in 1-2 sentences. Be concise and factual.

Title: {title}

Content: {content[:2000]}

Summary:"""
            
            response = model.generate_content(prompt, stream=False)
            return response.text.strip()
        except Exception:
            return None


class SentimentAnalyzer:
    """Analyzes sentiment of text using TextBlob"""
    
    def analyze(self, text):
        """Analyze sentiment and return label and polarity"""
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            
            if polarity > 0.1:
                return "Positive 😊", polarity
            elif polarity < -0.1:
                return "Negative 😢", polarity
            else:
                return "Neutral 😐", polarity
        except Exception:
            return "Neutral 😐", 0


class FactChecker:
    """Fact-checking using Gemini AI with Wikipedia fallback"""
    
    def __init__(self, config=None):
        self.config = config or Config()
    
    def check_fact(self, claim):
        """Check a claim using Gemini or Wikipedia fallback"""
        try:
            import google.generativeai as genai
        except ImportError:
            genai = None
        
        try:
            import wikipedia
        except ImportError:
            return None, "❌ Wikipedia library not installed. Run: pip install wikipedia"
        
        # Try Gemini first if available
        if genai and self.config.is_gemini_configured():
            result = self._check_with_gemini(claim, genai)
            if result:
                return result
        
        # Fallback to Wikipedia
        return self._check_with_wikipedia(claim)
    
    def _check_with_gemini(self, claim, genai):
        """Internal: Check fact using Gemini"""
        try:
            genai.configure(api_key=self.config.GEMINI_KEY)
            model = genai.GenerativeModel('gemini-2.0-flash')
            
            prompt = f"""You are a fact-checking expert. Analyze this claim.

CLAIM: {claim}

Respond in EXACT format:
RATING: [TRUE/FALSE/MIXED/INCONCLUSIVE]
EXPLANATION: [2-3 sentences]
CONFIDENCE: [HIGH/MEDIUM/LOW]"""
            
            response = model.generate_content(prompt, stream=False)
            result_text = response.text.strip()
            
            return self._parse_gemini_response(claim, result_text)
        except Exception:
            return None
    
    def _parse_gemini_response(self, claim, result_text):
        """Internal: Parse Gemini response into structured result"""
        lines = result_text.split('\n')
        result = {
            "claim": claim,
            "rating": "INCONCLUSIVE",
            "explanation": result_text,
            "confidence": "UNKNOWN",
            "source": "Gemini AI"
        }
        
        for line in lines:
            if line.startswith("RATING:"):
                result["rating"] = line.replace("RATING:", "").strip()
            elif line.startswith("EXPLANATION:"):
                result["explanation"] = line.replace("EXPLANATION:", "").strip()
            elif line.startswith("CONFIDENCE:"):
                result["confidence"] = line.replace("CONFIDENCE:", "").strip()
        
        return [result], None
    
    def _check_with_wikipedia(self, claim):
        """Internal: Check fact using Wikipedia"""
        try:
            import wikipedia
            search_results = wikipedia.search(claim, results=3)
            if search_results:
                page = wikipedia.page(search_results[0])
                summary = page.summary[:300]
                return [{
                    "claim": claim,
                    "rating": "WIKIPEDIA_MATCH",
                    "explanation": f"Wikipedia: {summary}...",
                    "confidence": "MEDIUM",
                    "source": f"Wikipedia: {page.title}"
                }], None
        except Exception as e:
            return None, f"Wikipedia error: {str(e)}"
        
        return [{
            "claim": claim,
            "rating": "UNVERIFIED",
            "explanation": "Could not verify this claim via Gemini or Wikipedia.",
            "confidence": "LOW",
            "source": "None"
        }], None


class ArticleProcessor:
    """Processes and analyzes news articles"""
    
    def __init__(self, config=None):
        self.config = config or Config()
        self.credibility_analyzer = CredibilityAnalyzer()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.summarizer = GeminiSummarizer(self.config)
    
    def process_articles(self, articles, use_gemini=True, progress_callback=None):
        """Process a list of articles"""
        processed = []
        
        for idx, article in enumerate(articles):
            if progress_callback:
                progress_callback(idx + 1, len(articles))
            
            processed_article = self._process_single_article(article, use_gemini)
            processed.append(processed_article)
        
        return processed
    
    def _process_single_article(self, article, use_gemini):
        """Process a single article"""
        title = article.get("title", "N/A")
        source = article.get("source", {}).get("name", "Unknown")
        description = article.get("description", "")
        content = article.get("content", "")
        full_content = description + " " + content if description else content
        
        credibility, color = self.credibility_analyzer.calculate_score(source, full_content)
        sentiment, polarity = self.sentiment_analyzer.analyze(full_content)
        
        # Get summary
        summary = None
        if use_gemini and self.config.is_gemini_configured():
            summary = self.summarizer.summarize(full_content, title)
        if not summary:
            summary = description[:200] if description else "No summary available"
        
        return {
            "title": title,
            "source": source,
            "credibility": credibility,
            "color": color,
            "sentiment": sentiment,
            "polarity": polarity,
            "summary": summary,
            "image": article.get("urlToImage", ""),
            "url": article.get("url", ""),
            "published": article.get("publishedAt", "N/A")
        }


# For backward compatibility - keep old function signatures
def fetch_news(query, days=2):
    client = NewsAPIClient()
    return client.fetch_news(query, days)


def check_fact(claim):
    checker = FactChecker()
    return checker.check_fact(claim)


def summarize_with_gemini(content, title):
    summarizer = GeminiSummarizer()
    return summarizer.summarize(content, title)


def get_sentiment(text):
    analyzer = SentimentAnalyzer()
    return analyzer.analyze(text)


def process_articles(articles, use_gemini=True):
    processor = ArticleProcessor()
    return processor.process_articles(articles, use_gemini)
