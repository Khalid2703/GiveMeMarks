import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { MessageSquare, Loader, Database, RefreshCw, Info } from 'lucide-react'

const API_URL = import.meta.env.PROD 
  ? 'https://uoh-academic-backend.onrender.com'
  : 'http://localhost:8000'

export default function AIQueryPage() {
  const [chatMessages, setChatMessages] = useState([])
  const [chatInput, setChatInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [batches, setBatches] = useState([])
  const [selectedBatch, setSelectedBatch] = useState(null)
  const [loadingBatches, setLoadingBatches] = useState(true)
  const [contextInfo, setContextInfo] = useState(null)

  useEffect(() => {
    fetchBatches()
  }, [])

  const fetchBatches = async () => {
    setLoadingBatches(true)
    try {
      const response = await axios.get(`${API_URL}/api/batches/all`)
      const batchList = response.data.batches || []
      setBatches(batchList)
      
      // Auto-select the most recent batch
      if (batchList.length > 0) {
        const mostRecent = batchList[batchList.length - 1]
        setSelectedBatch(mostRecent.filename)
      }
    } catch (error) {
      console.error('Failed to fetch batches:', error)
    } finally {
      setLoadingBatches(false)
    }
  }

  const handleSendMessage = async () => {
    if (!chatInput.trim()) return
    
    const userMessage = chatInput
    
    // Add user message
    setChatMessages(prev => [...prev, { role: 'user', content: userMessage }])
    setChatInput('')
    setLoading(true)
    
    try {
      const response = await axios.post(`${API_URL}/api/ai/query`, { 
        query: userMessage,
        batch: selectedBatch // Send selected batch for context
      })
      
      const aiResponse = response.data.response || 'No response received'
      const contextStats = response.data.context_stats
      
      // Add AI response
      setChatMessages(prev => [...prev, { 
        role: 'assistant', 
        content: aiResponse,
        contextInfo: contextStats
      }])
      
      // Update context info display
      if (contextStats) {
        setContextInfo(contextStats)
      }
    } catch (error) {
      console.error('AI query error:', error)
      setChatMessages(prev => [...prev, { 
        role: 'assistant', 
        content: `Sorry, I encountered an error: ${error.response?.data?.detail || error.message}. Please try again.` 
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

  const suggestedQuestions = [
    "What is the average CGPA of all students?",
    "How many students are in the Computer Science department?",
    "Who are the top 5 performers?",
    "What's the CGPA distribution across departments?",
    "Show me students with CGPA above 8.5"
  ]

  return (
    <div className="p-6 flex flex-col" style={{ height: 'calc(100vh - 100px)' }}>
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">AI Query Assistant</h1>
        <p className="text-gray-600">Ask questions about student performance and academic data using AI (Powered by Cohere)</p>
      </div>

      {/* Batch Selector */}
      <div className="bg-white rounded-xl shadow-lg p-4 mb-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3 flex-1">
            <Database className="h-5 w-5 text-blue-600" />
            <div className="flex-1">
              <label className="text-sm font-medium text-gray-700 mb-1 block">
                Select Data Batch
              </label>
              {loadingBatches ? (
                <div className="flex items-center gap-2 text-gray-500">
                  <Loader className="h-4 w-4 animate-spin" />
                  <span className="text-sm">Loading batches...</span>
                </div>
              ) : batches.length === 0 ? (
                <p className="text-sm text-red-600">No processed batches found. Please upload and process documents first.</p>
              ) : (
                <select
                  value={selectedBatch || ''}
                  onChange={(e) => setSelectedBatch(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
                >
                  {batches.map((batch, idx) => (
                    <option key={idx} value={batch.filename}>
                      {batch.filename} ({batch.student_count} students)
                    </option>
                  ))}
                </select>
              )}
            </div>
          </div>
          <button
            onClick={fetchBatches}
            className="ml-3 p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
            title="Refresh batches"
          >
            <RefreshCw className="h-5 w-5" />
          </button>
        </div>

        {/* Context Info */}
        {contextInfo && (
          <div className="mt-3 flex items-center gap-2 text-sm text-gray-600 bg-blue-50 p-2 rounded-lg">
            <Info className="h-4 w-4 text-blue-600" />
            <span>
              Context: {contextInfo.total_students} students, Avg CGPA: {contextInfo.avg_cgpa}, 
              {contextInfo.departments} departments
            </span>
          </div>
        )}
      </div>
      
      <div className="flex-1 bg-white rounded-xl shadow-lg flex flex-col overflow-hidden">
        {/* Messages Area */}
        <div className="flex-1 p-6 overflow-y-auto">
          {chatMessages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center">
              <MessageSquare className="h-24 w-24 text-gray-300 mb-4" />
              <h2 className="text-2xl font-semibold text-gray-700 mb-2">
                Ask Questions About Academic Data
              </h2>
              <p className="text-gray-500 max-w-md text-center mb-6">
                Get intelligent insights from student performance, academic trends, and department statistics using AI
              </p>

              {/* Suggested Questions */}
              <div className="w-full max-w-2xl">
                <p className="text-sm font-medium text-gray-700 mb-3">Try asking:</p>
                <div className="grid grid-cols-1 gap-2">
                  {suggestedQuestions.map((question, idx) => (
                    <button
                      key={idx}
                      onClick={() => setChatInput(question)}
                      className="text-left px-4 py-3 bg-gray-50 hover:bg-blue-50 border border-gray-200 hover:border-blue-300 rounded-lg transition-colors text-sm text-gray-700 hover:text-blue-700"
                    >
                      {question}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {chatMessages.map((msg, idx) => (
                <div 
                  key={idx} 
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div 
                    className={`max-w-2xl p-4 rounded-lg ${
                      msg.role === 'user' 
                        ? 'bg-blue-600 text-white' 
                        : 'bg-gray-100 text-gray-900'
                    }`}
                  >
                    <p className="whitespace-pre-wrap">{msg.content}</p>
                    {msg.contextInfo && (
                      <div className="mt-2 pt-2 border-t border-gray-300 text-xs text-gray-600">
                        <span className="font-medium">Context:</span> {msg.contextInfo.total_students} students, 
                        Avg CGPA: {msg.contextInfo.avg_cgpa}
                      </div>
                    )}
                  </div>
                </div>
              ))}
              
              {loading && (
                <div className="flex justify-start">
                  <div className="bg-gray-100 p-4 rounded-lg flex items-center gap-2">
                    <Loader className="animate-spin h-5 w-5 text-gray-600" />
                    <span className="text-sm text-gray-600">Analyzing data with Cohere AI...</span>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="border-t border-gray-200 p-4 bg-gray-50">
          <div className="flex gap-3">
            <input
              type="text"
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder={selectedBatch ? "Ask a question about the data..." : "Select a batch first..."}
              disabled={loading || !selectedBatch}
              autoFocus
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none disabled:bg-gray-100 disabled:cursor-not-allowed"
            />
            <button
              onClick={handleSendMessage}
              disabled={loading || !chatInput.trim() || !selectedBatch}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? 'Sending...' : 'Send'}
            </button>
          </div>
          
          {!selectedBatch && batches.length > 0 && (
            <p className="mt-2 text-sm text-amber-600">
              Please select a data batch above to start querying
            </p>
          )}
        </div>
      </div>
    </div>
  )
}
