import os
import streamlit as st
import time
import config
from api import fetch_news, process_articles, check_fact
from ui import inject_css, display_article_card


def main():
    st.set_page_config(
        page_title="📰 News Analyzer",
        page_icon="📰",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.write("App loaded successfully")
    # inject_css()

    if 'articles_cache' not in st.session_state:
        st.session_state.articles_cache = None
    if 'cache_time' not in st.session_state:
        st.session_state.cache_time = None
    if 'force_refresh' not in st.session_state:
        st.session_state.force_refresh = False

    try:
        config.NEWSAPI_KEY = st.secrets["NEWSAPI_KEY"]
        config.GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
    except Exception:
        config.NEWSAPI_KEY = config.NEWSAPI_KEY or os.getenv("NEWSAPI_KEY", "")
        config.GEMINI_KEY = config.GEMINI_KEY or os.getenv("GEMINI_API_KEY", "")

    st.markdown('<h1 class="main-header">📰 NEWS ANALYZER</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Real-time Credibility Scoring | Sentiment Analysis | AI Summaries</p>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📰 News Analyzer", "✓ Fact-Checker"])

    with tab1:
        st.markdown('<div class="search-panel">', unsafe_allow_html=True)

        col1, col2 = st.columns([2, 1])
        with col1:
            search_query = st.text_input(
                "🔍 Search Topic:",
                placeholder="e.g., Tesla, Bitcoin, Artificial Intelligence, Climate Change...",
                value="Technology"
            )
        with col2:
            days_back = st.selectbox("📅 Time range:", [1, 3, 7, 30], index=2)

        col1, col2, col3 = st.columns(3)
        with col1:
            use_gemini = st.checkbox("✨ AI Summaries (Gemini)", value=True, help="Slower but better summaries")
        with col2:
            sort_by = st.selectbox("Sort by:", ["Credibility ↓", "Latest", "Sentiment"], index=0)
        with col3:
            if st.button("🚀 FETCH & ANALYZE", type="primary"):
                st.session_state.force_refresh = True

        st.markdown('</div>', unsafe_allow_html=True)

        if search_query:
            should_fetch = True
            if st.session_state.articles_cache and st.session_state.cache_time:
                time_diff = time.time() - st.session_state.cache_time
                if time_diff < config.CACHE_DURATION_SECONDS:
                    should_fetch = False

            if st.session_state.force_refresh or should_fetch:
                with st.spinner(f"🔄 Fetching news about '{search_query}'..."):
                    articles, error = fetch_news(search_query, days=days_back)
                if error:
                    st.error(error)
                    articles = None
                else:
                    st.session_state.articles_cache = articles
                    st.session_state.cache_time = time.time()
                    st.session_state.force_refresh = False
            else:
                articles = st.session_state.articles_cache

            if articles:
                with st.spinner("⏳ Analyzing articles..."):
                    processed = process_articles(articles, use_gemini=use_gemini)

                if sort_by == "Credibility ↓":
                    processed.sort(key=lambda x: x["credibility"], reverse=True)
                elif sort_by == "Latest":
                    processed.sort(key=lambda x: x["published"], reverse=True)
                elif sort_by == "Sentiment":
                    processed.sort(key=lambda x: x["polarity"], reverse=True)

                stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)
                avg_credibility = sum(a["credibility"] for a in processed) / len(processed)
                positive_count = sum(1 for a in processed if "Positive" in a["sentiment"])
                negative_count = sum(1 for a in processed if "Negative" in a["sentiment"])
                neutral_count = len(processed) - positive_count - negative_count

                with stats_col1:
                    st.metric("📈 Articles Found", len(processed))
                with stats_col2:
                    st.metric("🎯 Avg Credibility", f"{avg_credibility:.0f}%")
                with stats_col3:
                    st.metric("😊 Positive Tone", f"{positive_count}")
                with stats_col4:
                    st.metric("😢 Negative Tone", f"{negative_count}")

                st.subheader("📰 Analyzed Articles")
                for article in processed:
                    display_article_card(article)
        else:
            st.info("👈 Enter a search query to get started!")

    with tab2:
        st.markdown("### Check Any Claim")
        st.markdown("Enter a statement or claim below, and I'll verify it using AI analysis.")

        claim_input = st.text_area(
            "Enter statement to verify:",
            placeholder="e.g., 'The Earth is flat' or 'Climate change is real'",
            height=100,
            key="claim_input"
        )

        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            check_button = st.button("⚡ CHECK FACT", type="primary", use_container_width=True)
        with col2:
            st.write("")
        with col3:
            clear_button = st.button("CLEAR", use_container_width=True)

        if clear_button:
            st.session_state.claim_input = ""
            st.rerun()

        if check_button:
            if not claim_input.strip():
                st.warning("⚠️ Please enter a statement to check.")
            else:
                with st.spinner("🔍 Analyzing claim with AI..."):
                    results, error = check_fact(claim_input)

                if error:
                    st.error(error)
                elif results:
                    for result in results:
                        st.markdown(f"**Claim:** {result['claim']}")
                        rating = result.get("rating", "INCONCLUSIVE").upper()
                        rating_colors = {
                            "TRUE": "🟢",
                            "FALSE": "🔴",
                            "MIXED": "🟡",
                            "INCONCLUSIVE": "⚪"
                        }
                        rating_emoji = rating_colors.get(rating, "⚪")
                        st.markdown(f"**Verdict:** {rating_emoji} **{rating}**", unsafe_allow_html=True)
                        st.markdown(f"**Analysis:** {result.get('explanation', 'No analysis available')}")
                        confidence = result.get('confidence', 'UNKNOWN')
                        st.markdown(f"**Confidence Level:** {confidence}")
                        st.divider()
                else:
                    st.info("Unable to analyze this claim. Please try rephrasing it.")

    st.divider()
    st.markdown(
        """
        <div style='text-align: center; color: gray; font-size: 0.9em;'>
        💡 <b>How This Works:</b> Fetches real news, analyzes credibility based on source & content, 
        generates AI summaries with Gemini, and detects sentiment. Always verify with official sources!

        

        🔐 <b>Privacy:</b> Searches not stored. Real-time processing only.
        </div>
        """,
        unsafe_allow_html=True

    )

if __name__ == "__main__":
    main()
