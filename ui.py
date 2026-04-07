import streamlit as st

CSS = """
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
    .stSelectbox [role="listbox"] {
        background-color: #36393f !important;
        border: 1px solid #202225 !important;
        border-radius: 8px !important;
    }
    .stSelectbox [role="option"] {
        color: #ffffff !important;
        background-color: #2c2f33 !important;
        font-weight: 500;
    }
    .stSelectbox [role="option"]:hover {
        background-color: #5865f2 !important;
        color: white !important;
    }
    .stCheckbox {
        padding: 8px 12px;
        background-color: #2c2f33;
        border-radius: 6px;
        border: 1px solid #202225;
        transition: all 0.2s ease;
    }
    .stCheckbox label {
        color: #e1e8ed !important;
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
    .stButton > button:active {
        transform: translateY(0);
    }
    .search-panel {
        background: linear-gradient(135deg, #2c2f33 0%, #23262a 100%);
        border: 1px solid #202225;
        border-radius: 8px;
        padding: 8px 10px;
        margin: 0;
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.2);
    }
    .stats-panel {
        background-color: transparent;
        border: none;
        border-radius: 0;
        padding: 0;
        margin: 0;
        box-shadow: none;
    }
    .stMetric {
        background-color: #2c2f33 !important;
        border: 1px solid #202225 !important;
        border-radius: 6px !important;
        padding: 8px 10px !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.15) !important;
        margin: 2px 0 !important;
    }
    .stMetric [data-testid="metricDelta"] {
        color: #5865f2 !important;
    }
    .stMetric label {
        color: #c8cdd3 !important;
        font-size: 10px !important;
        font-weight: 700 !important;
        margin: 0 !important;
    }
    .stMetric [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 18px !important;
        font-weight: bold !important;
        margin: 2px 0 0 0 !important;
    }
    .tier1 { color: #6ec46d; font-weight: bold; }
    .tier2 { color: #5865f2; font-weight: bold; }
    .tier3 { color: #8b7aa8; font-weight: bold; }
    .unreliable { color: #d97777; font-weight: bold; }
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
    .stDivider {
        border-top: 1px solid #202225 !important;
        margin: 2px 0 !important;
    }
    h2 {
        color: #e1e8ed !important;
        margin-top: 6px !important;
        margin-bottom: 4px !important;
        font-size: 16px !important;
    }
    .stAlert {
        background-color: #2c2f33 !important;
        border-left: 4px solid #5865f2 !important;
        border-radius: 8px !important;
        color: #e1e8ed !important;
    }
    .stSpinner {
        color: #5865f2 !important;
    }
    [data-testid="column"] {
        gap: 0 !important;
    }
    .stForm {
        gap: 0 !important;
    }
    .stContainer {
        padding: 0 !important;
    }
    [data-testid="stVerticalBlockContainer"] {
        gap: 0 !important;
    }
    label {
        color: #e8ecf1 !important;
        font-weight: 500;
    }
    p {
        color: #e1e8ed !important;
    }
    </style>
"""


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)


def display_article_card(article):
    cred = article["credibility"]
    color = article["color"]
    st.markdown(f"""
    <div class="card" style="border-left-color: {color};">
        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 15px;">
            <h3 style="margin: 0; color: #ffffff; font-weight: 700;">{article['title']}</h3>
            <span class="credibility-badge" style="background-color: {color}; color: white;">
                {cred}% CREDIBLE
            </span>
        </div>
        <p style="color: #c8cdd3; margin: 5px 0; font-size: 0.9em; font-weight: 500;">
            📰 <strong>{article['source']}</strong> | 📅 {article['published'][:10]} | {article['sentiment']}
        </p>
        <p style="color: #e1e8ed; line-height: 1.6; margin: 10px 0;">
            {article['summary']}
        </p>
        <a href="{article['url']}" target="_blank" style="
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
    """, unsafe_allow_html=True)
