# Lexen Legal AI Assistant

An intelligent legal research and analysis system built with CrewAI and powered by local Ollama models.

## Features

- **Legal Research Specialist**: Conducts comprehensive legal research on complex queries
- **Legal Document Analyst**: Provides detailed legal interpretation and analysis  
- **Privacy Expert**: Synthesizes findings into actionable privacy requirements and recommendations
- **Local LLM Processing**: Uses Ollama with Llama3 for complete privacy and control

## Setup

### Prerequisites

1. **Install Ollama**:
   ```bash
   # macOS
   brew install ollama

   # Linux
   curl -fsSL https://ollama.ai/install.sh | sh

   # Windows
   winget install Ollama.Ollama
   ```

2. **Pull the Llama3 model**:
   ```bash
   ollama pull llama3
   ```

3. **Start Ollama server**:
   ```bash
   ollama serve
   ```

### Installation

1. **Clone/Create the project directory**:
   ```bash
   mkdir lexen-legal-ai
   cd lexen-legal-ai
   ```

2. **Install dependencies**:
   ```bash
   pip install crewai[tools] python-dotenv litellm
   # or use poetry:
   poetry install
   ```

3. **Verify Ollama is running**:
   ```bash
   curl http://localhost:11434/api/tags
   ```

## Usage

### Basic Usage

Run the legal analysis crew:

```bash
python main.py
```

### Custom Queries

Modify the query in `main.py`:

```python
inputs = {
    'query': 'Your legal research question here',
    'current_year': str(datetime.now().year)
}
```

### Example Queries

- "Summarize privacy requirements in GDPR Article 5"
- "Analyze data retention requirements under CCPA"
- "What are the key compliance obligations for HIPAA covered entities?"
- "Explain the right to be forgotten under GDPR"

## Project Structure

```
lexen-legal-ai/
├── config/
│   ├── agents.yaml          # Agent configurations
│   └── tasks.yaml           # Task definitions
├── output/                  # Generated reports
│   └── legal_summary.md     # Final analysis output
├── crew.py                  # Crew definition
├── main.py                  # Main execution script
├── .env                     # Environment variables
├── pyproject.toml          # Project dependencies
└── README.md               # This file
```

## Configuration

### Environment Variables

The `.env` file contains all necessary Ollama configurations:

```bash
CREWAI_MODEL_PROVIDER=ollama
CREWAI_MODEL=llama3
LITELLM_PROVIDER=ollama
LITELLM_MODEL=ollama/llama3
LITELLM_API_BASE=http://localhost:11434
OPENAI_API_BASE=http://localhost:11434/v1
OPENAI_API_KEY=ollama-local
```

### Agents

- **Legal Researcher**: Conducts initial legal research and fact-finding
- **Legal Analyst**: Provides detailed legal interpretation and analysis
- **Privacy Expert**: Creates actionable recommendations and summaries

### Tasks

1. **Research Task**: Comprehensive legal research on the query
2. **Analysis Task**: Detailed legal interpretation of research findings  
3. **Summary Task**: Professional summary with recommendations

## Output

The crew generates a comprehensive legal analysis saved to `output/legal_summary.md` containing:

- Executive summary of key findings
- Detailed privacy requirements and obligations
- Practical implementation recommendations
- Best practices for compliance
- Key takeaways and action items

## Troubleshooting

### Common Issues

1. **"LLM value is None" error**:
   - Ensure Ollama is running: `ollama serve`
   - Verify model is available: `ollama list`

2. **Connection refused**:
   - Check if Ollama is running on port 11434
   - Try: `curl http://localhost:11434/api/tags`

3. **Model not found**:
   - Pull the model: `ollama pull llama3`
   - List available models: `ollama list`

### Advanced Configuration

To use a different model, update both the `.env` file and the LLM configuration in `crew.py`:

```python
self.ollama_llm = LLM(
    model="ollama/your-model-name",
    base_url="http://localhost:11434"
)
```

## License

MIT License - feel free to modify and distribute as needed.
