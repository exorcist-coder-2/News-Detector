"""
Gemini Fact Checker 
"""
import os
from dotenv import load_dotenv
from config import Config

load_dotenv()


class GeminiModelManager:
    """Manages Gemini model selection and configuration"""
    
    PREFERRED_MODELS = [
        'gemini-2.0-flash',
        'gemini-1.5-flash',
        'gemini-pro',
        'gemini-1.5-pro',
    ]
    
    def __init__(self, config=None):
        self.config = config or Config()
        self.model = None
        self.model_name = None
    
    def configure(self):
        """Configure and select available model"""
        try:
            import google.generativeai as genai
            
            if not self.config.is_gemini_configured():
                return False, "❌ No GEMINI_API_KEY found in .env"
            
            genai.configure(api_key=self.config.GEMINI_KEY)
            
            for model_name in self.PREFERRED_MODELS:
                try:
                    self.model = genai.GenerativeModel(model_name)
                    self.model_name = model_name
                    return True, f"✅ Using model: {model_name}"
                except Exception as e:
                    print(f"⚠️ Model {model_name} not available: {str(e)[:80]}")
                    continue
            
            return False, "❌ No available Gemini models found"
            
        except ImportError:
            return False, "❌ google.generativeai not installed"
    
    def list_available_models(self):
        """List all available models"""
        try:
            import google.generativeai as genai
            
            if not self.config.is_gemini_configured():
                print("❌ No GEMINI_API_KEY found in .env")
                return
            
            genai.configure(api_key=self.config.GEMINI_KEY)
            models = genai.list_models()
            
            print("✅ Available models for generateContent:\n")
            for model in models:
                if 'generateContent' in model.supported_generation_methods:
                    model_name = model.name.split('/')[-1]
                    print(f"  ✓ {model_name}")
                    
        except Exception as e:
            print(f"❌ Error listing models: {e}")


class GeminiFactChecker:
    """Fact-checking service using Gemini AI"""
    
    def __init__(self, config=None):
        self.config = config or Config()
        self.model_manager = GeminiModelManager(self.config)
        self.prompt_template = """You are a fact-checking expert. Analyze this claim.

CLAIM: {claim}

Respond in this EXACT format (no extra text):
RATING: [TRUE/FALSE/MIXED/INCONCLUSIVE]
EXPLANATION: [2-3 sentences explaining the rating]
CONFIDENCE: [HIGH/MEDIUM/LOW]"""
    
    def check_fact(self, claim):
        """Check a claim using Gemini"""
        success, message = self.model_manager.configure()
        if not success:
            return None, message
        
        try:
            prompt = self.prompt_template.format(claim=claim)
            response = self.model_manager.model.generate_content(prompt, stream=False)
            result_text = response.text.strip()
            
            result = self._parse_response(claim, result_text)
            return result, None
            
        except Exception as e:
            return None, f"❌ Error: {str(e)}"
    
    def _parse_response(self, claim, result_text):
        """Parse Gemini response into structured result"""
        lines = result_text.split('\n')
        result = {
            "claim": claim,
            "rating": "INCONCLUSIVE",
            "explanation": result_text,
            "confidence": "UNKNOWN"
        }
        
        for line in lines:
            if line.startswith("RATING:"):
                result["rating"] = line.replace("RATING:", "").strip()
            elif line.startswith("EXPLANATION:"):
                result["explanation"] = line.replace("EXPLANATION:", "").strip()
            elif line.startswith("CONFIDENCE:"):
                result["confidence"] = line.replace("CONFIDENCE:", "").strip()
        
        return result


class WikipediaFallbackChecker:
    """Fallback fact-checker using Wikipedia"""
    
    def check_fact(self, claim):
        """Check a claim using Wikipedia"""
        try:
            import wikipedia
            search_results = wikipedia.search(claim, results=3)
            
            if search_results:
                page = wikipedia.page(search_results[0])
                summary = page.summary[:300]
                return {
                    "claim": claim,
                    "rating": "WIKIPEDIA_MATCH",
                    "explanation": f"Wikipedia: {summary}...",
                    "confidence": "MEDIUM",
                    "source": f"Wikipedia: {page.title}"
                }, None
                
        except Exception as e:
            return None, f"Wikipedia error: {str(e)}"
        
        return {
            "claim": claim,
            "rating": "UNVERIFIED",
            "explanation": "Could not verify this claim via Wikipedia.",
            "confidence": "LOW",
            "source": "None"
        }, None


class HybridFactChecker:
    """Hybrid fact-checker using Gemini with Wikipedia fallback"""
    
    def __init__(self, config=None):
        self.config = config or Config()
        self.gemini_checker = GeminiFactChecker(self.config)
        self.wikipedia_checker = WikipediaFallbackChecker()
    
    def check_fact(self, claim):
        """Check fact using Gemini first, fallback to Wikipedia"""
        # Try Gemini first
        if self.config.is_gemini_configured():
            result, error = self.gemini_checker.check_fact(claim)
            if result:
                return [result], None
            # If Gemini quota exceeded, fallback
            if "429" in str(error) or "quota" in str(error).lower():
                print("⚠️ Gemini quota exceeded, using Wikipedia fallback...")
                result, error = self.wikipedia_checker.check_fact(claim)
                if result:
                    return [result], None
            return None, error
        
        # No Gemini, use Wikipedia directly
        result, error = self.wikipedia_checker.check_fact(claim)
        if result:
            return [result], None
        return None, error


# For backward compatibility - keep old function signatures
def get_available_models():
    """List available Gemini models"""
    manager = GeminiModelManager()
    manager.list_available_models()


def check_fact_with_gemini(claim):
    """Check a fact using Gemini"""
    checker = GeminiFactChecker()
    return checker.check_fact(claim)


if __name__ == "__main__":
    print("=" * 60)
    print("GEMINI FACT CHECKER TEST")
    print("=" * 60)
    
    # List available models
    print("\n1. Checking available models...")
    get_available_models()
    
    # Test fact-checking
    print("\n2. Testing fact-check...\n")
    test_claims = [
        "The Earth is round",
        "Paris is the capital of France",
        "Water boils at 100 degrees Celsius",
    ]
    
    checker = HybridFactChecker()
    
    for claim in test_claims:
        print(f"\nClaim: {claim}")
        results, error = checker.check_fact(claim)
        
        if error:
            print(f"  {error}")
        else:
            for result in results:
                print(f"  Rating: {result['rating']}")
                print(f"  Explanation: {result['explanation']}")
                print(f"  Confidence: {result['confidence']}")
