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
            return (
                None,
                "NewsAPI key not found! Please set NEWSAPI_KEY environment variable.",
            )

        try:
            from_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            params = {
                "q": query,
                "from": from_date,
                "sortBy": "publishedAt",
                "language": "en",
                "pageSize": 10,
                "apiKey": self.config.NEWSAPI_KEY,
            }

            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("status") == "ok":
                return data["articles"], None
            return None, f"API Error: {data.get('message', 'Unknown error')}"
        except requests.exceptions.RequestException as e:
            return None, f"Network error: {str(e)}"
        except Exception as e:
            return None, f"Error: {str(e)}"

    def _normalize_rating(self, textual_rating):
        """Normalize textual rating to our format"""
        rating_lower = textual_rating.lower()
        if "true" in rating_lower and "false" not in rating_lower:
            return "TRUE"
        elif "false" in rating_lower:
            return "FALSE"
        elif "mixed" in rating_lower or "partly" in rating_lower:
            return "MIXED"
        else:
            return "INCONCLUSIVE"

    def _create_inconclusive_result(self, claim, explanation):
        """Create a default inconclusive result"""
        return {
            "claim": claim,
            "rating": "INCONCLUSIVE",
            "explanation": explanation,
            "confidence": "LOW",
            "source": "Google Fact Check Tools",
        }


class GeminiSummarizer:
    """AI-powered article summarizer using Gemini"""

    def __init__(self, config=None):
        self.config = config or Config()

    def summarize(self, content, title):
        """Summarize article content using Gemini"""
        if not self.config.is_gemini_configured():
            return None

        try:
            import google.genai as genai

            genai.configure(api_key=self.config.GEMINI_KEY)
            model = genai.GenerativeModel("gemini-1.5-flash")

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
                return "Positive", polarity
            elif polarity < -0.1:
                return "Negative", polarity
            else:
                return "Neutral", polarity
        except Exception:
            return "Neutral", 0


class FactChecker:
    """Fact-checking using Google Fact Check Tools API"""

    def __init__(self, config=None):
        self.config = config or Config()

    def check_fact(self, claim):
        """Check a claim using Google Fact Check Tools API"""
        if not self.config.is_fact_check_configured():
            return (
                None,
                "⚠️ Google Fact Check API key not configured. Please set FACT_CHECK_API_KEY in .env",
            )

        return self._check_with_google_fact_check(claim)

    def _check_with_google_fact_check(self, claim):
        """Internal: Check fact using Google Fact Check Tools API with Gemini fallback"""
        try:
            url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
            params = {
                "query": claim,
                "key": self.config.FACT_CHECK_KEY,
                "languageCode": "en",
            }

            response = requests.get(url, params=params, timeout=10)
            
            # Handle quota exceeded (429) by falling back to Gemini
            if response.status_code == 429:
                return self._check_with_gemini_fallback(claim)
            
            response.raise_for_status()
            data = response.json()

            if "claims" in data and data["claims"]:
                # Take the first claim
                claim_data = data["claims"][0]
                claim_reviews = claim_data.get("claimReview", [])

                if claim_reviews:
                    review = claim_reviews[0]
                    textual_rating = review.get("textualRating", "Inconclusive")
                    title = review.get("title", "")
                    publisher = review.get("publisher", {}).get("name", "Unknown")
                    url = review.get("url", "")

                    # Normalize rating
                    rating = self._normalize_rating(textual_rating)

                    explanation = f"{title} (Source: {publisher})"
                    if url:
                        explanation += f" - {url}"

                    confidence = "HIGH"  # Since it's from fact-checkers

                    result = {
                        "claim": claim,
                        "rating": rating,
                        "explanation": explanation,
                        "confidence": confidence,
                        "source": "Google Fact Check Tools",
                    }
                    return [result], None
                else:
                    # No reviews found - use Gemini as fallback
                    return self._check_with_gemini_fallback(claim)
            else:
                # No fact-checks found - use Gemini as fallback
                return self._check_with_gemini_fallback(claim)

        except requests.exceptions.RequestException as e:
            # If Google API fails, fall back to Gemini
            return self._check_with_gemini_fallback(claim)
        except Exception as e:
            # If anything goes wrong, fall back to Gemini
            return self._check_with_gemini_fallback(claim)

    def _check_with_gemini_fallback(self, claim):
        """Fallback: Check fact using Gemini AI when Google Fact Check API has no results"""
        if not self.config.is_gemini_configured():
            return [
                self._create_inconclusive_result(
                    claim, "No fact-checks found. Gemini AI not configured as fallback."
                )
            ], None

        try:
            import google.generativeai as genai

            genai.configure(api_key=self.config.GEMINI_KEY)
            model = genai.GenerativeModel("gemini-2.0-flash")

            prompt = f"""You are a fact-checking expert. Analyze this claim BRIEFLY.

CLAIM: {claim}

Respond EXACTLY in this format:
RATING: [TRUE/FALSE/MIXED/INCONCLUSIVE]
EXPLANATION: [1-2 sentences only]
CONFIDENCE: [HIGH/MEDIUM/LOW]"""

            response = model.generate_content(prompt, stream=False)
            result_text = response.text.strip()

            lines = result_text.split("\n")
            result = {
                "claim": claim,
                "rating": "INCONCLUSIVE",
                "explanation": result_text,
                "confidence": "MEDIUM",
                "source": "AI Analysis (Gemini Fallback)",
            }

            for line in lines:
                if line.startswith("RATING:"):
                    result["rating"] = line.replace("RATING:", "").strip()
                elif line.startswith("EXPLANATION:"):
                    result["explanation"] = line.replace("EXPLANATION:", "").strip()
                elif line.startswith("CONFIDENCE:"):
                    result["confidence"] = line.replace("CONFIDENCE:", "").strip()

            return [result], None

        except Exception as e:
            return [
                self._create_inconclusive_result(
                    claim, f"Could not verify claim: {str(e)[:50]}"
                )
            ], None

    def _normalize_rating(self, textual_rating):
        """Normalize textual rating to our format"""
        rating_lower = textual_rating.lower()
        if "true" in rating_lower and "false" not in rating_lower:
            return "TRUE"
        elif "false" in rating_lower:
            return "FALSE"
        elif "mixed" in rating_lower or "partly" in rating_lower:
            return "MIXED"
        else:
            return "INCONCLUSIVE"

    def _create_inconclusive_result(self, claim, explanation):
        """Create a default inconclusive result"""
        return {
            "claim": claim,
            "rating": "INCONCLUSIVE",
            "explanation": explanation,
            "confidence": "LOW",
            "source": "Google Fact Check Tools",
        }


class ArticleProcessor:
    """Processes and analyzes news articles"""

    def __init__(self, config=None):
        self.config = config or Config()
        # Initialize analyzers when needed to avoid circular imports

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

        # Initialize analyzers
        credibility_analyzer = CredibilityAnalyzer()
        sentiment_analyzer = SentimentAnalyzer()
        summarizer = GeminiSummarizer(self.config)

        credibility, color = credibility_analyzer.calculate_score(source, full_content)
        sentiment, polarity = sentiment_analyzer.analyze(full_content)

        # Get summary
        summary = None
        if use_gemini and self.config.is_gemini_configured():
            summary = summarizer.summarize(full_content, title)
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
            "published": article.get("publishedAt", "N/A"),
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
