"""
LegisAI Backend - AI-Powered Legal Assistant

Features:
- Hybrid legal research (FAISS + BM25)
- Multi-agent orchestration with LangGraph
- Clause analysis & risk detection
- Compliance checking
- Document drafting with streaming
- Knowledge graph builder
- Regulatory monitoring
- Monte Carlo risk simulations

Orchestration: LangGraph (graph-based workflows with state management)
"""

import os
import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException, UploadFile, File, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import json
import asyncio
import aiofiles
import time
import re

# LLM Integration with Ollama - Import check only, don't initialize yet
try:
    import ollama
    from ollama import AsyncClient
    LLM_AVAILABLE = True
    USE_ASYNC_CLIENT = True
except ImportError:
    LLM_AVAILABLE = False
    ollama = None
    USE_ASYNC_CLIENT = False
    print("⚠️ Ollama not available. Install with: pip install ollama")

# Embeddings model (optional)
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    SentenceTransformer = None
    print("⚠️ Sentence transformers not available. Install with: pip install sentence-transformers")

# FAISS Vector Store
try:
    from services.vector_store import VectorStore
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    VectorStore = None
    print("⚠️ FAISS not available. Install with: pip install faiss-cpu")

# CourtListener API Service
try:
    from services.courtlistener_api import get_courtlistener_service, COURTLISTENER_AVAILABLE
except ImportError:
    COURTLISTENER_AVAILABLE = False
    get_courtlistener_service = None
    print("⚠️ CourtListener API service not available")

# Hybrid Retriever (BM25 + FAISS)
try:
    from services.hybrid_retriever import HybridRetriever
    HYBRID_RETRIEVER_AVAILABLE = True
except ImportError:
    HYBRID_RETRIEVER_AVAILABLE = False
    HybridRetriever = None
    print("⚠️ Hybrid retriever not available. Install with: pip install rank-bm25")

# Clause Analyzer
try:
    from services.clause_analyzer import ClauseAnalyzer
    CLAUSE_ANALYZER_AVAILABLE = True
except ImportError:
    CLAUSE_ANALYZER_AVAILABLE = False
    ClauseAnalyzer = None
    print("⚠️ Clause analyzer not available")

# Summarization Agent
try:
    from services.summarization_agent import SummarizationAgent
    SUMMARIZATION_AVAILABLE = True
except ImportError:
    SUMMARIZATION_AVAILABLE = False
    SummarizationAgent = None
    print("⚠️ Summarization agent not available")

# Precedent Reasoning Agent
try:
    from services.precedent_reasoning_agent import PrecedentReasoningAgent
    PRECEDENT_REASONING_AVAILABLE = True
except ImportError:
    PRECEDENT_REASONING_AVAILABLE = False
    PrecedentReasoningAgent = None
    print("⚠️ Precedent reasoning agent not available")

# Knowledge Graph Builder
try:
    from services.knowledge_graph_builder import KnowledgeGraphBuilder
    KNOWLEDGE_GRAPH_AVAILABLE = True
except ImportError:
    KNOWLEDGE_GRAPH_AVAILABLE = False
    KnowledgeGraphBuilder = None
    print("⚠️ Knowledge graph builder not available (install networkx for full functionality)")

# Redlining & Comparison Agent
try:
    from services.redlining_comparison_agent import RedliningComparisonAgent
    REDLINING_AVAILABLE = True
except ImportError:
    REDLINING_AVAILABLE = False
    RedliningComparisonAgent = None
    print("⚠️ Redlining comparison agent not available")

# Clause Generation Agent
try:
    from services.clause_generation_agent import ClauseGenerationAgent
    CLAUSE_GENERATION_AVAILABLE = True
except ImportError:
    CLAUSE_GENERATION_AVAILABLE = False
    ClauseGenerationAgent = None
    print("⚠️ Clause generation agent not available")

# Regulatory Monitoring Agent
try:
    from services.regulatory_monitoring_agent import RegulatoryMonitoringAgent
    REGULATORY_MONITORING_AVAILABLE = True
except ImportError:
    REGULATORY_MONITORING_AVAILABLE = False
    RegulatoryMonitoringAgent = None
    print("⚠️ Regulatory monitoring agent not available")

# Monte Carlo Risk Agent
try:
    from services.monte_carlo_risk_agent import MonteCarloRiskAgent
    MONTE_CARLO_AVAILABLE = True
except ImportError:
    MONTE_CARLO_AVAILABLE = False
    MonteCarloRiskAgent = None
    print("⚠️ Monte Carlo risk agent not available")

# Explainability Service
try:
    from services.explainability_service import ExplainabilityService
    EXPLAINABILITY_AVAILABLE = True
except ImportError:
    EXPLAINABILITY_AVAILABLE = False
    ExplainabilityService = None
    print("⚠️ Explainability service not available")

# HITL Service
try:
    from services.hitl_service import HITLService
    HITL_AVAILABLE = True
except ImportError:
    HITL_AVAILABLE = False
    HITLService = None
    print("⚠️ HITL service not available")

# Domain Compliance Packs
try:
    from services.domain_compliance_packs import DomainCompliancePacks
    DOMAIN_COMPLIANCE_AVAILABLE = True
except ImportError:
    DOMAIN_COMPLIANCE_AVAILABLE = False
    DomainCompliancePacks = None
    print("⚠️ Domain compliance packs not available")

# LangGraph Orchestrator
try:
    from services.langgraph_orchestrator import LangGraphOrchestrator
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    LangGraphOrchestrator = None
    print("⚠️ LangGraph orchestrator not available (install with: pip install langgraph langchain-core)")

# Multi-Modal Legal Intelligence Agents
# OCR Agent
try:
    from services.ocr_agent import OCRAgent
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    OCRAgent = None
    print("⚠️ OCR Agent not available")

# Timeline Builder Agent
try:
    from services.timeline_builder_agent import TimelineBuilderAgent
    TIMELINE_BUILDER_AVAILABLE = True
except ImportError:
    TIMELINE_BUILDER_AVAILABLE = False
    TimelineBuilderAgent = None
    print("⚠️ Timeline Builder Agent not available")

# Speech TTS Agent
try:
    from services.speech_tts_agent import SpeechTTSAgent
    SPEECH_TTS_AVAILABLE = True
except ImportError:
    SPEECH_TTS_AVAILABLE = False
    SpeechTTSAgent = None
    print("⚠️ Speech TTS Agent not available")

# Global LLM models
ollama_client = None
embeddings_model = None
ollama_model = "llama3.1:8b"  # Default model

# Global Vector Store
vector_store = None

# Global Hybrid Retriever
hybrid_retriever = None

# Global Clause Analyzer
clause_analyzer = None

# Global Summarization Agent
summarization_agent = None

# Global Precedent Reasoning Agent
precedent_reasoning_agent = None

# Global Knowledge Graph Builder
knowledge_graph = None

# Global Redlining & Comparison Agent
redlining_agent = None

# Global Clause Generation Agent
clause_generation_agent = None

# Global Regulatory Monitoring Agent
regulatory_monitoring_agent = None

# Global Monte Carlo Risk Agent
monte_carlo_agent = None

# Global LangGraph Orchestrator
langgraph_orchestrator = None

# Global Multi-Modal Agents
ocr_agent = None
timeline_builder_agent = None
speech_tts_agent = None

# Global Explainability Service
explainability_service = None

# Global HITL Service
hitl_service = None

# Global Domain Compliance Packs
domain_compliance_packs = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Pydantic models
class UploadResponse(BaseModel):
    file_id: str
    filename: str
    file_type: str
    size: int
    status: str
    processing_results: Optional[Dict[str, Any]] = None

class ResearchRequest(BaseModel):
    query: str
    max_results: Optional[int] = 10
    similarity_threshold: Optional[float] = 0.3
    semantic_weight: Optional[float] = 0.6
    keyword_weight: Optional[float] = 0.4

class DraftRequest(BaseModel):
    query: str
    document_type: Optional[str] = "contract"
    context: Optional[str] = ""

# Multi-Modal Legal Intelligence Request Models
class OCRRequest(BaseModel):
    file_path: str
    extract_entities: Optional[bool] = True

class TimelineDocumentRequest(BaseModel):
    document_id: str
    text: str
    metadata: Optional[Dict[str, Any]] = None

class TimelineBuildRequest(BaseModel):
    sort_by_date: Optional[bool] = True

class TranscribeRequest(BaseModel):
    audio_path: str
    language: Optional[str] = "en"
    transcript_type: Optional[str] = "general"  # "general" or "court"

class TTSRequest(BaseModel):
    text: str
    voice: Optional[str] = "en-US-AriaNeural"
    rate: Optional[str] = "+0%"
    pitch: Optional[str] = "+0Hz"

class SummarizeAndSpeakRequest(BaseModel):
    text: str
    summary_length: Optional[str] = "short"  # "short", "medium", "long"
    voice: Optional[str] = "en-US-AriaNeural"

class ComplianceRequest(BaseModel):
    content: str
    jurisdiction: Optional[str] = "US"
    check_gdpr: Optional[bool] = False
    check_us_code: Optional[bool] = False
    check_eu_lex: Optional[bool] = False

class ClauseAnalysisRequest(BaseModel):
    content: str
    jurisdiction: Optional[str] = "US"
    analyze_full_document: Optional[bool] = True
    clause_text: Optional[str] = None  # If provided, analyze only this clause

class SummarizeRequest(BaseModel):
    case_text: str
    case_name: Optional[str] = None
    extract_type: Optional[str] = "all"  # "headnotes", "ratio", "obiter", "contrastive", "all"

class PrecedentAlignmentRequest(BaseModel):
    position: str
    position_type: Optional[str] = "plaintiff"  # "plaintiff", "defendant", "neutral"
    max_cases: Optional[int] = 10

class PrecedentStatusRequest(BaseModel):
    case_name: str
    case_text: Optional[str] = None

class ContractComparisonRequest(BaseModel):
    contract1_text: str
    contract2_text: str
    contract1_name: Optional[str] = None
    contract2_name: Optional[str] = None
    jurisdiction: Optional[str] = "US"

class ClauseGenerationRequest(BaseModel):
    clause_type: str
    contract_context: Optional[str] = None
    jurisdiction: Optional[str] = "US"
    custom_requirements: Optional[str] = None

class MissingClausesRequest(BaseModel):
    contract_text: str
    contract_type: Optional[str] = None
    jurisdiction: Optional[str] = "US"

class RegulatoryMonitoringRequest(BaseModel):
    contract_text: str
    jurisdiction: Optional[str] = "US"
    days_back: Optional[int] = 30

class MonteCarloSimulationRequest(BaseModel):
    contract_text: str
    scenarios: Optional[List[str]] = None
    num_simulations: Optional[int] = 1000
    jurisdiction: Optional[str] = "US"

class OrchestrationRequest(BaseModel):
    contract_text: str
    jurisdiction: Optional[str] = "US"
    workflow_type: Optional[str] = "comprehensive"  # "comprehensive", "research_draft", "consistency_check"

class ConsistencyCheckRequest(BaseModel):
    clause_text: str
    jurisdiction: Optional[str] = "US"

class HITLFeedbackRequest(BaseModel):
    feature_type: str
    action: str  # "accept", "reject", "edit"
    original_output: Dict[str, Any]
    user_edit: Optional[str] = None
    feedback_reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class DomainComplianceRequest(BaseModel):
    content: str
    domains: List[str]  # ["finance", "healthcare", "labor", "gdpr", "ccpa"]
    jurisdiction: Optional[str] = "US"

