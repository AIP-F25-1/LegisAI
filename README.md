# LegisAI - AI-Powered Legal Assistant

A production-ready legal AI assistant with intelligent document analysis, multi-agent orchestration, clause risk detection, and hybrid search capabilities.

## 🚀 Features

### Core Capabilities
- ✅ **Legal Research** - Hybrid search (FAISS + BM25) with 1,200+ contract clauses
- ✅ **Document Drafting** - AI-powered contract generation with streaming responses
- ✅ **Compliance Checking** - GDPR/CCPA and jurisdiction-aware analysis
- ✅ **Clause Analysis** - 4-tier risk scoring (low/medium/high/critical)
- ✅ **Risk Visualization** - Interactive D3.js heatmap for clause-level risks
- ✅ **Document Upload** - PDF processing and analysis
- ✅ **Streaming Responses** - Real-time word-by-word generation

### Advanced AI Agents
- 🔍 **Summarization Agent** - Extract headnotes, ratio decidendi, obiter dicta
- 🎯 **Precedent Reasoning Agent** - Cross-case alignment, outdated precedent detection
- 📊 **Knowledge Graph Builder** - Auto-builds graph of precedents and statutes
- 📝 **Redlining & Comparison Agent** - ML-based clause alignment, risk-focused changes
- ⚙️ **Clause Generation Agent** - Detect missing clauses, generate standard clauses
- 📋 **Regulatory Monitoring Agent** - Track regulations, flag new requirements
- 🎲 **Monte Carlo Risk Agent** - What-if scenario simulations
- 🔄 **Multi-Agent Orchestration** - LangGraph for complex workflows with state management

### Technical Features
- 🔍 **FAISS Vector Store** - Semantic search with sentence transformers
- 🎯 **Hybrid Retrieval** - Combines semantic (FAISS) + keyword (BM25) search
- 📚 **Real Legal Data** - 1,200+ contract clauses from CUAD dataset
- ⚖️ **Jurisdiction-Aware** - US, EU, UK legal rules
- 🔒 **Cross-Consistency Checking** - Multiple agents validate same clause
- 🌐 **Graph-Based Workflows** - LangGraph orchestration with conditional routing

## 📊 Project Status

**Overall Completion: ~95% of core features**

- ✅ **16 Major Features** Fully Implemented
- ⚠️ **5 Features** Partially Implemented
- ❌ **4 Features** Not Yet Implemented

See [FEATURE_COMPARISON.md](FEATURE_COMPARISON.md) for detailed status.

## 🚀 Quick Start

### Prerequisites

**For Docker:**
- Docker Desktop installed and running
- At least 8GB RAM
- ~15GB free disk space

**For Local Development:**
- Python 3.11+ installed
- Node.js 18+ installed
- Ollama installed and running locally

### Start the Application

**Option 1: Docker (Recommended)**

```bash
# Start Backend with Docker
docker-backend.bat

# Start Frontend with Docker (in another terminal)
docker-frontend.bat
```

**Option 2: Local Development**

```bash
# Start Backend locally
backend.bat

# Start Frontend locally (in another terminal)
frontend.bat
```

### Access the Application

- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs

For detailed instructions, see [QUICK_START.md](QUICK_START.md).

## 📁 Project Structure

```
LegisAI/
├── backend/
│   ├── main.py                    # FastAPI application (47 endpoints)
│   ├── requirements.txt           # Python dependencies
│   ├── services/                  # 14 AI agent services
│   │   ├── vector_store.py       # FAISS integration
│   │   ├── hybrid_retriever.py   # BM25 + FAISS
│   │   ├── clause_analyzer.py    # Risk detection
│   │   ├── summarization_agent.py
│   │   ├── precedent_reasoning_agent.py
│   │   ├── knowledge_graph_builder.py
│   │   ├── redlining_comparison_agent.py
│   │   ├── clause_generation_agent.py
│   │   ├── regulatory_monitoring_agent.py
│   │   ├── monte_carlo_risk_agent.py
│   │   ├── langgraph_orchestrator.py  # LangGraph workflows
│   │   └── courtlistener_api.py
│   ├── data/                      # Vector store data
│   └── uploads/                   # User uploads
├── frontend/
│   ├── src/
│   │   ├── pages/                # React pages
│   │   ├── components/           # UI components
│   │   └── utils/                # Utilities
│   └── package.json
├── backend.bat                    # Start backend locally
├── docker-backend.bat             # Start backend with Docker
├── frontend.bat                   # Start frontend locally
├── docker-frontend.bat           # Start frontend with Docker
└── docker-compose.yml             # Full stack Docker setup
```

## 🛠️ Installation

### Quick Start Scripts

