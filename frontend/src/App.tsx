import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { TimelineProvider } from './contexts/TimelineContext'
import { ResearchProvider } from './contexts/ResearchContext'
import { DraftingProvider } from './contexts/DraftingContext'
import { ComplianceProvider } from './contexts/ComplianceContext'
import { UploadProvider } from './contexts/UploadContext'
import Layout from './components/Layout'
import VideoBackground from './components/VideoBackground'
import Home from './pages/Home'
import Research from './pages/Research'
import Drafting from './pages/Drafting'
import Compliance from './pages/Compliance'
import Upload from './pages/Upload'

function App() {
  return (
    <TimelineProvider>
      <ResearchProvider>
        <DraftingProvider>
          <ComplianceProvider>
            <UploadProvider>
              <Router>
                <div className="min-h-screen relative">
                  {/* Video Background */}
                  <VideoBackground />
                  
                  {/* Content Layer */}
                  <div className="relative z-10">
                    <Layout>
                      <Routes>
                        <Route path="/" element={<Home />} />
                        <Route path="/research" element={<Research />} />
                        <Route path="/drafting" element={<Drafting />} />
                        <Route path="/compliance" element={<Compliance />} />
                        <Route path="/upload" element={<Upload />} />
                      </Routes>
                    </Layout>
                    <Toaster position="top-right" />
                  </div>
                </div>
              </Router>
            </UploadProvider>
          </ComplianceProvider>
        </DraftingProvider>
      </ResearchProvider>
    </TimelineProvider>
  )
}

export default App
