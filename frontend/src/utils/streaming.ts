// Shared streaming handler for all endpoints with cancellation support
export async function handleStreamingRequest(
  endpoint: string,
  body: any,
  setStreamingText: (text: string) => void,
  setIsStreaming: (isStreaming: boolean) => void,
  onComplete: (fullText: string) => void,
  abortController?: AbortController
) {
  setIsStreaming(true)
  setStreamingText('')
  
  try {
    console.log(`🌊 Starting streaming request to ${endpoint}`)
    
    const response = await fetch(`/api/${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
      signal: abortController?.signal
    })
    
    console.log('📡 Response status:', response.status, response.statusText)
    
    if (!response.ok) {
      const errorText = await response.text()
      console.error('❌ Response error:', errorText)
      throw new Error(`HTTP error! status: ${response.status}, body: ${errorText}`)
    }
    
    console.log('✅ Response OK, getting reader...')
    
    const reader = response.body?.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    let fullText = ''
    
    if (!reader) {
      throw new Error('No reader available')
    }
    
    while (true) {
      const { done, value } = await reader.read()
      
      // Process any remaining data even if done is true
      if (value) {
        buffer += decoder.decode(value, { stream: !done })
      }
      
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))
            console.log('📥 Received SSE data:', data)
            if (data.content) {
              fullText += data.content
              setStreamingText(fullText)
              console.log(`📝 Updated text: ${fullText.length} chars`)
            }
            if (data.done) {
              console.log('✅ Streaming completed, full text length:', fullText.length)
              setIsStreaming(false)
              onComplete(fullText)
              return
            }
            if (data.error) {
              console.error('❌ SSE error:', data.error)
              throw new Error(data.error)
            }
          } catch (err) {
            console.error('❌ Error parsing SSE data:', err, line)
          }
        } else if (line.trim()) {
          console.log('📄 Non-data line:', line)
        }
      }
      
      // Break after processing all data
      if (done) {
        // Process any remaining buffer
        if (buffer.trim()) {
          const line = buffer.trim()
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              if (data.content) {
                fullText += data.content
                setStreamingText(fullText)
              }
              if (data.done) {
                console.log('✅ Streaming completed (final), full text length:', fullText.length)
                setIsStreaming(false)
                onComplete(fullText)
                return
              }
            } catch (err) {
              console.error('❌ Error parsing final SSE data:', err, line)
            }
          }
        }
        break
      }
    }
    
    // If we exit the loop without getting done=true, call onComplete anyway
    if (fullText.length > 0) {
      console.log('✅ Streaming ended, calling onComplete with text length:', fullText.length)
      setIsStreaming(false)
      onComplete(fullText)
    }
  } catch (error: any) {
    if (error.name === 'AbortError') {
      console.log('🛑 Streaming cancelled by user')
      setIsStreaming(false)
      return
    }
    console.error('❌ Streaming error:', error)
    setIsStreaming(false)
    throw error
  }
}
