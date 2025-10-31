import { useEffect, useState } from "react";
import { api } from "../api";

export default function ItemEditor({ job, onUpdated }) {
  const [items, setItems] = useState([]);
  const [collapsed, setCollapsed] = useState(true);

  // ✅ Always reflect the current job items
  useEffect(() => {
    if (job) {
      setItems(job.items || []);
    }
  }, [job]);

  const handleUpdate = async (itemName, newCount) => {
    try {
      const count = parseInt(newCount, 10);
      if (isNaN(count)) return alert("Enter a valid number");

      await api.put(`/job/${job.id}/item`, { name: itemName, count });
      await onUpdated();
    } catch (err) {
      console.error("Error updating item:", err);
      alert("Error updating item quantity.");
    }
  };

  return (
    <div className="bg-white border border-gray-200 rounded-2xl shadow-sm">
      {/* Header */}
      <div
        onClick={() => setCollapsed(!collapsed)}
        className="cursor-pointer px-6 py-3 bg-gray-100 border-b flex justify-between items-center rounded-t-2xl"
      >
        <h2 className="font-bold text-xl text-gray-800">
          Edit Items ({job.name})
        </h2>
        <span className="text-gray-500 text-lg">
          {collapsed ? "▼" : "▲"}
        </span>
      </div>

      {/* Expanded */}
      {!collapsed && (
        <div className="p-6">
          {items.length === 0 ? (
            <p className="text-gray-400">No items to edit.</p>
          ) : (
            <ul className="divide-y divide-gray-200">
              {items.map((item, index) => (
                <li
                  key={index}
                  className="flex justify-between items-center py-2"
                >
                  <span className="font-medium text-gray-800">
                    {item.name}
                  </span>
                  <div className="flex items-center gap-2">
                    <input
                      type="number"
                      value={item.current_qty}
                      onChange={(e) => {
                        const newVal = e.target.value;
                        setItems((prev) =>
                          prev.map((i) =>
                            i.name === item.name
                              ? { ...i, current_qty: newVal }
                              : i
                          )
                        );
                      }}
                      onBlur={(e) =>
                        handleUpdate(item.name, e.target.value)
                      }
                      className="border rounded-lg px-2 py-1 w-20 text-center text-gray-700 focus:ring-2 focus:ring-blue-400 focus:outline-none"
                    />
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
