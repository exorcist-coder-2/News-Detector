"""
Standalone Gemini fact-checker - fresh implementation
"""
import os
from dotenv import load_dotenv

load_dotenv()

def get_available_models():
    """List available Gemini models"""
    try:
        import google.generativeai as genai
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("❌ No GEMINI_API_KEY found in .env")
            return
        
        genai.configure(api_key=api_key)
        models = genai.list_models()
        
        print("✅ Available models for generateContent:\n")
        for model in models:
            if 'generateContent' in model.supported_generation_methods:
                model_name = model.name.split('/')[-1]
                print(f"  ✓ {model_name}")
                
    except Exception as e:
        print(f"❌ Error listing models: {e}")

def check_fact_with_gemini(claim):
    """Fact-check a claim using Gemini"""
    try:
        import google.generativeai as genai
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return None, "❌ GEMINI_API_KEY not found in .env"
        
        genai.configure(api_key=api_key)
        
        # Try different model names in order of preference
        models_to_try = [
            'gemini-2.0-flash',
            'gemini-1.5-flash',
            'gemini-pro',
            'gemini-1.5-pro',
        ]
        
        model = None
        for model_name in models_to_try:
            try:
                model = genai.GenerativeModel(model_name)
                print(f"✅ Using model: {model_name}")
                break
            except Exception as e:
                print(f"⚠️ Model {model_name} not available: {str(e)[:80]}")
                continue
        
        if model is None:
            return None, "❌ No available Gemini models found. Please check your API key."
        
        prompt = f"""You are a fact-checking expert. Analyze this claim.

CLAIM: {claim}

Respond in this EXACT format (no extra text):
RATING: [TRUE/FALSE/MIXED/INCONCLUSIVE]
EXPLANATION: [2-3 sentences explaining the rating]
CONFIDENCE: [HIGH/MEDIUM/LOW]"""
        
        response = model.generate_content(prompt, stream=False)
        result_text = response.text.strip()
        
        # Parse result
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
        
        return result, None
        
    except Exception as e:
        return None, f"❌ Error: {str(e)}"

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
    
    for claim in test_claims:
        print(f"\nClaim: {claim}")
        result, error = check_fact_with_gemini(claim)
        
        if error:
            print(f"  {error}")
        else:
            print(f"  Rating: {result['rating']}")
            print(f"  Explanation: {result['explanation']}")
            print(f"  Confidence: {result['confidence']}")
