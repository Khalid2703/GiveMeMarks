import React, { useEffect, useState } from 'react'
import axios from 'axios'
import { AlertTriangle, CheckCircle, Info, AlertCircle, Users, RefreshCw, ChevronDown, X } from 'lucide-react'

const API_URL = import.meta.env.PROD 
  ? 'https://uoh-academic-backend.onrender.com'
  : 'http://localhost:8000'

export default function AcademicAlerts() {
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [batches, setBatches] = useState([])
  const [selectedBatches, setSelectedBatches] = useState([])
  const [showBatchSelector, setShowBatchSelector] = useState(false)

  useEffect(() => {
    fetchBatches()
  }, [])

  useEffect(() => {
    if (batches.length > 0) {
      fetchAlerts()
    }
  }, [selectedBatches, batches])

  const fetchBatches = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/batches/all`)
      const batchList = response.data.batches || []
      setBatches(batchList)
      // By default, select all batches
      setSelectedBatches(batchList.map(b => b.filename))
    } catch (err) {
      console.error('Failed to fetch batches:', err)
    }
  }

  const fetchAlerts = async () => {
    setLoading(true)
    try {
      // Pass selected batches to the backend
      const params = selectedBatches.length > 0 ? { batches: selectedBatches.join(',') } : {}
      const response = await axios.get(`${API_URL}/api/dashboard/alerts`, { params })
      setAlerts(response.data.alerts || [])
      setError(null)
    } catch (err) {
      console.error('Failed to fetch alerts:', err)
      setError('Failed to load alerts')
    } finally {
      setLoading(false)
    }
  }

  const toggleBatch = (batchFilename) => {
    setSelectedBatches(prev => {
      if (prev.includes(batchFilename)) {
        return prev.filter(b => b !== batchFilename)
      } else {
        return [...prev, batchFilename]
      }
    })
  }

  const selectAllBatches = () => {
    setSelectedBatches(batches.map(b => b.filename))
  }

  const deselectAllBatches = () => {
    setSelectedBatches([])
  }

  const getAlertIcon = (type) => {
    switch (type) {
      case 'warning':
        return <AlertTriangle className="h-5 w-5" />
      case 'success':
        return <CheckCircle className="h-5 w-5" />
      case 'info':
        return <Info className="h-5 w-5" />
      default:
        return <AlertCircle className="h-5 w-5" />
    }
  }

  const getAlertColor = (type) => {
    switch (type) {
      case 'warning':
        return 'border-amber-200 bg-amber-50'
      case 'success':
        return 'border-green-200 bg-green-50'
      case 'info':
        return 'border-blue-200 bg-blue-50'
      default:
        return 'border-gray-200 bg-gray-50'
    }
  }

  const getIconColor = (type) => {
    switch (type) {
      case 'warning':
        return 'text-amber-600'
      case 'success':
        return 'text-green-600'
      case 'info':
        return 'text-blue-600'
      default:
        return 'text-gray-600'
    }
  }

  const getSeverityBadge = (severity) => {
    const colors = {
      high: 'bg-red-100 text-red-800',
      medium: 'bg-orange-100 text-orange-800',
      low: 'bg-blue-100 text-blue-800'
    }
    return (
      <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${colors[severity] || colors.low}`}>
        {severity?.toUpperCase()}
      </span>
    )
  }

  const getBatchDisplayName = (filename) => {
    // Extract readable name from filename like "academic_batch_2025-01-25.xlsx"
    const match = filename.match(/batch_(.+)\.xlsx/)
    return match ? match[1] : filename
  }

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-gray-900">Academic Alerts & Recommendations</h2>
        </div>
        <div className="flex items-center justify-center py-12">
          <RefreshCw className="h-8 w-8 animate-spin text-blue-600" />
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-gray-900">Academic Alerts & Recommendations</h2>
        </div>
        <div className="text-center py-12">
          <AlertCircle className="h-12 w-12 text-red-400 mx-auto mb-3" />
          <p className="text-gray-600">{error}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-xl font-bold text-gray-900">Academic Alerts & Recommendations</h2>
          <p className="text-sm text-gray-500 mt-1">Faculty action items based on student data analysis</p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowBatchSelector(!showBatchSelector)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all ${
              showBatchSelector 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            <Users size={18} />
            <span className="text-sm">
              {selectedBatches.length === batches.length 
                ? 'All Batches' 
                : `${selectedBatches.length} Batch${selectedBatches.length !== 1 ? 'es' : ''}`}
            </span>
            <ChevronDown 
              size={16} 
              className={`transition-transform ${showBatchSelector ? 'rotate-180' : ''}`}
            />
          </button>
          <button
            onClick={fetchAlerts}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            title="Refresh alerts"
          >
            <RefreshCw className="h-5 w-5 text-gray-600" />
          </button>
        </div>
      </div>

      {/* Batch Selector Dropdown */}
      {showBatchSelector && (
        <div className="mb-4 bg-gray-50 rounded-lg p-4 border border-gray-200 animate-fadeIn">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold text-gray-700">Select Batches to Monitor</h3>
            <div className="flex gap-2">
              <button
                onClick={selectAllBatches}
                className="text-xs text-blue-600 hover:text-blue-700 font-medium"
              >
                Select All
              </button>
              <span className="text-gray-300">|</span>
              <button
                onClick={deselectAllBatches}
                className="text-xs text-red-600 hover:text-red-700 font-medium"
              >
                Deselect All
              </button>
            </div>
          </div>
          
          <div className="space-y-2 max-h-48 overflow-y-auto">
            {batches.map((batch, idx) => (
              <label
                key={idx}
                className="flex items-center gap-3 p-2 hover:bg-white rounded-lg cursor-pointer transition-colors"
              >
                <input
                  type="checkbox"
                  checked={selectedBatches.includes(batch.filename)}
                  onChange={() => toggleBatch(batch.filename)}
                  className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                />
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">
                    {getBatchDisplayName(batch.filename)}
                  </p>
                  <p className="text-xs text-gray-500">
                    {batch.student_count} student{batch.student_count !== 1 ? 's' : ''}
                  </p>
                </div>
              </label>
            ))}
          </div>

          {selectedBatches.length === 0 && (
            <div className="mt-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
              <p className="text-xs text-yellow-800 flex items-center gap-2">
                <AlertCircle size={14} />
                Please select at least one batch to view alerts
              </p>
            </div>
          )}
        </div>
      )}

      {/* Selected Batches Display */}
      {selectedBatches.length > 0 && selectedBatches.length < batches.length && !showBatchSelector && (
        <div className="mb-4 flex flex-wrap gap-2">
          {selectedBatches.map((filename, idx) => (
            <span
              key={idx}
              className="inline-flex items-center gap-2 px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium"
            >
              {getBatchDisplayName(filename)}
              <button
                onClick={() => toggleBatch(filename)}
                className="hover:bg-blue-200 rounded-full p-0.5"
              >
                <X size={12} />
              </button>
            </span>
          ))}
        </div>
      )}

      {/* Alerts Display */}
      {selectedBatches.length === 0 ? (
        <div className="text-center py-12">
          <Users className="h-12 w-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-600 font-medium">No batches selected</p>
          <p className="text-sm text-gray-500 mt-1">Select batches to view alerts</p>
        </div>
      ) : alerts.length === 0 ? (
        <div className="text-center py-12">
          <CheckCircle className="h-12 w-12 text-green-400 mx-auto mb-3" />
          <p className="text-gray-600 font-medium">All clear!</p>
          <p className="text-sm text-gray-500 mt-1">No critical alerts for selected batch{selectedBatches.length !== 1 ? 'es' : ''}</p>
        </div>
      ) : (
        <div className="space-y-3">
          {alerts.map((alert, idx) => (
            <div
              key={idx}
              className={`border-2 rounded-lg p-4 transition-all hover:shadow-md ${getAlertColor(alert.type)}`}
            >
              <div className="flex items-start gap-3">
                <div className={`mt-0.5 ${getIconColor(alert.type)}`}>
                  {getAlertIcon(alert.type)}
                </div>
                
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-semibold text-gray-900">{alert.title}</h3>
                    {getSeverityBadge(alert.severity)}
                  </div>
                  
                  <p className="text-sm text-gray-700 mb-2">{alert.description}</p>
                  
                  {alert.details && (
                    <p className="text-xs text-gray-600 mb-3 italic">{alert.details}</p>
                  )}
                  
                  <div className="flex items-center justify-between mt-3 pt-3 border-t border-gray-200">
                    <div className="flex items-center gap-2 text-xs text-gray-600">
                      <Users className="h-3 w-3" />
                      <span className="font-medium">{alert.count} affected</span>
                    </div>
                    <div className="text-xs font-medium text-gray-800 bg-white px-3 py-1.5 rounded-lg border border-gray-200">
                      🎯 Action: {alert.action}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