async def load_llm_models():
    """Load LLM models using Ollama (Refactored)"""
    global ollama_client, embeddings_model, ollama_model
    
    if not LLM_AVAILABLE or ollama is None:
        logger.warning("LLM libraries not available, using fallback responses")
        return
    
    try:
        logger.info("🤖 Loading Ollama models...")
        
        # Initialize Ollama client (using helper)
        ollama_client = await _initialize_ollama_client()
        if ollama_client is None:
            logger.error("❌ Failed to connect to Ollama")
            return
        
        # Get and parse models (using helper)
        try:
            if USE_ASYNC_CLIENT:
                models = await asyncio.wait_for(ollama_client.list(), timeout=5.0)
            else:
                import concurrent.futures
                loop = asyncio.get_event_loop()
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = loop.run_in_executor(executor, ollama_client.list)
                    models = await asyncio.wait_for(future, timeout=5.0)
        except (asyncio.TimeoutError, Exception) as e:
            logger.warning(f"Could not get models list: {e}")
            models = {'models': []}
                
        # Parse model names (using helper)
        model_names = _parse_ollama_models(models)
        if model_names:
            ollama_model = model_names[0]
            logger.info(f"🎯 Using model: {ollama_model}")
        else:
            logger.warning(f"⚠️ No models found, using default: {ollama_model}")
        
        # Load embeddings model
        if EMBEDDINGS_AVAILABLE and SentenceTransformer is not None:
            logger.info("Loading embeddings model...")
            try:
                embeddings_model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("✅ Embeddings model loaded successfully")
            except Exception as e:
                logger.warning(f"⚠️ Embeddings model failed: {e}")
                embeddings_model = None
        else:
            logger.info("Embeddings model not available (sentence_transformers not installed)")
            embeddings_model = None
            
    except Exception as e:
        logger.error(f"❌ Failed to load LLM models: {e}")
        ollama_client = None
        embeddings_model = None
    
    # Initialize Vector Store (optimized for large datasets)
    global vector_store
    if FAISS_AVAILABLE and VectorStore is not None:
        try:
            logger.info("🔍 Initializing Vector Store (optimized for large datasets)...")
            # Use 'auto' to automatically choose best index type based on dataset size
            vector_store = VectorStore(index_type='auto', persist_dir='data/vector_store')
            logger.info("✅ Vector Store initialized successfully")
            
            # Initialize Hybrid Retriever
            global hybrid_retriever
            if HYBRID_RETRIEVER_AVAILABLE and HybridRetriever is not None:
                try:
                    hybrid_retriever = HybridRetriever(vector_store=vector_store)
                    logger.info("✅ Hybrid Retriever initialized")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to initialize Hybrid Retriever: {e}")
                    hybrid_retriever = None
            
            # Check if we loaded existing documents or need to add samples
            doc_count = vector_store.get_document_count()
            if doc_count > 0:
                logger.info(f"📂 Loaded {doc_count} existing documents from disk")
                # Index existing documents for BM25
                if hybrid_retriever:
                    try:
                        # Get all documents from vector store for BM25 indexing
                        all_docs = []
                        for i in range(doc_count):
                            doc = vector_store.get_document(i)
                            if doc:
                                all_docs.append(doc)
                        hybrid_retriever.index_documents(all_docs)
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to index documents for BM25: {e}")
            else:
                # Add sample legal documents to vector store if empty
                logger.info("📚 Adding sample legal documents to vector store...")
                sample_documents = [
                    {
                        "text": "Smith v. Jones Contract Dispute (2023). This landmark case established important principles for contract enforceability. The court held that performance metrics must be clearly defined and measurable to be enforceable. The decision emphasized the importance of specific terms in service agreements and the need for clear performance standards.",
                        "metadata": {
                            "type": "case_law",
                            "title": "Smith v. Jones Contract Dispute",
                            "court": "Supreme Court",
                            "year": 2023,
                            "tags": ["contract", "dispute", "software", "breach", "performance"],
                            "citations": ["Smith v. Jones, 2023 SC 123"]
                        }
                    },
                    {
                        "text": "Data Privacy Compliance v. TechCorp (2023). This case set important precedents for GDPR compliance in data processing agreements. The court found multiple violations including inadequate consent mechanisms, insufficient data protection measures, and failure to provide proper data subject rights. The ruling established stricter standards for data processing consent and privacy notices.",
                        "metadata": {
                            "type": "case_law",
                            "title": "Data Privacy Compliance v. TechCorp",
                            "court": "Federal Court",
                            "year": 2023,
                            "tags": ["gdpr", "privacy", "data", "compliance", "consent"],
                            "citations": ["Data Privacy Compliance v. TechCorp, 2023 FC 456"]
                        }
                    },
                    {
                        "text": "Employment Termination Procedures Act (2022). This legislation establishes comprehensive requirements for employee termination procedures including notice periods, severance pay calculations, and documentation requirements. The act applies to all employers with more than 50 employees and requires written notice of termination at least 30 days in advance.",
                        "metadata": {
                            "type": "legislation",
                            "title": "Employment Termination Procedures Act",
                            "year": 2022,
                            "tags": ["employment", "termination", "labor", "compliance"],
                            "citations": ["ETPA 2022, Section 15"]
                        }
                    },
                    {
                        "text": "Intellectual Property Rights in Software Development. Software code, algorithms, and technical documentation are protected under copyright law as literary works. Patents may apply to novel software processes and methods. Trade secrets protect proprietary algorithms and business logic. Open source licenses determine usage rights and obligations.",
                        "metadata": {
                            "type": "legal_principle",
                            "title": "Intellectual Property in Software",
                            "tags": ["intellectual_property", "software", "copyright", "patent", "trade_secret"],
                            "citations": ["Copyright Act Section 101", "Patent Act Section 35"]
                        }
                    },
                    {
                        "text": "Liability Limitations in Service Agreements. Service providers may limit liability through contractual provisions, but such limitations must be reasonable and not violate public policy. Limitations on consequential damages are generally enforceable, while limitations on gross negligence or willful misconduct are often unenforceable. Jurisdiction-specific variations apply.",
                        "metadata": {
                            "type": "legal_principle",
                            "title": "Liability Limitations in Service Agreements",
                            "tags": ["liability", "service_agreement", "limitation", "damages"],
                            "citations": ["Hadley v. Baxendale (1854)", "Various state court decisions"]
                        }
                    }
                ]
                
                texts = [doc["text"] for doc in sample_documents]
                metadata_list = [doc["metadata"] for doc in sample_documents]
                doc_ids = vector_store.add_documents(texts, metadata_list, batch_size=10)
                logger.info(f"✅ Added {len(sample_documents)} sample documents to vector store")
                
                # Index documents for BM25 hybrid search
                if hybrid_retriever:
                    try:
                        # Get all documents from vector store (including newly added samples)
                        all_docs = []
                        total_docs = vector_store.get_document_count()
                        for i in range(total_docs):
                            doc = vector_store.get_document(i)
                            if doc:
                                all_docs.append(doc)
                        
                        hybrid_retriever.index_documents(all_docs)
                        logger.info(f"✅ Indexed {len(all_docs)} documents for BM25 hybrid search")
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to index for BM25: {e}")
                        import traceback
                        logger.error(traceback.format_exc())
                
                # Save after adding samples
                vector_store.save()
        except Exception as e:
            logger.warning(f"⚠️ Failed to initialize Vector Store: {e}")
            vector_store = None
    else:
        logger.warning("⚠️ Vector Store not available (FAISS not installed)")
    
    # Initialize Clause Analyzer
    global clause_analyzer
    if CLAUSE_ANALYZER_AVAILABLE and ClauseAnalyzer is not None:
        try:
            clause_analyzer = ClauseAnalyzer()
            logger.info("✅ Clause Analyzer initialized")
        except Exception as e:
            logger.warning(f"⚠️ Failed to initialize Clause Analyzer: {e}")
            clause_analyzer = None
    else:
        logger.warning("⚠️ Clause Analyzer not available")
    
    # Initialize Summarization Agent
    global summarization_agent
    if SUMMARIZATION_AVAILABLE and SummarizationAgent is not None and ollama_client is not None:
        try:
            summarization_agent = SummarizationAgent(
                ollama_client=ollama_client,
                ollama_model=ollama_model
            )
            logger.info("✅ Summarization Agent initialized")
        except Exception as e:
            logger.warning(f"⚠️ Failed to initialize Summarization Agent: {e}")
            summarization_agent = None
    else:
        if not SUMMARIZATION_AVAILABLE:
            logger.warning("⚠️ Summarization Agent not available (module not found)")
        elif ollama_client is None:
            logger.warning("⚠️ Summarization Agent not available (Ollama client not initialized)")
    
    # Initialize Precedent Reasoning Agent
    global precedent_reasoning_agent
    if PRECEDENT_REASONING_AVAILABLE and PrecedentReasoningAgent is not None:
        try:
            precedent_reasoning_agent = PrecedentReasoningAgent(
                hybrid_retriever=hybrid_retriever,
                vector_store=vector_store,
                ollama_client=ollama_client,
                ollama_model=ollama_model
            )
            logger.info("✅ Precedent Reasoning Agent initialized")
        except Exception as e:
            logger.warning(f"⚠️ Failed to initialize Precedent Reasoning Agent: {e}")
            precedent_reasoning_agent = None
    else:
        if not PRECEDENT_REASONING_AVAILABLE:
            logger.warning("⚠️ Precedent Reasoning Agent not available (module not found)")
    
    # Initialize Knowledge Graph Builder
    global knowledge_graph
    if KNOWLEDGE_GRAPH_AVAILABLE and KnowledgeGraphBuilder is not None:
        try:
            knowledge_graph = KnowledgeGraphBuilder(
                vector_store=vector_store,
                hybrid_retriever=hybrid_retriever
            )
            logger.info("✅ Knowledge Graph Builder initialized")
            # Build graph in background (non-blocking)
            asyncio.create_task(knowledge_graph.build_graph_async(max_documents=500))
            logger.info("📊 Knowledge graph building started in background")
        except Exception as e:
            logger.warning(f"⚠️ Failed to initialize Knowledge Graph Builder: {e}")
            knowledge_graph = None
    else:
        if not KNOWLEDGE_GRAPH_AVAILABLE:
            logger.warning("⚠️ Knowledge Graph Builder not available (module not found)")
    
    # Initialize Redlining & Comparison Agent
    global redlining_agent
    if REDLINING_AVAILABLE and RedliningComparisonAgent is not None:
        try:
            redlining_agent = RedliningComparisonAgent(
                clause_analyzer=clause_analyzer,
                ollama_client=ollama_client,
                ollama_model=ollama_model,
                embeddings_model=embeddings_model
            )
            logger.info("✅ Redlining & Comparison Agent initialized")
        except Exception as e:
            logger.warning(f"⚠️ Failed to initialize Redlining & Comparison Agent: {e}")
            redlining_agent = None
    else:
        if not REDLINING_AVAILABLE:
            logger.warning("⚠️ Redlining & Comparison Agent not available (module not found)")
    
    # Initialize Clause Generation Agent
    global clause_generation_agent
    if CLAUSE_GENERATION_AVAILABLE and ClauseGenerationAgent is not None:
        try:
            clause_generation_agent = ClauseGenerationAgent(
                ollama_client=ollama_client,
                ollama_model=ollama_model,
                hybrid_retriever=hybrid_retriever
            )
            logger.info("✅ Clause Generation Agent initialized")
        except Exception as e:
            logger.warning(f"⚠️ Failed to initialize Clause Generation Agent: {e}")
            clause_generation_agent = None
    else:
        if not CLAUSE_GENERATION_AVAILABLE:
            logger.warning("⚠️ Clause Generation Agent not available (module not found)")
    
    # Initialize Regulatory Monitoring Agent
    global regulatory_monitoring_agent
    if REGULATORY_MONITORING_AVAILABLE and RegulatoryMonitoringAgent is not None:
        try:
            regulatory_monitoring_agent = RegulatoryMonitoringAgent(
                ollama_client=ollama_client,
                ollama_model=ollama_model,
                vector_store=vector_store
            )
            logger.info("✅ Regulatory Monitoring Agent initialized")
        except Exception as e:
            logger.warning(f"⚠️ Failed to initialize Regulatory Monitoring Agent: {e}")
            regulatory_monitoring_agent = None
    else:
        if not REGULATORY_MONITORING_AVAILABLE:
            logger.warning("⚠️ Regulatory Monitoring Agent not available (module not found)")
    
    # Initialize Monte Carlo Risk Agent
    global monte_carlo_agent
    if MONTE_CARLO_AVAILABLE and MonteCarloRiskAgent is not None:
        try:
            monte_carlo_agent = MonteCarloRiskAgent(
                clause_analyzer=clause_analyzer,
                ollama_client=ollama_client,
                ollama_model=ollama_model
            )
            logger.info("✅ Monte Carlo Risk Agent initialized")
        except Exception as e:
            logger.warning(f"⚠️ Failed to initialize Monte Carlo Risk Agent: {e}")
            monte_carlo_agent = None
    else:
        if not MONTE_CARLO_AVAILABLE:
            logger.warning("⚠️ Monte Carlo Risk Agent not available (module not found)")
    
    # Initialize LangGraph Orchestrator
    global langgraph_orchestrator
    if LANGGRAPH_AVAILABLE and LangGraphOrchestrator is not None:
        try:
            langgraph_orchestrator = LangGraphOrchestrator(
                summarization_agent=summarization_agent,
                precedent_reasoning_agent=precedent_reasoning_agent,
                clause_analyzer=clause_analyzer,
                clause_generation_agent=clause_generation_agent,
                redlining_agent=redlining_agent,
                regulatory_monitoring_agent=regulatory_monitoring_agent,
                monte_carlo_agent=monte_carlo_agent,
                ollama_client=ollama_client,
                ollama_model=ollama_model
            )
            logger.info("✅ LangGraph Orchestrator initialized")
        except ImportError as e:
            logger.warning(f"⚠️ LangGraph not installed: {e}")
            langgraph_orchestrator = None
        except Exception as e:
            logger.warning(f"⚠️ Failed to initialize LangGraph Orchestrator: {e}")
            langgraph_orchestrator = None
    else:
        if not LANGGRAPH_AVAILABLE:
            logger.warning("⚠️ LangGraph Orchestrator not available (LangGraph not installed)")
    
    # Initialize Multi-Modal Legal Intelligence Agents
    global ocr_agent, timeline_builder_agent, speech_tts_agent
    
    # Initialize OCR Agent
    if OCR_AVAILABLE and OCRAgent is not None:
        try:
            ocr_agent = OCRAgent()
            logger.info("✅ OCR Agent initialized")
        except Exception as e:
            logger.warning(f"⚠️ Failed to initialize OCR Agent: {e}")
            ocr_agent = None
    else:
        if not OCR_AVAILABLE:
            logger.warning("⚠️ OCR Agent not available")
    
    # Initialize Timeline Builder Agent
    if TIMELINE_BUILDER_AVAILABLE and TimelineBuilderAgent is not None:
        try:
            timeline_builder_agent = TimelineBuilderAgent(ocr_agent=ocr_agent)
            logger.info("✅ Timeline Builder Agent initialized")
        except Exception as e:
            logger.warning(f"⚠️ Failed to initialize Timeline Builder Agent: {e}")
            timeline_builder_agent = None
    else:
        if not TIMELINE_BUILDER_AVAILABLE:
            logger.warning("⚠️ Timeline Builder Agent not available")
    
    # Initialize Speech TTS Agent
    if SPEECH_TTS_AVAILABLE and SpeechTTSAgent is not None:
        try:
            speech_tts_agent = SpeechTTSAgent()
            logger.info("✅ Speech TTS Agent initialized")
        except Exception as e:
            logger.warning(f"⚠️ Failed to initialize Speech TTS Agent: {e}")
            speech_tts_agent = None
    else:
        if not SPEECH_TTS_AVAILABLE:
            logger.warning("⚠️ Speech TTS Agent not available")
    
    # Initialize Explainability Service
    global explainability_service
    if EXPLAINABILITY_AVAILABLE and ExplainabilityService is not None:
        try:
            explainability_service = ExplainabilityService()
            logger.info("✅ Explainability Service initialized")
        except Exception as e:
            logger.warning(f"⚠️ Failed to initialize Explainability Service: {e}")
            explainability_service = None
    else:
        if not EXPLAINABILITY_AVAILABLE:
            logger.warning("⚠️ Explainability Service not available")
    
    # Initialize HITL Service
    global hitl_service
    if HITL_AVAILABLE and HITLService is not None:
        try:
            feedback_file = os.path.join(os.path.dirname(__file__), "..", "feedback_data.json")
            learning_file = os.path.join(os.path.dirname(__file__), "..", "learning_patterns.json")
            hitl_service = HITLService(feedback_file=feedback_file, learning_file=learning_file)
            logger.info("✅ HITL Service initialized")
        except Exception as e:
            logger.warning(f"⚠️ Failed to initialize HITL Service: {e}")
            hitl_service = None
    else:
        if not HITL_AVAILABLE:
            logger.warning("⚠️ HITL Service not available")
    
    # Initialize Domain Compliance Packs
    global domain_compliance_packs
    if DOMAIN_COMPLIANCE_AVAILABLE and DomainCompliancePacks is not None:
        try:
            domain_compliance_packs = DomainCompliancePacks()
            logger.info("✅ Domain Compliance Packs initialized")
        except Exception as e:
            logger.warning(f"⚠️ Failed to initialize Domain Compliance Packs: {e}")
            domain_compliance_packs = None
    else:
        if not DOMAIN_COMPLIANCE_AVAILABLE:
            logger.warning("⚠️ Domain Compliance Packs not available")

# ============================================================================
# Helper Functions for Research Legal Query (Complexity Reduction)
# ============================================================================

async def _fetch_courtlistener_cases(query: str, max_results: int) -> List[Dict[str, Any]]:
    """Fetch case law from CourtListener API"""
    if not COURTLISTENER_AVAILABLE:
        return []
    
    try:
        courtlistener_service = get_courtlistener_service()
        if not courtlistener_service:
            logger.warning("⚠️ CourtListener service not available")
            return []
        
        logger.info(f"📡 Fetching case law from CourtListener API for query: '{query}'...")
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(
                courtlistener_service.search_cases,
                query,
                max_results=max_results,
                court_type=None
            )
            case_law_results = future.result(timeout=15)
            logger.info(f"✅ Found {len(case_law_results)} cases from CourtListener API")
            if case_law_results:
                logger.info(f"   First case: {case_law_results[0].get('case_name', 'Unknown')[:60]}...")
            return case_law_results
    except concurrent.futures.TimeoutError:
        logger.warning("⚠️ CourtListener API timeout (15s)")
        return []
    except Exception as e:
        logger.warning(f"⚠️ CourtListener API error: {e}")
        return []

def _format_hybrid_search_results(search_results: List[Dict], similarity_threshold: float, max_results: int) -> List[Dict[str, Any]]:
    """Format hybrid search results"""
    relevant_docs = []
    for result in search_results:
        combined_score = result.get('combined_score', 0)
        if combined_score >= similarity_threshold:
            metadata = result.get('metadata', {})
            relevant_docs.append({
                "id": result.get('id', 'unknown'),
                "score": combined_score,
                "semantic_score": result.get('semantic_score', 0.0),
                "keyword_score": result.get('keyword_score', 0.0),
                "content": result.get('text', ''),
                "title": metadata.get('title', 'Legal Document'),
                "tags": metadata.get('tags', []),
                "court": metadata.get('court', 'Unknown'),
                "year": metadata.get('year', 'Unknown'),
                "citations": metadata.get('citations', []),
                "type": metadata.get('type', 'document'),
                "search_method": "hybrid"
            })
    
    relevant_docs.sort(key=lambda x: x["score"], reverse=True)
    return relevant_docs[:max_results]

def _format_faiss_search_results(search_results: List[Dict], similarity_threshold: float, max_results: int) -> List[Dict[str, Any]]:
    """Format FAISS search results"""
    relevant_docs = []
    for result in search_results:
        if result.get('score', 0) >= similarity_threshold:
            metadata = result.get('metadata', {})
            relevant_docs.append({
                "id": result.get('id', 'unknown'),
                "score": result.get('score', 0.0),
                "content": result.get('text', ''),
                "title": metadata.get('title', 'Legal Document'),
                "tags": metadata.get('tags', []),
                "court": metadata.get('court', 'Unknown'),
                "year": metadata.get('year', 'Unknown'),
                "citations": metadata.get('citations', []),
                "type": metadata.get('type', 'document'),
                "distance": result.get('distance', 0.0),
                "search_method": "semantic_only"
            })
    
    relevant_docs.sort(key=lambda x: x["score"], reverse=True)
    return relevant_docs[:max_results]

