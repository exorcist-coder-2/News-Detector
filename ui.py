import streamlit as st


class UITheme:
    """Manages UI theme and CSS styling"""
    
    DARK_THEME = """
    <style>
    body { 
        background-color: #1e1e1e !important;
        color: #e8ecf1;
    }
    .main {
        background-color: #1e1e1e;
    }
    .stApp {
        background-color: #1e1e1e;
    }
    .main-header { 
        font-size: 1.6em !important; 
        color: #ffffff !important; 
        margin-bottom: -8px !important;
        margin-top: -16px !important;
        padding: 0 !important;
        font-weight: 900 !important;
        letter-spacing: 1px;
        text-shadow: 0 2px 12px rgba(88, 020, 8, 0);
    }
    .subtitle {
        font-size: 0.7em;
        color: #d5dadf;
        margin-bottom: 4px;
        margin-top: -12px;
        padding: 0;
        letter-spacing: 0.5px;
        font-weight: 500;
    }
    .stTextInput input {
        background-color: #2c2f33 !important;
        color: #ffffff !important;
        border: 1px solid #202225 !important;
        border-radius: 6px !important;
        padding: 6px 10px !important;
        font-size: 12px !important;
        transition: all 0.2s ease !important;
        height: 28px !important;
        font-weight: 500 !important;
    }
    .stTextInput input:focus {
        background-color: #2c2f33 !important;
        border-color: #5865f2 !important;
        box-shadow: 0 0 8px rgba(88, 101, 242, 0.4) !important;
    }
    .stTextInput input::placeholder {
        color: #a0a8b0 !important;
    }
    .stSelectbox [role="button"] {
        background-color: #2c2f33 !important;
        color: #ffffff !important;
        border: 1px solid #202225 !important;
        border-radius: 6px !important;
        padding: 6px 10px !important;
        font-size: 12px !important;
        min-height: 28px !important;
        font-weight: 500 !important;
    }
    .stButton > button {
        background-color: #5865f2 !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 6px 14px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
        font-size: 12px !important;
        height: 28px !important;
    }
    .stButton > button:hover {
        background-color: #4752c4 !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(88, 101, 242, 0.5) !important;
    }
    .card { 
        background: linear-gradient(135deg, #2c2f33 0%, #23262a 100%);
        padding: 12px; 
        border-radius: 8px; 
        border-left: 3px solid #5865f2;
        border: 1px solid #202225;
        margin: 4px 0;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
        transition: all 0.2s ease;
    }
    .card:hover {
        border-color: #5865f2;
        box-shadow: 0 6px 20px rgba(88, 101, 242, 0.2);
    }
    .credibility-badge {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85em;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
    }
    .stMetric {
        background-color: #2c2f33 !important;
        border: 1px solid #202225 !important;
        border-radius: 6px !important;
        padding: 8px 10px !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.15) !important;
        margin: 2px 0 !important;
    }
    </style>
    """
    
    @classmethod
    def inject(cls):
        """Inject CSS into Streamlit"""
        st.markdown(cls.DARK_THEME, unsafe_allow_html=True)


class ArticleCard:
    """Renders an article card in Streamlit"""
    
    def __init__(self, article):
        self.article = article
    
    def render(self):
        """Render the article card"""
        cred = self.article["credibility"]
        color = self.article["color"]
        
        html = f"""
        <div class="card" style="border-left-color: {color};">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 15px;">
                <h3 style="margin: 0; color: #ffffff; font-weight: 700;">{self.article['title']}</h3>
                <span class="credibility-badge" style="background-color: {color}; color: white;">
                    {cred}% CREDIBLE
                </span>
            </div>
            <p style="color: #c8cdd3; margin: 5px 0; font-size: 0.9em; font-weight: 500;">
                📰 <strong>{self.article['source']}</strong> | 📅 {self.article['published'][:10]} | {self.article['sentiment']}
            </p>
            <p style="color: #e1e8ed; line-height: 1.6; margin: 10px 0;">
                {self.article['summary']}
            </p>
            <a href="{self.article['url']}" target="_blank" style="
                display: inline-block;
                padding: 8px 16px;
                background-color: {color};
                color: white;
                text-decoration: none;
                border-radius: 5px;
                font-weight: bold;
                margin-top: 10px;
            ">→ Read Full Article</a>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)


class StatsPanel:
    """Renders statistics panel"""
    
    def __init__(self, articles):
        self.articles = articles
    
    def render(self):
        """Render statistics"""
        if not self.articles:
            return
        
        avg_credibility = sum(a["credibility"] for a in self.articles) / len(self.articles)
        positive_count = sum(1 for a in self.articles if "Positive" in a["sentiment"])
        negative_count = sum(1 for a in self.articles if "Negative" in a["sentiment"])
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📈 Articles Found", len(self.articles))
        with col2:
            st.metric("🎯 Avg Credibility", f"{avg_credibility:.0f}%")
        with col3:
            st.metric("😊 Positive Tone", f"{positive_count}")
        with col4:
            st.metric("😢 Negative Tone", f"{negative_count}")


class SearchPanel:
    """Renders search panel UI"""
    
    def __init__(self):
        self.query = None
        self.days_back = None
        self.use_gemini = None
        self.sort_by = None
        self.fetch_clicked = False
    
    def render(self):
        """Render search panel and return user inputs"""
        st.markdown('<div class="search-panel">', unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        with col1:
            self.query = st.text_input(
                "🔍 Search Topic:",
                placeholder="e.g., Tesla, Bitcoin, Artificial Intelligence...",
                value="Technology"
            )
        with col2:
            self.days_back = st.selectbox("📅 Time range:", [1, 3, 7, 30], index=2)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            self.use_gemini = st.checkbox("✨ AI Summaries (Gemini)", value=True)
        with col2:
            self.sort_by = st.selectbox("Sort by:", ["Credibility ↓", "Latest", "Sentiment"], index=0)
        with col3:
            self.fetch_clicked = st.button("🚀 FETCH & ANALYZE", type="primary")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        return {
            "query": self.query,
            "days_back": self.days_back,
            "use_gemini": self.use_gemini,
            "sort_by": self.sort_by,
            "fetch_clicked": self.fetch_clicked
        }


class FactCheckPanel:
    """Renders fact-checking panel"""
    
    def __init__(self):
        self.claim = None
        self.check_clicked = False
        self.clear_clicked = False
    
    def render(self):
        """Render fact-check panel and return inputs"""
        st.markdown("### Check Any Claim")
        st.markdown("Enter a statement or claim below, and I'll verify it using AI analysis.")
        
        self.claim = st.text_area(
            "Enter statement to verify:",
            placeholder="e.g., 'The Earth is flat' or 'Climate change is real'",
            height=100,
            key="claim_input"
        )
        
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            self.check_clicked = st.button("⚡ CHECK FACT", type="primary", use_container_width=True)
        with col3:
            self.clear_clicked = st.button("CLEAR", use_container_width=True)
        
        return {
            "claim": self.claim,
            "check_clicked": self.check_clicked,
            "clear_clicked": self.clear_clicked
        }
    
    def display_result(self, result):
        """Display a fact-check result"""
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
        st.markdown(f"**Confidence Level:** {result.get('confidence', 'UNKNOWN')}")
        st.divider()


# For backward compatibility
def inject_css():
    UITheme.inject()


def display_article_card(article):
    card = ArticleCard(article)
    card.render()
