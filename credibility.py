from config import SourceTiers


class CredibilityAnalyzer:
    """Analyzes credibility of news sources and content"""
    
    SENSATIONAL_WORDS = [
        "shocking", "unbelievable", "you won't believe",
        "doctors hate", "secret", "exposed", "scandal"
    ]
    
    def __init__(self):
        self.source_tiers = SourceTiers()
    
    def analyze_source(self, source_name):
        """Get credibility tier for a source"""
        return self.source_tiers.get_tier_info(source_name)
    
    def analyze_content_quality(self, content):
        """Analyze content quality and return score adjustment"""
        if not content or len(content) < 50:
            return -15
        
        score_adjustment = 0
        
        # Check sentence structure
        sentences = [s for s in content.split('.') if len(s.strip()) > 10]
        if len(sentences) < 2:
            score_adjustment -= 10
        elif len(sentences) > 15:
            score_adjustment += 5
        
        # Check for quoted sources
        if '"' in content or "'" in content:
            score_adjustment += 5
        
        # Check for sensationalism
        sensational_count = sum(1 for word in self.SENSATIONAL_WORDS 
                              if word.lower() in content.lower())
        score_adjustment -= sensational_count * 3
        
        # Check for excessive caps
        caps_words = len([w for w in content.split() 
                         if w.isupper() and len(w) > 2])
        if caps_words > 5:
            score_adjustment -= 5
        
        # Check for excessive exclamation marks
        exclamation_count = content.count("!")
        if exclamation_count > 3:
            score_adjustment -= 3
        
        return max(-20, min(20, score_adjustment))
    
    def get_color_by_score(self, score):
        """Get color based on credibility score"""
        score = max(0, min(100, score))
        
        color_map = [
            (20, "#c97171"),  # Dark red
            (40, "#d97777"),  # Red
            (50, "#dfa676"),  # Orange
            (60, "#d4a574"),  # Yellow
            (75, "#8b9d6b"),  # Light green
            (90, "#6ec46d"),  # Green
            (100, "#5aad5a")  # Dark green
        ]
        
        for threshold, color in color_map:
            if score < threshold:
                return color
        return "#5aad5a"
    
    def calculate_score(self, source, content):
        """Calculate final credibility score"""
        tier_info = self.analyze_source(source)
        base_score = tier_info["score"]
        content_adjustment = self.analyze_content_quality(content)
        
        final_score = base_score + content_adjustment
        final_score = max(0, min(100, final_score))
        
        color = self.get_color_by_score(final_score)
        return final_score, color


# For backward compatibility - keep old function names
def get_source_tier(source_name):
    analyzer = CredibilityAnalyzer()
    info = analyzer.analyze_source(source_name)
    return info["tier"], info["score"], info["color"]


def analyze_content_quality(content):
    analyzer = CredibilityAnalyzer()
    return analyzer.analyze_content_quality(content)


def get_color_by_score(score):
    analyzer = CredibilityAnalyzer()
    return analyzer.get_color_by_score(score)


def get_credibility_score(source, content):
    analyzer = CredibilityAnalyzer()
    return analyzer.calculate_score(source, content)
