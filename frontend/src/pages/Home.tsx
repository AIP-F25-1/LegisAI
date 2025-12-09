import React from 'react'
import { Link } from 'react-router-dom'
import {
  Search,
  FileText,
  Shield,
  Upload,
  Brain,
  Scale,
  ArrowRight,
  Network,
  GitBranch,
  BarChart3,
  FileCheck,
  AlertTriangle,
  Clock,
  Eye,
  Mic,
  Image,
  Zap,
  Layers,
  Target
} from 'lucide-react'

const Home: React.FC = () => {
  const coreFeatures = [
    {
      icon: Search,
      title: 'Legal Research',
      description: 'AI-powered legal research with hybrid search (FAISS + BM25), precedent analysis, and case law retrieval from CourtListener API',
      href: '/research',
      color: 'bg-blue-500/20',
      badge: 'Hybrid Search'
    },
    {
      icon: FileText,
      title: 'Document Drafting',
      description: 'Generate legal documents, contracts, and clauses with AI assistance and streaming responses',
      href: '/drafting',
      color: 'bg-green-500/20',
      badge: 'AI-Powered'
    },
    {
      icon: Shield,
      title: 'Compliance Check',
      description: 'Automated compliance checking against GDPR, CCPA, US Code, and jurisdiction-aware regulations',
      href: '/compliance',
      color: 'bg-purple-500/20',
      badge: 'Multi-Jurisdiction'
    },
    {
      icon: Upload,
      title: 'Document Analysis',
      description: 'Upload and analyze legal documents with OCR, entity extraction, and AI-powered insights',
      href: '/upload',
      color: 'bg-orange-500/20',
      badge: 'OCR + AI'
    }
  ]

  const advancedAgents = [
    {
      icon: Brain,
      title: 'Summarization Agent',
      description: 'Extract headnotes, ratio decidendi, obiter dicta, and contrastive analysis (pro-plaintiff vs. pro-defendant)',
      color: 'text-blue-600'
    },
    {
      icon: Target,
      title: 'Precedent Reasoning',
      description: 'Cross-case alignment to find supporting/weakening cases and detect outdated precedents',
      color: 'text-green-600'
    },
    {
      icon: Network,
      title: 'Knowledge Graph',
      description: 'Auto-build graph of precedents, statutes, and clauses. Identify most influential cases',
      color: 'text-purple-600'
    },
    {
      icon: FileCheck,
      title: 'Redlining & Comparison',
      description: 'ML-based clause alignment across contracts with risk-focused change detection',
      color: 'text-orange-600'
    },
    {
      icon: Layers,
      title: 'Clause Generation',
      description: 'Detect missing standard clauses and generate customized versions (confidentiality, force majeure, etc.)',
      color: 'text-pink-600'
    },
    {
      icon: AlertTriangle,
      title: 'Regulatory Monitoring',
      description: 'Track regulatory changes, flag new legal requirements, and suggest clause updates',
      color: 'text-red-600'
    },
    {
      icon: BarChart3,
      title: 'Monte Carlo Risk',
      description: 'What-if scenario simulations for counterparty defaults, breaches, and risk assessment',
      color: 'text-indigo-600'
    },
    {
      icon: GitBranch,
      title: 'LangGraph Orchestration',
      description: 'Multi-agent workflows with state management, conditional routing, and cross-consistency checking',
      color: 'text-cyan-600'
    }
  ]

  const multimodalFeatures = [
    {
      icon: Image,
      title: 'Document OCR',
      description: 'Process scanned legal filings with Tesseract OCR and extract entities (parties, dates, monetary values)',
      color: 'text-blue-600'
    },
    {
      icon: Clock,
      title: 'Timeline Builder',
      description: 'Construct case chronologies from multiple documents with automatic entity linking across filings',
      color: 'text-green-600'
    },
    {
      icon: Mic,
      title: 'Speech-to-Text & TTS',
      description: 'Whisper for court transcript ingestion and EdgeTTS for spoken summaries',
      color: 'text-purple-600'
    }
  ]

  return (
    <div className="space-y-16">
      {/* Hero Section */}
      <div className="text-center">
        <div className="flex justify-center mb-6">
          <div className="p-4 bg-gradient-to-br from-blue-100 to-purple-100 rounded-full">
            <Scale className="h-16 w-16 text-blue-600" />
          </div>
        </div>
        <h1 className="text-4xl font-bold text-white sm:text-5xl md:text-6xl bg-gradient-to-r from-white to-blue-200 bg-clip-text text-transparent">
          LegisAI
        </h1>
        <p className="mt-3 max-w-2xl mx-auto text-lg text-white/90 sm:text-xl md:mt-5 md:text-2xl">
          AI-Powered Legal Assistant with Multi-Agent Orchestration
        </p>
        <p className="mt-4 max-w-3xl mx-auto text-base text-white/80">
          Advanced legal research, document drafting, compliance checking, and intelligent analysis powered by LangGraph orchestration and local LLMs
        </p>
        <div className="mt-8 flex flex-col sm:flex-row gap-4 justify-center items-center">
          <Link
            to="/research"
            className="glass-button inline-flex items-center px-8 py-3 text-base font-medium"
          >
            Get Started
            <ArrowRight className="ml-2 h-5 w-5" />
          </Link>
          <Link
            to="/upload"
            className="glass-button inline-flex items-center px-8 py-3 text-base font-medium"
          >
            Analyze Document
            <Eye className="ml-2 h-5 w-5" />
          </Link>
        </div>
      </div>

      {/* Core Features Grid */}
      <div>
        <h2 className="text-3xl font-bold text-white text-center mb-4">Core Features</h2>
        <p className="text-center text-white/80 mb-8">Essential legal AI capabilities at your fingertips</p>
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {coreFeatures.map((feature) => (
            <Link
              key={feature.title}
              to={feature.href}
              className="group relative liquid-glass-card glass-content p-6 hover:scale-[1.02] transition-all duration-300"
            >
              <div className="flex items-start justify-between">
                <span className={`inline-flex p-3 ${feature.color} backdrop-blur-sm text-white shadow-lg`}>
                  <feature.icon className="h-6 w-6" />
                </span>
                <span className="text-xs px-2 py-1 bg-white/10 text-white font-medium backdrop-blur-sm">
                  {feature.badge}
                </span>
              </div>
              <div className="mt-6">
                <h3 className="text-lg font-semibold text-white group-hover:text-blue-200 transition-colors">
                  {feature.title}
                </h3>
                <p className="mt-2 text-sm text-white/80 leading-relaxed">
                  {feature.description}
                </p>
              </div>
              <span className="absolute bottom-6 right-6 text-white/60 group-hover:text-white transition-colors">
                <ArrowRight className="h-5 w-5" />
              </span>
            </Link>
          ))}
        </div>
      </div>

      {/* Advanced AI Agents */}
      <div className="p-8 md:p-12">
        <div className="text-center mb-8">
          <div className="inline-flex items-center px-4 py-2 bg-white/20 rounded-full mb-4">
            <Zap className="h-5 w-5 text-white mr-2" />
            <span className="text-sm font-medium text-white">Advanced AI Agents</span>
          </div>
          <h2 className="text-3xl font-bold text-white mb-4">Intelligent Legal Agents</h2>
          <p className="text-white/80 max-w-2xl mx-auto">
            Specialized AI agents powered by LangGraph orchestration for complex legal workflows
          </p>
        </div>
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {advancedAgents.map((agent, index) => (
            <div
              key={index}
              className="liquid-glass-card glass-content p-6 hover:scale-[1.02] transition-all duration-300"
            >
              <div className="inline-flex p-3 rounded-lg bg-white/10 backdrop-blur-sm mb-4">
                <agent.icon className="h-8 w-8 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">{agent.title}</h3>
              <p className="text-sm text-white/80 leading-relaxed">{agent.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Multi-Modal Features */}
      <div>
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-white mb-4">Multi-Modal Legal Intelligence</h2>
          <p className="text-white/80 max-w-2xl mx-auto">
            Process documents, audio, and build timelines with advanced AI capabilities
          </p>
        </div>
        <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
          {multimodalFeatures.map((feature, index) => (
            <div
              key={index}
              className="liquid-glass-card glass-content p-6 hover:scale-[1.02] transition-all duration-300"
            >
              <div className="inline-flex p-3 bg-white/10 backdrop-blur-sm mb-4">
                <feature.icon className="h-10 w-10 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">{feature.title}</h3>
              <p className="text-sm text-white/80 leading-relaxed">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* How It Works */}
      <div className="p-8 md:p-12">
        <h2 className="text-3xl font-bold text-white mb-8 text-center">How It Works</h2>
        <div className="grid grid-cols-1 gap-8 md:grid-cols-3">
          <div className="text-center liquid-glass-card glass-content p-6 hover:scale-[1.02] transition-all duration-300">
            <div className="flex justify-center mb-4">
              <div className="p-4 bg-blue-500/20 backdrop-blur-sm">
                <Brain className="h-10 w-10 text-white" />
              </div>
            </div>
            <h3 className="text-xl font-semibold text-white mb-3">Multi-Agent AI</h3>
            <p className="text-white/80 leading-relaxed">
              Specialized AI agents orchestrated with LangGraph for research, drafting, compliance, and reasoning.
              State management ensures seamless workflows across complex legal tasks.
            </p>
          </div>
          <div className="text-center liquid-glass-card glass-content p-6 hover:scale-[1.02] transition-all duration-300">
            <div className="flex justify-center mb-4">
              <div className="p-4 bg-green-500/20 backdrop-blur-sm">
                <Network className="h-10 w-10 text-white" />
              </div>
            </div>
            <h3 className="text-xl font-semibold text-white mb-3">Hybrid Search</h3>
            <p className="text-white/80 leading-relaxed">
              Combines semantic search (FAISS) with keyword search (BM25) for comprehensive legal research.
              Access to 1,200+ contract clauses and real-time case law via CourtListener API.
            </p>
          </div>
          <div className="text-center liquid-glass-card glass-content p-6 hover:scale-[1.02] transition-all duration-300">
            <div className="flex justify-center mb-4">
              <div className="p-4 bg-purple-500/20 backdrop-blur-sm">
                <Shield className="h-10 w-10 text-white" />
              </div>
            </div>
            <h3 className="text-xl font-semibold text-white mb-3">Intelligent Analysis</h3>
            <p className="text-white/80 leading-relaxed">
              Automated compliance checking, risk assessment, and clause analysis with jurisdiction-aware rules.
              Timeline builder tracks case chronologies with entity linking across documents.
            </p>
          </div>
        </div>
      </div>

      {/* Technology Stack */}
      <div className="p-8 md:p-12">
        <h2 className="text-3xl font-bold text-white mb-8 text-center">Powered by Open Source AI</h2>
        <div className="grid grid-cols-2 gap-6 md:grid-cols-4 lg:grid-cols-6">
          <div className="text-center liquid-glass-card glass-content p-4">
            <div className="text-sm font-semibold text-white mb-1">Ollama</div>
            <div className="text-xs text-white/70">LLM Runtime</div>
          </div>
          <div className="text-center liquid-glass-card glass-content p-4">
            <div className="text-sm font-semibold text-white mb-1">Llama 3.1</div>
            <div className="text-xs text-white/70">8B Model</div>
          </div>
          <div className="text-center liquid-glass-card glass-content p-4">
            <div className="text-sm font-semibold text-white mb-1">LangGraph</div>
            <div className="text-xs text-white/70">Orchestration</div>
          </div>
          <div className="text-center liquid-glass-card glass-content p-4">
            <div className="text-sm font-semibold text-white mb-1">FAISS</div>
            <div className="text-xs text-white/70">Vector Search</div>
          </div>
          <div className="text-center liquid-glass-card glass-content p-4">
            <div className="text-sm font-semibold text-white mb-1">Sentence Transformers</div>
            <div className="text-xs text-white/70">Embeddings</div>
          </div>
          <div className="text-center liquid-glass-card glass-content p-4">
            <div className="text-sm font-semibold text-white mb-1">FastAPI</div>
            <div className="text-xs text-white/70">Backend</div>
          </div>
        </div>
        <div className="mt-8 grid grid-cols-2 gap-6 md:grid-cols-4 lg:grid-cols-6">
          <div className="text-center liquid-glass-card glass-content p-4">
            <div className="text-sm font-semibold text-white mb-1">React + TypeScript</div>
            <div className="text-xs text-white/70">Frontend</div>
          </div>
          <div className="text-center liquid-glass-card glass-content p-4">
            <div className="text-sm font-semibold text-white mb-1">Tesseract</div>
            <div className="text-xs text-white/70">OCR</div>
          </div>
          <div className="text-center liquid-glass-card glass-content p-4">
            <div className="text-sm font-semibold text-white mb-1">Whisper</div>
            <div className="text-xs text-white/70">Speech-to-Text</div>
          </div>
          <div className="text-center liquid-glass-card glass-content p-4">
            <div className="text-sm font-semibold text-white mb-1">EdgeTTS</div>
            <div className="text-xs text-white/70">Text-to-Speech</div>
          </div>
          <div className="text-center liquid-glass-card glass-content p-4">
            <div className="text-sm font-semibold text-white mb-1">spaCy</div>
            <div className="text-xs text-white/70">NER</div>
          </div>
          <div className="text-center liquid-glass-card glass-content p-4">
            <div className="text-sm font-semibold text-white mb-1">BM25</div>
            <div className="text-xs text-white/70">Keyword Search</div>
          </div>
        </div>
      </div>

      {/* State Persistence & Timeline */}
      <div className="p-8 md:p-12">
        <div className="text-center mb-8">
          <Clock className="h-12 w-12 text-white mx-auto mb-4" />
          <h2 className="text-3xl font-bold text-white mb-4">Session Management</h2>
          <p className="text-white/80 max-w-2xl mx-auto">
            Your work persists across navigation with intelligent state management
          </p>
        </div>
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
          <div className="liquid-glass-card glass-content p-6">
            <h3 className="text-lg font-semibold text-white mb-3">State Persistence</h3>
            <ul className="space-y-2 text-sm text-white/90">
              <li className="flex items-start">
                <span className="text-blue-300 mr-2">✓</span>
                <span>All results cached in sessionStorage</span>
              </li>
              <li className="flex items-start">
                <span className="text-blue-300 mr-2">✓</span>
                <span>Navigate between tabs without losing work</span>
              </li>
              <li className="flex items-start">
                <span className="text-blue-300 mr-2">✓</span>
                <span>History panels show previous activities</span>
              </li>
              <li className="flex items-start">
                <span className="text-blue-300 mr-2">✓</span>
                <span>Run multiple agents simultaneously</span>
              </li>
            </ul>
          </div>
          <div className="liquid-glass-card glass-content p-6">
            <h3 className="text-lg font-semibold text-white mb-3">Timeline Builder</h3>
            <ul className="space-y-2 text-sm text-white/90">
              <li className="flex items-start">
                <span className="text-green-300 mr-2">✓</span>
                <span>Automatic case chronology construction</span>
              </li>
              <li className="flex items-start">
                <span className="text-green-300 mr-2">✓</span>
                <span>Entity linking across multiple documents</span>
              </li>
              <li className="flex items-start">
                <span className="text-green-300 mr-2">✓</span>
                <span>Visible on all pages during active session</span>
              </li>
              <li className="flex items-start">
                <span className="text-green-300 mr-2">✓</span>
                <span>Tracks all feature activities automatically</span>
              </li>
            </ul>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="liquid-glass-card glass-content text-center p-12 md:p-16">
        <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">Ready to Transform Your Legal Workflow?</h2>
        <p className="text-xl md:text-2xl text-white/90 mb-8 max-w-3xl mx-auto">
          Experience the power of AI-driven legal research, drafting, and analysis
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            to="/research"
            className="glass-button inline-flex items-center px-8 py-3 text-base font-medium"
          >
            Start Researching
            <Search className="ml-2 h-5 w-5" />
          </Link>
          <Link
            to="/upload"
            className="glass-button inline-flex items-center px-8 py-3 text-base font-medium bg-white/20 hover:bg-white/30"
          >
            Analyze Document
            <Upload className="ml-2 h-5 w-5" />
          </Link>
        </div>
      </div>
    </div>
  )
}

export default Home
