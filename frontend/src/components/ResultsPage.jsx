import React, { useState } from 'react'
import axios from 'axios'
import { Search, Loader, AlertCircle, Filter } from 'lucide-react'

const API_URL = import.meta.env.PROD 
  ? 'https://uoh-academic-backend.onrender.com'
  : 'http://localhost:8000'

export default function ResultsPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])
  const [searching, setSearching] = useState(false)
  const [hasSearched, setHasSearched] = useState(false)

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      // If empty, search for all students
      setSearchQuery('')
    }
    
    setSearching(true)
    setHasSearched(true)
    
    try {
      const response = await axios.get(`${API_URL}/api/search/students`, {
        params: { query: searchQuery.trim() }
      })
      setSearchResults(response.data.results || [])
    } catch (error) {
      console.error('Search error:', error)
      setSearchResults([])
    } finally {
      setSearching(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearch()
    }
  }

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">Search Student Results</h1>
      
      {/* Search Bar */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Search by name or roll number..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={handleKeyPress}
              disabled={searching}
              autoFocus
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none disabled:bg-gray-100"
            />
          </div>
          <button 
            onClick={handleSearch}
            disabled={searching}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 flex items-center gap-2 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            {searching ? (
              <>
                <Loader className="animate-spin" size={20} />
                Searching...
              </>
            ) : (
              <>
                <Search size={20} />
                Search
              </>
            )}
          </button>
          <button 
            className="bg-gray-100 text-gray-700 px-6 py-3 rounded-lg font-semibold hover:bg-gray-200 flex items-center gap-2 transition-colors"
            title="Filters coming soon"
          >
            <Filter size={20} />
            Filter
          </button>
        </div>
        
        {/* Quick tip */}
        <p className="text-sm text-gray-500 mt-3">
          💡 Tip: Leave empty and click Search to see all students
        </p>
      </div>

      {/* Results Section */}
      {searching && (
        <div className="flex items-center justify-center h-64">
          <Loader className="animate-spin h-12 w-12 text-blue-600" />
        </div>
      )}

      {!searching && hasSearched && searchResults.length > 0 && (
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h2 className="text-xl font-semibold mb-4 text-gray-900">
            Results ({searchResults.length})
          </h2>
          
          <div className="space-y-4">
            {searchResults.map((student, idx) => (
              <div 
                key={idx} 
                className="border border-gray-200 rounded-lg p-5 hover:shadow-md hover:border-blue-300 transition-all duration-200"
              >
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div>
                    <p className="text-sm text-gray-500 mb-1">Name</p>
                    <p className="font-semibold text-gray-900 text-lg">{student.name}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500 mb-1">Roll Number</p>
                    <p className="font-semibold text-gray-900">{student.roll_number}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500 mb-1">CGPA</p>
                    <p className="font-bold text-blue-600 text-lg">{student.cgpa}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500 mb-1">Department</p>
                    <p className="font-semibold text-gray-900">{student.department}</p>
                  </div>
                </div>
                
                {/* Additional Info */}
                {(student.email || student.semester) && (
                  <div className="mt-3 pt-3 border-t border-gray-100 grid grid-cols-1 md:grid-cols-2 gap-3">
                    {student.email && (
                      <div>
                        <p className="text-xs text-gray-500">Email</p>
                        <p className="text-sm text-gray-700">{student.email}</p>
                      </div>
                    )}
                    {student.semester && (
                      <div>
                        <p className="text-xs text-gray-500">Semester</p>
                        <p className="text-sm text-gray-700">{student.semester}</p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {!searching && hasSearched && searchResults.length === 0 && (
        <div className="bg-white rounded-xl shadow-lg p-12 text-center">
          <AlertCircle className="mx-auto h-16 w-16 text-gray-300 mb-4" />
          <h2 className="text-xl font-semibold text-gray-700 mb-2">No Results Found</h2>
          <p className="text-gray-500">
            {searchQuery 
              ? `No students found matching "${searchQuery}". Try a different search term.`
              : "No students found in the database. Upload and process documents first."
            }
          </p>
        </div>
      )}

      {!searching && !hasSearched && (
        <div className="bg-white rounded-xl shadow-lg p-12 text-center">
          <Search className="mx-auto h-16 w-16 text-gray-300 mb-4" />
          <h2 className="text-xl font-semibold text-gray-700 mb-2">Start Your Search</h2>
          <p className="text-gray-500 mb-4">
            Enter a student name or roll number above, or leave empty to see all students.
          </p>
          <button
            onClick={handleSearch}
            className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
          >
            Show All Students
          </button>
        </div>
      )}
    </div>
  )
}
