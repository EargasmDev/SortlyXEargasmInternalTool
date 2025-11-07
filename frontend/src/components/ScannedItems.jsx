import { useEffect, useState } from "react";
import { api } from "../api";

export default function ScannedItems({ job }) {
  const [scans, setScans] = useState([]);

  const loadScans = async () => {
    try {
      const res = await api.get(`/job/${job.id}/scans`);
      setScans(res.data);
    } catch (err) {
      console.error("Error loading scans:", err);
    }
  };

  useEffect(() => {
    loadScans();
    const interval = setInterval(loadScans, 10000); // refresh every 10 seconds
    return () => clearInterval(interval);
  }, [job.id]);

  return (
    <div className="mt-6 border-t border-gray-200 pt-4">
      <h3 className="text-lg font-semibold mb-3 text-gray-700">Scanned Items</h3>
      {scans.length === 0 ? (
        <p className="text-gray-500">No scans yet.</p>
      ) : (
        <ul className="divide-y divide-gray-100">
          {scans.map((scan) => (
            <li key={scan.id} className="py-2 flex justify-between text-sm">
              <span className="font-medium text-gray-800">{scan.item_name}</span>
              <span className="text-gray-500">
                {new Date(scan.timestamp).toLocaleTimeString()}
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
