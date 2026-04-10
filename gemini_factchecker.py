

import os
import requests
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
            import google.generativeai as genai

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
            import google.generativeai as genai

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


class FactChecker:
    """Hybrid fact-checker using Google Fact Check API with Gemini fallback"""

    def __init__(self, config=None):
        self.config = config or Config()
        self.model_manager = GeminiModelManager(self.config)

    def check_fact(self, claim):
        """Check a claim using Google Fact Check API first, then Gemini as fallback"""
        if not self.config.is_fact_check_configured():
            return (
                None,
                "⚠️ Google Fact Check API key not configured. Please set FACT_CHECK_API_KEY in .env",
            )

        return self._check_with_google_fact_check(claim)

    def _check_with_google_fact_check(self, claim):
        """Internal: Check fact using Google Fact Check Tools API with Gemini fallback"""
        try:
            url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
            params = {
                "query": claim,
                "key": self.config.FACT_CHECK_KEY,
                "languageCode": "en",
            }

            response = requests.get(url, params=params, timeout=10)

            # Handle quota exceeded (429) by falling back to Gemini
            if response.status_code == 429:
                return self._check_with_gemini_fallback(claim)

            response.raise_for_status()
            data = response.json()

            if "claims" in data and data["claims"]:
                # Take the first claim
                claim_data = data["claims"][0]
                claim_reviews = claim_data.get("claimReview", [])

                if claim_reviews:
                    review = claim_reviews[0]
                    textual_rating = review.get("textualRating", "Inconclusive")
                    title = review.get("title", "")
                    publisher = review.get("publisher", {}).get("name", "Unknown")
                    url = review.get("url", "")

                    # Normalize rating
                    rating = self._normalize_rating(textual_rating)

                    explanation = f"{title} (Source: {publisher})"
                    if url:
                        explanation += f" - {url}"

                    confidence = "HIGH"  # Since it's from fact-checkers

                    result = {
                        "claim": claim,
                        "rating": rating,
                        "explanation": explanation,
                        "confidence": confidence,
                        "source": "Google Fact Check Tools",
                    }
                    return [result], None
                else:
                    # No reviews found - use Gemini as fallback
                    return self._check_with_gemini_fallback(claim)
            else:
                # No fact-checks found - use Gemini as fallback
                return self._check_with_gemini_fallback(claim)

        except requests.exceptions.RequestException:
            # If Google API fails, fall back to Gemini
            return self._check_with_gemini_fallback(claim)
        except Exception:
            # If anything goes wrong, fall back to Gemini
            return self._check_with_gemini_fallback(claim)

    def _check_with_gemini_fallback(self, claim):
        """Fallback: Check fact using Gemini AI when Google Fact Check API has no results"""
        if not self.config.is_gemini_configured():
            return [
                self._create_inconclusive_result(
                    claim, "No fact-checks found. Gemini AI not configured as fallback."
                )
            ], None

        try:
            import google.generativeai as genai

            genai.configure(api_key=self.config.GEMINI_KEY)
            model = genai.GenerativeModel("gemini-2.0-flash")

            prompt = f"""You are a fact-checking expert. Analyze this claim BRIEFLY.

CLAIM: {claim}

Respond EXACTLY in this format:
RATING: [TRUE/FALSE/MIXED/INCONCLUSIVE]
EXPLANATION: [1-2 sentences only]
CONFIDENCE: [HIGH/MEDIUM/LOW]"""

            response = model.generate_content(prompt, stream=False)
            result_text = response.text.strip()

            lines = result_text.split("\n")
            result = {
                "claim": claim,
                "rating": "INCONCLUSIVE",
                "explanation": result_text,
                "confidence": "MEDIUM",
                "source": "AI Analysis (Gemini Fallback)",
            }

            for line in lines:
                if line.startswith("RATING:"):
                    result["rating"] = line.replace("RATING:", "").strip()
                elif line.startswith("EXPLANATION:"):
                    result["explanation"] = line.replace("EXPLANATION:", "").strip()
                elif line.startswith("CONFIDENCE:"):
                    result["confidence"] = line.replace("CONFIDENCE:", "").strip()

            return [result], None

        except Exception as e:
            return [
                self._create_inconclusive_result(
                    claim, f"Could not verify claim: {str(e)[:50]}"
                )
            ], None

    def _normalize_rating(self, textual_rating):
        """Normalize textual rating to our format"""
        rating_lower = textual_rating.lower()
        if "true" in rating_lower and "false" not in rating_lower:
            return "TRUE"
        elif "false" in rating_lower:
            return "FALSE"
        elif "mixed" in rating_lower or "partly" in rating_lower:
            return "MIXED"
        else:
            return "INCONCLUSIVE"

    def _create_inconclusive_result(self, claim, explanation):
        """Create a default inconclusive result"""
        return {
            "claim": claim,
            "rating": "INCONCLUSIVE",
            "explanation": explanation,
            "confidence": "LOW",
            "source": "Fact Checker",
        }


# For backward compatibility - keep old function signatures
def get_available_models():
    """List available Gemini models"""
    manager = GeminiModelManager()
    manager.list_available_models()


def check_fact_with_gemini(claim):
    """Check a fact using hybrid approach (Google Fact Check API + Gemini fallback)"""
    checker = FactChecker()
    return checker.check_fact(claim)


if __name__ == "__main__":
    print("=" * 60)
    print("HYBRID FACT CHECKER TEST (Google Fact Check + Gemini)")
    print("=" * 60)

    # List available models
    print("\n1. Checking available Gemini models...")
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
                print(f"  Source: {result['source']}")

