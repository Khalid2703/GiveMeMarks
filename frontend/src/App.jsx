/**
 * UOH Academic Evaluation System - Main React App
 * Mobile & Laptop Responsive
 * 
 * COMPONENT STATUS: ✅ COMPLETE
 * LAST UPDATED: 2025-01-21
 * RESPONSIVE: Mobile, Tablet, Laptop, Desktop
 */
import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { 
  Upload, 
  Download, 
  Check, 
  X, 
  FileText, 
  Users, 
  TrendingUp,
  AlertCircle,
  Loader,
  Trash2,
  RefreshCw
} from 'lucide-react'

// API Configuration
const API_URL = import.meta.env.PROD 
  ? 'https://uoh-academic-backend.onrender.com'  // Update with your Render URL
  : 'http://localhost:8000'

function App() {
  // State Management
  const [files, setFiles] = useState([])
  const [uploading, setUploading] = useState(false)
  const [processing, setProcessing] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [systemStatus, setSystemStatus] = useState(null)
  const [documentCount, setDocumentCount] = useState(0)
  const [batches, setBatches] = useState([])
  const [showBatches, setShowBatches] = useState(false)

  // Check system status on load
  useEffect(() => {
    checkSystemStatus()
    checkDocumentCount()
    fetchBatches()
  }, [])

  // Check system status
  const checkSystemStatus = async () => {
    try {
      const response = await axios.get(`${API_URL}/status`)
      setSystemStatus(response.data)
    } catch (error) {
      console.error('Failed to fetch status:', error)
    }
  }

  // Check document count
  const checkDocumentCount = async () => {
    try {
      const response = await axios.get(`${API_URL}/documents/count`)
      setDocumentCount(response.data.count)
    } catch (error) {
      console.error('Failed to fetch document count:', error)
    }
  }

  // Fetch available batches
  const fetchBatches = async () => {
    try {
      const response = await axios.get(`${API_URL}/batches`)
      setBatches(response.data.batches || [])
    } catch (error) {
      console.error('Failed to fetch batches:', error)
    }
  }

  // File upload handler
  const handleUpload = async (e) => {
    const selectedFiles = Array.from(e.target.files)
    
    if (selectedFiles.length === 0) return

    // Validate file types
    const invalidFiles = selectedFiles.filter(f => !f.name.endsWith('.pdf'))
    if (invalidFiles.length > 0) {
      setError('Only PDF files are allowed')
      return
    }

    const formData = new FormData()
    selectedFiles.forEach(file => formData.append('files', file))

    setUploading(true)
    setError(null)

    try {
      const response = await axios.post(`${API_URL}/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      
      setFiles(selectedFiles)
      await checkDocumentCount()
      
      // Show success message
      alert(`✅ Successfully uploaded ${selectedFiles.length} files`)
    } catch (error) {
      setError('Upload failed: ' + (error.response?.data?.detail || error.message))
    } finally {
      setUploading(false)
    }
  }

  // Process documents
  const handleProcess = async () => {
    if (documentCount === 0) {
      setError('No documents to process. Please upload PDFs first.')
      return
    }

    setProcessing(true)
    setError(null)

    try {
      const response = await axios.post(`${API_URL}/process`, null, {
        params: {
          batch_name: `batch_${new Date().toISOString().split('T')[0]}`
        }
      })
      
      setResult(response.data.result)
      setFiles([])
      await checkDocumentCount()
      await fetchBatches()
      
      // Success notification
      alert(`✅ Processing complete! ${response.data.result.successful}/${response.data.result.total_documents} documents processed successfully`)
    } catch (error) {
      setError('Processing failed: ' + (error.response?.data?.detail || error.message))
    } finally {
      setProcessing(false)
    }
  }

  // Download results
  const handleDownload = async (batchId) => {
    try {
      const url = `${API_URL}/batches/${batchId}/download`
      window.open(url, '_blank')
    } catch (error) {
      setError('Download failed: ' + error.message)
    }
  }

  // Clear all documents
  const handleClear = async () => {
    if (!confirm('Clear all uploaded documents?')) return

    try {
      await axios.delete(`${API_URL}/documents`)
      setFiles([])
      setDocumentCount(0)
      alert('✅ All documents cleared')
    } catch (error) {
      setError('Failed to clear documents')
    }
  }

  // Reset and start over
  const handleReset = () => {
    setFiles([])
    setResult(null)
    setError(null)
    checkDocumentCount()
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      {/* Header */}
      <header className="bg-white shadow-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-6">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
            <div className="mb-2 sm:mb-0">
              <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-gray-900 flex items-center">
                🎓 UOH Academic Evaluation
              </h1>
              <p className="text-sm sm:text-base text-gray-600 mt-1">
                AI-powered document processing for University of Hyderabad
              </p>
            </div>
            
            {/* System Status Badge */}
            {systemStatus && (
              <div className="flex flex-col sm:flex-row gap-2 text-xs sm:text-sm">
                <span className={`px-3 py-1 rounded-full font-semibold ${
                  systemStatus.llm_available 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-red-100 text-red-800'
                }`}>
                  LLM: {systemStatus.llm_provider || 'Offline'}
                </span>
                <span className={`px-3 py-1 rounded-full font-semibold ${
                  systemStatus.supabase_available 
                    ? 'bg-blue-100 text-blue-800' 
                    : 'bg-gray-100 text-gray-800'
                }`}>
                  DB: {systemStatus.supabase_available ? 'Connected' : 'Offline'}
                </span>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
        
        {/* Error Alert */}
        {error && (
          <div className="mb-6 bg-red-50 border-l-4 border-red-500 p-4 rounded-lg">
            <div className="flex items-start">
              <AlertCircle className="h-5 w-5 text-red-500 mt-0.5 mr-3 flex-shrink-0" />
              <div>
                <p className="text-sm font-medium text-red-800">Error</p>
                <p className="text-sm text-red-700 mt-1">{error}</p>
              </div>
              <button 
                onClick={() => setError(null)}
                className="ml-auto text-red-500 hover:text-red-700"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
          </div>
        )}

        {/* Stats Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 mb-6 sm:mb-8">
          <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-blue-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Documents in Queue</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{documentCount}</p>
              </div>
              <FileText className="h-12 w-12 text-blue-500 opacity-80" />
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-green-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Batches</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{batches.length}</p>
              </div>
              <Users className="h-12 w-12 text-green-500 opacity-80" />
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-purple-500 sm:col-span-2 lg:col-span-1">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">System Status</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">
                  {systemStatus?.status === 'operational' ? '✅ Ready' : '⚠️ Check'}
                </p>
              </div>
              <TrendingUp className="h-12 w-12 text-purple-500 opacity-80" />
            </div>
          </div>
        </div>

        {/* Upload Section */}
        {!result && (
          <div className="bg-white rounded-xl shadow-lg p-6 sm:p-8 mb-6">
            <h2 className="text-xl sm:text-2xl font-semibold mb-4 sm:mb-6 text-gray-900">
              Upload Academic Documents
            </h2>
            
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 sm:p-12 text-center hover:border-blue-400 transition-colors">
              <Upload className="mx-auto h-12 w-12 sm:h-16 sm:w-16 text-gray-400 mb-4" />
              
              <label className="cursor-pointer">
                <span className="mt-2 block text-base sm:text-lg font-medium text-gray-900">
                  Click to upload PDF documents
                </span>
                <span className="mt-1 block text-sm text-gray-500">
                  or drag and drop files here
                </span>
                <input
                  type="file"
                  multiple
                  accept=".pdf"
                  onChange={handleUpload}
                  className="hidden"
                  disabled={uploading || processing}
                />
              </label>

              {uploading && (
                <div className="mt-4 flex items-center justify-center">
                  <Loader className="animate-spin h-6 w-6 text-blue-600 mr-2" />
                  <span className="text-sm text-gray-600">Uploading...</span>
                </div>
              )}

              {files.length > 0 && !uploading && (
                <div className="mt-4">
                  <p className="text-sm font-medium text-green-600">
                    ✅ {files.length} file{files.length > 1 ? 's' : ''} uploaded successfully
                  </p>
                  <div className="mt-2 text-xs text-gray-500 max-h-32 overflow-y-auto">
                    {files.map((file, idx) => (
                      <div key={idx} className="truncate">{file.name}</div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Action Buttons */}
            <div className="mt-6 flex flex-col sm:flex-row gap-3">
              <button
                onClick={handleProcess}
                disabled={documentCount === 0 || processing}
                className="flex-1 bg-blue-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center transition-colors"
              >
                {processing ? (
                  <>
                    <Loader className="animate-spin h-5 w-5 mr-2" />
                    Processing...
                  </>
                ) : (
                  <>
                    <RefreshCw className="h-5 w-5 mr-2" />
                    Process Documents ({documentCount})
                  </>
                )}
              </button>

              {documentCount > 0 && (
                <button
                  onClick={handleClear}
                  disabled={processing}
                  className="sm:w-auto bg-red-50 text-red-600 py-3 px-6 rounded-lg font-semibold hover:bg-red-100 disabled:opacity-50 flex items-center justify-center transition-colors"
                >
                  <Trash2 className="h-5 w-5 mr-2" />
                  Clear All
                </button>
              )}
            </div>
          </div>
        )}

        {/* Results Section */}
        {result && (
          <div className="space-y-6">
            {/* Results Header */}
            <div className="bg-white rounded-xl shadow-lg p-6 sm:p-8">
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6">
                <h2 className="text-xl sm:text-2xl font-semibold text-gray-900 mb-4 sm:mb-0">
                  Processing Results
                </h2>
                <button
                  onClick={handleReset}
                  className="bg-gray-100 text-gray-700 py-2 px-4 rounded-lg font-semibold hover:bg-gray-200 flex items-center justify-center"
                >
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Process More
                </button>
              </div>

              {/* Stats Grid */}
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <p className="text-3xl sm:text-4xl font-bold text-blue-600">
                    {result.total_documents}
                  </p>
                  <p className="text-xs sm:text-sm text-gray-600 mt-1">Total Documents</p>
                </div>
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <p className="text-3xl sm:text-4xl font-bold text-green-600">
                    {result.successful}
                  </p>
                  <p className="text-xs sm:text-sm text-gray-600 mt-1">Successful</p>
                </div>
                <div className="text-center p-4 bg-red-50 rounded-lg">
                  <p className="text-3xl sm:text-4xl font-bold text-red-600">
                    {result.failed}
                  </p>
                  <p className="text-xs sm:text-sm text-gray-600 mt-1">Failed</p>
                </div>
                <div className="text-center p-4 bg-purple-50 rounded-lg col-span-2 lg:col-span-1">
                  <p className="text-3xl sm:text-4xl font-bold text-purple-600">
                    {result.success_rate.toFixed(1)}%
                  </p>
                  <p className="text-xs sm:text-sm text-gray-600 mt-1">Success Rate</p>
                </div>
              </div>

              {/* Download Button */}
              <button
                onClick={() => handleDownload(result.batch_id)}
                className="w-full bg-green-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-green-700 flex items-center justify-center transition-colors"
              >
                <Download className="mr-2 h-5 w-5" />
                Download Excel Report
              </button>
            </div>

            {/* Students Table */}
            <div className="bg-white rounded-xl shadow-lg p-6 sm:p-8">
              <h3 className="text-lg sm:text-xl font-semibold mb-4 text-gray-900">
                Processed Students ({result.students.length})
              </h3>
              
              {/* Mobile Cards View */}
              <div className="block sm:hidden space-y-4">
                {result.students.map((student, idx) => (
                  <div key={idx} className="border border-gray-200 rounded-lg p-4 bg-gray-50">
                    <div className="font-semibold text-gray-900 mb-2">
                      {student.student_name}
                    </div>
                    <div className="space-y-1 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Roll Number:</span>
                        <span className="font-medium">{student.roll_number}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Department:</span>
                        <span className="font-medium">{student.department}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">CGPA:</span>
                        <span className="font-medium text-blue-600">{student.cgpa}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Email:</span>
                        <span className="font-medium text-xs truncate max-w-[180px]">
                          {student.email}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Desktop Table View */}
              <div className="hidden sm:block overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Student Name
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Roll Number
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Department
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        CGPA
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Email
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {result.students.map((student, idx) => (
                      <tr key={idx} className="hover:bg-gray-50 transition-colors">
                        <td className="px-4 py-3 text-sm font-medium text-gray-900">
                          {student.student_name}
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-600">
                          {student.roll_number}
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-600">
                          {student.department}
                        </td>
                        <td className="px-4 py-3 text-sm font-semibold text-blue-600">
                          {student.cgpa}
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-600 truncate max-w-xs">
                          {student.email}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* Previous Batches Section */}
        {batches.length > 0 && (
          <div className="mt-6 bg-white rounded-xl shadow-lg p-6 sm:p-8">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg sm:text-xl font-semibold text-gray-900">
                Previous Batches ({batches.length})
              </h3>
              <button
                onClick={() => setShowBatches(!showBatches)}
                className="text-sm text-blue-600 hover:text-blue-800 font-medium"
              >
                {showBatches ? 'Hide' : 'Show'}
              </button>
            </div>

            {showBatches && (
              <div className="space-y-2">
                {batches.slice(0, 10).map((batch, idx) => (
                  <div 
                    key={idx}
                    className="flex flex-col sm:flex-row sm:items-center sm:justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                  >
                    <div className="mb-2 sm:mb-0">
                      <p className="font-medium text-gray-900 text-sm sm:text-base">
                        {batch.filename}
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        Created: {new Date(batch.created_at).toLocaleString()}
                        {batch.record_count && ` • ${batch.record_count} records`}
                      </p>
                    </div>
                    <button
                      onClick={() => handleDownload(batch.filename.replace('.xlsx', ''))}
                      className="bg-blue-600 text-white py-2 px-4 rounded-lg text-sm font-semibold hover:bg-blue-700 flex items-center justify-center transition-colors"
                    >
                      <Download className="h-4 w-4 mr-2" />
                      Download
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-sm text-gray-600">
            © 2025 University of Hyderabad - Academic Evaluation System
          </p>
          <p className="text-center text-xs text-gray-500 mt-1">
            Powered by AI • Gemini + Cohere
          </p>
        </div>
      </footer>
    </div>
  )
}

export default App
