#!/usr/bin/env python
"""
Test script to verify Ollama connection and CrewAI configuration
"""

import requests
import os
from dotenv import load_dotenv

def test_ollama_connection():
    """Test if Ollama is running and accessible"""
    print("🔍 Testing Ollama connection...")

    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            print("✅ Ollama is running")
            print(f"📋 Available models: {len(models)}")

            llama3_found = any("llama3" in model.get("name", "") for model in models)
            if llama3_found:
                print("✅ Llama3 model is available")
                return True
            else:
                print("❌ Llama3 model not found. Run: ollama pull llama3")
                return False
        else:
            print(f"❌ Ollama responded with status: {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama. Is it running?")
        print("   Run: ollama serve")
        return False
    except Exception as e:
        print(f"❌ Error testing Ollama: {e}")
        return False

def test_environment():
    """Test environment configuration"""
    print("\n🔍 Testing environment configuration...")

    load_dotenv()

    required_vars = [
        "CREWAI_MODEL_PROVIDER",
        "CREWAI_MODEL", 
        "LITELLM_PROVIDER",
        "LITELLM_MODEL",
        "LITELLM_API_BASE"
    ]

    all_good = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var} = {value}")
        else:
            print(f"❌ {var} is not set")
            all_good = False

    return all_good

def test_litellm():
    """Test LiteLLM configuration"""
    print("\n🔍 Testing LiteLLM configuration...")

    try:
        import litellm
        from litellm import completion

        # Test configuration
        response = completion(
            model="ollama/llama3",
            messages=[{"role": "user", "content": "Hello, respond with just 'OK'"}],
            api_base="http://localhost:11434",
            max_tokens=10
        )

        if response and response.choices:
            print("✅ LiteLLM can communicate with Ollama")
            print(f"📝 Response: {response.choices[0].message.content}")
            return True
        else:
            print("❌ LiteLLM test failed - no response")
            return False

    except Exception as e:
        print(f"❌ LiteLLM test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Lexen Legal AI - Connection Test")
    print("=" * 50)

    tests = [
        ("Ollama Connection", test_ollama_connection),
        ("Environment Variables", test_environment),
        ("LiteLLM Integration", test_litellm)
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results.append((test_name, False))

    print("\n" + "=" * 50)
    print("🧪 Test Summary:")

    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {status}: {test_name}")
        if not passed:
            all_passed = False

    if all_passed:
        print("\n🎉 All tests passed! You can run: python main.py")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        print("\n💡 Common solutions:")
        print("   • Start Ollama: ollama serve")
        print("   • Pull model: ollama pull llama3") 
        print("   • Check .env file configuration")

if __name__ == "__main__":
    main()
