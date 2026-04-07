import os
from dotenv import load_dotenv

load_dotenv()

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "")
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")

CACHE_DURATION_SECONDS = 300

TIER_1_SOURCES = {
    "bbc", "bbc news", "reuters", "ap news", "associated press",
    "guardian", "new york times", "nyt", "washington post",
    "financial times", "the times", "the telegraph", "telegraph",
    "economist", "nikkei asia", "ft", "wsj", "wall street journal",
    "bbc world", "cnn international"
}

TIER_2_SOURCES = {
    "cnn", "bbc america", "cnbc", "politico", "politico pro",
    "bloomberg", "reuters news", "vox", "the verge", "techcrunch",
    "wired", "slate", "the atlantic", "time", "newsweek",
    "independent", "the independent", "open democracy"
}

TIER_3_SOURCES = {
    "medium", "forbes", "entrepreneur", "business insider",
    "huffpost", "huff post", "mashable", "polygon", "variety",
    "hollywood reporter", "deadline", "tvline"
}

UNRELIABLE_SOURCES = {
    "twitter", "x", "reddit", "4chan", "tiktok", "instagram"
}
