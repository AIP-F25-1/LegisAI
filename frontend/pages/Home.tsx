import React from 'react'
import { Link } from 'react-router-dom'
import { 
  Search, 
  FileText, 
  Shield, 
  Upload, 
  Brain,
  Scale,
  ArrowRight
} from 'lucide-react'

const Home: React.FC = () => {
  const features = [
    {
      icon: Search,
      title: 'Legal Research',
      description: 'AI-powered legal research with precedent analysis and case law retrieval',
      href: '/research',
      color: 'bg-blue-500'
    },
    {
      icon: FileText,
      title: 'Document Drafting',
      description: 'Generate legal documents, contracts, and clauses with AI assistance',
      href: '/drafting',
      color: 'bg-green-500'
    },
    {
      icon: Shield,
      title: 'Compliance Check',
      description: 'Automated compliance checking against GDPR, US Code, and other regulations',
      href: '/compliance',
      color: 'bg-purple-500'
    },
    {
      icon: Upload,
      title: 'Document Analysis',
      description: 'Upload and analyze legal documents with AI-powered insights',
      href: '/upload',
      color: 'bg-orange-500'
    }
  ]

  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <div className="text-center">
        <div className="flex justify-center mb-6">
          <div className="p-4 bg-blue-100 rounded-full">
            <Scale className="h-16 w-16 text-blue-600" />
          </div>
        </div>
        <h1 className="text-4xl font-bold text-gray-900 sm:text-5xl md:text-6xl">
          LegisAI
        </h1>
        <p className="mt-3 max-w-md mx-auto text-base text-gray-500 sm:text-lg md:mt-5 md:text-xl md:max-w-3xl">
          Multi-Agent Legal Research and Drafting Assistant powered by AI
        </p>
        <div className="mt-5 max-w-md mx-auto sm:flex sm:justify-center md:mt-8">
          <div className="rounded-md shadow">
            <Link
              to="/research"
              className="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 md:py-4 md:text-lg md:px-10"
            >
              Get Started
              <ArrowRight className="ml-2 h-5 w-5" />
            </Link>
          </div>
        </div>
      </div>

      {/* Features Grid */}
      <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-4">
        {features.map((feature) => (
          <Link
            key={feature.title}
            to={feature.href}
            className="group relative bg-white p-6 rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow duration-200"
          >
            <div>
              <span className={`inline-flex p-3 rounded-md ${feature.color} text-white`}>
                <feature.icon className="h-6 w-6" />
              </span>
            </div>
            <div className="mt-8">
              <h3 className="text-lg font-medium text-gray-900 group-hover:text-blue-600">
                {feature.title}
              </h3>
              <p className="mt-2 text-base text-gray-500">
                {feature.description}
              </p>
            </div>
            <span className="absolute top-6 right-6 text-gray-300 group-hover:text-gray-400">
              <ArrowRight className="h-5 w-5" />
            </span>
          </Link>
        ))}
      </div>

      {/* How It Works */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">How It Works</h2>
        <div className="grid grid-cols-1 gap-8 md:grid-cols-3">
          <div className="text-center">
            <div className="flex justify-center mb-4">
              <div className="p-3 bg-blue-100 rounded-full">
                <Brain className="h-8 w-8 text-blue-600" />
              </div>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">Multi-Agent AI</h3>
            <p className="text-gray-500">
              Our system uses specialized AI agents for research, drafting, compliance, and reasoning
            </p>
          </div>
          <div className="text-center">
            <div className="flex justify-center mb-4">
              <div className="p-3 bg-green-100 rounded-full">
                <Search className="h-8 w-8 text-green-600" />
              </div>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">Legal Knowledge</h3>
            <p className="text-gray-500">
              Access to comprehensive legal databases including case law, regulations, and precedents
            </p>
          </div>
          <div className="text-center">
            <div className="flex justify-center mb-4">
              <div className="p-3 bg-purple-100 rounded-full">
                <Shield className="h-8 w-8 text-purple-600" />
              </div>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">Compliance Focus</h3>
            <p className="text-gray-500">
              Automated compliance checking ensures your documents meet legal requirements
            </p>
          </div>
        </div>
      </div>

      {/* Technology Stack */}
      <div className="bg-gray-50 rounded-lg p-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Powered by Open Source AI</h2>
        <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
          <div className="text-center">
            <div className="text-sm font-medium text-gray-900">Mistral-7B</div>
            <div className="text-xs text-gray-500">Summarization</div>
          </div>
          <div className="text-center">
            <div className="text-sm font-medium text-gray-900">LLaMA-3-8B</div>
            <div className="text-xs text-gray-500">Text Generation</div>
          </div>
          <div className="text-center">
            <div className="text-sm font-medium text-gray-900">DeepSeek-R1</div>
            <div className="text-xs text-gray-500">Reasoning</div>
          </div>
          <div className="text-center">
            <div className="text-sm font-medium text-gray-900">ChatLaw-13B</div>
            <div className="text-xs text-gray-500">Legal Analysis</div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Home
