import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import Layout from './components/Layout'
import Home from './pages/Home'
import Research from './pages/Research'
import Drafting from './pages/Drafting'
import Compliance from './pages/Compliance'
import Upload from './pages/Upload'

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-background">
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
    </Router>
  )
}

export default App
