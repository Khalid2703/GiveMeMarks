import React, { useState } from 'react'
import { Home, FileSpreadsheet, BarChart3, MessageSquare, Settings as SettingsIcon, Menu } from 'lucide-react'
import Homepage from './pages/Homepage'
import ResultsPage from './components/ResultsPage'
import Dashboard from './pages/Dashboard'
import AIQueryPage from './components/AIQueryPage'
import SettingsPage from './pages/SettingsPage'

export default function App() {
  const [currentPage, setCurrentPage] = useState('homepage')
  const [sidebarOpen, setSidebarOpen] = useState(true)

  const Sidebar = () => (
    <div className={`${sidebarOpen ? 'w-64' : 'w-20'} bg-gradient-to-b from-indigo-900 to-indigo-800 min-h-screen transition-all duration-300 flex flex-col`}>
      <div className="p-6 border-b border-indigo-700">
        {sidebarOpen ? <h2 className="text-white font-bold text-xl">G.T.M</h2> : <div className="text-white font-bold text-center">GT</div>}
      </div>
      <nav className="flex-1 py-6">
        {[
          { icon: <Home size={20} />, label: 'Homepage', page: 'homepage' },
          { icon: <FileSpreadsheet size={20} />, label: 'Results', page: 'results' },
          { icon: <BarChart3 size={20} />, label: 'Dashboard', page: 'dashboard' },
          { icon: <MessageSquare size={20} />, label: 'AI Query', page: 'ai-query' },
          { icon: <SettingsIcon size={20} />, label: 'Settings', page: 'settings' }
        ].map(item => (
          <button key={item.page} onClick={() => setCurrentPage(item.page)} className={`w-full px-6 py-3 flex items-center gap-3 transition-colors ${currentPage === item.page ? 'bg-indigo-700 text-white border-l-4 border-white' : 'text-indigo-200 hover:bg-indigo-700/50'}`}>
            {item.icon}
            {sidebarOpen && <span className="font-medium">{item.label}</span>}
          </button>
        ))}
      </nav>
      <button onClick={() => setSidebarOpen(!sidebarOpen)} className="p-4 text-white hover:bg-indigo-700"><Menu size={20} /></button>
    </div>
  )

  const renderPage = () => {
    switch(currentPage) {
      case 'homepage': return <Homepage />
      case 'results': return <ResultsPage />
      case 'dashboard': return <Dashboard />
      case 'ai-query': return <AIQueryPage />
      case 'settings': return <SettingsPage />
      default: return <Homepage />
    }
  }

  return (
    <div className="flex h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <Sidebar />
      <div className="flex-1 overflow-y-auto">{renderPage()}</div>
    </div>
  )
}
