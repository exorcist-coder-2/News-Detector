import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuration manager for API keys and settings"""
    
    def __init__(self):
        self.NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "")
        self.GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")
        self.FACT_CHECK_KEY = os.getenv("FACT_CHECK_API_KEY", "")
        self.CACHE_DURATION_SECONDS = 300
    
    def is_newsapi_configured(self):
        return bool(self.NEWSAPI_KEY)
    
    def is_gemini_configured(self):
        return bool(self.GEMINI_KEY)
    
    def is_fact_check_configured(self):
        return bool(self.FACT_CHECK_KEY)
    
    @classmethod
    def from_streamlit_secrets(cls, st_secrets):
        """Create config from Streamlit secrets"""
        config = cls()
        try:
            config.NEWSAPI_KEY = st_secrets.get("NEWSAPI_KEY", "")
            config.GEMINI_KEY = st_secrets.get("GEMINI_API_KEY", "")
            config.FACT_CHECK_KEY = st_secrets.get("FACT_CHECK_API_KEY", "")
        except Exception:
            pass
        return config


class SourceTiers:
    """Manages news source credibility tiers"""
    
    TIER_1 = {
        "bbc", "bbc news", "reuters", "ap news", "associated press",
        "guardian", "new york times", "nyt", "washington post",
        "financial times", "the times", "the telegraph", "telegraph",
        "economist", "nikkei asia", "ft", "wsj", "wall street journal",
        "bbc world", "cnn international"
    }
    
    TIER_2 = {
        "cnn", "bbc america", "cnbc", "politico", "politico pro",
        "bloomberg", "reuters news", "vox", "the verge", "techcrunch",
        "wired", "slate", "the atlantic", "time", "newsweek",
        "independent", "the independent", "open democracy"
    }
    
    TIER_3 = {
        "medium", "forbes", "entrepreneur", "business insider",
        "huffpost", "huff post", "mashable", "polygon", "variety",
        "hollywood reporter", "deadline", "tvline"
    }
    
    UNRELIABLE = {
        "twitter", "x", "reddit", "4chan", "tiktok", "instagram"
    }
    
    @classmethod
    def get_tier_info(cls, source_name):
        """Get tier info for a source"""
        source_lower = source_name.lower().strip()
        
        if any(tier1 in source_lower for tier1 in cls.TIER_1):
            return {"tier": "tier1", "score": 93, "color": "#6ec46d"}
        elif any(tier2 in source_lower for tier2 in cls.TIER_2):
            return {"tier": "tier2", "score": 78, "color": "#5b8fc4"}
        elif any(tier3 in source_lower for tier3 in cls.TIER_3):
            return {"tier": "tier3", "score": 65, "color": "#8b7aa8"}
        elif any(unreliable in source_lower for unreliable in cls.UNRELIABLE):
            return {"tier": "unreliable", "score": 35, "color": "#d97777"}
        else:
            return {"tier": "unknown", "score": 55, "color": "#a0a8b0"}


# For backward compatibility
NEWSAPI_KEY = Config().NEWSAPI_KEY
GEMINI_KEY = Config().GEMINI_KEY
CACHE_DURATION_SECONDS = 300

TIER_1_SOURCES = SourceTiers.TIER_1
TIER_2_SOURCES = SourceTiers.TIER_2
TIER_3_SOURCES = SourceTiers.TIER_3
UNRELIABLE_SOURCES = SourceTiers.UNRELIABLE
