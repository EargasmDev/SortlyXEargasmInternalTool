import { useEffect, useState } from 'react'
import { api } from './api'
import JobCreator from './components/JobCreator'
import JobViewer from './components/JobViewer'
import ScanSimulator from './components/ScanSimulator'
import ItemEditor from './components/ItemEditor'
import ScannedItems from './components/ScannedItems'

export default function App() {
  const [jobs, setJobs] = useState([])
  const [selectedJob, setSelectedJob] = useState(null)

  // Fetch jobs from backend
  const loadJobs = async () => {
    try {
      const res = await api.get('/job/list/all')
      const updatedJobs = res.data
      setJobs(updatedJobs)

      // ✅ Preserve selected job if still exists in updated data
      if (selectedJob) {
        const stillExists = updatedJobs.find(j => j.id === selectedJob.id)
        if (stillExists) {
          setSelectedJob(stillExists)
        } else {
          setSelectedJob(null)
        }
      }
    } catch (err) {
      console.error('Error loading jobs:', err)
    }
  }

  // Initial load
  useEffect(() => {
    loadJobs()
  }, [])

  // ✅ Auto-refresh every 10 seconds (can increase to 30s if needed)
  useEffect(() => {
    const interval = setInterval(loadJobs, 10000)
    return () => clearInterval(interval)
  }, [selectedJob])

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

        {/* Scan Simulator + Scanned Items */}
        <div className="bg-white shadow-md rounded-2xl p-6 border border-gray-200">
          {selectedJob ? (
            <>
              <ScanSimulator job={selectedJob} onScanSuccess={loadJobs} />
              <div className="mt-6">
               {/* <ScannedItems job={selectedJob} /> */}

              </div>
            </>
          ) : (
            <p className="text-gray-500 text-center py-16">
              Select a Picklist to begin scanning.
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
