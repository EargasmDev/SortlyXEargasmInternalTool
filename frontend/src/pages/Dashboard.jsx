import { useState, useEffect } from 'react'
import { api } from '../api'

export default function Dashboard() {
  const [jobs, setJobs] = useState([])
  const [lastSync, setLastSync] = useState(null)
  const [syncing, setSyncing] = useState(false)
  const [error, setError] = useState(null)

  // Fetch jobs from backend
  const fetchJobs = async () => {
    try {
      const res = await api.get('/job/list/all')
      setJobs(res.data)
    } catch (err) {
      console.error('Error loading jobs', err)
      setError('Error loading jobs')
    }
  }

  // Auto sync every 30s
  useEffect(() => {
    if (!jobs?.length) return

    const interval = setInterval(async () => {
      try {
        setSyncing(true)
        setError(null)

        for (const job of jobs) {
          await api.get(`/sortly/sync/${job.id}`)
          console.log(`✅ Synced Sortly updates for ${job.name}`)
        }

        await fetchJobs()
        setLastSync(new Date().toLocaleTimeString())
      } catch (err) {
        console.error('❌ Error syncing with Sortly', err)
        setError('Error syncing with Sortly')
      } finally {
        setSyncing(false)
      }
    }, 30000)

    return () => clearInterval(interval)
  }, [jobs])

  // Load jobs on mount
  useEffect(() => {
    fetchJobs()
  }, [])

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">
        Eargasm Pick List
      </h1>

      <div className="mb-4 flex items-center justify-between bg-gray-50 border rounded-lg p-3 shadow-sm">
        <div className="flex flex-col">
          <span className="text-sm text-gray-600">
            {syncing
              ? '🔄 Syncing with Sortly...'
              : lastSync
              ? `✅ Last synced at ${lastSync}`
              : 'Waiting for first sync...'}
          </span>
          {error && <span className="text-sm text-red-500">{error}</span>}
        </div>
      </div>

      <div className="space-y-6">
        {jobs.map((job) => (
          <div
            key={job.id}
            className="border border-gray-200 rounded-xl p-5 bg-white shadow-sm"
          >
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-xl font-semibold text-gray-800">
                {job.name}
              </h2>
              <span className="text-sm text-gray-400">Job ID: {job.id}</span>
            </div>

            <details open className="border-t border-gray-100 pt-3">
              <summary className="cursor-pointer text-gray-600 font-medium mb-2">
                Items Remaining
              </summary>
              {job.items?.length ? (
                <ul className="grid grid-cols-2 sm:grid-cols-3 gap-3 mt-2">
                  {job.items.map((item, idx) => (
                    <li
                      key={idx}
                      className="border rounded-lg p-3 flex justify-between bg-gray-50 text-sm"
                    >
                      <span className="font-medium text-gray-800">
                        {item.name}
                      </span>
                      <span className="text-gray-600">
                        {item.current_qty}
                      </span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-gray-500 text-sm">No items listed.</p>
              )}
            </details>
          </div>
        ))}

        {jobs.length === 0 && (
          <p className="text-gray-500 text-center">No active jobs found.</p>
        )}
      </div>
    </div>
  )
}