def _convert_courtlistener_case_to_doc(case: Dict[str, Any]) -> Dict[str, Any]:
    """Convert CourtListener API case to document format"""
    # Generate case ID
    case_id_raw = case.get("id", "")
    if isinstance(case_id_raw, str) and case_id_raw.startswith("courtlistener_"):
        case_id = case_id_raw
    elif case_id_raw and str(case_id_raw).strip():
        case_id = f"courtlistener_{case_id_raw}"
    else:
        case_name_slug = case.get("case_name", "").replace(" ", "_").replace(".", "").replace(",", "")[:50] if case.get("case_name") else "unknown"
        case_id = f"courtlistener_{abs(hash(case_name_slug)) % 100000}"
    
    # Build content from opinion text and metadata
    content_parts = []
    opinion_text = case.get("opinion_text", "")
    if opinion_text and len(opinion_text.strip()) > 100:
        content_parts.append(opinion_text[:800])
    elif opinion_text and len(opinion_text.strip()) > 50:
        content_parts.append(opinion_text)
    
    # Build metadata summary
    metadata_parts = []
    case_name = case.get("case_name", "")
    citation = case.get("citation", "")
    court = case.get("court", "")
    date_filed = case.get("date_filed", "")
    
    if case_name:
        metadata_parts.append(f"Case: {case_name}")
    if citation:
        if isinstance(citation, str):
            citation_str = citation
        elif isinstance(citation, list):
            citation_str = ", ".join([c for c in citation if c])
        else:
            citation_str = str(citation)
        if citation_str:
            metadata_parts.append(f"Citation: {citation_str}")
    if court:
        metadata_parts.append(f"Court: {court}")
    if date_filed:
        metadata_parts.append(f"Date: {date_filed}")
    
    # Combine content
    if content_parts:
        content = content_parts[0] + ("\n\n[" + " | ".join(metadata_parts) + "]" if metadata_parts else "")
    elif metadata_parts:
        content = "Case metadata available, but opinion text not included in search results.\n\n" + " | ".join(metadata_parts)
        if case.get("url"):
            content += f"\n\nTo view full case details, visit: {case.get('url')}"
    else:
        content = case_name if case_name else "Case Law from CourtListener API"
    
    if not content or len(content.strip()) < 10:
        content = f"Case: {case_name}" if case_name else "Case Law from CourtListener API"
    
    # Handle citations
    citations = []
    if case.get("citation"):
        if isinstance(case["citation"], str):
            citations = [case["citation"]]
        elif isinstance(case["citation"], list):
            citations = case["citation"]
    
    # Calculate score
    keyword_score = case.get("api_score", 0.7)
    if not case.get("opinion_text") or len(case.get("opinion_text", "").strip()) < 100:
        keyword_score = min(keyword_score, 0.75)
        if not case_name or not court:
            keyword_score = max(0.5, keyword_score - 0.1)
    
    return {
        "id": case_id,
        "score": keyword_score,
        "semantic_score": 0.0,
        "keyword_score": keyword_score,
        "content": content,
        "title": case.get("case_name", "Case Law"),
        "tags": [],
        "court": case.get("court", "Unknown"),
        "year": case.get("date_filed", "")[:4] if case.get("date_filed") else "Unknown",
        "citations": citations,
        "type": "case_law",
        "search_method": "courtlistener_api",
        "jurisdiction": case.get("jurisdiction", ""),
        "url": case.get("url", ""),
        "docket_number": case.get("docket_number", "")
    }

def _generate_fallback_summary(query: str, relevant_docs: List[Dict[str, Any]]) -> str:
    """Generate fallback summary when AI summary is not available"""
    doc_count = len(relevant_docs)
    api_count = sum(1 for doc in relevant_docs if doc.get("search_method") == "courtlistener_api")
    vector_count = doc_count - api_count
    
    summary = f"""LEGAL RESEARCH ANALYSIS
Query: {query}
Date: {time.strftime("%B %d, %Y")}

EXECUTIVE SUMMARY:
This analysis examines the legal aspects of "{query}", providing research findings and recommendations.

RELEVANT DOCUMENTS FOUND:
{doc_count} relevant document{'s' if doc_count != 1 else ''} {'has' if doc_count == 1 else 'have'} been identified.
"""
    if api_count > 0:
        summary += f"- {api_count} case{'s' if api_count != 1 else ''} from CourtListener API\n"
    if vector_count > 0:
        summary += f"- {vector_count} document{'s' if vector_count != 1 else ''} from local database\n"
    
    summary += """
Please review the relevant documents below for detailed information.

This research is based on:
- Semantic similarity search through legal document database
- Real-time case law retrieval from CourtListener API
- AI-powered legal analysis
"""
    return summary

# ============================================================================
# Helper Functions for Load LLM Models (Complexity Reduction)
# ============================================================================

async def _initialize_ollama_client() -> Optional[Any]:
    """Initialize and return Ollama client"""
    if not LLM_AVAILABLE or ollama is None:
        return None
    
    try:
        ollama_host = os.getenv('OLLAMA_HOST', 'http://127.0.0.1:11434')
        logger.info(f"🔗 Connecting to Ollama at: {ollama_host}")
        
        if USE_ASYNC_CLIENT:
            client = AsyncClient(host=ollama_host)
            logger.info("✅ Ollama async client created")
        else:
            client = ollama.Client(host=ollama_host)
            logger.info("✅ Ollama sync client created")
        
        # Test connection
        try:
            if USE_ASYNC_CLIENT:
                models = await asyncio.wait_for(client.list(), timeout=5.0)
            else:
                import concurrent.futures
                loop = asyncio.get_event_loop()
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = loop.run_in_executor(executor, client.list)
                    models = await asyncio.wait_for(future, timeout=5.0)
            logger.info("✅ Ollama client connected successfully")
            return client
        except asyncio.TimeoutError:
            logger.warning("Ollama list() call timed out")
            return client  # Return client anyway
        except Exception as e:
            logger.warning(f"Ollama list() call failed: {e}")
            return client  # Return client anyway
    except Exception as e:
        logger.error(f"❌ Failed to connect to Ollama: {e}")
        return None

def _parse_ollama_models(models: Any) -> List[str]:
    """Parse Ollama models from various response formats"""
    model_names = []
    
    if models is None:
        return model_names
    
    # Check if response is a dictionary with 'models' key
    if isinstance(models, dict) and 'models' in models:
        logger.info("📋 Found 'models' key in dictionary response")
        for model in models['models']:
            name = _extract_model_name(model)
            if name:
                model_names.append(name)
                logger.info(f"✅ Added model: {name}")
    
    # Check if response has 'models' attribute (ListResponse object)
    elif hasattr(models, 'models') and models.models:
        logger.info("📋 Found 'models' attribute in response")
        for model in models.models:
            name = _extract_model_name(model)
            if name:
                model_names.append(name)
                logger.info(f"✅ Added model: {name}")
    
    # If response is a list
    elif isinstance(models, list):
        logger.info("📋 Response is a list, checking directly")
        for model in models:
            name = _extract_model_name(model)
            if name:
                model_names.append(name)
                logger.info(f"✅ Added model: {name}")
    
    return model_names

def _extract_model_name(model: Any) -> Optional[str]:
    """Extract model name from model object/dict"""
    if isinstance(model, dict):
        name = model.get('name', model.get('model', '')).strip()
    else:
        name = getattr(model, 'name', getattr(model, 'model', '')).strip()
    
    if name and name != 'unknown' and name != '':
        return name
    return None

async def generate_ai_response(prompt: str, max_tokens: int = 1000, use_full_response: bool = True) -> str:
    """Generate AI response using Ollama or enhanced fallback
    
    Args:
        prompt: Input prompt
        max_tokens: Maximum tokens (used for estimates, but can be overridden)
        use_full_response: If True, don't limit response length (allow complete sentences)
    """
    global ollama_model
    
    if ollama_client is None:
        logger.warning("Ollama client is None - using fallback")
        return generate_enhanced_fallback_response(prompt)
    
    try:
        logger.info(f"🤖 Generating AI response for prompt: {prompt[:50]}...")
        
        # Check if model is available
        try:
            # Get available models (async or sync)
            if USE_ASYNC_CLIENT:
                models = await ollama_client.list()
            else:
                models = ollama_client.list()
            
            available_models = []
            # Check if response is a dictionary with 'models' key
            if isinstance(models, dict) and 'models' in models:
                for model in models['models']:
                    if isinstance(model, dict):
                        name = model.get('name', model.get('model', '')).strip()
                    else:
                        name = getattr(model, 'name', getattr(model, 'model', '')).strip()
                    if name and name != 'unknown':
                        available_models.append(name)
            # Check if response has 'models' attribute (ListResponse object)
            elif hasattr(models, 'models') and models.models:
                for model in models.models:
                    name = getattr(model, 'model', getattr(model, 'name', '')).strip()
                    if name and name != 'unknown':
                        available_models.append(name)
            # If response is a list
            elif isinstance(models, list):
                for model in models:
                    if isinstance(model, dict):
                        name = model.get('name', model.get('model', '')).strip()
                    else:
                        name = getattr(model, 'name', getattr(model, 'model', '')).strip()
                    if name and name != 'unknown':
                        available_models.append(name)
            
            if not available_models:
                logger.error("❌ No valid models found in Ollama container")
                logger.error("💡 To install a model, run: docker exec legisai-ollama ollama pull llama3.1:8b")
                logger.error("   Or restart with: docker compose up -d (the startup script should pull it automatically)")
                return generate_enhanced_fallback_response(prompt)
            
            if ollama_model not in available_models:
                logger.warning(f"⚠️ Model {ollama_model} not found. Using first available: {available_models[0]}")
                ollama_model = available_models[0]
        except Exception as e:
            logger.error(f"❌ Failed to check available models: {e}")
            return generate_enhanced_fallback_response(prompt)
        
        # Generate response using Ollama with proper async timeout
        # Extended timeout for slow models (600 seconds / 10 minutes) for full responses
        timeout_seconds = 600.0
        
        try:
            # Configure generation options
            gen_options = {
                'temperature': 0.7,
                'top_p': 0.9,
                'stop': ['\n\n---', '\n\n##', '---']
            }
            
            # Only set num_predict if we're not using full response mode
            if not use_full_response:
                gen_options['num_predict'] = max_tokens
            
            if USE_ASYNC_CLIENT:
                # Use async client directly
                response = await asyncio.wait_for(
                    ollama_client.generate(
                        model=ollama_model,
                        prompt=prompt,
                        options=gen_options
                    ),
                    timeout=timeout_seconds
                )
            else:
                # Use sync client in executor
                import concurrent.futures
                loop = asyncio.get_event_loop()
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = loop.run_in_executor(
                        executor,
                        lambda: ollama_client.generate(
                            model=ollama_model,
                            prompt=prompt,
                            options=gen_options
                        )
                    )
                    response = await asyncio.wait_for(future, timeout=timeout_seconds)
        except asyncio.TimeoutError:
            logger.warning(f"Ollama generation timed out after {timeout_seconds}s (using faster fallback)")
            return generate_enhanced_fallback_response(prompt)
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            logger.error(f"Error details: {type(e).__name__}: {str(e)}")
            return generate_enhanced_fallback_response(prompt)
        
        # Handle response format
        if isinstance(response, dict):
            generated_text = response.get('response', '').strip()
        elif hasattr(response, 'response'):
            generated_text = response.response.strip()
        else:
            generated_text = str(response).strip()
        
        if generated_text:
            logger.info(f"✅ AI response generated successfully: {generated_text[:100]}...")
            logger.info(f"✅ Full response length: {len(generated_text)} characters")
            return generated_text
        else:
            logger.warning("AI generated empty response - using fallback")
            return generate_enhanced_fallback_response(prompt)
            
    except Exception as e:
        logger.error(f"❌ AI generation failed: {e}")
        logger.error(f"❌ Ollama client: {ollama_client}")
        return generate_enhanced_fallback_response(prompt)

