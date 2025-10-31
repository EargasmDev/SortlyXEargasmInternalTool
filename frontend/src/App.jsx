import { useEffect, useState, useCallback } from "react";
import { api } from "./api";
import JobCreator from "./components/JobCreator";
import JobViewer from "./components/JobViewer";
import ScanSimulator from "./components/ScanSimulator";
import ItemEditor from "./components/ItemEditor";

export default function App() {
  const [jobs, setJobs] = useState([]);
  const [selectedJob, setSelectedJob] = useState(null);
  const [loading, setLoading] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(Date.now());

  const loadJobs = useCallback(async () => {
    try {
      setLoading(true);
      const res = await api.get("/job/list/all");
      const fresh = res.data || [];
      setJobs(fresh);

      if (selectedJob) {
        const updated = fresh.find((j) => j.id === selectedJob.id);
        if (updated) {
          // ✅ replace completely so nested arrays trigger re-render
          setSelectedJob(updated);
        } else {
          setSelectedJob(null);
        }
      }

      setLastUpdated(Date.now());
    } catch (err) {
      console.error("Error loading jobs:", err);
    } finally {
      setLoading(false);
    }
  }, [selectedJob?.id]);

  // initial load
  useEffect(() => {
    loadJobs();
  }, [loadJobs]);

  // short polling for near real-time updates
  useEffect(() => {
    const interval = setInterval(loadJobs, 5000);
    return () => clearInterval(interval);
  }, [loadJobs]);

  // unified refresh callback for mutations
  const handleMutated = async () => {
    await loadJobs();
  };

  return (
    <div className="min-h-screen bg-gray-50 py-10 px-6">
      <h1 className="text-4xl font-bold mb-10 text-center text-blue-700 tracking-tight">
        Eargasm Pick List
      </h1>

      <div className="max-w-6xl mx-auto grid md:grid-cols-2 gap-6">
        {/* Create Job */}
        <div className="bg-white shadow-md rounded-2xl p-6 border border-gray-200">
          <JobCreator onCreate={handleMutated} />
        </div>

        {/* Scan Simulator */}
        <div className="bg-white shadow-md rounded-2xl p-6 border border-gray-200">
          {selectedJob ? (
            <ScanSimulator job={selectedJob} onScanSuccess={handleMutated} />
          ) : (
            <p className="text-gray-500 text-center py-16">
              Select a job to begin scanning.
            </p>
          )}
        </div>

        {/* Item Editor */}
        {selectedJob && (
          <div className="bg-white shadow-md rounded-2xl p-6 border border-gray-200 md:col-span-2">
            <ItemEditor job={selectedJob} onUpdated={handleMutated} />
          </div>
        )}

        {/* Job Viewer */}
        <div className="bg-white shadow-md rounded-2xl p-6 border border-gray-200 md:col-span-2">
          <JobViewer
            jobs={jobs}
            loading={loading}
            onSelect={(job) => setSelectedJob(job)}
            onRefresh={loadJobs}
          />
        </div>
      </div>

      <p className="text-center text-gray-400 text-sm mt-8">
        Last updated: {new Date(lastUpdated).toLocaleTimeString()}
      </p>
    </div>
  );
}
