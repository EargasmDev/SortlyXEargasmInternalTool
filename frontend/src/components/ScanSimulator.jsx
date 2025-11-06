import { useState } from 'react'
import { api } from '../api'

export default function ScanSimulator({ job, onScanSuccess }) {
  const [scanValue, setScanValue] = useState('')
  const [message, setMessage] = useState('')
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleScan = async (e) => {
    e.preventDefault()
    if (!scanValue.trim()) return
    setLoading(true)
    setMessage('')
    setError(null)

    try {
      const res = await api.post('/scan', {
        job_name: job.name,
        scanned_name: scanValue.trim(),
      })
      setMessage(res.data.message)
      setScanValue('')
      onScanSuccess() // refresh jobs & quantities instantly
    } catch (err) {
      console.error(err)
      if (err.response?.data?.detail) {
        setError(err.response.data.detail)
      } else {
        setError('Error processing scan.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h3 className="text-xl font-semibold mb-3 text-gray-800">
        Scan Items ({job.name})
      </h3>

      {/* 🔒 Hidden scanner form */}
      <form
        onSubmit={handleScan}
        className="flex gap-3 mb-4"
        style={{ display: 'none' }}
      >
        <input
          type="text"
          value={scanValue}
          onChange={(e) => setScanValue(e.target.value)}
          placeholder="Scan barcode here..."
          autoFocus
          className="border p-2 rounded w-full focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          type="submit"
          disabled={loading}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? 'Processing...' : 'Scan'}
        </button>
      </form>

      {message && (
        <p className="text-green-600 font-medium bg-green-50 p-2 rounded mb-2">
          ✅ {message}
        </p>
      )}
      {error && (
        <p className="text-red-600 font-medium bg-red-50 p-2 rounded mb-2">
          ❌ {error}
        </p>
      )}

      <div className="mt-4">
        <h4 className="font-semibold text-gray-700 mb-2">Items Remaining</h4>
        <ul className="border rounded-md divide-y divide-gray-200">
          {job.items.map((item) => (
            <li
              key={item.name}
              className="flex justify-between p-2 text-sm text-gray-800"
            >
              <span>{item.name}</span>
              <span className="font-mono">{item.current_qty}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}
