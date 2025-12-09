import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { 
  Scale, 
  Search, 
  FileText, 
  Shield, 
  Upload,
  Menu,
  X
} from 'lucide-react'
import { useState } from 'react'
import TimelinePanel from './TimelinePanel'

interface LayoutProps {
  children: React.ReactNode
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const location = useLocation()
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  const navigation = [
    { name: 'Home', href: '/', icon: Scale },
    { name: 'Research', href: '/research', icon: Search },
    { name: 'Drafting', href: '/drafting', icon: FileText },
    { name: 'Compliance', href: '/compliance', icon: Shield },
    { name: 'Upload', href: '/upload', icon: Upload },
  ]

  return (
    <div className="min-h-screen">
      {/* Navigation */}
      <nav className="liquid-glass-card glass-content sticky top-0 z-50 py-2 px-4">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-12">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <Scale className="h-8 w-8 text-white" />
                <span className="ml-2 text-xl font-bold text-white">
                  LegisAI
                </span>
              </div>
              <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                {navigation.map((item) => {
                  const isActive = location.pathname === item.href
                  return (
                    <Link
                      key={item.name}
                      to={item.href}
                      className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${
                        isActive
                          ? 'border-white text-white'
                          : 'border-transparent text-white/80 hover:border-white/50 hover:text-white'
                      }`}
                    >
                      <item.icon className="h-4 w-4 mr-2" />
                      {item.name}
                    </Link>
                  )
                })}
              </div>
            </div>
            
            {/* Mobile menu button */}
            <div className="sm:hidden flex items-center">
              <button
                onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                className="inline-flex items-center justify-center p-2 rounded-md text-white/80 hover:text-white hover:bg-white/10"
              >
                {isMobileMenuOpen ? (
                  <X className="h-6 w-6" />
                ) : (
                  <Menu className="h-6 w-6" />
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile menu */}
        {isMobileMenuOpen && (
          <div className="sm:hidden">
            <div className="pt-2 pb-3 space-y-1">
              {navigation.map((item) => {
                const isActive = location.pathname === item.href
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={`block pl-3 pr-4 py-2 border-l-4 text-base font-medium ${
                      isActive
                        ? 'bg-white/20 border-white text-white'
                        : 'border-transparent text-white/80 hover:bg-white/10 hover:border-white/50 hover:text-white'
                    }`}
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    <div className="flex items-center">
                      <item.icon className="h-4 w-4 mr-3" />
                      {item.name}
                    </div>
                  </Link>
                )
              })}
            </div>
          </div>
        )}
      </nav>

      {/* Main content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8 relative z-10">
        {/* Timeline Panel - Visible on all pages */}
        <TimelinePanel />
        {children}
      </main>
    </div>
  )
}

export default Layout