**Windows Batch Files:**
- `backend.bat` - Start backend locally
- `docker-backend.bat` - Start backend with Docker
- `frontend.bat` - Start frontend locally
- `docker-frontend.bat` - Start frontend with Docker

**Usage:**
```bash
# Docker (Recommended)
docker-backend.bat    # Terminal 1
docker-frontend.bat   # Terminal 2

# Local Development
backend.bat           # Terminal 1
frontend.bat          # Terminal 2
```

## 📝 API Documentation

Full interactive API docs available at `http://localhost:8000/docs` when backend is running.

### Key Endpoints

**Research & Retrieval:**
- `POST /api/research` - Legal research with hybrid search
- `POST /api/summarize/headnotes` - Extract case headnotes
- `POST /api/summarize/ratio-decidendi` - Extract legal reasoning
- `POST /api/precedent/align` - Find supporting/weakening cases
- `POST /api/knowledge-graph/build` - Build knowledge graph

**Drafting & Contract Intelligence:**
- `POST /api/draft` - Generate legal documents
- `POST /api/clauses/analyze` - Clause risk analysis
- `POST /api/redlining/align` - Compare two contracts
- `POST /api/clauses/generate` - Generate missing clauses
- `POST /api/clauses/detect-missing` - Detect missing standard clauses

**Compliance & Risk:**
- `POST /api/compliance/check` - Compliance analysis
- `POST /api/regulatory/crawl` - Monitor regulations
- `POST /api/risk/monte-carlo` - Risk scenario simulations

**Orchestration:**
- `POST /api/langgraph/comprehensive-analysis` - Multi-agent comprehensive workflow
- `POST /api/langgraph/cross-consistency-check` - Consistency validation workflow
- `POST /api/langgraph/research-and-draft` - Research → draft → review workflow
- `GET /api/langgraph/status` - Orchestrator status

**Document Management:**
- `POST /api/upload` - Upload documents
- `GET /api/analyze/{file_id}` - Analyze uploaded document

## 📊 Data Sources

### Currently Integrated
- **CUAD Dataset** - 1,200+ contract clauses imported and indexed
- **Vector Store** - 1,267+ total documents (FAISS + BM25 indexed)
- **CourtListener API** - Real-time case law search (optional, requires API key)
- **Regulations** - GDPR, CCPA, US Code sections

## 🐳 Docker Configuration

### Environment Variables

Create `backend/.env`:

```env
# Ollama Configuration
OLLAMA_HOST=http://ollama:11434  # Docker
# OLLAMA_HOST=http://127.0.0.1:11434  # Local

# CourtListener API (optional)
COURTLISTENER_API_TOKEN=your_api_token_here

# Application
PORT=8000
ENVIRONMENT=production
```

### Docker Commands

```bash
# Start services
docker compose up -d

# View logs
docker compose logs -f

# Stop services
docker compose down

# Check status
docker compose ps
```

## 📚 Documentation

- **[README.md](README.md)** - This file (main documentation)
- **[FEATURE_COMPARISON.md](FEATURE_COMPARISON.md)** - Complete feature status and project progress
- **[QUICK_START.md](QUICK_START.md)** - Quick setup guide
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contribution guidelines
- **[COMPLEXITY_ANALYSIS.md](COMPLEXITY_ANALYSIS.md)** - Code complexity metrics
- **[HOW_ORCHESTRATION_WORKS.md](HOW_ORCHESTRATION_WORKS.md)** - Multi-agent orchestration guide
- **[LANGGRAPH_IMPLEMENTATION.md](LANGGRAPH_IMPLEMENTATION.md)** - LangGraph setup guide
- **[HOW_ORCHESTRATION_WORKS.md](HOW_ORCHESTRATION_WORKS.md)** - Multi-agent orchestration guide

## 🏗️ Architecture

### Backend
- **Framework**: FastAPI (Python)
- **LLM**: Ollama (local LLM hosting)
- **Vector Store**: FAISS (semantic search)
- **Search**: Hybrid (FAISS + BM25)
- **Orchestration**: LangGraph (graph-based workflows)
- **API**: RESTful with 47 endpoints

### Frontend
- **Framework**: React + TypeScript
- **Build Tool**: Vite
- **Styling**: TailwindCSS
- **Visualization**: D3.js (risk heatmap)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📄 License

MIT License - See LICENSE file for details

## 🆘 Support

For issues or questions:
- Create an issue on GitHub
- Check the documentation
- Review [QUICK_START.md](QUICK_START.md) for troubleshooting

## 🎉 Acknowledgments

- Ollama for local LLM hosting
- FAISS for vector search
- LangGraph for multi-agent orchestration
- FastAPI for the backend framework
- React + Vite for the frontend

---

**Built with ❤️ for the legal community**

**Version**: 4.0.0  
**Status**: Production Ready (95% Complete)
