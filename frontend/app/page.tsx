'use client'

import { useState, useEffect } from 'react'
import { Search, Loader2, CheckCircle, XCircle, ExternalLink, Copy, Download } from 'lucide-react'
import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface JobStatus {
  job_id: string
  status: string
  progress?: string
  result?: string
  sources?: Array<{ url: string; title: string }>
  error?: string
}

export default function Home() {
  const [query, setQuery] = useState('')
  const [jobId, setJobId] = useState<string | null>(null)
  const [jobStatus, setJobStatus] = useState<JobStatus | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const startResearch = async () => {
    if (!query.trim()) {
      setError('Please enter a research topic')
      return
    }

    setIsLoading(true)
    setError(null)
    setJobStatus(null)

    try {
      const response = await axios.post(`${API_URL}/api/research`, {
        query: query.trim(),
        n_results: 20
      })
      
      setJobId(response.data.job_id)
      pollJobStatus(response.data.job_id)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to start research')
      setIsLoading(false)
    }
  }

  const pollJobStatus = async (id: string) => {
    const pollInterval = setInterval(async () => {
      try {
        const response = await axios.get(`${API_URL}/api/jobs/${id}`)
        const status = response.data
        
        setJobStatus(status)

        if (status.status === 'completed' || status.status === 'error') {
          clearInterval(pollInterval)
          setIsLoading(false)
        }
      } catch (err) {
        clearInterval(pollInterval)
        setError('Failed to fetch job status')
        setIsLoading(false)
      }
    }, 2000) // Poll every 2 seconds
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    // You could add a toast notification here
  }

  const downloadResults = () => {
    if (!jobStatus?.result) return
    
    const blob = new Blob([jobStatus.result], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `research-${query.replace(/\s+/g, '-')}.txt`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <div className="container mx-auto px-4 py-12 max-w-6xl">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            Research Agent
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            AI-powered research assistant that discovers relevant research areas and topics
            by analyzing web sources and academic papers
          </p>
        </div>

        {/* Search Box */}
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-8">
          <div className="flex gap-4">
            <div className="flex-1">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && !isLoading && startResearch()}
                placeholder="Enter a research topic (e.g., 'AI in healthcare', 'Climate change solutions')"
                className="w-full px-6 py-4 text-lg text-gray-900 bg-white border-2 border-gray-200 rounded-xl focus:border-primary-500 focus:outline-none transition-colors placeholder:text-gray-400"
                disabled={isLoading}
              />
            </div>
            <button
              onClick={startResearch}
              disabled={isLoading || !query.trim()}
              className="px-8 py-4 bg-primary-600 text-white rounded-xl font-semibold hover:bg-primary-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
            >
              {isLoading ? (
                <>
                  <Loader2 className="animate-spin" size={20} />
                  Researching...
                </>
              ) : (
                <>
                  <Search size={20} />
                  Research
                </>
              )}
            </button>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-6 rounded-lg">
            <div className="flex items-center gap-2">
              <XCircle className="text-red-500" size={20} />
              <p className="text-red-700">{error}</p>
            </div>
          </div>
        )}

        {/* Progress Indicator */}
        {isLoading && jobStatus && (
          <div className="bg-blue-50 border-l-4 border-blue-500 p-6 mb-6 rounded-lg">
            <div className="flex items-center gap-3 mb-2">
              <Loader2 className="animate-spin text-blue-500" size={20} />
              <h3 className="font-semibold text-blue-900">Processing...</h3>
            </div>
            <p className="text-blue-700 ml-8">{jobStatus.progress || 'Analyzing sources...'}</p>
          </div>
        )}

        {/* Results */}
        {jobStatus?.status === 'completed' && jobStatus.result && (
          <div className="space-y-6">
            {/* Results Card */}
            <div className="bg-white rounded-2xl shadow-xl p-8">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                  <CheckCircle className="text-green-500" size={24} />
                  <h2 className="text-2xl font-bold text-gray-900">Research Results</h2>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => copyToClipboard(jobStatus.result!)}
                    className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
                    title="Copy to clipboard"
                  >
                    <Copy size={20} />
                  </button>
                  <button
                    onClick={downloadResults}
                    className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
                    title="Download results"
                  >
                    <Download size={20} />
                  </button>
                </div>
              </div>
              <div className="prose max-w-none">
                <div className="whitespace-pre-wrap text-gray-700 leading-relaxed">
                  {jobStatus.result}
                </div>
              </div>
            </div>

            {/* Sources Card */}
            {jobStatus.sources && jobStatus.sources.length > 0 && (
              <div className="bg-white rounded-2xl shadow-xl p-8">
                <h3 className="text-xl font-bold text-gray-900 mb-4">Sources</h3>
                <div className="space-y-3">
                  {jobStatus.sources.map((source, index) => (
                    <a
                      key={index}
                      href={source.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-3 p-4 border border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors group"
                    >
                      <ExternalLink className="text-gray-400 group-hover:text-primary-500" size={18} />
                      <span className="flex-1 text-gray-700 group-hover:text-primary-600 truncate">
                        {source.title || source.url}
                      </span>
                    </a>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Error Status */}
        {jobStatus?.status === 'error' && (
          <div className="bg-red-50 border-l-4 border-red-500 p-6 rounded-lg">
            <div className="flex items-center gap-3 mb-2">
              <XCircle className="text-red-500" size={24} />
              <h3 className="font-semibold text-red-900">Error</h3>
            </div>
            <p className="text-red-700 ml-8">{jobStatus.error || 'An error occurred during research'}</p>
          </div>
        )}

        {/* Footer */}
        <div className="mt-12 text-center text-gray-500 text-sm">
          <p>Powered by Gemini AI and DuckDuckGo Search</p>
        </div>
      </div>
    </main>
  )
}
