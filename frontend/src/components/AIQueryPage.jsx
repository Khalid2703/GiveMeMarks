import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { MessageSquare, Loader, Database, RefreshCw, Info, Users, TrendingUp, Sparkles, X } from 'lucide-react'

const API_URL = import.meta.env.PROD 
  ? 'https://uoh-academic-backend.onrender.com'
  : 'http://localhost:8000'

export default function AIQueryPage() {
  const [chatMessages, setChatMessages] = useState([])
  const [chatInput, setChatInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [batches, setBatches] = useState([])
  const [selectedBatches, setSelectedBatches] = useState([]) // Multiple selection
  const [loadingBatches, setLoadingBatches] = useState(true)
  const [contextInfo, setContextInfo] = useState(null)
  const [currentBatch, setCurrentBatch] = useState(null)
  const [showBatchSelector, setShowBatchSelector] = useState(false)

  useEffect(() => {
    fetchBatches()
  }, [])

  const fetchBatches = async () => {
    setLoadingBatches(true)
    try {
      const response = await axios.get(`${API_URL}/api/batches/all`)
      const batchList = response.data.batches || []
      const current = response.data.current_batch
      
      setBatches(batchList)
      setCurrentBatch(current)
      
      // Auto-select the current batch (most recent)
      if (current) {
        setSelectedBatches([current])
      } else if (batchList.length > 0) {
        setSelectedBatches([batchList[batchList.length - 1].filename])
      }
    } catch (error) {
      console.error('Failed to fetch batches:', error)
    } finally {
      setLoadingBatches(false)
    }
  }

  const toggleBatchSelection = (batchFilename) => {
    setSelectedBatches(prev => {
      if (prev.includes(batchFilename)) {
        return prev.filter(b => b !== batchFilename)
      } else {
        return [...prev, batchFilename]
      }
    })
  }

  const getTotalStudents = () => {
    return batches
      .filter(b => selectedBatches.includes(b.filename))
      .reduce((sum, b) => sum + b.student_count, 0)
  }

  const formatBatchName = (filename) => {
    return filename
      .replace('academic_batch_', '')
      .replace('.xlsx', '')
      .replace(/_/g, ' ')
  }

  const formatDate = (dateStr) => {
    try {
      return new Date(dateStr).toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric',
        year: 'numeric'
      })
    } catch {
      return dateStr
    }
  }

  const handleSendMessage = async () => {
    if (!chatInput.trim() || selectedBatches.length === 0) return
    
    const userMessage = chatInput
    
    setChatMessages(prev => [...prev, { role: 'user', content: userMessage }])
    setChatInput('')
    setLoading(true)
    
    try {
      // Send all selected batches to backend
      const response = await axios.post(`${API_URL}/api/ai/query`, { 
        query: userMessage,
        batches: selectedBatches  // Send array of all selected batches
      })
      
      const aiResponse = response.data.response || 'No response received'
      const contextStats = response.data.context_stats
      const batchUsed = response.data.batch_used
      const modelUsed = response.data.model
      const provider = response.data.provider
      
      setChatMessages(prev => [...prev, { 
        role: 'assistant', 
        content: aiResponse,
        contextInfo: contextStats,
        batchUsed: batchUsed,
        modelUsed: modelUsed,
        provider: provider
      }])
      
      if (contextStats) {
        setContextInfo(contextStats)
      }
    } catch (error) {
      console.error('AI query error:', error)
      const errorMsg = error.response?.data?.response || error.response?.data?.detail || error.message
      setChatMessages(prev => [...prev, { 
        role: 'assistant', 
        content: `I apologize, but I encountered an error: ${errorMsg}. Please try again.`,
        isError: true
      }])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const handleSuggestedQuestion = (question) => {
    if (selectedBatches.length === 0) return
    setChatInput(question)
    setTimeout(() => handleSendMessage(), 100)
  }

  const suggestedQuestions = [
    "What is the average CGPA?",
    "How many students are in each department?",
    "Who are the top 5 performers?",
    "What's the CGPA distribution?",
    "Show students with CGPA above 8.5",
    "Which department has highest average?"
  ]

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Compact Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <MessageSquare className="h-6 w-6 text-blue-600" />
            <h1 className="text-xl font-bold">AI Query Assistant</h1>
            <span className="px-2 py-1 bg-gradient-to-r from-blue-500 to-purple-600 text-white text-xs font-semibold rounded-full">
              Gemini
            </span>
          </div>
          
          {/* Batch Selector */}
          <div className="flex items-center gap-3">
            <Database className="h-4 w-4 text-gray-500" />
            
            {loadingBatches ? (
              <div className="flex items-center gap-2">
                <Loader className="h-4 w-4 animate-spin text-gray-400" />
                <span className="text-sm text-gray-500">Loading...</span>
              </div>
            ) : batches.length === 0 ? (
              <span className="text-sm text-red-600">No batches - Process documents first</span>
            ) : (
              <div className="relative">
                <button
                  onClick={() => setShowBatchSelector(!showBatchSelector)}
                  className="px-3 py-1.5 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-2"
                >
                  <span className="font-medium">
                    {selectedBatches.length} batch{selectedBatches.length !== 1 ? 'es' : ''} selected
                  </span>
                  <span className="text-gray-500">({getTotalStudents()} students)</span>
                </button>
                
                {/* Dropdown */}
                {showBatchSelector && (
                  <div className="absolute right-0 mt-2 w-96 bg-white border border-gray-200 rounded-lg shadow-lg z-50 max-h-96 overflow-y-auto">
                    <div className="p-3 border-b border-gray-200 flex items-center justify-between">
                      <span className="font-semibold text-sm">Select Batches</span>
                      <button
                        onClick={() => setShowBatchSelector(false)}
                        className="text-gray-400 hover:text-gray-600"
                      >
                        <X className="h-4 w-4" />
                      </button>
                    </div>
                    
                    {batches.map((batch, idx) => (
                      <div
                        key={idx}
                        onClick={() => toggleBatchSelection(batch.filename)}
                        className={`p-3 border-b border-gray-100 cursor-pointer transition-colors ${
                          selectedBatches.includes(batch.filename)
                            ? 'bg-blue-50 hover:bg-blue-100'
                            : 'hover:bg-gray-50'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <input
                              type="checkbox"
                              checked={selectedBatches.includes(batch.filename)}
                              onChange={() => {}}
                              className="rounded text-blue-600"
                            />
                            <div>
                              <div className="flex items-center gap-2">
                                <span className="text-sm font-medium">
                                  {batch.filename === currentBatch && '⭐ '}
                                  {formatBatchName(batch.filename)}
                                </span>
                              </div>
                              <div className="text-xs text-gray-500 mt-0.5">
                                {formatDate(batch.created_at)}
                              </div>
                            </div>
                          </div>
                          <div className="flex items-center gap-1 text-xs">
                            <Users className="h-3 w-3 text-gray-400" />
                            <span className="font-medium text-gray-600">
                              {batch.student_count}
                            </span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
            
            <button
              onClick={fetchBatches}
              className="p-1.5 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
              title="Refresh batches"
            >
              <RefreshCw className="h-4 w-4" />
            </button>
          </div>
        </div>

        {/* Selected Batches Preview */}
        {selectedBatches.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-2">
            {batches
              .filter(b => selectedBatches.includes(b.filename))
              .map((batch, idx) => (
                <div
                  key={idx}
                  className="flex items-center gap-2 px-3 py-1.5 bg-blue-50 border border-blue-200 rounded-lg text-xs"
                >
                  <span className="font-medium text-blue-900">
                    {formatBatchName(batch.filename)}
                  </span>
                  <span className="text-blue-600">({batch.student_count})</span>
                  <button
                    onClick={() => toggleBatchSelection(batch.filename)}
                    className="text-blue-600 hover:text-blue-800"
                  >
                    <X className="h-3 w-3" />
                  </button>
                </div>
              ))}
          </div>
        )}
      </div>
      
      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <div className="flex-1 overflow-y-auto px-6 py-4">
          {chatMessages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center">
              <div className="bg-gradient-to-br from-blue-500 to-purple-600 p-4 rounded-full mb-4">
                <Sparkles className="h-12 w-12 text-white" />
              </div>
              <h2 className="text-xl font-semibold text-gray-800 mb-2">
                AI-Powered Academic Analytics
              </h2>
              <p className="text-gray-500 text-sm text-center mb-6 max-w-md">
                Ask intelligent questions about student data using Gemini AI
              </p>

              <div className="w-full max-w-2xl">
                <p className="text-xs font-medium text-gray-600 mb-2 flex items-center gap-2">
                  <Info className="h-3 w-3" />
                  Quick questions:
                </p>
                <div className="grid grid-cols-2 gap-2">
                  {suggestedQuestions.map((question, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleSuggestedQuestion(question)}
                      disabled={selectedBatches.length === 0}
                      className="text-left px-3 py-2 bg-white hover:bg-blue-50 border border-gray-200 hover:border-blue-300 rounded-lg transition-all text-xs text-gray-700 hover:text-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {question}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="space-y-3 max-w-4xl mx-auto">
              {chatMessages.map((msg, idx) => (
                <div 
                  key={idx} 
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div 
                    className={`max-w-2xl px-4 py-3 rounded-lg ${
                      msg.role === 'user' 
                        ? 'bg-gradient-to-r from-blue-600 to-blue-500 text-white' 
                        : msg.isError
                        ? 'bg-red-50 text-red-900 border border-red-200'
                        : 'bg-white text-gray-900 border border-gray-200'
                    }`}
                  >
                    <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.content}</p>
                    
                    {msg.contextInfo && !msg.isError && (
                      <div className="mt-3 pt-3 border-t border-gray-200">
                        <div className="flex flex-wrap gap-2 text-xs">
                          <span className="px-2 py-1 bg-blue-50 text-blue-700 rounded">
                            {msg.contextInfo.total_students} students
                          </span>
                          <span className="px-2 py-1 bg-green-50 text-green-700 rounded">
                            CGPA {msg.contextInfo.avg_cgpa}
                          </span>
                          <span className="px-2 py-1 bg-purple-50 text-purple-700 rounded">
                            {msg.contextInfo.departments} depts
                          </span>
                          <span className="px-2 py-1 bg-indigo-50 text-indigo-700 rounded">
                            {msg.provider} {msg.modelUsed}
                          </span>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ))}
              
              {loading && (
                <div className="flex justify-start">
                  <div className="bg-gradient-to-r from-blue-50 to-purple-50 px-4 py-3 rounded-lg flex items-center gap-3 border border-blue-200">
                    <Loader className="animate-spin h-5 w-5 text-blue-600" />
                    <div>
                      <p className="text-sm font-medium text-blue-900 flex items-center gap-2">
                        <Sparkles className="h-4 w-4" />
                        Analyzing with Gemini AI...
                      </p>
                      <p className="text-xs text-blue-700 mt-0.5">
                        Processing {getTotalStudents()} student records from {selectedBatches.length} batch{selectedBatches.length !== 1 ? 'es' : ''}
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="border-t border-gray-200 bg-white px-6 py-3">
          <div className="flex gap-2 max-w-4xl mx-auto">
            <input
              type="text"
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder={selectedBatches.length > 0 ? "Ask about the data..." : "Select batches first..."}
              disabled={loading || selectedBatches.length === 0}
              autoFocus
              className="flex-1 px-4 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none disabled:bg-gray-100 disabled:cursor-not-allowed"
            />
            <button
              onClick={handleSendMessage}
              disabled={loading || !chatInput.trim() || selectedBatches.length === 0}
              className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-5 py-2 rounded-lg text-sm font-semibold hover:from-blue-700 hover:to-purple-700 disabled:from-gray-400 disabled:to-gray-400 disabled:cursor-not-allowed transition-all"
            >
              {loading ? 'Sending...' : 'Send'}
            </button>
          </div>
          
          {selectedBatches.length === 0 && batches.length > 0 && (
            <p className="mt-2 text-xs text-amber-600 text-center">
              Please select at least one batch to start querying
            </p>
          )}
        </div>
      </div>
    </div>
  )
}
