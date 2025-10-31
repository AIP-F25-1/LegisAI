import React from 'react'

// Markdown renderer for streaming content
export const MarkdownRenderer: React.FC<{ content: string }> = ({ content }) => {
  const formatMarkdown = (text: string) => {
    const lines = text.split('\n')
    const elements: React.ReactNode[] = []
    let currentIndex = 0

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim()
      
      if (line.startsWith('##')) {
        const text = line.substring(2).trim()
        elements.push(
          <h2 key={currentIndex++} className="text-xl font-bold text-gray-900 mt-6 mb-4 pb-2 border-b border-gray-200">
            {text}
          </h2>
        )
        continue
      }

      if (line.startsWith('###')) {
        const text = line.substring(3).trim()
        elements.push(
          <h3 key={currentIndex++} className="text-lg font-semibold text-gray-800 mt-4 mb-3">
            {text}
          </h3>
        )
        continue
      }

      if (line.match(/^\d+\.\s+(\*\*)?[A-Z]/)) {
        const text = line.replace(/^\d+\.\s+/, '').replace(/\*\*/g, '').trim()
        elements.push(
          <h3 key={currentIndex++} className="text-lg font-semibold text-gray-900 mt-5 mb-3 bg-gray-50 px-3 py-2 rounded">
            {text}
          </h3>
        )
        continue
      }

      let processedLine = line.replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-gray-900">$1</strong>')
      
      if (line.startsWith('-') || line.startsWith('•') || line.match(/^\d+\./)) {
        const content = processedLine.replace(/^[-•\d.]+/, '').trim()
        elements.push(
          <div key={currentIndex++} className="flex items-start mb-2 ml-4">
            <span className="text-blue-600 mr-2 mt-1">•</span>
            <span className="text-gray-700" dangerouslySetInnerHTML={{ __html: content }} />
          </div>
        )
        continue
      }

      if (line) {
        elements.push(
          <p key={currentIndex++} className="text-gray-700 mb-3 leading-relaxed" dangerouslySetInnerHTML={{ __html: processedLine }} />
        )
      }
    }

    return <div className="prose prose-lg max-w-none">{elements}</div>
  }

  return formatMarkdown(content)
}
