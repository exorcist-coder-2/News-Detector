from config import (
    TIER_1_SOURCES,
    TIER_2_SOURCES,
    TIER_3_SOURCES,
    UNRELIABLE_SOURCES,
)


def get_source_tier(source_name):
    source_lower = source_name.lower().strip()

    if any(tier1 in source_lower for tier1 in TIER_1_SOURCES):
        return "tier1", 93, "#6ec46d"
    elif any(tier2 in source_lower for tier2 in TIER_2_SOURCES):
        return "tier2", 78, "#5b8fc4"
    elif any(tier3 in source_lower for tier3 in TIER_3_SOURCES):
        return "tier3", 65, "#8b7aa8"
    elif any(unreliable in source_lower for unreliable in UNRELIABLE_SOURCES):
        return "unreliable", 35, "#d97777"
    else:
        return "unknown", 55, "#a0a8b0"


def analyze_content_quality(content):
    if not content or len(content) < 50:
        return -15

    score_adjustment = 0
    sentences = [s for s in content.split('.') if len(s.strip()) > 10]
    if len(sentences) < 2:
        score_adjustment -= 10
    elif len(sentences) > 15:
        score_adjustment += 5

    if '"' in content or "'" in content:
        score_adjustment += 5

    sensational_words = [
        "shocking", "unbelievable", "you won't believe",
        "doctors hate", "secret", "exposed", "scandal"
    ]
    sensational_count = sum(1 for word in sensational_words if word.lower() in content.lower())
    score_adjustment -= sensational_count * 3

    caps_words = len([w for w in content.split() if w.isupper() and len(w) > 2])
    if caps_words > 5:
        score_adjustment -= 5

    exclamation_count = content.count("!")
    if exclamation_count > 3:
        score_adjustment -= 3

    return max(-20, min(20, score_adjustment))


def get_color_by_score(score):
    score = max(0, min(100, score))
    if score < 20:
        return "#c97171"
    elif score < 40:
        return "#d97777"
    elif score < 50:
        return "#dfa676"
    elif score < 60:
        return "#d4a574"
    elif score < 75:
        return "#8b9d6b"
    elif score < 90:
        return "#6ec46d"
    else:
        return "#5aad5a"


def get_credibility_score(source, content):
    _, base_score, _ = get_source_tier(source)
    content_adjustment = analyze_content_quality(content)
    final_score = base_score + content_adjustment
    final_score = max(0, min(100, final_score))
    color = get_color_by_score(final_score)
    return final_score, color
