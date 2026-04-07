import os
import requests
import time
from datetime import datetime, timedelta
from textblob import TextBlob
import config


def fetch_news(query, days=2):
    if not config.NEWSAPI_KEY:
        return None, "❌ NewsAPI key not found! Please set NEWSAPI_KEY environment variable."

    try:
        from_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "from": from_date,
            "sortBy": "publishedAt",
            "language": "en",
            "pageSize": 10,
            "apiKey": config.NEWSAPI_KEY
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("status") == "ok":
            return data["articles"], None
        return None, f"API Error: {data.get('message', 'Unknown error')}"
    except requests.exceptions.RequestException as e:
        return None, f"❌ Network error: {str(e)}"


def check_fact(claim):
    try:
        import google.generativeai as genai
    except ImportError as e:
        return None, f"❌ Google Gemini package not installed: {e}"

    # Use Wikipedia if GEMINI_KEY missing
    if not config.GEMINI_KEY:
        try:
            import wikipedia
            search_results = wikipedia.search(claim, results=1)
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
        except Exception:
            return None, "⚠️ Gemini key missing and Wikipedia fallback failed."

    # Try Gemini
    try:
        genai.configure(api_key=config.GEMINI_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash')
        prompt = f"""You are a fact-checking expert. Analyze this claim.

CLAIM: {claim}

Respond in EXACT format:
RATING: [TRUE/FALSE/MIXED/INCONCLUSIVE]
EXPLANATION: [2-3 sentences]
CONFIDENCE: [HIGH/MEDIUM/LOW]"""
        response = model.generate_content(prompt, stream=False)
        result_text = response.text.strip()

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

    except Exception as gemini_error:
        # Fallback to Wikipedia if quota exceeded
        error_msg = str(gemini_error).lower()
        if "429" in error_msg or "quota" in error_msg:
            try:
                import wikipedia
                search_results = wikipedia.search(claim, results=1)
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
            except Exception:
                return None, "⚠️ Gemini quota exceeded and Wikipedia fallback failed."

        elif "401" in error_msg:
            return None, "⚠️ Gemini API key invalid. Please check .env file."
        else:
            return None, f"❌ Error: {gemini_error}"

def summarize_with_gemini(content, title):
    if not config.GEMINI_KEY:
        return None

    try:
        import google.generativeai as genai
        genai.configure(api_key=config.GEMINI_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""Summarize this news article in 1-2 sentences. Be concise and factual.

Title: {title}

Content: {content[:2000]}

Summary:"""
        response = model.generate_content(prompt, stream=False)
        return response.text.strip()
    except Exception:
        return None


def get_sentiment(text):
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


def process_articles(articles, use_gemini=True):
    processed = []
    progress_bar = None
    status_text = None
    try:
        import streamlit as st
        progress_bar = st.progress(0)
        status_text = st.empty()
    except Exception:
        pass

    for idx, article in enumerate(articles):
        if status_text:
            status_text.text(f"Processing article {idx+1}/{len(articles)}...")

        title = article.get("title", "N/A")
        source = article.get("source", {}).get("name", "Unknown")
        description = article.get("description", "")
        content = article.get("content", "")
        full_content = description + " " + content if description else content
        image = article.get("urlToImage", "")
        url = article.get("url", "")
        published = article.get("publishedAt", "N/A")

        from credibility import get_credibility_score
        credibility, color = get_credibility_score(source, full_content)
        sentiment, polarity = get_sentiment(full_content)

        summary = None
        if use_gemini and config.GEMINI_KEY:
            summary = summarize_with_gemini(full_content, title)
        if not summary:
            summary = description[:200] if description else "No summary available"

        processed.append({
            "title": title,
            "source": source,
            "credibility": credibility,
            "color": color,
            "sentiment": sentiment,
            "polarity": polarity,
            "summary": summary,
            "image": image,
            "url": url,
            "published": published
        })

        if progress_bar:
            progress_bar.progress((idx + 1) / len(articles))

    if progress_bar:
        progress_bar.empty()
    if status_text:
        status_text.empty()

    return processed
