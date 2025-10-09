#!/usr/bin/env python
"""
Example script showing how to run custom legal queries
"""

from dotenv import load_dotenv
import os
from datetime import datetime

# Load environment
load_dotenv()

# Configure Ollama
os.environ["CREWAI_MODEL_PROVIDER"] = "ollama"
os.environ["CREWAI_MODEL"] = "llama3"
os.environ["LITELLM_PROVIDER"] = "ollama"
os.environ["LITELLM_MODEL"] = "ollama/llama3"
os.environ["LITELLM_API_BASE"] = "http://localhost:11434"
os.environ["OPENAI_API_BASE"] = "http://localhost:11434/v1"
os.environ["OPENAI_API_KEY"] = "ollama-local"

from crew import LexenCrew

def run_custom_query(query):
    """Run a custom legal query through the Lexen crew"""

    inputs = {
        'query': query,
        'current_year': str(datetime.now().year)
    }

    print(f"🔍 Running query: {query}")
    print("=" * 60)

    try:
        crew = LexenCrew()
        result = crew.crew().kickoff(inputs=inputs)

        print("\n✅ Query completed successfully!")
        print(f"📄 Results saved to: output/legal_summary.md")

        return result

    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    """Interactive query runner"""

    print("🏛️ Lexen Legal AI - Custom Query Runner")
    print("=" * 50)

    # Example queries
    example_queries = [
        "Summarize privacy requirements in GDPR Article 5",
        "What are the data retention requirements under CCPA?",
        "Explain the key obligations for HIPAA covered entities",
        "Analyze the right to be forgotten under GDPR Article 17",
        "What are the consent requirements under GDPR Article 7?",
        "Summarize data breach notification requirements under GDPR"
    ]

    print("\n📚 Example queries:")
    for i, query in enumerate(example_queries, 1):
        print(f"  {i}. {query}")

    print("\n" + "=" * 50)

    while True:
        choice = input("\nEnter query number (1-6) or type your own query (q to quit): ").strip()

        if choice.lower() == 'q':
            break

        try:
            if choice.isdigit() and 1 <= int(choice) <= len(example_queries):
                query = example_queries[int(choice) - 1]
            else:
                query = choice

            if query:
                result = run_custom_query(query)

                if result:
                    print("\n" + "=" * 60)
                    print("Would you like to run another query? (y/n)")
                    if input().strip().lower() != 'y':
                        break

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
