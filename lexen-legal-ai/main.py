#!/usr/bin/env python
from dotenv import load_dotenv
import os, sys, warnings
from datetime import datetime

# ✅ Force-load .env first
load_dotenv()

# ✅ Set all required environment variables for Ollama
os.environ["CREWAI_MODEL_PROVIDER"] = "ollama"
os.environ["CREWAI_MODEL"] = "llama3"
os.environ["LITELLM_PROVIDER"] = "ollama"
os.environ["LITELLM_MODEL"] = "ollama/llama3"
os.environ["LITELLM_API_BASE"] = "http://localhost:11434"
os.environ["OPENAI_API_BASE"] = "http://localhost:11434/v1"
os.environ["OPENAI_API_KEY"] = "ollama-local"

print("🔧 Active Provider:", os.getenv("CREWAI_MODEL_PROVIDER"))
print("🔧 Active Model:", os.getenv("CREWAI_MODEL"))
print("🔧 API Base:", os.getenv("LITELLM_API_BASE"))

# Suppress warnings
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

from crew import LexenCrew

def run():
    """Run the crew."""
    # Create output directory if it doesn't exist
    os.makedirs('output', exist_ok=True)

    inputs = {
        'query': 'Summarize privacy requirements in GDPR Article 5',
        'current_year': str(datetime.now().year)
    }

    try:
        # Ensure LiteLLM is configured correctly
        import litellm
        litellm.set_verbose = True

        print("\n🚀 Starting Lexen Legal AI Crew...")
        print(f"📋 Query: {inputs['query']}")
        print("=" * 60)

        result = LexenCrew().crew().kickoff(inputs=inputs)

        print("\n" + "=" * 60)
        print("✅ Analysis Complete!")
        print("📄 Output saved to: output/legal_summary.md")
        print("=" * 60)

        return result

    except Exception as e:
        print(f"❌ Error occurred: {e}")
        raise Exception(f"An error occurred while running the crew: {e}")

def train():
    """Train the crew for a given number of iterations."""
    inputs = {
        'query': 'Summarize privacy requirements in GDPR Article 5',
        'current_year': str(datetime.now().year)
    }
    try:
        LexenCrew().crew().train(
            n_iterations=int(sys.argv[1]),
            filename=sys.argv[2],
            inputs=inputs
        )
    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """Replay the crew execution from a specific task."""
    try:
        LexenCrew().crew().replay(task_id=sys.argv[1])
    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """Test the crew execution and return the results."""
    inputs = {
        'query': 'Summarize privacy requirements in GDPR Article 5',
        'current_year': str(datetime.now().year)
    }
    try:
        LexenCrew().crew().test(
            n_iterations=int(sys.argv[1]),
            eval_llm=sys.argv[2],
            inputs=inputs
        )
    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

if __name__ == "__main__":
    run()
