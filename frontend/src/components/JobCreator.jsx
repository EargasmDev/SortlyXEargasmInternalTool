import { useState, useEffect } from 'react'
import { api } from '../api'

export default function JobCreator({ onCreated }) {
  const [name, setName] = useState('')
  const [items, setItems] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')      // use empty string, easier to clear
  const [success, setSuccess] = useState(false)

  // Auto-hide success after 3s
  useEffect(() => {
    if (!success) return
    const t = setTimeout(() => setSuccess(false), 3000)
    return () => clearTimeout(t)
  }, [success])

  const handleCreate = async () => {
    // reset UI state for a fresh attempt
    setSuccess(false)
    setError('')

    if (!name.trim() || !items.trim()) {
      setError('Please enter a job name and at least one item.')
      return
    }

    // Parse lines like "HF-Blue: 10" -> { name: "HF-Blue", count: 10 }
    const itemList = items
      .split('\n')
      .map(l => l.trim())
      .filter(l => l.length > 0)
      .map(l => {
        const [n, q] = l.split(':').map(p => p?.trim() ?? '')
        const count = Number.parseInt(q || '1', 10)
        return { name: n, count: Number.isNaN(count) ? 1 : count }
      })

    try {
      setLoading(true)
      const res = await api.post('/job', { name, items: itemList })

      // Treat any 2xx as success
      if (res.status >= 200 && res.status < 300) {
        setName('')
        setItems('')
        setError('')          // <— hard clear any lingering red message
        setSuccess(true)
        onCreated?.()
        return
      }

      // Non-2xx falls through to error
      setError('Error creating job. Please try again.')
      setSuccess(false)
    } catch (err) {
      // Backend actually failed
      const msg =
        err?.response?.data?.detail ||
        err?.message ||
        'Error creating job. Please try again.'
      setError(String(msg))
      setSuccess(false)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="rounded-2xl border border-gray-200 bg-white shadow-sm p-6">
      <h2 className="text-2xl font-bold mb-4 text-gray-900">Create Picklist</h2>

      <div className="flex flex-col gap-4">
        <input
          type="text"
          placeholder="e.g. Warehouse to Warped Tour LB"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="border rounded-lg p-3 focus:ring-2 focus:ring-blue-500 focus:outline-none text-gray-800 placeholder-gray-400"
        />

        <textarea
          placeholder={`e.g.\nHF-Blue: 10\nHF-Trans: 8\nHF-AG: 4`}
          value={items}
          onChange={(e) => setItems(e.target.value)}
          className="border rounded-lg p-3 h-32 resize-y focus:ring-2 focus:ring-blue-500 focus:outline-none text-gray-800 placeholder-gray-400"
        />

        {/* Only one message at a time */}
        {error && !success && (
          <p className="text-red-600 text-sm">{error}</p>
        )}
        {success && (
          <p className="text-green-600 text-sm">✅ Job created successfully!</p>
        )}

        <button
          onClick={handleCreate}
          disabled={loading}
          className={`px-5 py-2.5 rounded-lg font-semibold text-white transition ${
            loading ? 'bg-blue-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'
          }`}
        >
          {loading ? 'Creating...' : 'Create'}
        </button>
      </div>
    </div>
  )
}
