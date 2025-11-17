"use client";

import { useState, useEffect } from "react";

interface UsageLog {
  id: string;
  timestamp: string;
  api_key_name: string;
  model: string;
  operation: string;
  allowed: boolean;
  reason: string;
  latency_ms: number;
  input_length: number;
}

const LOGS_PER_PAGE = 20;

export default function LogsPage() {
  const [logs, setLogs] = useState<UsageLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [filterModel, setFilterModel] = useState<string>("");
  const [filterAllowed, setFilterAllowed] = useState<string>("all");

  useEffect(() => {
    fetchLogs();
  }, []);

  const fetchLogs = async () => {
    try {
      setLoading(true);
      // Fetch real data from backend API
      const params = new URLSearchParams({
        page: currentPage.toString(),
        limit: LOGS_PER_PAGE.toString(),
        ...(filterModel && { model: filterModel }),
        ...(filterAllowed !== "all" && { allowed: filterAllowed === "allowed" ? "true" : "false" }),
      });

      const response = await fetch(`http://localhost:8000/api/admin/logs?${params}`, {
        headers: {
          "Authorization": "Bearer test_admin_key",
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        // If backend not configured, show empty state
        if (response.status === 401 || response.status === 404) {
          setLogs([]);
          setError("Backend not configured. Make API calls to generate logs.");
        } else {
          throw new Error(`API error: ${response.status}`);
        }
      } else {
        const data = await response.json();
        setLogs(data || []);
        setError(null);
      }
    } catch (err) {
      setError("Failed to load logs. Ensure backend is running on port 8000.");
      console.error(err);
      setLogs([]);
    } finally {
      setLoading(false);
    }
  };

  // Filter logs
  const filteredLogs = logs.filter((log) => {
    if (filterModel && log.model !== filterModel) return false;
    if (filterAllowed === "allowed" && !log.allowed) return false;
    if (filterAllowed === "blocked" && log.allowed) return false;
    return true;
  });

  const totalPages = Math.ceil(filteredLogs.length / LOGS_PER_PAGE);
  const paginatedLogs = filteredLogs.slice(
    (currentPage - 1) * LOGS_PER_PAGE,
    currentPage * LOGS_PER_PAGE
  );

  const models = [...new Set(logs.map((l) => l.model))];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-3xl font-bold text-slate-900 dark:text-white">
          Usage Logs
        </h2>
        <p className="mt-1 text-slate-600 dark:text-slate-400">
          Last 50 governance checks (showing {filteredLogs.length} total)
        </p>
      </div>

      {/* Error Message */}
      {error && (
        <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-300 rounded-lg">
          {error}
        </div>
      )}

      {/* Filters */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 bg-white dark:bg-slate-800 p-4 rounded-lg shadow">
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
            Model
          </label>
          <select
            value={filterModel}
            onChange={(e) => {
              setFilterModel(e.target.value);
              setCurrentPage(1);
            }}
            className="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-900 text-slate-900 dark:text-white"
          >
            <option value="">All Models</option>
            {models.map((model) => (
              <option key={model} value={model}>
                {model}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
            Status
          </label>
          <select
            value={filterAllowed}
            onChange={(e) => {
              setFilterAllowed(e.target.value);
              setCurrentPage(1);
            }}
            className="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-900 text-slate-900 dark:text-white"
          >
            <option value="all">All</option>
            <option value="allowed">Allowed ✓</option>
            <option value="blocked">Blocked ✗</option>
          </select>
        </div>

        <div className="flex items-end">
          <button
            onClick={() => {
              setFilterModel("");
              setFilterAllowed("all");
              fetchLogs();
            }}
            className="w-full px-4 py-2 bg-slate-300 dark:bg-slate-600 hover:bg-slate-400 dark:hover:bg-slate-500 text-slate-900 dark:text-white font-semibold rounded-lg transition"
          >
            Reset Filters
          </button>
        </div>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="text-center py-8">
          <div className="animate-spin inline-block w-8 h-8 border-4 border-slate-200 dark:border-slate-700 border-t-blue-600 rounded-full"></div>
        </div>
      )}

      {/* Logs Table */}
      {!loading && paginatedLogs.length > 0 && (
        <div className="bg-white dark:bg-slate-800 rounded-lg shadow overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 dark:bg-slate-700 border-b border-slate-200 dark:border-slate-600">
                <tr>
                  <th className="px-4 py-3 text-left font-semibold text-slate-700 dark:text-slate-300">
                    Time
                  </th>
                  <th className="px-4 py-3 text-left font-semibold text-slate-700 dark:text-slate-300">
                    API Key
                  </th>
                  <th className="px-4 py-3 text-left font-semibold text-slate-700 dark:text-slate-300">
                    Model
                  </th>
                  <th className="px-4 py-3 text-left font-semibold text-slate-700 dark:text-slate-300">
                    Operation
                  </th>
                  <th className="px-4 py-3 text-left font-semibold text-slate-700 dark:text-slate-300">
                    Status
                  </th>
                  <th className="px-4 py-3 text-left font-semibold text-slate-700 dark:text-slate-300">
                    Reason
                  </th>
                  <th className="px-4 py-3 text-left font-semibold text-slate-700 dark:text-slate-300">
                    Latency
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 dark:divide-slate-700">
                {paginatedLogs.map((log) => (
                  <tr
                    key={log.id}
                    className="hover:bg-slate-50 dark:hover:bg-slate-700 transition"
                  >
                    <td className="px-4 py-3 whitespace-nowrap text-xs text-slate-600 dark:text-slate-400">
                      {new Date(log.timestamp).toLocaleTimeString()}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-xs font-medium text-slate-900 dark:text-white">
                      {log.api_key_name}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-xs">
                      <span className="px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded">
                        {log.model}
                      </span>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-xs text-slate-600 dark:text-slate-400">
                      {log.operation}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-xs">
                      <span
                        className={`px-2 py-1 rounded font-semibold ${
                          log.allowed
                            ? "bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300"
                            : "bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300"
                        }`}
                      >
                        {log.allowed ? "✓ Allowed" : "✗ Blocked"}
                      </span>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-xs text-slate-600 dark:text-slate-400">
                      {log.reason}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-xs font-mono text-slate-600 dark:text-slate-400">
                      {log.latency_ms.toFixed(1)}ms
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Empty State */}
      {!loading && paginatedLogs.length === 0 && (
        <div className="text-center py-12 bg-white dark:bg-slate-800 rounded-lg border-2 border-dashed border-slate-300 dark:border-slate-600">
          <p className="text-slate-600 dark:text-slate-400">No logs found</p>
        </div>
      )}

      {/* Pagination */}
      {!loading && filteredLogs.length > LOGS_PER_PAGE && (
        <div className="flex items-center justify-between bg-white dark:bg-slate-800 p-4 rounded-lg shadow">
          <div className="text-sm text-slate-600 dark:text-slate-400">
            Page {currentPage} of {totalPages} ({filteredLogs.length} total logs)
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
              disabled={currentPage === 1}
              className="px-4 py-2 bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 disabled:opacity-50 disabled:cursor-not-allowed text-slate-900 dark:text-white font-semibold rounded-lg transition"
            >
              ← Previous
            </button>

            {/* Page numbers */}
            <div className="flex gap-1">
              {Array.from({ length: totalPages }, (_, i) => i + 1)
                .filter(
                  (page) =>
                    page === 1 ||
                    page === totalPages ||
                    (page >= currentPage - 1 && page <= currentPage + 1)
                )
                .map((page, i, arr) => (
                  <div key={page}>
                    {i > 0 && arr[i - 1] !== page - 1 && (
                      <span className="px-2 py-2 text-slate-600 dark:text-slate-400">
                        ...
                      </span>
                    )}
                    <button
                      onClick={() => setCurrentPage(page)}
                      className={`px-4 py-2 rounded-lg transition font-semibold ${
                        page === currentPage
                          ? "bg-blue-600 text-white"
                          : "bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-900 dark:text-white"
                      }`}
                    >
                      {page}
                    </button>
                  </div>
                ))}
            </div>

            <button
              onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
              disabled={currentPage === totalPages}
              className="px-4 py-2 bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 disabled:opacity-50 disabled:cursor-not-allowed text-slate-900 dark:text-white font-semibold rounded-lg transition"
            >
              Next →
            </button>
          </div>
        </div>
      )}

      {/* Info Box */}
      <div className="p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
        <h3 className="font-semibold text-blue-900 dark:text-blue-300 mb-2">
          🔒 Privacy Notice
        </h3>
        <p className="text-sm text-blue-800 dark:text-blue-400">
          Logs are displayed with sensitive data masked. Full API keys and
          user details are never shown in this dashboard. All logs are encrypted
          at rest.
        </p>
      </div>
    </div>
  );
}
