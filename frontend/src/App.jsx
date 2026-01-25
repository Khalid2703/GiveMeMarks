import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { Upload, Download, X, FileText, Users, TrendingUp, AlertCircle, Loader, Trash2, RefreshCw, BarChart3, Home, FileSpreadsheet, MessageSquare, Settings as SettingsIcon, Menu, LogOut, Edit, Save, Award, GraduationCap } from 'lucide-react'
import AIQueryPage from './components/AIQueryPage'
import ResultsPage from './components/ResultsPage'
import AcademicAlerts from './components/AcademicAlerts'

const API_URL = 'https://givememarks.onrender.com'

export default function App() {
  const [currentPage, setCurrentPage] = useState('homepage')
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [files, setFiles] = useState([])
  const [uploading, setUploading] = useState(false)
  const [processing, setProcessing] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [systemStatus, setSystemStatus] = useState(null)
  const [documentCount, setDocumentCount] = useState(0)
  const [batches, setBatches] = useState([])
  const [dashboardData, setDashboardData] = useState(null)
  const [loadingDashboard, setLoadingDashboard] = useState(false)

  useEffect(() => {
    checkSystemStatus()
    checkDocumentCount()
    fetchBatches()
  }, [])

  useEffect(() => {
    if (currentPage === 'dashboard' && !dashboardData) fetchDashboardData()
  }, [currentPage])

  const checkSystemStatus = async () => {
    try {
      const response = await axios.get(`${API_URL}/status`)
      setSystemStatus(response.data)
    } catch (error) {
      console.error('Status error:', error)
    }
  }

  const checkDocumentCount = async () => {
    try {
      const response = await axios.get(`${API_URL}/documents/count`)
      setDocumentCount(response.data.count)
    } catch (error) {
      console.error('Count error:', error)
    }
  }

  const fetchBatches = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/batches/all`)
      setBatches(response.data.batches || [])
    } catch (error) {
      console.error('Batches error:', error)
    }
  }

  const fetchDashboardData = async () => {
    setLoadingDashboard(true)
    try {
      const response = await axios.get(`${API_URL}/api/dashboard/stats`)
      setDashboardData(response.data)
    } catch (error) {
      console.error('Dashboard error:', error)
    } finally {
      setLoadingDashboard(false)
    }
  }

  const handleUpload = async (e) => {
    const selectedFiles = Array.from(e.target.files)
    if (selectedFiles.length === 0) return
    if (selectedFiles.filter(f => !f.name.endsWith('.pdf')).length > 0) {
      setError('Only PDF files allowed')
      return
    }
    const formData = new FormData()
    selectedFiles.forEach(file => formData.append('files', file))
    setUploading(true)
    setError(null)
    try {
      await axios.post(`${API_URL}/upload`, formData, { headers: { 'Content-Type': 'multipart/form-data' } })
      setFiles(selectedFiles)
      await checkDocumentCount()
      alert(`✅ Uploaded ${selectedFiles.length} files`)
    } catch (error) {
      setError('Upload failed: ' + (error.response?.data?.detail || error.message))
    } finally {
      setUploading(false)
    }
  }

  const handleProcess = async () => {
    if (documentCount === 0) {
      setError('No documents to process')
      return
    }
    setProcessing(true)
    setError(null)
    try {
      const response = await axios.post(`${API_URL}/process`, null, { params: { batch_name: `batch_${new Date().toISOString().split('T')[0]}` } })
      setResult(response.data.result)
      setFiles([])
      await checkDocumentCount()
      await fetchBatches()
      alert(`✅ Processed ${response.data.result.successful}/${response.data.result.total_documents}`)
    } catch (error) {
      setError('Processing failed: ' + (error.response?.data?.detail || error.message))
    } finally {
      setProcessing(false)
    }
  }

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

  const Homepage = () => (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold">Welcome to G.T.M</h1>
      <p className="text-gray-600">AI-powered document processing for University of Hyderabad</p>
      {systemStatus && (
        <div className="flex gap-3">
          <span className={`px-4 py-2 rounded-full text-sm font-semibold ${systemStatus.llm_available ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>LLM: {systemStatus.llm_provider || 'Offline'}</span>
          <span className={`px-4 py-2 rounded-full text-sm font-semibold ${systemStatus.supabase_available ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'}`}>DB: {systemStatus.supabase_available ? 'Connected' : 'Offline'}</span>
        </div>
      )}
      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded-lg">
          <div className="flex items-start">
            <AlertCircle className="h-5 w-5 text-red-500 mt-0.5 mr-3" />
            <div className="flex-1"><p className="text-sm font-medium text-red-800">Error</p><p className="text-sm text-red-700 mt-1">{error}</p></div>
            <button onClick={() => setError(null)} className="text-red-500"><X className="h-5 w-5" /></button>
          </div>
        </div>
      )}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-blue-500">
          <div className="flex items-center justify-between"><div><p className="text-sm font-medium text-gray-600">Documents in Queue</p><p className="text-3xl font-bold mt-2">{documentCount}</p></div><FileText className="h-12 w-12 text-blue-500 opacity-80" /></div>
        </div>
        <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-green-500">
          <div className="flex items-center justify-between"><div><p className="text-sm font-medium text-gray-600">Total Batches</p><p className="text-3xl font-bold mt-2">{batches.length}</p></div><Users className="h-12 w-12 text-green-500 opacity-80" /></div>
        </div>
        <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-purple-500">
          <div className="flex items-center justify-between"><div><p className="text-sm font-medium text-gray-600">System Status</p><p className="text-3xl font-bold mt-2">{systemStatus?.status === 'operational' ? '✅ Ready' : '⚠️ Check'}</p></div><TrendingUp className="h-12 w-12 text-purple-500 opacity-80" /></div>
        </div>
      </div>
      <div className="bg-white rounded-xl shadow-lg p-8">
        <h2 className="text-2xl font-semibold mb-6">Upload & Process Documents</h2>
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center hover:border-blue-400 transition-colors">
          <Upload className="mx-auto h-16 w-16 text-gray-400 mb-4" />
          <label className="cursor-pointer">
            <span className="mt-2 block text-lg font-medium">Click to upload PDF documents</span>
            <span className="mt-1 block text-sm text-gray-500">Academic reports, transcripts, exam submissions</span>
            <input type="file" multiple accept=".pdf" onChange={handleUpload} className="hidden" disabled={uploading || processing} />
          </label>
          {uploading && <div className="mt-4 flex items-center justify-center"><Loader className="animate-spin h-6 w-6 text-blue-600 mr-2" /><span className="text-sm text-gray-600">Uploading...</span></div>}
          {files.length > 0 && !uploading && <div className="mt-4"><p className="text-sm font-medium text-green-600">✅ {files.length} file{files.length > 1 ? 's' : ''} uploaded</p></div>}
        </div>
        <div className="mt-6 flex gap-3">
          <button onClick={handleProcess} disabled={documentCount === 0 || processing} className="flex-1 bg-blue-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center">
            {processing ? <><Loader className="animate-spin h-5 w-5 mr-2" />Processing...</> : <><RefreshCw className="h-5 w-5 mr-2" />Process ({documentCount})</>}
          </button>
          {documentCount > 0 && <button onClick={async () => { if (confirm('Clear all?')) { await axios.delete(`${API_URL}/documents`); setFiles([]); setDocumentCount(0); alert('✅ Cleared') } }} disabled={processing} className="bg-red-50 text-red-600 py-3 px-6 rounded-lg font-semibold hover:bg-red-100"><Trash2 className="h-5 w-5 mr-2 inline" />Clear</button>}
        </div>
      </div>
      {result && (
        <div className="bg-white rounded-xl shadow-lg p-8">
          <div className="flex items-center justify-between mb-6"><h2 className="text-2xl font-semibold">Processing Results</h2><button onClick={() => { setFiles([]); setResult(null); setError(null); checkDocumentCount() }} className="bg-gray-100 text-gray-700 py-2 px-4 rounded-lg font-semibold hover:bg-gray-200 flex items-center"><RefreshCw className="h-4 w-4 mr-2" />Process More</button></div>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <div className="text-center p-4 bg-blue-50 rounded-lg"><p className="text-4xl font-bold text-blue-600">{result.total_documents}</p><p className="text-sm text-gray-600 mt-1">Total</p></div>
            <div className="text-center p-4 bg-green-50 rounded-lg"><p className="text-4xl font-bold text-green-600">{result.successful}</p><p className="text-sm text-gray-600 mt-1">Success</p></div>
            <div className="text-center p-4 bg-red-50 rounded-lg"><p className="text-4xl font-bold text-red-600">{result.failed}</p><p className="text-sm text-gray-600 mt-1">Failed</p></div>
            <div className="text-center p-4 bg-purple-50 rounded-lg"><p className="text-4xl font-bold text-purple-600">{result.success_rate?.toFixed(1)}%</p><p className="text-sm text-gray-600 mt-1">Rate</p></div>
          </div>
          <button onClick={() => window.open(`${API_URL}/batches/${result.batch_id}/download`, '_blank')} className="w-full bg-green-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-green-700 flex items-center justify-center"><Download className="mr-2 h-5 w-5" />Download Excel</button>
        </div>
      )}
    </div>
  )

  const Dashboard = () => (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold">Analytics Dashboard</h1>
      {loadingDashboard ? <div className="flex items-center justify-center h-64"><Loader className="animate-spin h-12 w-12 text-blue-600" /></div> : dashboardData ? (
        <>
          {/* Academic Alerts Section - NEW */}
          <AcademicAlerts />
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white rounded-xl shadow-lg p-6"><div className="flex items-center justify-between mb-4"><h3 className="text-lg font-semibold">Total Students</h3><Users className="h-8 w-8 text-blue-600" /></div><p className="text-4xl font-bold">{dashboardData.total_students}</p></div>
            <div className="bg-white rounded-xl shadow-lg p-6"><div className="flex items-center justify-between mb-4"><h3 className="text-lg font-semibold">Average CGPA</h3><GraduationCap className="h-8 w-8 text-green-600" /></div><p className="text-4xl font-bold">{dashboardData.average_cgpa}</p></div>
            <div className="bg-white rounded-xl shadow-lg p-6"><div className="flex items-center justify-between mb-4"><h3 className="text-lg font-semibold">Departments</h3><BarChart3 className="h-8 w-8 text-purple-600" /></div><p className="text-4xl font-bold">{dashboardData.departments?.length || 0}</p></div>
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white rounded-xl shadow-lg p-6"><h3 className="text-lg font-semibold mb-4">CGPA Distribution</h3><div className="space-y-3">{dashboardData.cgpa_distribution?.map((item, i) => (
              <div key={i} className="flex items-center justify-between"><span className="text-gray-700">{item.range}</span><div className="flex items-center gap-3"><div className="w-32 bg-gray-200 rounded-full h-2"><div className="bg-blue-600 h-2 rounded-full" style={{ width: `${(item.count / dashboardData.total_students) * 100}%` }}></div></div><span className="font-semibold w-12 text-right">{item.count}</span></div></div>
            ))}</div></div>
            <div className="bg-white rounded-xl shadow-lg p-6"><h3 className="text-lg font-semibold mb-4">Department Distribution</h3><div className="space-y-3">{dashboardData.departments?.map((dept, i) => (
              <div key={i} className="flex items-center justify-between"><span className="text-gray-700">{dept.name}</span><div className="flex items-center gap-3"><div className="w-32 bg-gray-200 rounded-full h-2"><div className="bg-green-600 h-2 rounded-full" style={{ width: `${(dept.count / dashboardData.total_students) * 100}%` }}></div></div><span className="font-semibold w-12 text-right">{dept.count}</span></div></div>
            ))}</div></div>
          </div>
          <div className="bg-white rounded-xl shadow-lg p-6"><h3 className="text-lg font-semibold mb-4">Top 10 Performers</h3><div className="overflow-x-auto"><table className="w-full"><thead><tr className="border-b"><th className="text-left py-3 px-4">Rank</th><th className="text-left py-3 px-4">Name</th><th className="text-left py-3 px-4">Roll Number</th><th className="text-left py-3 px-4">Department</th><th className="text-left py-3 px-4">CGPA</th></tr></thead><tbody>{dashboardData.top_performers?.map((s, i) => (
            <tr key={i} className="border-b hover:bg-gray-50"><td className="py-3 px-4"><span className={`font-bold ${i === 0 ? 'text-yellow-600' : i === 1 ? 'text-gray-400' : i === 2 ? 'text-orange-600' : 'text-gray-600'}`}>#{i + 1}</span></td><td className="py-3 px-4 font-medium">{s.name}</td><td className="py-3 px-4">{s.roll_number}</td><td className="py-3 px-4">{s.department}</td><td className="py-3 px-4"><span className="font-semibold text-blue-600">{s.cgpa}</span></td></tr>
          ))}</tbody></table></div></div>
        </>
      ) : <div className="bg-white rounded-xl shadow-lg p-12 text-center"><BarChart3 className="mx-auto h-24 w-24 text-gray-300 mb-4" /><h2 className="text-2xl font-semibold text-gray-700 mb-2">No Data Available</h2><p className="text-gray-500">Process documents to see analytics</p></div>}
    </div>
  )

  const SettingsPage = () => (
    <div className="p-8 space-y-8 max-w-4xl mx-auto">
      <h1 className="text-4xl font-bold">Settings</h1>
      <div className="bg-white rounded-2xl shadow-xl p-8 space-y-8">
        <div><h3 className="text-2xl font-semibold mb-4 flex items-center gap-3"><Users className="text-blue-600" />User Management</h3><button className="bg-red-600 text-white px-8 py-4 rounded-xl font-semibold hover:bg-red-700 flex items-center gap-3"><LogOut size={22} />Logout</button></div>
        <div className="pt-6 border-t-2"><h3 className="text-2xl font-semibold mb-4 flex items-center gap-3"><Edit className="text-green-600" />Data Management</h3><p className="text-gray-600 mb-4 text-lg">Edit and manage student records, batch information, and system configuration.</p><button className="bg-green-600 text-white px-8 py-4 rounded-xl font-semibold hover:bg-green-700 flex items-center gap-3"><Save size={22} />Save Changes</button></div>
        <div className="pt-6 border-t-2"><h3 className="text-2xl font-semibold mb-4 flex items-center gap-3"><SettingsIcon className="text-purple-600" />System Configuration</h3><p className="text-gray-600 text-lg">Advanced settings and configuration options.</p></div>
      </div>
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
