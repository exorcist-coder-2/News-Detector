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
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-pro",
        "gemini-1.5-pro",
    ]

    def __init__(self, config=None):
        self.config = config or Config()
        self.model = None
        self.model_name = None

    def configure(self):
        """Configure and select available model"""
        try:
            import google.genai as genai

            if not self.config.is_gemini_configured():
                return False, "No GEMINI_API_KEY found in .env"

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
            import google.genai as genai

            if not self.config.is_gemini_configured():
                print("No GEMINI_API_KEY found in .env")
                return

            genai.configure(api_key=self.config.GEMINI_KEY)
            models = genai.list_models()

            print("✅ Available models for generateContent:\n")
            for model in models:
                if "generateContent" in model.supported_generation_methods:
                    model_name = model.name.split("/")[-1]
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
        lines = result_text.split("\n")
        result = {
            "claim": claim,
            "rating": "INCONCLUSIVE",
            "explanation": result_text,
            "confidence": "UNKNOWN",
        }

        for line in lines:
            if line.startswith("RATING:"):
                result["rating"] = line.replace("RATING:", "").strip()
            elif line.startswith("EXPLANATION:"):
                result["explanation"] = line.replace("EXPLANATION:", "").strip()
            elif line.startswith("CONFIDENCE:"):
                result["confidence"] = line.replace("CONFIDENCE:", "").strip()

        return result


class FactChecker:
    """Fact-checker using Gemini AI only"""

    def __init__(self, config=None):
        self.config = config or Config()
        self.gemini_checker = GeminiFactChecker(self.config)

    def check_fact(self, claim):
        """Check fact using Gemini only"""
        if not self.config.is_gemini_configured():
            return (
                None,
                "⚠️ Gemini API key not configured. Please set GEMINI_API_KEY in .env",
            )

        result, error = self.gemini_checker.check_fact(claim)
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

    checker = FactChecker()

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
