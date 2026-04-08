import os
import streamlit as st
import time
from config import Config
from api import NewsAPIClient, ArticleProcessor, FactChecker
from ui import UITheme, ArticleCard, StatsPanel, SearchPanel, FactCheckPanel


class NewsAnalyzerApp:
    """Main News Analyzer Application"""
    
    def __init__(self):
        """Initialize the application"""
        self.config = self._load_config()
        self.news_client = NewsAPIClient(self.config)
        self.article_processor = ArticleProcessor(self.config)
        self.fact_checker = FactChecker(self.config)
        self._init_session_state()
    
    def _load_config(self):
        """Load configuration from environment or Streamlit secrets"""
        config = Config()
        
        # Try to load from Streamlit secrets first
        try:
            config = Config.from_streamlit_secrets(st.secrets)
        except Exception:
            # Fall back to environment variables
            config.NEWSAPI_KEY = config.NEWSAPI_KEY or os.getenv("NEWSAPI_KEY", "")
            config.GEMINI_KEY = config.GEMINI_KEY or os.getenv("GEMINI_API_KEY", "")
        
        return config
    
    def _init_session_state(self):
        """Initialize Streamlit session state"""
        if 'articles_cache' not in st.session_state:
            st.session_state.articles_cache = None
        if 'cache_time' not in st.session_state:
            st.session_state.cache_time = None
        if 'force_refresh' not in st.session_state:
            st.session_state.force_refresh = False
    
    def setup_page(self):
        """Configure Streamlit page settings"""
        st.set_page_config(
            page_title="📰 News Analyzer",
            page_icon="📰",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        UITheme.inject()
    
    def render_header(self):
        """Render application header"""
        st.markdown('<h1 class="main-header">📰 NEWS ANALYZER</h1>', unsafe_allow_html=True)
        st.markdown('<p class="subtitle">Real-time Credibility Scoring | Sentiment Analysis | AI Summaries</p>', unsafe_allow_html=True)
    
    def run_news_analyzer_tab(self):
        """Run the News Analyzer tab"""
        search_panel = SearchPanel()
        inputs = search_panel.render()
        
        if not inputs["query"]:
            st.info("👈 Enter a search query to get started!")
            return
        
        # Check cache
        should_fetch = self._should_fetch(inputs["query"])
        
        if inputs["fetch_clicked"]:
            st.session_state.force_refresh = True
        
        if st.session_state.force_refresh or should_fetch:
            articles = self._fetch_and_cache(inputs["query"], inputs["days_back"])
        else:
            articles = st.session_state.articles_cache
        
        if articles:
            self._display_articles(articles, inputs["sort_by"], inputs["use_gemini"])
    
    def _should_fetch(self, query):
        """Determine if we should fetch new data"""
        if not st.session_state.articles_cache or not st.session_state.cache_time:
            return True
        
        time_diff = time.time() - st.session_state.cache_time
        return time_diff >= self.config.CACHE_DURATION_SECONDS
    
    def _fetch_and_cache(self, query, days):
        """Fetch news and cache results"""
        with st.spinner(f"🔄 Fetching news about '{query}'..."):
            articles, error = self.news_client.fetch_news(query, days=days)
        
        if error:
            st.error(error)
            return None
        
        st.session_state.articles_cache = articles
        st.session_state.cache_time = time.time()
        st.session_state.force_refresh = False
        
        return articles
    
    def _display_articles(self, articles, sort_by, use_gemini):
        """Process and display articles"""
        with st.spinner("⏳ Analyzing articles..."):
            # Progress callback for Streamlit
            def progress_callback(current, total):
                st.progress(current / total)
            
            processed = self.article_processor.process_articles(
                articles, 
                use_gemini=use_gemini,
                progress_callback=progress_callback
            )
        
        # Sort articles
        processed = self._sort_articles(processed, sort_by)
        
        # Display stats
        stats_panel = StatsPanel(processed)
        stats_panel.render()
        
        # Display articles
        st.subheader("📰 Analyzed Articles")
        for article in processed:
            card = ArticleCard(article)
            card.render()
    
    def _sort_articles(self, articles, sort_by):
        """Sort articles based on criteria"""
        if sort_by == "Credibility ↓":
            articles.sort(key=lambda x: x["credibility"], reverse=True)
        elif sort_by == "Latest":
            articles.sort(key=lambda x: x["published"], reverse=True)
        elif sort_by == "Sentiment":
            articles.sort(key=lambda x: x["polarity"], reverse=True)
        return articles
    
    def run_fact_checker_tab(self):
        """Run the Fact Checker tab"""
        panel = FactCheckPanel()
        inputs = panel.render()
        
        if inputs["clear_clicked"]:
            st.session_state.claim_input = ""
            st.rerun()
        
        if inputs["check_clicked"]:
            if not inputs["claim"].strip():
                st.warning("⚠️ Please enter a statement to check.")
            else:
                self._perform_fact_check(inputs["claim"], panel)
    
    def _perform_fact_check(self, claim, panel):
        """Perform fact-checking"""
        with st.spinner("🔍 Analyzing claim with AI..."):
            results, error = self.fact_checker.check_fact(claim)
        
        if error:
            st.error(error)
        elif results:
            for result in results:
                panel.display_result(result)
        else:
            st.info("Unable to analyze this claim. Please try rephrasing it.")
    
    def render_footer(self):
        """Render application footer"""
        st.divider()
        st.markdown(
            """
            <div style='text-align: center; color: gray; font-size: 0.9em;'>
            💡 <b>How This Works:</b> Fetches real news, analyzes credibility based on source & content, 
            generates AI summaries with Gemini, and detects sentiment. Always verify with official sources!
            <br><br>
            🔐 <b>Privacy:</b> Searches not stored. Real-time processing only.
            </div>
            """,
            unsafe_allow_html=True
        )
    
    def run(self):
        """Main application entry point"""
        self.setup_page()
        self.render_header()
        
        tab1, tab2 = st.tabs(["📰 News Analyzer", "✓ Fact-Checker"])
        
        with tab1:
            self.run_news_analyzer_tab()
        
        with tab2:
            self.run_fact_checker_tab()
        
        self.render_footer()


def main():
    """Entry point"""
    app = NewsAnalyzerApp()
    app.run()


if __name__ == "__main__":
    main()
