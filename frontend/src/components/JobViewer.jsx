import { api } from '../api'

export default function JobViewer({ jobs, onSelect, onRefresh }) {
  // Separate active vs completed pick lists
  const activeJobs = jobs.filter(j => j.items.some(i => i.current_qty > 0))
  const completedJobs = jobs.filter(j => j.items.every(i => i.current_qty === 0))

  const renderJobCard = job => (
    <div key={job.name} className="border rounded-xl p-4 shadow-sm">
      <div className="flex justify-between items-center mb-2">
        <h3
          onClick={() => onSelect(job)}
          className="font-semibold text-blue-600 cursor-pointer hover:underline"
        >
          {job.name}
        </h3>
        <button
          onClick={async () => {
            if (!window.confirm(`Delete pick list "${job.name}"?`)) return
            await api.delete(`/job/${job.name}`)
            onRefresh()
          }}
          className="text-red-500 hover:text-red-700"
        >
          ✕
        </button>
      </div>
      {job.items.map(item => (
        <div key={item.name} className="flex justify-between text-sm">
          <span>{item.name}</span>
          <span
            className={`font-semibold ${
              item.current_qty === 0 ? 'text-gray-400' : 'text-gray-700'
            }`}
          >
            {item.current_qty}
          </span>
        </div>
      ))}
    </div>
  )

  return (
    <div className="space-y-10">
      {/* Active Pick Lists */}
      <section>
        <h2 className="text-2xl font-bold mb-4 text-gray-900">Active Pick Lists</h2>
        {activeJobs.length > 0 ? (
          <div className="grid md:grid-cols-2 gap-4">
            {activeJobs.map(renderJobCard)}
          </div>
        ) : (
          <p className="text-gray-500 italic">No active pick lists.</p>
        )}
      </section>

      {/* Completed Pick Lists */}
      <section>
        <h2 className="text-2xl font-bold mb-4 text-gray-900">Completed Pick Lists</h2>
        {completedJobs.length > 0 ? (
          <div className="grid md:grid-cols-2 gap-4">
            {completedJobs.map(renderJobCard)}
          </div>
        ) : (
          <p className="text-gray-500 italic">No completed pick lists yet.</p>
        )}
      </section>
    </div>
  )
}