async def generate_ai_response_stream(prompt: str):
    """Generate AI response with streaming for word-by-word display"""
    global ollama_model
    
    if ollama_client is None:
        yield "data: " + json.dumps({"content": "LLM not available", "done": True}) + "\n\n"
        return
    
    try:
        logger.info(f"🌊 Starting streaming AI response for: {prompt[:50]}...")
        
        # Generate response using Ollama with streaming
        # For async client, we need to iterate the awaitable result
        async def get_stream():
            async for chunk in await ollama_client.generate(
                model=ollama_model,
                prompt=prompt,
                stream=True,
                options={
                    'temperature': 0.7,
                    'top_p': 0.9,
                }
            ):
                yield chunk
        
        async for chunk in get_stream():
            try:
                # Extract content from chunk
                if hasattr(chunk, 'response'):
                    content = chunk.response
                elif isinstance(chunk, dict):
                    content = chunk.get('response', '')
                else:
                    content = str(chunk) if chunk else ''
                
                if content:
                    logger.info(f"📤 Streaming chunk: '{content[:20]}...' ({len(content)} chars)")
                    yield "data: " + json.dumps({"content": content, "done": False}) + "\n\n"
                
                # Check if this is the final chunk
                if hasattr(chunk, 'done') and chunk.done:
                    break
            except Exception as e:
                logger.error(f"❌ Error processing chunk: {e}")
                continue
        
        # Send done signal
        logger.info("✅ Streaming complete")
        yield "data: " + json.dumps({"content": "", "done": True}) + "\n\n"
        
    except Exception as e:
        logger.error(f"❌ Streaming error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        yield "data: " + json.dumps({"error": str(e), "done": True}) + "\n\n"

async def generate_structured_legal_research(query: str) -> str:
    """Generate structured legal research using AI"""
    
    # Use AI to generate comprehensive legal research
    research_prompt = f"""As a legal research assistant, provide a comprehensive analysis of the following legal query:

Query: "{query}"

Please provide:
1. EXECUTIVE SUMMARY - Brief overview of the topic
2. KEY LEGAL PRINCIPLES - Important legal concepts and rules
3. RELEVANT LEGAL CONSIDERATIONS - Jurisdiction-specific requirements and variations
4. RISK ASSESSMENT - Potential legal risks and their severity
5. COMPLIANCE REQUIREMENTS - Regulatory and statutory obligations
6. PRACTICAL RECOMMENDATIONS - Actionable steps
7. CASE LAW REFERENCES - Relevant precedents (if applicable)
8. NEXT STEPS - Recommended actions

Format the response in a clear, professional manner with proper sections. Be specific to the query and provide jurisdiction-specific details where mentioned."""

    try:
        logger.info(f"🤖 Generating AI-powered legal research for: {query[:50]}...")
        ai_research = await asyncio.wait_for(
            generate_ai_response(research_prompt, max_tokens=800, use_full_response=True),
            timeout=600.0
        )
        
        if ai_research and "FALLBACK RESPONSE" not in ai_research and "LLM NOT WORKING" not in ai_research:
            logger.info("✅ AI research generated successfully")
            return f"LEGAL RESEARCH ANALYSIS\nQuery: {query}\nDate: {time.strftime('%B %d, %Y')}\n\n{ai_research}\n\n---\nThis research analysis is provided for informational purposes only and does not constitute legal advice."
        else:
            logger.warning("AI research failed, using fallback")
    except asyncio.TimeoutError:
        logger.warning("AI research timed out, using fallback")
    except Exception as e:
        logger.warning(f"AI research failed: {e}, using fallback")
    
    # Fallback to template-based approach
    if "liability" in query.lower() and "service" in query.lower():
        template = f"""LEGAL RESEARCH ANALYSIS
Query: {query}
Date: {time.strftime("%B %d, %Y")}

EXECUTIVE SUMMARY:
This analysis examines liability limitations in service agreements, focusing on legal frameworks, risk management strategies, and compliance requirements for service providers.

KEY LEGAL PRINCIPLES:
• Limitation of Liability Clauses: Legal enforceability varies by jurisdiction
• Standard of Care: Professional duty and negligence standards apply
• Indemnification Provisions: Scope and enforceability considerations
• Force Majeure Clauses: Circumstances beyond reasonable control
• Consequential Damages: Limitations on indirect and special damages

RELEVANT LEGAL CONSIDERATIONS:
• Jurisdictional Variations: State and federal law differences
• Industry Standards: Professional service industry requirements
• Insurance Requirements: Professional liability coverage obligations
• Contract Formation: Essential elements for enforceable agreements
• Public Policy Limitations: Restrictions on liability limitations

RISK ASSESSMENT:
• High Risk: Unlimited liability exposure without proper limitations
• Medium Risk: Inadequate limitation clauses or improper drafting
• Low Risk: Well-drafted limitations with appropriate carve-outs

COMPLIANCE REQUIREMENTS:
• Professional Standards: Industry-specific compliance obligations
• Regulatory Compliance: Federal and state regulatory requirements
• Documentation Standards: Proper contract drafting and execution
• Disclosure Requirements: Transparency in limitation provisions

PRACTICAL RECOMMENDATIONS:
1. Draft clear, specific limitation clauses with appropriate carve-outs
2. Include indemnification provisions for third-party claims
3. Maintain professional liability insurance coverage
4. Regular contract review and updates
5. Legal consultation for complex agreements

CASE LAW REFERENCES:
• Hadley v. Baxendale (1854) - Consequential damages limitation
• Various state court decisions on limitation clause enforceability
• Professional liability case law precedents

NEXT STEPS:
1. Review existing service agreements for adequate limitations
2. Consult with qualified legal counsel for specific drafting
3. Implement risk management strategies
4. Ensure compliance with applicable regulations

CONFIDENCE LEVEL: High
RESEARCH COMPLETENESS: Comprehensive
RECOMMENDED ACTION: Professional legal consultation advised

---
This research analysis is provided for informational purposes only and does not constitute legal advice."""
        
        # Try to enhance with AI for specific details with timeout
        try:
            enhancement_prompt = f"""Add specific legal considerations for liability limitations in service agreements related to: "{query}"

            Focus on:
            - Specific limitation clause language
            - Industry-specific considerations
            - Recent legal developments
            - Practical implementation tips
            
            Keep response concise and professional."""
            
            # Add timeout to prevent hanging
            ai_enhancement = await asyncio.wait_for(
                generate_ai_response(enhancement_prompt, max_tokens=500, use_full_response=True),
                timeout=600.0  # 600 second (10 minute) timeout
            )
            if ai_enhancement and "FALLBACK RESPONSE" not in ai_enhancement and "LLM NOT WORKING" not in ai_enhancement:
                return template + "\n\nSPECIFIC CONSIDERATIONS:\n" + ai_enhancement
        except asyncio.TimeoutError:
            logger.warning("AI enhancement timed out, returning template without enhancement")
        except Exception as e:
            logger.warning(f"AI enhancement failed: {e}, returning template without enhancement")
        
        return template
    
    elif "marriage" in query.lower() or "marital" in query.lower() or "divorce" in query.lower() or "family" in query.lower():
        template = f"""LEGAL RESEARCH ANALYSIS
Query: {query}
Date: {time.strftime("%B %d, %Y")}

EXECUTIVE SUMMARY:
This analysis examines family law matters including marriage, divorce, and related legal procedures, focusing on legal requirements, property rights, and compliance obligations.

KEY LEGAL PRINCIPLES:
• Marriage Validity: Legal capacity, consent, and formal requirements
• Divorce Grounds: No-fault vs. fault-based divorce procedures
• Property Division: Community property vs. separate property states
• Spousal Support: Alimony and maintenance considerations
• Child Custody: Best interests of the child standard
• Child Support: Guidelines and calculation methods

RELEVANT LEGAL CONSIDERATIONS:
• State-Specific Laws: Jurisdictional variations in marriage and divorce requirements
• Divorce Procedures: Filing requirements, waiting periods, and procedural steps
• Prenuptial Agreements: Validity and enforceability standards
• Property Settlement: Asset division and debt allocation procedures
• Custody Arrangements: Legal and physical custody considerations
• Support Calculations: Spousal and child support determination methods

RISK ASSESSMENT:
• High Risk: Contested divorces and complex property disputes
• Medium Risk: Inadequate documentation and custody disputes
• Low Risk: Uncontested divorces with proper legal guidance

COMPLIANCE REQUIREMENTS:
• Divorce Filing: Proper petition filing and service requirements
• Waiting Periods: Mandatory waiting periods by jurisdiction
• Documentation: Financial disclosure and asset documentation
• Mediation Requirements: Court-ordered mediation in some jurisdictions
• Final Orders: Proper entry of divorce decrees and support orders

PRACTICAL RECOMMENDATIONS:
1. Understand divorce procedures in your jurisdiction
2. Gather comprehensive financial documentation
3. Consider mediation or collaborative divorce options
4. Plan for child custody and support arrangements
5. Consult with family law attorney for complex situations

CASE LAW REFERENCES:
• Landmark family law cases on marriage validity
• Property division precedents by jurisdiction
• Child custody and support case law

NEXT STEPS:
1. Review marriage requirements in your jurisdiction
2. Consider prenuptial agreement if appropriate
3. Plan for property and estate considerations
4. Consult with qualified family law attorney

CONFIDENCE LEVEL: High
RESEARCH COMPLETENESS: Comprehensive
RECOMMENDED ACTION: Professional legal consultation advised

---
This research analysis is provided for informational purposes only and does not constitute legal advice."""
        
        return template
    
    elif "employment" in query.lower() or "termination" in query.lower() or "workplace" in query.lower():
        template = f"""LEGAL RESEARCH ANALYSIS
Query: {query}
Date: {time.strftime("%B %d, %Y")}

EXECUTIVE SUMMARY:
This analysis examines employment law regarding termination procedures, focusing on legal requirements, employee rights, and employer obligations in the termination process.

KEY LEGAL PRINCIPLES:
• At-Will Employment: Most employment relationships are at-will unless contractually modified
• Wrongful Termination: Prohibited terminations based on protected characteristics
• Due Process: Fair procedures for disciplinary actions and terminations
• Notice Requirements: Advance notice obligations for certain terminations
• Final Pay Requirements: Timely payment of final wages and benefits

RELEVANT LEGAL CONSIDERATIONS:
• Federal Laws: Title VII, ADA, ADEA, FMLA, and other federal protections
• State Employment Laws: Varying requirements by jurisdiction
• Employment Contracts: Contractual limitations on termination rights
• Union Agreements: Collective bargaining agreement requirements
• Severance Agreements: Legal requirements for separation packages

RISK ASSESSMENT:
• High Risk: Terminations violating anti-discrimination laws
• Medium Risk: Inadequate documentation and procedural failures
• Low Risk: Proper documentation and lawful termination procedures

COMPLIANCE REQUIREMENTS:
• Documentation Standards: Comprehensive record-keeping requirements
• Notice Obligations: Required advance notice for certain terminations
• Final Pay Laws: State-specific final wage payment requirements
• COBRA Notifications: Health insurance continuation requirements
• Unemployment Benefits: Proper handling of unemployment claims

PRACTICAL RECOMMENDATIONS:
1. Develop clear termination policies and procedures
2. Maintain comprehensive documentation of performance issues
3. Provide proper notice and follow due process requirements
4. Ensure compliance with final pay and benefit obligations
5. Consider severance agreements for high-risk terminations

CASE LAW REFERENCES:
• McDonnell Douglas Corp. v. Green (1973) - Burden shifting in discrimination cases
• Various state court decisions on wrongful termination
• Employment law precedents on termination procedures

NEXT STEPS:
1. Review current termination policies and procedures
2. Ensure compliance with applicable federal and state laws
3. Train management on proper termination procedures
4. Consult with employment law attorney for complex situations

CONFIDENCE LEVEL: High
RESEARCH COMPLETENESS: Comprehensive
RECOMMENDED ACTION: Professional legal consultation advised

---
This research analysis is provided for informational purposes only and does not constitute legal advice."""
        
        return template
    
    else:
        # General legal research template
        template = f"""LEGAL RESEARCH ANALYSIS
Query: {query}
Date: {time.strftime("%B %d, %Y")}

EXECUTIVE SUMMARY:
This analysis examines the legal aspects of "{query}", providing comprehensive research findings and recommendations for legal professionals.

KEY LEGAL PRINCIPLES:
• Applicable Law: Relevant statutes, regulations, and case law
• Legal Standards: Industry-specific standards and requirements
• Compliance Framework: Regulatory and professional requirements
• Risk Management: Identification and mitigation strategies

RELEVANT LEGAL CONSIDERATIONS:
• Jurisdictional Requirements: Applicable laws vary by jurisdiction
• Professional Standards: Industry-specific standards and best practices
• Documentation Requirements: Proper record-keeping and evidence standards
• Timeline Considerations: Statute of limitations and procedural deadlines

RISK ASSESSMENT:
• Legal Compliance: Regulatory and statutory compliance risks
• Professional Liability: Standards of care and duty obligations
• Documentation Risks: Record-keeping and evidence requirements
• Procedural Risks: Timeline and procedural compliance

COMPLIANCE REQUIREMENTS:
• Regulatory Compliance: Federal, state, and local regulations
• Industry Standards: Professional association guidelines
• Documentation Standards: Required record-keeping and reporting
• Audit Requirements: Regular compliance monitoring and review

PRACTICAL RECOMMENDATIONS:
1. Consult with qualified legal counsel for specific guidance
2. Review applicable laws and regulations in your jurisdiction
3. Implement appropriate compliance and risk management measures
4. Maintain comprehensive documentation and records
5. Establish ongoing monitoring and review processes

CASE LAW REFERENCES:
• Relevant legal precedents and case law
• Statutory references and regulatory guidance
• Industry-specific legal developments

NEXT STEPS:
1. Engage qualified legal counsel for specific guidance
2. Review applicable laws and regulations
3. Implement recommended compliance measures
4. Establish ongoing monitoring processes

CONFIDENCE LEVEL: High
RESEARCH COMPLETENESS: Comprehensive
RECOMMENDED ACTION: Professional legal consultation advised

---
This research analysis is provided for informational purposes only and does not constitute legal advice."""
        
        return template

async def generate_comprehensive_legal_document(query: str, doc_type: str) -> str:
    """Generate comprehensive legal document using templates + AI enhancement"""
    
    # Base template for software development contract
    if "software" in query.lower() or "development" in query.lower():
        template = f"""
PROFESSIONAL SOFTWARE DEVELOPMENT CONTRACT

CONTRACT NO: SD-{int(time.time()) % 10000}
DATE: {time.strftime("%B %d, %Y")}

PARTIES:
This Software Development Contract ("Contract") is entered into on {time.strftime("%B %d, %Y")} between:

CLIENT: [Client Company Name]
Address: [Client Address]
Contact: [Client Contact Information]

DEVELOPER: [Development Company Name]  
Address: [Developer Address]
Contact: [Developer Contact Information]

RECITALS:
WHEREAS, Client desires to engage Developer to provide software development services;
WHEREAS, Developer has the expertise and capability to provide such services;
WHEREAS, both parties wish to establish the terms and conditions for such engagement;

NOW, THEREFORE, the parties agree as follows:

1. SCOPE OF WORK
Developer shall provide software development services including:
- Requirements analysis and system design
- Software development and programming
- Testing and quality assurance
- Documentation and user manuals
- Deployment and implementation support

Project Description: {query}

2. DELIVERABLES
Developer shall deliver:
- Complete source code
- Executable software application
- Technical documentation
- User documentation
- Test reports and quality assurance documentation

3. TIMELINE AND MILESTONES
Project Timeline: [To be specified based on project scope]
Key Milestones:
- Requirements completion: [Date]
- Design approval: [Date]  
- Development completion: [Date]
- Testing completion: [Date]
- Final delivery: [Date]

4. COMPENSATION AND PAYMENT TERMS
Total Contract Value: $[Amount]
Payment Schedule:
- Initial payment (30%): $[Amount] upon contract execution
- Milestone payments (40%): $[Amount] upon milestone completion
- Final payment (30%): $[Amount] upon project completion

5. INTELLECTUAL PROPERTY RIGHTS
All intellectual property rights in the developed software shall belong to Client upon full payment. Developer retains rights to:
- Pre-existing intellectual property
- General programming knowledge and techniques
- Development tools and methodologies

6. CONFIDENTIALITY
Both parties agree to maintain strict confidentiality regarding:
- Business information and trade secrets
- Technical specifications and requirements
- Proprietary algorithms and methodologies
- Client data and sensitive information

7. WARRANTIES AND LIABILITIES
Developer warrants that:
- Work will be performed in a professional manner
- Software will function according to specifications
- No third-party intellectual property rights are infringed

8. TERMINATION CONDITIONS
Either party may terminate this contract:
- With 30 days written notice
- Immediately for material breach
- Upon mutual agreement

9. DISPUTE RESOLUTION
Any disputes shall be resolved through:
- Good faith negotiations
- Mediation if negotiations fail
- Binding arbitration as final recourse

10. GOVERNING LAW
This contract shall be governed by the laws of [Jurisdiction] and any disputes shall be resolved in the courts of [Jurisdiction].

11. SIGNATURES
IN WITNESS WHEREOF, the parties have executed this contract on the date first written above.

CLIENT:                           DEVELOPER:
_________________________         _________________________
[Client Representative Name]       [Developer Representative Name]
Title: [Title]                    Title: [Title]
Date: [Date]                      Date: [Date]

_________________________         _________________________
Signature                         Signature
"""
        
        # Enhance template with AI for specific requirements
        enhancement_prompt = f"""Enhance this software development contract template for the specific project: "{query}"

        Add specific details, clauses, and provisions that would be relevant for this particular project.
        Focus on technical specifications, security requirements, and project-specific terms.
        Keep the professional legal structure but make it more specific to the project requirements."""
        
        try:
            ai_enhancement = await generate_ai_response(enhancement_prompt, max_tokens=500, use_full_response=True)
            if ai_enhancement and "FALLBACK RESPONSE" not in ai_enhancement and "LLM NOT WORKING" not in ai_enhancement:
                return template + "\n\nPROJECT-SPECIFIC ENHANCEMENTS:\n" + ai_enhancement
        except:
            pass
        
        return template
    
    # Generic contract template
    else:
        template = f"""
PROFESSIONAL CONTRACT AGREEMENT

CONTRACT NO: CNT-{int(time.time()) % 10000}
DATE: {time.strftime("%B %d, %Y")}

PARTIES:
This Contract Agreement ("Agreement") is entered into on {time.strftime("%B %d, %Y")} between:

PARTY A: [Party A Name]
Address: [Party A Address]
Contact: [Party A Contact Information]

PARTY B: [Party B Name]  
Address: [Party B Address]
Contact: [Party B Contact Information]

RECITALS:
WHEREAS, the parties desire to enter into a contractual relationship;
WHEREAS, both parties have the legal capacity to enter into this agreement;
WHEREAS, the terms and conditions set forth below are mutually agreed upon;

NOW, THEREFORE, the parties agree as follows:

1. PURPOSE AND SCOPE
The purpose of this agreement is: {query}

2. TERMS AND CONDITIONS
[Specific terms and conditions to be detailed based on the nature of the agreement]

3. OBLIGATIONS OF PARTIES
Party A shall:
- [Specific obligations]

Party B shall:
- [Specific obligations]

4. COMPENSATION
Payment terms: [To be specified]
Amount: $[Amount]
Payment schedule: [Schedule]

5. TERM AND TERMINATION
This agreement shall commence on [Start Date] and continue until [End Date] or until terminated according to the provisions herein.

6. CONFIDENTIALITY
Both parties agree to maintain confidentiality of all proprietary and confidential information.

7. GOVERNING LAW
This agreement shall be governed by the laws of [Jurisdiction].

8. SIGNATURES
IN WITNESS WHEREOF, the parties have executed this agreement.

PARTY A:                           PARTY B:
_________________________         _________________________
[Name]                             [Name]
Title: [Title]                     Title: [Title]
Date: [Date]                       Date: [Date]

_________________________         _________________________
Signature                          Signature
"""
        
        # Enhance with AI
        enhancement_prompt = f"""Enhance this contract template for: "{query}"

        Add specific clauses, terms, and provisions relevant to this particular agreement.
        Make it comprehensive and professional for legal review."""
        
        try:
            ai_enhancement = await generate_ai_response(enhancement_prompt, max_tokens=500, use_full_response=True)
            if ai_enhancement and "FALLBACK RESPONSE" not in ai_enhancement and "LLM NOT WORKING" not in ai_enhancement:
                return template + "\n\nSPECIFIC PROVISIONS:\n" + ai_enhancement
        except:
            pass
        
        return template

def generate_enhanced_fallback_response(query: str) -> str:
    """Simple test response to verify LLM integration"""
    return f"""🚨 FALLBACK RESPONSE - LLM NOT WORKING 🚨

Query: {query[:100]}

This is a fallback response because the LLM models failed to load.
If you see this message, the AI integration is not working properly.

Expected: Real AI-generated legal analysis
Actual: This fallback response

Please check:
1. LLM models are loaded
2. ollama_client is not None
3. AI response generation is working

Status: LLM Integration Failed"""



@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("🚀 Starting LegisAI with Real LLM Integration...")
    logger.info("✅ Enhanced PDF analysis system loaded")
    logger.info("✅ Intelligent legal response system activated")
    
    # Load LLM models
    await load_llm_models()
    
    # Check if models loaded successfully
    global ollama_client
    if ollama_client is not None:
        logger.info("🤖 Ollama models loaded successfully")
        # Test the model with a simple test
        try:
            test_response = await generate_ai_response("Hello, how are you?", max_tokens=20)
            logger.info(f"✅ Ollama test successful: {test_response[:50]}...")
        except Exception as e:
            logger.error(f"❌ Ollama test failed: {e}")
            logger.error(f"❌ Ollama client: {ollama_client}")
    else:
        logger.error("❌ Ollama client is None - using fallback responses")
        logger.error("❌ Check Ollama installation and model availability")
    
    yield
    logger.info("🛑 Shutting down LegisAI Backend...")

# Create FastAPI app
app = FastAPI(
    title="LegisAI Enhanced",
    description="Multi-Agent Legal Research and Drafting Assistant with Enhanced PDF Analysis",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health endpoints
@app.get("/api/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "LegisAI AI-Powered v4.0",
        "version": "4.0.0",
        "legal_knowledge_loaded": True,
        "intelligent_responses": True,
        "pdf_extraction_improved": True,
        "enhanced_analysis": True,
        "cleanup_completed": True,
        "single_file_backend": True,
        "ai_powered": True,
        "llm_status": "template-based",  # Using template responses
        "vector_store_available": FAISS_AVAILABLE,
        "vector_store_initialized": vector_store is not None,
        "vector_store_documents": vector_store.get_document_count() if vector_store else 0
    }

@app.post("/api/clauses/analyze")
async def analyze_clauses(request: ClauseAnalysisRequest) -> Dict[str, Any]:
    """Analyze clauses for risks and compliance issues"""
    logger.info(f"🔍 Clause analysis request for jurisdiction: {request.jurisdiction}")
    
    if not clause_analyzer:
        raise HTTPException(
            status_code=503, 
            detail="Clause analyzer not available"
        )
    
    try:
        jurisdiction = request.jurisdiction or "US"
        
        if request.clause_text:
            # Analyze single clause
            risk = clause_analyzer.analyze_clause(
                request.clause_text, 
                jurisdiction, 
                request.content
            )
            
            # Find similar clauses using hybrid search if available
            similar_clauses = []
            if hybrid_retriever and hybrid_retriever.bm25_index:
                try:
                    search_results = hybrid_retriever.search(
                        request.clause_text,
                        k=3,
                        semantic_weight=0.7,
                        keyword_weight=0.3
                    )
                    for result in search_results:
                        similar_clauses.append({
                            "text": result.get('text', '')[:200],
                            "score": result.get('combined_score', 0),
                            "metadata": result.get('metadata', {})
                        })
                except Exception as e:
                    logger.warning(f"Failed to find similar clauses: {e}")
            
            return {
                "clause_text": request.clause_text[:200],
                "risk_level": risk.risk_level,
                "risk_score": risk.risk_score,
                "risk_type": risk.risk_type,
                "issues": risk.issues,
                "recommendations": risk.recommendations,
                "jurisdiction": jurisdiction,
                "legal_basis": risk.legal_basis,
                "similar_clauses": similar_clauses
            }
        else:
            # Analyze full document
            analysis = clause_analyzer.analyze_document(request.content, jurisdiction)
            
            # Sort clause_risks by risk_score (highest first) and take top 10
            sorted_clause_risks = sorted(
                analysis["clause_risks"], 
                key=lambda x: x.get("risk_score", 0), 
                reverse=True
            )[:10]
            
            return {
                "jurisdiction": jurisdiction,
                "total_clauses": analysis["total_clauses"],
                "high_risk_clauses": analysis["high_risk_clauses"],
                "document_risk_level": analysis["document_risk_level"],
                "average_risk_score": analysis["average_risk_score"],
                "clause_risks": sorted_clause_risks,
                "summary": {
                    "total_clauses": analysis["total_clauses"],
                    "high_risk_clauses": analysis["high_risk_clauses"],
                    "document_risk_level": analysis["document_risk_level"],
                    "average_risk_score": analysis["average_risk_score"],
                    "critical_risks": analysis["summary"].get("critical_risks", 0),
                    "high_risks": analysis["summary"].get("high_risks", 0),
                    "medium_risks": analysis["summary"].get("medium_risks", 0),
                    "low_risks": analysis["summary"].get("low_risks", 0)
                }
            }
            
    except Exception as e:
        logger.error(f"Clause analysis error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/vector-store/status")
async def vector_store_status() -> Dict[str, Any]:
    """Get vector store status and statistics"""
    if not vector_store:
        return {
            "available": False,
            "initialized": False,
            "message": "Vector store not available (FAISS not installed or initialization failed)"
        }
    
    stats = vector_store.get_stats() if hasattr(vector_store, 'get_stats') else {}
    hybrid_stats = hybrid_retriever.get_stats() if hybrid_retriever else {}
    
    return {
        "available": True,
        "initialized": True,
        "document_count": vector_store.get_document_count(),
        "embedding_model": "all-MiniLM-L6-v2",
        "dimension": vector_store.dimension if hasattr(vector_store, 'dimension') else None,
        "index_type": stats.get('index_type', 'flat'),
        "index_trained": stats.get('index_trained', True),
        "persist_dir": stats.get('persist_dir', 'data/vector_store'),
        "index_size_mb": round(stats.get('index_size_mb', 0), 2),
        "hybrid_search_available": hybrid_stats.get('bm25_available', False) and hybrid_stats.get('bm25_indexed', False),
        "search_method": "hybrid" if hybrid_stats.get('bm25_indexed') else "semantic_only"
    }

@app.post("/api/vector-store/bulk-import")
async def bulk_import_documents(request: Dict[str, Any]) -> Dict[str, Any]:
    """Bulk import documents into vector store (for large datasets)"""
    if not vector_store:
        raise HTTPException(status_code=503, detail="Vector store not available")
    
    try:
        documents = request.get('documents', [])
        batch_size = request.get('batch_size', 100)
        
        if not documents:
            raise HTTPException(status_code=400, detail="No documents provided")
        
        logger.info(f"📚 Bulk importing {len(documents)} documents in batches of {batch_size}...")
        
        # Extract texts and metadata
        texts = []
        metadata_list = []
        for doc in documents:
            if isinstance(doc, dict):
                texts.append(doc.get('text', ''))
                metadata_list.append(doc.get('metadata', {}))
            elif isinstance(doc, str):
                texts.append(doc)
                metadata_list.append({})
        
        # Add documents in batches
        doc_ids = vector_store.add_documents(texts, metadata_list, batch_size=batch_size)
        
        # Save after import
        vector_store.save()
        
        return {
            "status": "success",
            "documents_imported": len(doc_ids),
            "total_documents": vector_store.get_document_count(),
            "message": f"Successfully imported {len(doc_ids)} documents"
        }
        
    except Exception as e:
        logger.error(f"Bulk import error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/debug/llm-status")
async def debug_llm_status() -> Dict[str, Any]:
    """Debug endpoint to check LLM status"""
    test_response = await generate_ai_response("Test query for LLM", max_tokens=50)
    return {
        "llm_available": LLM_AVAILABLE,
        "ollama_client_loaded": ollama_client is not None,
        "embeddings_model_loaded": embeddings_model is not None,
        "ollama_model": ollama_model,
        "test_response": test_response,
        "test_response_length": len(test_response),
        "is_fallback": "FALLBACK RESPONSE" in test_response
    }

@app.get("/api/debug/test-ai")
async def test_ai_simple() -> Dict[str, Any]:
    """Simple AI test endpoint"""
    try:
        response = await generate_ai_response("Hello, how are you?", max_tokens=30)
        return {
            "success": True,
            "response": response,
            "length": len(response),
            "is_ai": "FALLBACK RESPONSE" not in response
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "response": "Error occurred"
        }

# Research endpoints
@app.post("/api/research/stream")
async def research_legal_query_stream(request: ResearchRequest):
    """Stream research results word-by-word"""
    query = request.query
    logger.info(f"🌊 Streaming research for: {query[:50]}...")
    
    # Create research prompt
    research_prompt = f"""As a legal research assistant, provide a comprehensive analysis of the following legal query:

Query: "{query}"

Please provide:
1. EXECUTIVE SUMMARY - Brief overview of the topic
2. KEY LEGAL PRINCIPLES - Important legal concepts and rules
3. RELEVANT LEGAL CONSIDERATIONS - Jurisdiction-specific requirements and variations
4. RISK ASSESSMENT - Potential legal risks and their severity
5. COMPLIANCE REQUIREMENTS - Regulatory and statutory obligations
6. PRACTICAL RECOMMENDATIONS - Actionable steps
7. CASE LAW REFERENCES - Relevant precedents (if applicable)
8. NEXT STEPS - Recommended actions

Format the response in a clear, professional manner with proper sections. Be specific to the query and provide jurisdiction-specific details where mentioned."""
    
    # Stream the response
    return StreamingResponse(
        generate_ai_response_stream(research_prompt),
        media_type="text/event-stream"
    )

@app.post("/api/research")
async def research_legal_query(request: ResearchRequest) -> Dict[str, Any]:
    """Perform legal research using FAISS semantic search + CourtListener API + AI (Refactored)"""
    logger.info(f"🔍 Research request: {request.query}")
    
    try:
        query = request.query
        max_results = request.max_results or 10
        similarity_threshold = request.similarity_threshold or 0.3
        
        # Fetch case law from CourtListener API (using helper)
        case_law_results = await _fetch_courtlistener_cases(query, max_results)
        
        # Generate AI summary (non-blocking)
        ai_summary_task = asyncio.create_task(
            asyncio.wait_for(generate_structured_legal_research(query), timeout=600.0)
            )
        ai_summary = None
        try:
            ai_summary = await asyncio.wait_for(ai_summary_task, timeout=5.0)
            logger.info("✅ AI summary generated quickly")
        except (asyncio.TimeoutError, Exception) as e:
            logger.info("AI summary generation taking too long, will use fallback")
            ai_summary = None
        
        # Perform vector store search (using helpers)
        relevant_docs = []
        
        # Try hybrid search first
        if hybrid_retriever and hybrid_retriever.bm25_index is not None:
            logger.info(f"🔍 Using HYBRID search (BM25 + FAISS)...")
            try:
                semantic_weight = request.semantic_weight or 0.6
                keyword_weight = request.keyword_weight or 0.4
                search_results = hybrid_retriever.search(
                    query, k=max_results * 2,
                    semantic_weight=semantic_weight,
                    keyword_weight=keyword_weight
                )
                relevant_docs = _format_hybrid_search_results(search_results, similarity_threshold, max_results)
                logger.info(f"✅ Found {len(relevant_docs)} relevant documents via HYBRID search")
            except Exception as e:
                logger.error(f"❌ Hybrid search error: {e}")
                relevant_docs = []
        
        # Fallback to FAISS-only search
        if not relevant_docs and vector_store and vector_store.get_document_count() > 0:
            logger.info(f"🔍 Using FAISS-only semantic search...")
            try:
                search_results = vector_store.search(query, k=max_results * 2)
                relevant_docs = _format_faiss_search_results(search_results, similarity_threshold, max_results)
                logger.info(f"✅ Found {len(relevant_docs)} relevant documents via FAISS search")
            except Exception as e:
                logger.error(f"❌ Vector store search error: {e}")
                relevant_docs = []
        
        # Convert CourtListener cases to document format (using helper)
        for case in case_law_results:
            relevant_docs.append(_convert_courtlistener_case_to_doc(case))
        
        # Sort and limit results
        relevant_docs.sort(key=lambda x: x["score"], reverse=True)
        relevant_docs = relevant_docs[:max_results]
        
        # Generate fallback summary if needed (using helper)
        if ai_summary is None or not ai_summary:
            ai_summary = _generate_fallback_summary(query, relevant_docs)
        
        # Calculate confidence and prepare response
        if relevant_docs:
            avg_score = sum(doc["score"] for doc in relevant_docs) / len(relevant_docs)
            confidence_score = min(0.95, 0.7 + (avg_score * 0.25))
        else:
            confidence_score = 0.75
        
        api_count = sum(1 for doc in relevant_docs if doc.get("search_method") == "courtlistener_api")
        vector_count = len(relevant_docs) - api_count
        
        logger.info(f"✅ Returning {len(relevant_docs)} documents (API: {api_count}, Vector: {vector_count})")
        
        # Extract citations from documents
        all_citations = []
        for doc in relevant_docs:
            citations = doc.get("citations", [])
            if isinstance(citations, list):
                all_citations.extend(citations)
            elif isinstance(citations, str):
                all_citations.append(citations)
        
        # Enhance with explainability if service is available
        result = {
            "query": query,
            "documents": relevant_docs,
            "summary": ai_summary,
            "confidence_score": confidence_score,
            "ai_generated": ollama_client is not None,
            "vector_search_used": vector_store is not None and vector_store.get_document_count() > 0,
            "hybrid_search_used": hybrid_retriever is not None and hybrid_retriever.bm25_index is not None,
            "courtlistener_api_used": api_count > 0,
            "api_results_count": api_count,
            "vector_store_results_count": vector_count,
            "total_documents_searched": vector_store.get_document_count() if vector_store else 0,
            "search_method": "hybrid_api" if api_count > 0 and vector_count > 0 else ("hybrid" if (hybrid_retriever and hybrid_retriever.bm25_index) else "semantic_only" if vector_store else "api_only" if api_count > 0 else "none")
        }
        
        # Add explainability metadata
        if explainability_service and all_citations:
            result = explainability_service.add_citations_to_result(
                result,
                all_citations,
                probability=confidence_score
            )
        
        return result
        
    except asyncio.TimeoutError:
        logger.error("Research request timed out")
        raise HTTPException(status_code=504, detail="Request timed out. Please try again with a simpler query.")
    except Exception as e:
        logger.error(f"Research error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

# Drafting endpoints
@app.post("/api/draft/stream")
async def draft_legal_document_stream(request: DraftRequest):
    """Stream draft results word-by-word"""
    query = request.query
    doc_type = request.document_type or "contract"
    logger.info(f"🌊 Streaming draft for: {query[:50]}...")
    
    # Create draft prompt
    draft_prompt = f"""Create a comprehensive {doc_type} document based on the following description:

Description: "{query}"

Please provide a complete, professional {doc_type} with:
1. Clear title and parties section
2. Detailed terms and conditions
3. Obligations and rights of all parties
4. Payment and compensation terms (if applicable)
5. Termination and dispute resolution clauses
6. Governing law and jurisdiction
7. Signature sections

Format the response with proper sections and clear language suitable for legal use."""
    
    # Stream the response
    return StreamingResponse(
        generate_ai_response_stream(draft_prompt),
        media_type="text/event-stream"
    )

@app.post("/api/draft")
async def draft_legal_document(request: DraftRequest) -> Dict[str, Any]:
    """Draft legal document using real AI"""
    logger.info(f"📝 Drafting request: {request.query}")
    
    try:
        query = request.query
        doc_type = request.document_type or "contract"
        
        # Generate comprehensive legal document using template + AI enhancement
        ai_draft = await generate_comprehensive_legal_document(query, doc_type)
        
        # Generate AI-powered suggestions
        suggestions_prompt = f"""For this {doc_type} about "{query}", provide 6 practical suggestions for:
1. Legal review considerations
2. Compliance requirements
3. Risk mitigation measures
4. Best practices
5. Additional clauses to consider
6. Implementation recommendations

Format as a numbered list of actionable recommendations."""
        
        ai_suggestions = await generate_ai_response(suggestions_prompt, max_tokens=300, use_full_response=True)
        
        # Parse suggestions into list
        suggestions = []
        if ai_suggestions:
            lines = ai_suggestions.split('\n')
            for line in lines:
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                    suggestions.append(line)
        
        if not suggestions:
            suggestions = [
                "Review with qualified legal counsel",
                "Ensure compliance with applicable laws",
                "Include specific performance metrics",
                "Add dispute resolution mechanisms",
                "Consider confidentiality provisions",
                "Implement risk management measures"
            ]
        
        return {
            "query": query,
            "draft_content": ai_draft,
            "clauses": [
                {"type": "definitions", "content": "Standard definitions and terminology"},
                {"type": "scope", "content": f"Scope of work for {query}"},
                {"type": "terms", "content": "Standard terms and conditions"},
                {"type": "compliance", "content": "Compliance and regulatory requirements"},
                {"type": "termination", "content": "Termination and transition procedures"}
            ],
            "suggestions": suggestions[:6],
            "confidence_score": 0.85,
            "ai_generated": ollama_client is not None
        }
        
    except Exception as e:
        logger.error(f"Drafting error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/draft/download")
async def download_draft_docx(request: Dict[str, Any]):
    """Generate and download DOCX file from draft content"""
    try:
        content = request.get('content', '')
        title = request.get('title', 'legal_document')
        document_type = request.get('document_type', 'contract')
        
        logger.info(f"📥 Generating DOCX for: {title}")
        
        # Try to import python-docx
        try:
            from docx import Document
            from docx.shared import Pt, Inches
            from docx.enum.text import WD_ALIGN_PARAGRAPH
            import io
            
            # Create new document
            doc = Document()
            
            # Add title
            title_para = doc.add_heading(title, 0)
            title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            # Add document type
            doc.add_paragraph(f"Document Type: {document_type.upper()}")
            doc.add_paragraph(f"Generated: {time.strftime('%B %d, %Y at %I:%M %p')}")
            
            # Add content
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    doc.add_paragraph()
                    continue
                
                # Handle headers
                if line.startswith('##'):
                    doc.add_heading(line.replace('#', '').strip(), level=2)
                elif line.startswith('#'):
                    doc.add_heading(line.replace('#', '').strip(), level=1)
                # Handle bold text
                elif line.startswith('**') and line.endswith('**'):
                    p = doc.add_paragraph()
                    run = p.add_run(line.replace('**', ''))
                    run.bold = True
                # Handle list items
                elif line.startswith('-') or line.startswith('•') or line[0].isdigit() and '. ' in line:
                    doc.add_paragraph(line, style='List Bullet')
                else:
                    doc.add_paragraph(line)
            
            # Create a BytesIO object to hold the DOCX file in memory
            buffer = io.BytesIO()
            doc.save(buffer)
            buffer.seek(0)
            
            # Return the DOCX file as a response
            from fastapi.responses import Response
            filename = f"{document_type}_{int(time.time())}.docx"
            
            return Response(
                content=buffer.getvalue(),
                media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                headers={
                    "Content-Disposition": f"attachment; filename={filename}"
                }
            )
            
        except ImportError:
            logger.error("python-docx not installed")
            raise HTTPException(status_code=500, detail="DOCX generation not available. Please install python-docx.")
            
    except Exception as e:
        logger.error(f"DOCX generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Compliance endpoints
@app.post("/api/compliance/stream")
async def check_compliance_stream(request: ComplianceRequest):
    """Stream compliance results word-by-word"""
    content = request.content
    jurisdiction = request.jurisdiction or 'US'
    logger.info(f"🌊 Streaming compliance check for: {content[:50]}...")
    
    # Create compliance prompt
    compliance_prompt = f"""As a legal compliance expert, analyze this content for compliance issues:

Content: "{content[:500]}"
Jurisdiction: {jurisdiction}

Provide a comprehensive compliance analysis including:
1. EXECUTIVE SUMMARY - Overall compliance status
2. IDENTIFIED ISSUES - Specific compliance problems found
3. RISK ASSESSMENT - Risk level and impact analysis
4. COMPLIANCE REQUIREMENTS - Applicable regulations and standards
5. PRACTICAL RECOMMENDATIONS - Actionable steps to achieve compliance
6. NEXT STEPS - Immediate and long-term actions required

Format the response clearly with proper sections and actionable guidance."""
    
    # Stream the response
    return StreamingResponse(
        generate_ai_response_stream(compliance_prompt),
        media_type="text/event-stream"
    )

@app.post("/api/compliance/check")
async def check_compliance(request: ComplianceRequest) -> Dict[str, Any]:
    """Check compliance using real AI"""
    logger.info(f"🛡️ Compliance check for jurisdiction: {request.jurisdiction or 'US'}")
    
    try:
        content = request.content
        jurisdiction = request.jurisdiction or 'US'
        check_gdpr = request.check_gdpr or False
        check_us_code = request.check_us_code or False
        check_eu_lex = request.check_eu_lex or False
        
        # Generate AI-powered compliance analysis
        compliance_prompt = f"""As a legal compliance expert, analyze this content for compliance issues:

Content: "{content[:500]}"
Jurisdiction: {jurisdiction}

Analyze for:
1. GDPR compliance (if applicable)
2. US Code compliance
3. EU Lex compliance (if applicable)
4. General legal compliance issues
5. Risk assessment and scoring
6. Specific recommendations

Provide a comprehensive compliance analysis with risk scoring and actionable recommendations."""
        
        ai_analysis = await generate_ai_response(compliance_prompt, max_tokens=500, use_full_response=True)
        
        # Generate AI-powered recommendations
        recommendations_prompt = f"""For this compliance analysis, provide specific recommendations to address any issues found in: "{content[:300]}"

Focus on:
1. Immediate actions required
2. Compliance improvements needed
3. Risk mitigation measures
4. Best practices to implement
5. Legal review requirements

Format as actionable recommendations."""
        
        ai_recommendations = await generate_ai_response(recommendations_prompt, max_tokens=300, use_full_response=True)
        
        # Parse recommendations into list
        recommendations = []
        if ai_recommendations:
            lines = ai_recommendations.split('\n')
            for line in lines:
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                    recommendations.append(line)
        
        if not recommendations:
            recommendations = [
                "Review with qualified legal counsel",
                "Ensure compliance with applicable laws",
                "Implement proper consent mechanisms",
                "Add data protection measures",
                "Update privacy policies",
                "Conduct regular compliance audits"
            ]
        
        # Calculate risk score based on content analysis
        risk_score = 0.2
        issues = []
        
        content_lower = content.lower()
        
        # Basic compliance checks
        if "unlimited liability" in content_lower:
            issues.append({
                "type": "LIABILITY",
                "severity": "high",
                "description": "Unlimited liability clauses may be unenforceable"
            })
            risk_score += 0.3
        
        if check_gdpr and "personal data" in content_lower and "consent" not in content_lower:
            issues.append({
                "type": "GDPR_CONSENT",
                "severity": "high",
                "description": "Missing consent mechanisms for data processing"
            })
            risk_score += 0.3
        
        compliance_status = "compliant" if risk_score < 0.4 else "needs_review" if risk_score < 0.7 else "high_risk"
        
        return {
            "content": content,
            "risk_score": min(risk_score, 1.0),
            "issues": issues,
            "recommendations": recommendations[:6],
            "compliance_status": compliance_status,
            "analysis": ai_analysis,
            "ai_generated": ollama_client is not None
        }
        
    except Exception as e:
        logger.error(f"Compliance check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Upload endpoints
@app.post("/api/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)) -> UploadResponse:
    """Upload a legal document for analysis and index in vector store"""
    logger.info(f"📁 Document upload: {file.filename}")
    
    try:
        # Create uploads directory
        upload_dir = Path("uploads")
        upload_dir.mkdir(exist_ok=True)
        
        # Read and save file
        content = await file.read()
        file_id = f"doc_{int(time.time())}"
        file_path = upload_dir / f"{file_id}_{file.filename}"
        
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
        # Extract text and add to vector store
        text_content = ""
        pages_extracted = 0
        indexed_in_vector_store = False
        
        if file_path.suffix.lower() == '.pdf':
            try:
                import PyPDF2
                import io
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
                text_parts = []
                for page_num in range(min(10, len(pdf_reader.pages))):  # Extract first 10 pages
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()
                    if page_text.strip():
                        text_parts.append(page_text)
                        pages_extracted += 1
                text_content = "\n\n".join(text_parts)
            except Exception as e:
                logger.warning(f"PDF extraction failed: {e}")
                text_content = ""
        
        # Add to vector store if text was extracted and vector store is available
        if text_content and vector_store:
            try:
                # Split long documents into chunks (max 1000 chars per chunk for better search)
                chunk_size = 1000
                chunks = []
                for i in range(0, len(text_content), chunk_size):
                    chunk = text_content[i:i + chunk_size]
                    if chunk.strip():
                        chunks.append(chunk)
                
                # Prepare metadata for all chunks
                metadata_list = []
                for idx in range(len(chunks)):
                    metadata = {
                        "type": "uploaded_document",
                        "title": file.filename,
                        "file_id": file_id,
                        "chunk_index": idx,
                        "total_chunks": len(chunks),
                        "pages_extracted": pages_extracted,
                        "upload_date": time.strftime("%Y-%m-%d")
                    }
                    metadata_list.append(metadata)
                
                # Add chunks to vector store in batch
                doc_ids = vector_store.add_documents(chunks, metadata_list, batch_size=50)
                
                # Index chunks for BM25 hybrid search
                if hybrid_retriever:
                    try:
                        # Get all existing documents from vector store
                        all_docs = []
                        total_docs = vector_store.get_document_count()
                        for i in range(total_docs):
                            doc = vector_store.get_document(i)
                            if doc:
                                all_docs.append(doc)
                        
                        # Re-index all documents (existing + new chunks) for BM25
                        hybrid_retriever.index_documents(all_docs)
                        logger.info(f"✅ Updated BM25 index with {len(chunks)} new chunks (total: {len(all_docs)} documents)")
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to update BM25 index: {e}")
                        import traceback
                        logger.error(traceback.format_exc())
                
                indexed_in_vector_store = True
                logger.info(f"✅ Indexed {len(chunks)} chunks from {file.filename} in vector store")
            except Exception as e:
                logger.error(f"❌ Failed to index document in vector store: {e}")
        
        return UploadResponse(
            file_id=file_id,
            filename=file.filename,
            file_type=file.content_type,
            size=len(content),
            status="uploaded",
            processing_results={
                "pages_extracted": pages_extracted,
                "text_length": len(text_content),
                "language_detected": "en",
                "document_type": "legal_document",
                "indexed_in_vector_store": indexed_in_vector_store,
                "vector_store_documents": vector_store.get_document_count() if vector_store else 0
            }
        )
        
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/files")
async def list_uploaded_files() -> Dict[str, Any]:
    """List uploaded files"""
    try:
        upload_dir = Path("uploads")
        files = []
        
        if upload_dir.exists():
            for file_path in upload_dir.iterdir():
                if file_path.is_file():
                    files.append({
                        "file_id": file_path.stem.split('_')[0],
                        "filename": '_'.join(file_path.stem.split('_')[1:]),
                        "size": file_path.stat().st_size,
                        "upload_date": "2024-01-01T00:00:00Z"
                    })
        
        return {"files": files, "total_files": len(files)}
    except Exception as e:
        logger.error(f"List files error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/files/{file_id}")
async def delete_file(file_id: str) -> Dict[str, Any]:
    """Delete uploaded file"""
    try:
        upload_dir = Path("uploads")
        deleted = False
        
        if upload_dir.exists():
            for file_path in upload_dir.iterdir():
                if file_path.is_file() and file_path.stem.startswith(file_id):
                    file_path.unlink()
                    deleted = True
                    break
        
        if not deleted:
            raise HTTPException(status_code=404, detail="File not found")
        
        return {"file_id": file_id, "status": "deleted"}
    except Exception as e:
        logger.error(f"Delete file error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analyze/{file_id}")
async def analyze_document(file_id: str) -> Dict[str, Any]:
    """Analyze uploaded document with enhanced AI"""
    logger.info(f"🔍 Enhanced analysis for document: {file_id}")
    
    # Track processing start time
    start_time = time.time()
    
    try:
        upload_dir = Path("uploads")
        file_path = None
        
        # Find the file
        if upload_dir.exists():
            for path in upload_dir.iterdir():
                if path.is_file() and path.stem.startswith(file_id):
                    file_path = path
                    break
        
        if not file_path or not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        # Read file content
        async with aiofiles.open(file_path, 'rb') as f:
            content = await f.read()
        
        # Enhanced text extraction
        text_content = ""
        extraction_status = "limited"
        document_preview = ""
        
        if file_path.suffix.lower() == '.pdf':
            # Try to extract text from PDF
            try:
                # Try PyPDF2 first
                try:
                    import PyPDF2
                    import io
                    pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
                    text_content = ""
                    for page_num in range(min(5, len(pdf_reader.pages))):  # Extract first 5 pages
                        page = pdf_reader.pages[page_num]
                        text_content += page.extract_text() + "\n"
                    
                    if text_content.strip():
                        extraction_status = "full"
                        document_preview = text_content[:2000]  # First 2000 chars
                    else:
                        extraction_status = "partial"
                except ImportError:
                    # Fallback to regex extraction
                    pdf_text = content.decode('utf-8', errors='ignore')
                    legal_patterns = [
                        r'(?:Party|Parties|Agreement|Contract|Terms|Conditions)',
                        r'(?:WHEREAS|THEREFORE|NOW THEREFORE)',
                        r'(?:Section|Article|Clause|Paragraph)',
                        r'(?:Signature|Date|Witness)',
                        r'(?:Confidential|Proprietary|Intellectual Property)',
                        r'(?:Liability|Indemnification|Warranty)',
                        r'(?:Termination|Breach|Default)',
                        r'(?:Governing Law|Jurisdiction|Dispute Resolution)'
                    ]
                    
                    extracted_terms = []
                    for pattern in legal_patterns:
                        matches = re.findall(pattern, pdf_text, re.IGNORECASE)
                        extracted_terms.extend(matches)
                    
                    if extracted_terms:
                        text_content = "Legal document with: " + ', '.join(set(extracted_terms[:15]))
                        extraction_status = "partial"
                    else:
                        text_content = "PDF document requiring specialized parsing"
                        extraction_status = "limited"
                        
            except Exception as e:
                logger.warning(f"PDF extraction error: {e}")
                text_content = f"PDF document (Size: {len(content):,} bytes)"
                extraction_status = "limited"
        else:
            # For text files, decode normally
            text_content = content.decode('utf-8', errors='ignore')
            document_preview = text_content[:2000]
            extraction_status = "full"
        
        # Generate enhanced legal analysis using AI
        # Use document_preview if available, otherwise use text_content
        document_content = document_preview if document_preview else text_content
        
        analysis_prompt = f"""You are a legal document analyst. Analyze this legal document and provide a comprehensive summary:

Document Name: {file_path.name}
Document Type: {file_path.suffix.upper()}

Document Content:
{document_content[:1500]}

Please provide a detailed analysis with the following structure:

1. DOCUMENT SUMMARY
   - Type of legal document
   - Main parties involved
   - Purpose and scope of the document

2. KEY TERMS AND PROVISIONS
   - Important clauses and provisions
   - Payment terms (if applicable)
   - Duration and termination conditions
   - Rights and obligations of parties

3. RISK ASSESSMENT
   - Legal risks and concerns
   - Potential issues or ambiguities
   - Compliance considerations

4. RECOMMENDATIONS
   - Action items for the parties
   - Suggested improvements
   - Legal review recommendations

Keep the analysis professional, detailed, and practical for legal review."""
        
        # Generate AI-powered analysis with timeout
        logger.info("Generating AI-powered document analysis...")
        try:
            # Use Ollama with timeout to generate real analysis
            if ollama_client and LLM_AVAILABLE:
                ai_analysis = await asyncio.wait_for(
                    generate_ai_response(analysis_prompt, max_tokens=1200, use_full_response=True),
                    timeout=600.0  # 600 second (10 minute) timeout
                )
                logger.info("✅ AI analysis generated successfully")
            else:
                # Fallback to template if Ollama not available
                logger.warning("Ollama not available, using template analysis")
                raise TimeoutError("Ollama not available")
        except (asyncio.TimeoutError, Exception) as e:
            logger.warning(f"AI analysis timed out or failed: {e}, using fallback")
            ai_analysis = f"""Document Analysis for: {file_path.name}

DOCUMENT TYPE: Legal Document
SIZE: {len(content):,} bytes
FILE TYPE: {file_path.suffix}

SUMMARY:
This document appears to be a legal document and requires professional review. The document has been successfully uploaded and processed.

KEY FINDINGS:
• Document appears to be a legal document
• Professional legal review recommended
• Compliance verification required
• Risk assessment necessary

RECOMMENDATIONS:
1. Review with qualified legal counsel
2. Verify compliance with applicable laws
3. Ensure all terms are clearly defined
4. Implement proper risk management measures

This analysis was generated using our template-based system."""
        
        # Generate AI-powered recommendations
        recommendations_prompt = f"""For this legal document analysis, provide specific recommendations for: "{file_path.name}"

Focus on:
1. Legal review requirements
2. Compliance improvements
3. Risk mitigation measures
4. Best practices to implement
5. Additional considerations

Format as actionable recommendations."""
        
        # Generate AI-powered recommendations with timeout
        try:
            if ollama_client and LLM_AVAILABLE:
                ai_recommendations = await asyncio.wait_for(
                    generate_ai_response(recommendations_prompt, max_tokens=500, use_full_response=True),
                    timeout=600.0  # 600 second (10 minute) timeout
                )
                logger.info("✅ AI recommendations generated successfully")
            else:
                ai_recommendations = ""
        except (asyncio.TimeoutError, Exception) as e:
            logger.warning(f"Recommendations generation failed: {e}")
            ai_recommendations = ""
        
        # Parse recommendations into list
        recommendations = []
        if ai_recommendations:
            lines = ai_recommendations.split('\n')
            for line in lines:
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                    recommendations.append(line)
        
        if not recommendations:
            recommendations = [
                "Review with qualified legal counsel",
                "Verify compliance with applicable laws",
                "Ensure all terms are clearly defined",
                "Implement proper risk management measures"
            ]
        
        # Calculate actual processing time
        elapsed_time = time.time() - start_time
        if elapsed_time < 1:
            processing_time_str = f"{elapsed_time * 1000:.0f} ms"
        elif elapsed_time < 60:
            processing_time_str = f"{elapsed_time:.2f} seconds"
        else:
            minutes = int(elapsed_time // 60)
            seconds = elapsed_time % 60
            processing_time_str = f"{minutes}m {seconds:.1f}s"
        
        # Get version from package.json or use default
        version = "3.0.0"
        try:
            package_json_path = Path(__file__).parent.parent / "package.json"
            if package_json_path.exists():
                with open(package_json_path, 'r') as f:
                    package_data = json.load(f)
                    version = package_data.get("version", "3.0.0")
        except Exception:
            pass  # Use default version if can't read package.json
        
        # Enhanced analysis results
        analysis_results = {
            "file_id": file_id,
            "filename": file_path.name,
            "document_type": "legal_document",
            "analysis": ai_analysis,
            "key_findings": [
                "Document appears to be a legal document",
                "Professional legal review recommended",
                "Compliance verification required",
                "Risk assessment necessary"
            ],
            "recommendations": recommendations[:6],
            "confidence_score": 0.85,
            "risk_level": "medium",
            "compliance_status": "needs_review",
            "processing_time": processing_time_str,
            "text_extraction_status": extraction_status,
            "enhanced_analysis": True,
            "ai_generated": ollama_client is not None,
            "version": version
        }
        
        logger.info(f"✅ Analysis completed in {processing_time_str} for {file_id}")
        return analysis_results
        
    except Exception as e:
        elapsed_time = time.time() - start_time
        logger.error(f"Analysis error after {elapsed_time:.2f}s: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Summarization Agent Endpoints
@app.post("/api/summarize/headnotes")
async def extract_headnotes(request: SummarizeRequest) -> Dict[str, Any]:
    """Extract headnotes from case text"""
    if not summarization_agent:
        raise HTTPException(
            status_code=503,
            detail="Summarization agent not available. Ensure Ollama is running and LLM is initialized."
        )
    
    try:
        logger.info(f"📝 Extracting headnotes from case: {request.case_name or 'Unknown'}")
        result = await summarization_agent.extract_headnotes(
            case_text=request.case_text,
            case_name=request.case_name
        )
        return {
            "status": "success",
            "case_name": request.case_name,
            "headnotes": result
        }
    except Exception as e:
        logger.error(f"Error extracting headnotes: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to extract headnotes: {str(e)}")

@app.post("/api/summarize/ratio-decidendi")
async def extract_ratio_decidendi(request: SummarizeRequest) -> Dict[str, Any]:
    """Extract ratio decidendi (legal reasoning) from case text"""
    if not summarization_agent:
        raise HTTPException(
            status_code=503,
            detail="Summarization agent not available. Ensure Ollama is running and LLM is initialized."
        )
    
    try:
        logger.info(f"⚖️ Extracting ratio decidendi from case: {request.case_name or 'Unknown'}")
        result = await summarization_agent.extract_ratio_decidendi(
            case_text=request.case_text,
            case_name=request.case_name
        )
        return {
            "status": "success",
            "case_name": request.case_name,
            "ratio_decidendi": result
        }
    except Exception as e:
        logger.error(f"Error extracting ratio decidendi: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to extract ratio decidendi: {str(e)}")

@app.post("/api/summarize/obiter-dicta")
async def extract_obiter_dicta(request: SummarizeRequest) -> Dict[str, Any]:
    """Extract obiter dicta (incidental remarks) from case text"""
    if not summarization_agent:
        raise HTTPException(
            status_code=503,
            detail="Summarization agent not available. Ensure Ollama is running and LLM is initialized."
        )
    
    try:
        logger.info(f"💬 Extracting obiter dicta from case: {request.case_name or 'Unknown'}")
        result = await summarization_agent.extract_obiter_dicta(
            case_text=request.case_text,
            case_name=request.case_name
        )
        return {
            "status": "success",
            "case_name": request.case_name,
            "obiter_dicta": result
        }
    except Exception as e:
        logger.error(f"Error extracting obiter dicta: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to extract obiter dicta: {str(e)}")

@app.post("/api/summarize/contrastive")
async def generate_contrastive_summary(request: SummarizeRequest) -> Dict[str, Any]:
    """Generate contrastive summary (pro-plaintiff vs pro-defendant)"""
    if not summarization_agent:
        raise HTTPException(
            status_code=503,
            detail="Summarization agent not available. Ensure Ollama is running and LLM is initialized."
        )
    
    try:
        logger.info(f"⚖️ Generating contrastive summary for case: {request.case_name or 'Unknown'}")
        result = await summarization_agent.contrastive_summary(
            case_text=request.case_text,
            case_name=request.case_name
        )
        return {
            "status": "success",
            "case_name": request.case_name,
            "contrastive_summary": result
        }
    except Exception as e:
        logger.error(f"Error generating contrastive summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate contrastive summary: {str(e)}")

@app.post("/api/summarize/all")
async def extract_all_summaries(request: SummarizeRequest) -> Dict[str, Any]:
    """Extract all summary types (headnotes, ratio decidendi, obiter dicta, contrastive)"""
    if not summarization_agent:
        raise HTTPException(
            status_code=503,
            detail="Summarization agent not available. Ensure Ollama is running and LLM is initialized."
        )
    
    try:
        logger.info(f"📚 Extracting all summaries from case: {request.case_name or 'Unknown'}")
        
        # Run all extractions in parallel for efficiency
        headnotes_task = summarization_agent.extract_headnotes(
            case_text=request.case_text,
            case_name=request.case_name
        )
        ratio_task = summarization_agent.extract_ratio_decidendi(
            case_text=request.case_text,
            case_name=request.case_name
        )
        obiter_task = summarization_agent.extract_obiter_dicta(
            case_text=request.case_text,
            case_name=request.case_name
        )
        contrastive_task = summarization_agent.contrastive_summary(
            case_text=request.case_text,
            case_name=request.case_name
        )
        
        # Wait for all to complete
        headnotes, ratio, obiter, contrastive = await asyncio.gather(
            headnotes_task,
            ratio_task,
            obiter_task,
            contrastive_task,
            return_exceptions=True
        )
        
        # Handle any exceptions
        if isinstance(headnotes, Exception):
            logger.error(f"Headnotes extraction failed: {headnotes}")
            headnotes = {"error": str(headnotes)}
        if isinstance(ratio, Exception):
            logger.error(f"Ratio decidendi extraction failed: {ratio}")
            ratio = {"error": str(ratio)}
        if isinstance(obiter, Exception):
            logger.error(f"Obiter dicta extraction failed: {obiter}")
            obiter = {"error": str(obiter)}
        if isinstance(contrastive, Exception):
            logger.error(f"Contrastive summary failed: {contrastive}")
            contrastive = {"error": str(contrastive)}
        
        return {
            "status": "success",
            "case_name": request.case_name,
            "headnotes": headnotes,
            "ratio_decidendi": ratio,
            "obiter_dicta": obiter,
            "contrastive_summary": contrastive
        }
    except Exception as e:
        logger.error(f"Error extracting all summaries: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to extract summaries: {str(e)}")

# Precedent Reasoning Agent Endpoints
@app.post("/api/precedent/align")
async def cross_case_alignment(request: PrecedentAlignmentRequest) -> Dict[str, Any]:
    """Find cases that support or weaken a legal position"""
    if not precedent_reasoning_agent:
        raise HTTPException(
            status_code=503,
            detail="Precedent reasoning agent not available"
        )
    
    try:
        logger.info(f"🔍 Finding case alignment for position: {request.position[:50]}...")
        result = await precedent_reasoning_agent.cross_case_alignment(
            position=request.position,
            position_type=request.position_type,
            max_cases=request.max_cases
        )
        return {
            "status": "success",
            "alignment": result
        }
    except Exception as e:
        logger.error(f"Error in cross-case alignment: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze case alignment: {str(e)}")

@app.post("/api/precedent/status")
async def check_precedent_status(request: PrecedentStatusRequest) -> Dict[str, Any]:
    """Check if a precedent is outdated (overruled, distinguished, or limited)"""
    if not precedent_reasoning_agent:
        raise HTTPException(
            status_code=503,
            detail="Precedent reasoning agent not available"
        )
    
    try:
        logger.info(f"🔍 Checking precedent status for: {request.case_name}")
        result = await precedent_reasoning_agent.detect_outdated_precedent(
            case_name=request.case_name,
            case_text=request.case_text
        )
        return {
            "status": "success",
            "precedent_status": result
        }
    except Exception as e:
        logger.error(f"Error checking precedent status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to check precedent status: {str(e)}")

# Knowledge Graph Builder Endpoints
@app.get("/api/knowledge-graph/status")
async def knowledge_graph_status() -> Dict[str, Any]:
    """Get knowledge graph status and statistics"""
    if not knowledge_graph:
        return {
            "available": False,
            "is_built": False,
            "message": "Knowledge graph builder not available"
        }
    
    try:
        stats = knowledge_graph.get_graph_stats()
        return {
            "available": True,
            **stats
        }
    except Exception as e:
        logger.error(f"Error getting graph status: {e}")
        return {
            "available": True,
            "is_built": False,
            "error": str(e)
        }

@app.post("/api/knowledge-graph/build")
async def build_knowledge_graph(max_documents: Optional[int] = None) -> Dict[str, Any]:
    """Build or rebuild the knowledge graph"""
    if not knowledge_graph:
        raise HTTPException(
            status_code=503,
            detail="Knowledge graph builder not available"
        )
    
    try:
        logger.info(f"🔗 Building knowledge graph (max_documents: {max_documents})...")
        result = await knowledge_graph.build_graph_async(max_documents=max_documents)
        return {
            "status": "success",
            "build_result": result
        }
    except Exception as e:
        logger.error(f"Error building knowledge graph: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to build knowledge graph: {str(e)}")

@app.get("/api/knowledge-graph/influential-cases")
async def get_influential_cases(top_n: int = 10) -> Dict[str, Any]:
    """Get the most influential or cited cases"""
    if not knowledge_graph:
        raise HTTPException(
            status_code=503,
            detail="Knowledge graph builder not available"
        )
    
    try:
        if not knowledge_graph.is_built:
            return {
                "status": "not_built",
                "message": "Knowledge graph not built yet. Call /api/knowledge-graph/build first.",
                "influential_cases": []
            }
        
        cases = knowledge_graph.get_influential_cases(top_n=top_n)
        return {
            "status": "success",
            "count": len(cases),
            "influential_cases": cases
        }
    except Exception as e:
        logger.error(f"Error getting influential cases: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get influential cases: {str(e)}")

@app.get("/api/knowledge-graph/case/{case_id}/connections")
async def get_case_connections(case_id: str, max_connections: int = 10) -> Dict[str, Any]:
    """Get connections for a specific case in the knowledge graph"""
    if not knowledge_graph:
        raise HTTPException(
            status_code=503,
            detail="Knowledge graph builder not available"
        )
    
    try:
        if not knowledge_graph.is_built:
            return {
                "status": "not_built",
                "message": "Knowledge graph not built yet",
                "connections": []
            }
        
        connections = knowledge_graph.get_case_connections(case_id, max_connections=max_connections)
        return {
            "status": "success",
            **connections
        }
    except Exception as e:
        logger.error(f"Error getting case connections: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get case connections: {str(e)}")

# Redlining & Comparison Agent Endpoints
@app.post("/api/redlining/align")
async def align_contracts(request: ContractComparisonRequest) -> Dict[str, Any]:
    """ML-based clause alignment across two contracts"""
    if not redlining_agent:
        raise HTTPException(
            status_code=503,
            detail="Redlining comparison agent not available"
        )
    
    try:
        logger.info(f"🔍 Aligning clauses between contracts...")
        result = await redlining_agent.align_clauses(
            contract1_text=request.contract1_text,
            contract2_text=request.contract2_text,
            contract1_name=request.contract1_name,
            contract2_name=request.contract2_name
        )
        return {
            "status": "success",
            "alignment": result
        }
    except Exception as e:
        logger.error(f"Error aligning contracts: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to align contracts: {str(e)}")

@app.post("/api/redlining/risk-changes")
async def detect_risk_changes(request: ContractComparisonRequest) -> Dict[str, Any]:
    """Risk-focused change detection (not just diff)"""
    if not redlining_agent:
        raise HTTPException(
            status_code=503,
            detail="Redlining comparison agent not available"
        )
    
    try:
        logger.info(f"⚠️ Detecting risk-focused changes...")
        result = await redlining_agent.detect_risk_changes(
            contract1_text=request.contract1_text,
            contract2_text=request.contract2_text,
            jurisdiction=request.jurisdiction or "US"
        )
        return {
            "status": "success",
            "risk_analysis": result
        }
    except Exception as e:
        logger.error(f"Error detecting risk changes: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to detect risk changes: {str(e)}")

# Clause Generation Agent Endpoints
@app.post("/api/clauses/generate")
async def generate_clause(request: ClauseGenerationRequest) -> Dict[str, Any]:
    """Generate a standard clause (e.g., confidentiality, force majeure)"""
    if not clause_generation_agent:
        raise HTTPException(
            status_code=503,
            detail="Clause generation agent not available"
        )
    
    try:
        logger.info(f"📝 Generating {request.clause_type} clause...")
        result = await clause_generation_agent.generate_clause(
            clause_type=request.clause_type,
            contract_context=request.contract_context,
            jurisdiction=request.jurisdiction or "US",
            custom_requirements=request.custom_requirements
        )
        return {
            "status": "success",
            "clause": result
        }
    except Exception as e:
        logger.error(f"Error generating clause: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate clause: {str(e)}")

@app.post("/api/clauses/detect-missing")
async def detect_missing_clauses(request: MissingClausesRequest) -> Dict[str, Any]:
    """Detect which standard clauses are missing from a contract"""
    if not clause_generation_agent:
        raise HTTPException(
            status_code=503,
            detail="Clause generation agent not available"
        )
    
    try:
        logger.info(f"🔍 Detecting missing standard clauses...")
        missing = clause_generation_agent.detect_missing_clauses(
            contract_text=request.contract_text,
            contract_type=request.contract_type
        )
        return {
            "status": "success",
            "missing_clauses": missing,
            "total_missing": len(missing),
            "required_missing": len([c for c in missing if c.get("is_required", False)])
        }
    except Exception as e:
        logger.error(f"Error detecting missing clauses: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to detect missing clauses: {str(e)}")

@app.post("/api/clauses/generate-all-missing")
async def generate_all_missing_clauses(request: MissingClausesRequest) -> Dict[str, Any]:
    """Detect and generate all missing standard clauses"""
    if not clause_generation_agent:
        raise HTTPException(
            status_code=503,
            detail="Clause generation agent not available"
        )
    
    try:
        logger.info(f"📋 Generating all missing standard clauses...")
        result = await clause_generation_agent.generate_all_missing_clauses(
            contract_text=request.contract_text,
            contract_type=request.contract_type,
            jurisdiction=request.jurisdiction or "US"
        )
        return {
            "status": "success",
            **result
        }
    except Exception as e:
        logger.error(f"Error generating missing clauses: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate missing clauses: {str(e)}")

@app.get("/api/clauses/standard-types")
async def get_standard_clause_types() -> Dict[str, Any]:
    """Get list of available standard clause types"""
    if not clause_generation_agent:
        raise HTTPException(
            status_code=503,
            detail="Clause generation agent not available"
        )
    
    try:
        clause_types = []
        for clause_type, clause in clause_generation_agent.standard_clauses.items():
            clause_types.append({
                "type": clause_type,
                "name": clause.name,
                "description": clause.description,
                "required_in": clause.required_in
            })
        
        return {
            "status": "success",
            "available_types": clause_types,
            "total": len(clause_types)
        }
    except Exception as e:
        logger.error(f"Error getting clause types: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get clause types: {str(e)}")

# Regulatory Monitoring Agent Endpoints
@app.post("/api/regulatory/crawl")
async def crawl_regulations(
    jurisdiction: str = "US",
    max_results: int = 20,
    days_back: int = 30
) -> Dict[str, Any]:
    """Periodically crawl open regulation datasets"""
    if not regulatory_monitoring_agent:
        raise HTTPException(
            status_code=503,
            detail="Regulatory monitoring agent not available"
        )
    
    try:
        logger.info(f"📡 Crawling regulations for {jurisdiction}...")
        updates = await regulatory_monitoring_agent.crawl_regulation_datasets(
            jurisdiction=jurisdiction,
            max_results=max_results,
            days_back=days_back
        )
        return {
            "status": "success",
            "jurisdiction": jurisdiction,
            "updates_found": len(updates),
            "updates": [
                {
                    "regulation_id": u.regulation_id,
                    "title": u.title,
                    "description": u.description,
                    "effective_date": u.effective_date,
                    "impact_level": u.impact_level,
                    "affected_clauses": u.affected_clauses
                }
                for u in updates
            ]
        }
    except Exception as e:
        logger.error(f"Error crawling regulations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to crawl regulations: {str(e)}")

@app.post("/api/regulatory/flag-requirements")
async def flag_new_requirements(request: RegulatoryMonitoringRequest) -> Dict[str, Any]:
    """Flag new legal requirements + suggest clause updates"""
    if not regulatory_monitoring_agent:
        raise HTTPException(
            status_code=503,
            detail="Regulatory monitoring agent not available"
        )
    
    try:
        logger.info(f"🚩 Flagging new requirements for contract...")
        result = await regulatory_monitoring_agent.flag_new_requirements(
            contract_text=request.contract_text,
            jurisdiction=request.jurisdiction or "US",
            days_back=request.days_back or 30
        )
        return {
            "status": "success",
            **result
        }
    except Exception as e:
        logger.error(f"Error flagging requirements: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to flag requirements: {str(e)}")

@app.get("/api/regulatory/last-check/{jurisdiction}")
async def get_last_check_time(jurisdiction: str) -> Dict[str, Any]:
    """Get last check time for a jurisdiction"""
    if not regulatory_monitoring_agent:
        raise HTTPException(
            status_code=503,
            detail="Regulatory monitoring agent not available"
        )
    
    try:
        last_check = regulatory_monitoring_agent.get_last_check_time(jurisdiction)
        return {
            "status": "success",
            "jurisdiction": jurisdiction,
            "last_check_time": last_check,
            "checked": last_check is not None
        }
    except Exception as e:
        logger.error(f"Error getting last check time: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get last check time: {str(e)}")

# Monte Carlo Risk Agent Endpoints
@app.post("/api/risk/monte-carlo")
async def run_monte_carlo_simulation(request: MonteCarloSimulationRequest) -> Dict[str, Any]:
    """Run Monte Carlo simulations on "what if" scenarios"""
    if not monte_carlo_agent:
        raise HTTPException(
            status_code=503,
            detail="Monte Carlo risk agent not available"
        )
    
    try:
        logger.info(f"🎲 Running Monte Carlo simulation ({request.num_simulations or 1000} iterations)...")
        result = await monte_carlo_agent.simulate_scenarios(
            contract_text=request.contract_text,
            scenarios=request.scenarios,
            num_simulations=request.num_simulations or 1000,
            jurisdiction=request.jurisdiction or "US"
        )
        return {
            "status": "success",
            **result
        }
    except Exception as e:
        logger.error(f"Error running Monte Carlo simulation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to run simulation: {str(e)}")

@app.get("/api/risk/scenarios")
async def get_available_scenarios() -> Dict[str, Any]:
    """Get list of available risk scenarios"""
    if not monte_carlo_agent:
        raise HTTPException(
            status_code=503,
            detail="Monte Carlo risk agent not available"
        )
    
    try:
        scenarios = list(monte_carlo_agent.default_probabilities.keys())
        return {
            "status": "success",
            "available_scenarios": scenarios,
            "scenario_descriptions": {
                "counterparty_default": "Simulates counterparty default or insolvency",
                "breach_of_contract": "Simulates contract breach scenarios",
                "payment_delay": "Simulates payment delays and defaults",
                "force_majeure": "Simulates force majeure events",
                "regulatory_change": "Simulates impact of regulatory changes",
                "intellectual_property_dispute": "Simulates IP disputes and claims",
                "data_breach": "Simulates data breach and privacy violations",
                "termination": "Simulates contract termination scenarios"
            },
            "total_scenarios": len(scenarios)
        }
    except Exception as e:
        logger.error(f"Error getting scenarios: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get scenarios: {str(e)}")

# ============================================================================
# LangGraph Multi-Agent Orchestration Endpoints
# ============================================================================
# These endpoints use LangGraph for intelligent workflow orchestration with
# state management, conditional routing, and cross-agent consistency checking.
# ============================================================================

@app.post("/api/langgraph/comprehensive-analysis")
async def langgraph_comprehensive_analysis(request: OrchestrationRequest) -> Dict[str, Any]:
    """Run comprehensive analysis workflow using LangGraph"""
    if not langgraph_orchestrator:
        raise HTTPException(
            status_code=503,
            detail="LangGraph orchestrator not available. Install with: pip install langgraph langchain-core"
        )
    
    try:
        logger.info("🎯 Running LangGraph comprehensive analysis...")
        result = await langgraph_orchestrator.comprehensive_analysis(
            contract_text=request.contract_text,
            jurisdiction=request.jurisdiction or "US"
        )
        return {
            "status": "success",
            "orchestrator": "langgraph",
            **result
        }
    except Exception as e:
        logger.error(f"Error in LangGraph orchestration: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to run workflow: {str(e)}")

@app.post("/api/langgraph/research-and-draft")
async def langgraph_research_and_draft(request: DraftRequest) -> Dict[str, Any]:
    """Run research → draft → review workflow using LangGraph"""
    if not langgraph_orchestrator:
        raise HTTPException(
            status_code=503,
            detail="LangGraph orchestrator not available. Install with: pip install langgraph langchain-core"
        )
    
    try:
        logger.info("🔄 Running LangGraph research → draft workflow...")
        result = await langgraph_orchestrator.research_and_draft(
            query=request.query,
            document_type=request.document_type or "contract"
        )
        return {
            "status": "success",
            "orchestrator": "langgraph",
            **result
        }
    except Exception as e:
        logger.error(f"Error in LangGraph workflow: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to run workflow: {str(e)}")

@app.post("/api/langgraph/cross-consistency-check")
async def langgraph_cross_consistency_check(request: ConsistencyCheckRequest) -> Dict[str, Any]:
    """Run cross-consistency check workflow using LangGraph"""
    if not langgraph_orchestrator:
        raise HTTPException(
            status_code=503,
            detail="LangGraph orchestrator not available. Install with: pip install langgraph langchain-core"
        )
    
    try:
        logger.info("🔍 Running LangGraph cross-consistency check...")
        result = await langgraph_orchestrator.cross_consistency_check(
            clause_text=request.clause_text,
            jurisdiction=request.jurisdiction or "US"
        )
        return {
            "status": "success",
            "orchestrator": "langgraph",
            **result
        }
    except Exception as e:
        logger.error(f"Error in LangGraph consistency check: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to run consistency check: {str(e)}")

@app.get("/api/langgraph/status")
async def langgraph_status() -> Dict[str, Any]:
    """Get LangGraph orchestrator status"""
    if not langgraph_orchestrator:
        return {
            "available": False,
            "message": "LangGraph orchestrator not available. Install with: pip install langgraph langchain-core",
            "langgraph_installed": False
        }
    
    try:
        workflows_available = []
        if hasattr(langgraph_orchestrator, 'comprehensive_workflow') and langgraph_orchestrator.comprehensive_workflow:
            workflows_available.append("comprehensive-analysis")
        if hasattr(langgraph_orchestrator, 'research_draft_workflow') and langgraph_orchestrator.research_draft_workflow:
            workflows_available.append("research-and-draft")
        if hasattr(langgraph_orchestrator, 'consistency_check_workflow') and langgraph_orchestrator.consistency_check_workflow:
            workflows_available.append("cross-consistency-check")
        
        return {
            "available": True,
            "langgraph_installed": True,
            "workflows_available": workflows_available,
            "total_workflows": len(workflows_available),
            "features": [
                "State management",
                "Conditional routing",
                "Multi-agent orchestration",
                "Cross-consistency checking"
            ]
        }
    except Exception as e:
        return {
            "available": True,
            "langgraph_installed": True,
            "error": str(e)
        }

# ============================================================================
# Multi-Modal Legal Intelligence Endpoints
# ============================================================================

# OCR Agent Endpoints
@app.post("/api/ocr/process")
async def process_ocr(request: OCRRequest) -> Dict[str, Any]:
    """Process document with OCR and entity extraction"""
    if not ocr_agent:
        raise HTTPException(
            status_code=503,
            detail="OCR Agent not available. Install with: pip install pytesseract pillow pdf2image"
        )
    
    try:
        result = ocr_agent.process_document(
            file_path=request.file_path,
            extract_entities=request.extract_entities
        )
        return result
    except Exception as e:
        logger.error(f"OCR processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ocr/extract-entities")
async def extract_entities_from_text(text: str = Body(...)) -> Dict[str, Any]:
    """Extract entities from text"""
    if not ocr_agent:
        raise HTTPException(
            status_code=503,
            detail="OCR Agent not available"
        )
    
    try:
        result = ocr_agent.extract_entities(text)
        return result
    except Exception as e:
        logger.error(f"Entity extraction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ocr/status")
async def ocr_status() -> Dict[str, Any]:
    """Get OCR Agent status"""
    if not ocr_agent:
        return {
            "available": False,
            "ocr_available": False,
            "spacy_available": False,
            "message": "OCR Agent not available"
        }
    
    return {
        "available": True,
        "ocr_available": ocr_agent.ocr_available,
        "spacy_available": ocr_agent.spacy_available,
        "features": {
            "image_ocr": ocr_agent.ocr_available,
            "pdf_ocr": ocr_agent.ocr_available,
            "entity_extraction": True,
            "spacy_ner": ocr_agent.spacy_available
        }
    }

# Timeline Builder Agent Endpoints
@app.post("/api/timeline/add-document")
async def add_timeline_document(request: TimelineDocumentRequest) -> Dict[str, Any]:
    """Add document to timeline builder"""
    if not timeline_builder_agent:
        raise HTTPException(
            status_code=503,
            detail="Timeline Builder Agent not available"
        )
    
    try:
        result = timeline_builder_agent.add_document(
            document_id=request.document_id,
            text=request.text,
            metadata=request.metadata
        )
        return result
    except Exception as e:
        logger.error(f"Timeline document addition error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/timeline/build")
async def build_timeline(request: TimelineBuildRequest) -> Dict[str, Any]:
    """Build timeline from all added documents"""
    if not timeline_builder_agent:
        raise HTTPException(
            status_code=503,
            detail="Timeline Builder Agent not available"
        )
    
    try:
        result = timeline_builder_agent.build_timeline(sort_by_date=request.sort_by_date)
        return result
    except Exception as e:
        logger.error(f"Timeline build error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/timeline/entity/{entity_name}")
async def get_entity_timeline(entity_name: str) -> Dict[str, Any]:
    """Get timeline for specific entity"""
    if not timeline_builder_agent:
        raise HTTPException(
            status_code=503,
            detail="Timeline Builder Agent not available"
        )
    
    try:
        result = timeline_builder_agent.get_entity_timeline(entity_name)
        return result
    except Exception as e:
        logger.error(f"Entity timeline error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/timeline/clear")
async def clear_timeline() -> Dict[str, Any]:
    """Clear timeline builder"""
    if not timeline_builder_agent:
        raise HTTPException(
            status_code=503,
            detail="Timeline Builder Agent not available"
        )
    
    try:
        timeline_builder_agent.clear()
        return {"success": True, "message": "Timeline cleared"}
    except Exception as e:
        logger.error(f"Timeline clear error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Speech TTS Agent Endpoints
@app.post("/api/speech/transcribe")
async def transcribe_audio(request: TranscribeRequest) -> Dict[str, Any]:
    """Transcribe audio file to text"""
    if not speech_tts_agent:
        raise HTTPException(
            status_code=503,
            detail="Speech TTS Agent not available. Install with: pip install openai-whisper"
        )
    
    try:
        if request.transcript_type == "court":
            result = await speech_tts_agent.transcribe_court_transcript(
                audio_path=request.audio_path
            )
        else:
            result = await speech_tts_agent.transcribe_audio(
                audio_path=request.audio_path,
                language=request.language
            )
        return result
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/speech/tts")
async def text_to_speech(request: TTSRequest) -> Dict[str, Any]:
    """Convert text to speech"""
    if not speech_tts_agent:
        raise HTTPException(
            status_code=503,
            detail="Speech TTS Agent not available. Install with: pip install edge-tts"
        )
    
    try:
        result = await speech_tts_agent.text_to_speech(
            text=request.text,
            voice=request.voice,
            rate=request.rate,
            pitch=request.pitch
        )
        return result
    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/speech/summarize-and-speak")
async def summarize_and_speak(request: SummarizeAndSpeakRequest) -> Dict[str, Any]:
    """Generate spoken summary of text"""
    if not speech_tts_agent:
        raise HTTPException(
            status_code=503,
            detail="Speech TTS Agent not available"
        )
    
    try:
        result = await speech_tts_agent.summarize_and_speak(
            text=request.text,
            summary_length=request.summary_length,
            voice=request.voice
        )
        return result
    except Exception as e:
        logger.error(f"Summarize and speak error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/speech/voices")
async def get_available_voices(language: str = "en") -> Dict[str, Any]:
    """Get available TTS voices"""
    if not speech_tts_agent:
        raise HTTPException(
            status_code=503,
            detail="Speech TTS Agent not available"
        )
    
    try:
        result = await speech_tts_agent.get_available_voices(language=language)
        return result
    except Exception as e:
        logger.error(f"Get voices error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/speech/status")
async def speech_tts_status() -> Dict[str, Any]:
    """Get Speech TTS Agent status"""
    if not speech_tts_agent:
        return {
            "available": False,
            "whisper_available": False,
            "edgetts_available": False,
            "message": "Speech TTS Agent not available"
        }
    
    return speech_tts_agent.get_status()

# ============================================================================
# HITL (Human-in-the-Loop) Endpoints
# ============================================================================

@app.post("/api/hitl/feedback")
async def submit_hitl_feedback(request: HITLFeedbackRequest) -> Dict[str, Any]:
    """Submit user feedback for agent outputs"""
    if not hitl_service:
        raise HTTPException(
            status_code=503,
            detail="HITL service not available"
        )
    
    try:
        feedback_id = hitl_service.submit_feedback(
            feature_type=request.feature_type,
            action=request.action,
            original_output=request.original_output,
            user_edit=request.user_edit,
            feedback_reason=request.feedback_reason,
            metadata=request.metadata
        )
        
        return {
            "status": "success",
            "feedback_id": feedback_id,
            "message": f"Feedback submitted successfully ({request.action})"
        }
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/hitl/stats")
async def get_hitl_stats(feature_type: Optional[str] = None) -> Dict[str, Any]:
    """Get feedback statistics"""
    if not hitl_service:
        raise HTTPException(
            status_code=503,
            detail="HITL service not available"
        )
    
    try:
        stats = hitl_service.get_feedback_stats(feature_type)
        return {
            "status": "success",
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/hitl/insights")
async def get_hitl_insights(feature_type: Optional[str] = None) -> Dict[str, Any]:
    """Get learning insights"""
    if not hitl_service:
        raise HTTPException(
            status_code=503,
            detail="HITL service not available"
        )
    
    try:
        insights = hitl_service.get_learning_insights(feature_type)
        return {
            "status": "success",
            "insights": insights
        }
    except Exception as e:
        logger.error(f"Error getting insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/hitl/recent")
async def get_recent_feedback(limit: int = 10) -> Dict[str, Any]:
    """Get recent feedback entries"""
    if not hitl_service:
        raise HTTPException(
            status_code=503,
            detail="HITL service not available"
        )
    
    try:
        feedback = hitl_service.get_recent_feedback(limit)
        return {
            "status": "success",
            "feedback": feedback
        }
    except Exception as e:
        logger.error(f"Error getting recent feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Domain Compliance Packs Endpoints
# ============================================================================

@app.post("/api/compliance/domain-check")
async def check_domain_compliance(request: DomainComplianceRequest) -> Dict[str, Any]:
    """Check compliance against domain-specific rules"""
    if not domain_compliance_packs:
        raise HTTPException(
            status_code=503,
            detail="Domain compliance packs not available"
        )
    
    try:
        result = domain_compliance_packs.check_compliance(
            contract_text=request.content,
            domains=request.domains,
            jurisdiction=request.jurisdiction
        )
        
        return {
            "status": "success",
            **result
        }
    except Exception as e:
        logger.error(f"Error checking domain compliance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/compliance/domains")
async def get_available_domains() -> Dict[str, Any]:
    """Get list of available domain compliance packs"""
    if not domain_compliance_packs:
        raise HTTPException(
            status_code=503,
            detail="Domain compliance packs not available"
        )
    
    try:
        domains = domain_compliance_packs.get_available_domains()
        return {
            "status": "success",
            "domains": domains
        }
    except Exception as e:
        logger.error(f"Error getting domains: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/compliance/domain/{domain}")
async def get_domain_info(domain: str) -> Dict[str, Any]:
    """Get information about a specific domain pack"""
    if not domain_compliance_packs:
        raise HTTPException(
            status_code=503,
            detail="Domain compliance packs not available"
        )
    
    try:
        info = domain_compliance_packs.get_domain_info(domain)
        return {
            "status": "success",
            **info
        }
    except Exception as e:
        logger.error(f"Error getting domain info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Explainability Endpoints
# ============================================================================

@app.post("/api/explainability/format-citation")
async def format_citation(citation_text: str, citation_type: Optional[str] = None) -> Dict[str, Any]:
    """Format a citation with explainability metadata"""
    if not explainability_service:
        raise HTTPException(
            status_code=503,
            detail="Explainability service not available"
        )
    
    try:
        citation = explainability_service.format_citation(citation_text, citation_type)
        return {
            "status": "success",
            "citation": {
                "text": citation.text,
                "type": citation.type,
                "credibility_score": citation.credibility_score,
                "probability": citation.probability,
                "metadata": citation.metadata
            }
        }
    except Exception as e:
        logger.error(f"Error formatting citation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "LegisAI AI-Powered Legal Assistant",
        "status": "operational",
        "version": "4.0.0",
        "service": "LegisAI AI-Powered v4.0",
        "features": [
            "Hybrid legal research (FAISS + BM25)",
            "AI-powered document drafting with streaming",
            "Comprehensive compliance checking",
            "Advanced clause analysis & risk detection",
            "Multi-agent orchestration (LangGraph)",
            "Cross-consistency checking",
            "Knowledge graph builder",
            "Regulatory monitoring",
            "Monte Carlo risk simulations",
            "Legal knowledge base integration"
        ],
        "orchestration": {
            "framework": "LangGraph",
            "available": langgraph_orchestrator is not None,
            "workflows": [
                "comprehensive-analysis",
                "research-and-draft",
                "cross-consistency-check"
            ] if langgraph_orchestrator else []
        },
        "docs": "/docs",
        "api_endpoints": 47
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        workers=1
    )
