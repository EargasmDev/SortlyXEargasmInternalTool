import { useEffect, useState } from 'react'
import { api } from './api'
import JobCreator from './components/JobCreator'
import JobViewer from './components/JobViewer'
import ScanSimulator from './components/ScanSimulator'
import ItemEditor from './components/ItemEditor'

export default function App() {
  const [jobs, setJobs] = useState([])
  const [selectedJob, setSelectedJob] = useState(null)

  // Fetch jobs from backend
  const loadJobs = async () => {
    try {
      const res = await api.get('/job/list/all')
      setJobs(res.data)

      // Keep selected job if it still exists
      if (res.data.length && !selectedJob) {
        setSelectedJob(res.data[0])
      } else if (selectedJob) {
        const stillExists = res.data.find(j => j.name === selectedJob.name)
        if (!stillExists) setSelectedJob(null)
        else setSelectedJob(stillExists)
      }
    } catch (err) {
      console.error('Error loading jobs:', err)
    }
  }

  // Initial load
  useEffect(() => {
    loadJobs()
  }, [])

  // 🔁 Auto-refresh every 10 seconds
  useEffect(() => {
    const interval = setInterval(loadJobs, 10000) // 10 seconds
    return () => clearInterval(interval)
  }, []) // empty deps = always running

  return (
    <div className="min-h-screen bg-gray-50 py-10 px-6">
      <h1 className="text-4xl font-bold mb-10 text-center text-blue-700 tracking-tight">
        Eargasm Pick List
      </h1>

      <div className="max-w-6xl mx-auto grid md:grid-cols-2 gap-6">
        {/* Create Job */}
        <div className="bg-white shadow-md rounded-2xl p-6 border border-gray-200">
          <JobCreator onCreate={loadJobs} />
        </div>

        {/* Scan Simulator */}
        <div className="bg-white shadow-md rounded-2xl p-6 border border-gray-200">
          {selectedJob ? (
            <ScanSimulator job={selectedJob} onScanSuccess={loadJobs} />
          ) : (
            <p className="text-gray-500 text-center py-16">
              Select a job to begin scanning.
            </p>
          )}
        </div>

        {/* Item Editor */}
        {selectedJob && (
          <div className="bg-white shadow-md rounded-2xl p-6 border border-gray-200 md:col-span-2">
            <ItemEditor job={selectedJob} onUpdated={loadJobs} />
          </div>
        )}

        {/* Job Viewer */}
        <div className="bg-white shadow-md rounded-2xl p-6 border border-gray-200 md:col-span-2">
          <JobViewer jobs={jobs} onSelect={setSelectedJob} onRefresh={loadJobs} />
        </div>
      </div>
    </div>
  )
}
