import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { Search, Loader, AlertCircle, Filter, X, ChevronDown } from 'lucide-react'

const API_URL = 'http://localhost:8000'

export default function ResultsPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])
  const [searching, setSearching] = useState(false)
  const [hasSearched, setHasSearched] = useState(false)
  
  // Filter states
  const [showFilters, setShowFilters] = useState(false)
  const [selectedDepartment, setSelectedDepartment] = useState('')
  const [minCGPA, setMinCGPA] = useState(0)
  const [maxCGPA, setMaxCGPA] = useState(10)
  const [departments, setDepartments] = useState([])
  const [activeFiltersCount, setActiveFiltersCount] = useState(0)

  // Auto-load all students and departments on mount
  useEffect(() => {
    initialLoad()
    fetchDepartments()
  }, [])

  // Update active filters count
  useEffect(() => {
    let count = 0
    if (selectedDepartment) count++
    if (minCGPA > 0) count++
    if (maxCGPA < 10) count++
    setActiveFiltersCount(count)
  }, [selectedDepartment, minCGPA, maxCGPA])

  const fetchDepartments = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/dashboard/stats`)
      const depts = response.data.departments || []
      setDepartments(depts.map(d => d.name))
    } catch (error) {
      console.error('Failed to fetch departments:', error)
    }
  }

  // Initial load - gets all students without filters
  const initialLoad = async () => {
    setSearching(true)
    setHasSearched(true)
    
    try {
      const response = await axios.get(`${API_URL}/api/search/students`, { 
        params: { query: '' } 
      })
      setSearchResults(response.data.results || [])
    } catch (error) {
      console.error('Search error:', error)
      setSearchResults([])
    } finally {
      setSearching(false)
    }
  }

  const handleSearch = async () => {
    setSearching(true)
    setHasSearched(true)
    
    try {
      const params = {
        query: searchQuery.trim()
      }
      
      // Only add filters if they are not at default values
      if (selectedDepartment) {
        params.department = selectedDepartment
      }
      
      if (minCGPA > 0) {
        params.min_cgpa = minCGPA
      }
      
      if (maxCGPA < 10) {
        params.max_cgpa = maxCGPA
      }
      
      const response = await axios.get(`${API_URL}/api/search/students`, { params })
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

  const clearFilters = () => {
    setSelectedDepartment('')
    setMinCGPA(0)
    setMaxCGPA(10)
    setSearchQuery('')
  }

  const clearFiltersAndSearch = () => {
    clearFilters()
    // Trigger search after clearing
    setTimeout(() => {
      initialLoad()
    }, 100)
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Search Student Results</h1>
        <button
          onClick={() => setShowFilters(!showFilters)}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg font-semibold transition-all ${
            showFilters 
              ? 'bg-blue-600 text-white' 
              : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
          }`}
        >
          <Filter size={20} />
          Filters
          {activeFiltersCount > 0 && (
            <span className="bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
              {activeFiltersCount}
            </span>
          )}
          <ChevronDown 
            size={16} 
            className={`transition-transform ${showFilters ? 'rotate-180' : ''}`}
          />
        </button>
      </div>
      
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
        </div>
        
        {/* Quick tip */}
        <p className="text-sm text-gray-500 mt-3">
          💡 Tip: Leave empty and click Search to see all students
        </p>
      </div>

      {/* Filters Panel */}
      {showFilters && (
        <div className="bg-white rounded-xl shadow-lg p-6 animate-fadeIn">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Filter Options</h3>
            {activeFiltersCount > 0 && (
              <button
                onClick={clearFiltersAndSearch}
                className="text-sm text-red-600 hover:text-red-700 font-medium flex items-center gap-1"
              >
                <X size={16} />
                Clear All Filters
              </button>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Department Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Department
              </label>
              <select
                value={selectedDepartment}
                onChange={(e) => setSelectedDepartment(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
              >
                <option value="">All Departments</option>
                {departments.map((dept, idx) => (
                  <option key={idx} value={dept}>{dept}</option>
                ))}
              </select>
            </div>

            {/* Min CGPA Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Minimum CGPA: {minCGPA.toFixed(1)}
              </label>
              <input
                type="range"
                min="0"
                max="10"
                step="0.1"
                value={minCGPA}
                onChange={(e) => setMinCGPA(parseFloat(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>0.0</span>
                <span>10.0</span>
              </div>
            </div>

            {/* Max CGPA Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Maximum CGPA: {maxCGPA.toFixed(1)}
              </label>
              <input
                type="range"
                min="0"
                max="10"
                step="0.1"
                value={maxCGPA}
                onChange={(e) => setMaxCGPA(parseFloat(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>0.0</span>
                <span>10.0</span>
              </div>
            </div>
          </div>

          <div className="mt-4 pt-4 border-t border-gray-200">
            <button
              onClick={handleSearch}
              className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
            >
              Apply Filters
            </button>
          </div>
        </div>
      )}

      {/* Active Filters Display */}
      {activeFiltersCount > 0 && (
        <div className="flex flex-wrap gap-2">
          {selectedDepartment && (
            <span className="inline-flex items-center gap-2 px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
              Department: {selectedDepartment}
              <button
                onClick={() => setSelectedDepartment('')}
                className="hover:bg-blue-200 rounded-full p-0.5"
              >
                <X size={14} />
              </button>
            </span>
          )}
          {minCGPA > 0 && (
            <span className="inline-flex items-center gap-2 px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
              Min CGPA: {minCGPA.toFixed(1)}
              <button
                onClick={() => setMinCGPA(0)}
                className="hover:bg-green-200 rounded-full p-0.5"
              >
                <X size={14} />
              </button>
            </span>
          )}
          {maxCGPA < 10 && (
            <span className="inline-flex items-center gap-2 px-3 py-1 bg-orange-100 text-orange-800 rounded-full text-sm font-medium">
              Max CGPA: {maxCGPA.toFixed(1)}
              <button
                onClick={() => setMaxCGPA(10)}
                className="hover:bg-orange-200 rounded-full p-0.5"
              >
                <X size={14} />
              </button>
            </span>
          )}
        </div>
      )}

      {/* Results Section */}
      {searching && (
        <div className="flex items-center justify-center h-64">
          <Loader className="animate-spin h-12 w-12 text-blue-600" />
        </div>
      )}

      {!searching && hasSearched && searchResults.length > 0 && (
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h2 className="text-xl font-semibold mb-4 text-gray-900">
            Results ({searchResults.length} student{searchResults.length !== 1 ? 's' : ''})
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
            {searchQuery || activeFiltersCount > 0
              ? `No students found matching your search criteria. Try adjusting your filters.`
              : "No students found in the database. Upload and process documents first."
            }
          </p>
          {activeFiltersCount > 0 && (
            <button
              onClick={clearFiltersAndSearch}
              className="mt-4 text-blue-600 hover:text-blue-700 font-medium"
            >
              Clear all filters and search again
            </button>
          )}
        </div>
      )}
    </div>
  )
}
