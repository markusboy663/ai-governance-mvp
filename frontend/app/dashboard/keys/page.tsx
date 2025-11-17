"use client";

import { useState, useEffect } from "react";

interface ApiKey {
  id: string;
  name: string;
  key_id: string;
  created_at: string;
  last_used: string | null;
  requests_count: number;
}

export default function KeysPage() {
  const [keys, setKeys] = useState<ApiKey[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [newKeyName, setNewKeyName] = useState("");
  const [showNewKeyDialog, setShowNewKeyDialog] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  // Fetch keys on mount
  useEffect(() => {
    fetchKeys();
  }, []);

  const fetchKeys = async () => {
    try {
      setLoading(true);
      // Fetch real data from backend API
      const response = await fetch("http://localhost:8000/api/admin/keys", {
        headers: {
          "Authorization": "Bearer test_admin_key",
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        // If backend not configured, show empty state
        if (response.status === 401 || response.status === 404) {
          setKeys([]);
          setError("Backend not configured. Create first test customer to see data.");
        } else {
          throw new Error(`API error: ${response.status}`);
        }
      } else {
        const data = await response.json();
        setKeys(data || []);
        setError(null);
      }
    } catch (err) {
      setError("Failed to load API keys. Ensure backend is running on port 8000.");
      console.error(err);
      setKeys([]);
    } finally {
      setLoading(false);
    }
  };

  const handleCopyKey = (keyId: string) => {
    navigator.clipboard.writeText(keyId);
    setCopiedId(keyId);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleRotateKey = async (keyId: string) => {
    if (
      confirm(
        "Rotating this key will generate a new key. The old key will be invalidated. Continue?"
      )
    ) {
      try {
        // In real app: POST /api/keys/{keyId}/rotate
        alert("Key rotated successfully. New key: key_rotated_" + keyId);
        fetchKeys();
      } catch (err) {
        setError("Failed to rotate key");
      }
    }
  };

  const handleDeleteKey = async (keyId: string) => {
    if (confirm("Are you sure you want to delete this API key?")) {
      try {
        // In real app: DELETE /api/keys/{keyId}
        setKeys(keys.filter((k) => k.id !== keyId));
      } catch (err) {
        setError("Failed to delete key");
      }
    }
  };

  const handleCreateKey = async () => {
    if (!newKeyName.trim()) {
      setError("Key name is required");
      return;
    }

    try {
      // In real app: POST /api/keys
      const newKey: ApiKey = {
        id: "key_" + Date.now(),
        name: newKeyName,
        key_id: "550e8400-e29b-41d4-a716-" + Math.random().toString().slice(2, 12),
        created_at: new Date().toISOString(),
        last_used: null,
        requests_count: 0,
      };
      setKeys([...keys, newKey]);
      setNewKeyName("");
      setShowNewKeyDialog(false);
    } catch (err) {
      setError("Failed to create key");
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-slate-900 dark:text-white">
            API Keys
          </h2>
          <p className="mt-1 text-slate-600 dark:text-slate-400">
            Manage your API keys for authentication
          </p>
        </div>
        <button
          onClick={() => setShowNewKeyDialog(true)}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition"
        >
          + Create New Key
        </button>
      </div>

      {/* Error Message */}
      {error && (
        <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-300 rounded-lg">
          {error}
        </div>
      )}

      {/* Create Key Dialog */}
      {showNewKeyDialog && (
        <div className="p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg space-y-3">
          <h3 className="font-semibold text-slate-900 dark:text-white">
            Create New API Key
          </h3>
          <input
            type="text"
            placeholder="Key name (e.g., 'Production Key')"
            value={newKeyName}
            onChange={(e) => setNewKeyName(e.target.value)}
            className="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white"
          />
          <div className="flex gap-2">
            <button
              onClick={handleCreateKey}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition"
            >
              Create
            </button>
            <button
              onClick={() => {
                setShowNewKeyDialog(false);
                setNewKeyName("");
              }}
              className="px-4 py-2 bg-slate-300 dark:bg-slate-600 hover:bg-slate-400 dark:hover:bg-slate-500 text-slate-900 dark:text-white font-semibold rounded-lg transition"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="text-center py-8">
          <div className="animate-spin inline-block w-8 h-8 border-4 border-slate-200 dark:border-slate-700 border-t-blue-600 rounded-full"></div>
        </div>
      )}

      {/* Keys Table */}
      {!loading && keys.length > 0 && (
        <div className="bg-white dark:bg-slate-800 rounded-lg shadow overflow-hidden">
          <table className="w-full">
            <thead className="bg-slate-50 dark:bg-slate-700 border-b border-slate-200 dark:border-slate-600">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 dark:text-slate-300 uppercase tracking-wider">
                  Name
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 dark:text-slate-300 uppercase tracking-wider">
                  Key ID
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 dark:text-slate-300 uppercase tracking-wider">
                  Created
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 dark:text-slate-300 uppercase tracking-wider">
                  Last Used
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 dark:text-slate-300 uppercase tracking-wider">
                  Requests
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-700 dark:text-slate-300 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 dark:divide-slate-700">
              {keys.map((key) => (
                <tr
                  key={key.id}
                  className="hover:bg-slate-50 dark:hover:bg-slate-700 transition"
                >
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-900 dark:text-white">
                    {key.name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <div className="flex items-center gap-2">
                      <code className="text-xs bg-slate-100 dark:bg-slate-700 px-2 py-1 rounded text-slate-600 dark:text-slate-300 font-mono">
                        {key.key_id.substring(0, 12)}...
                      </code>
                      <button
                        onClick={() => handleCopyKey(key.key_id)}
                        className="text-xs px-2 py-1 bg-slate-200 dark:bg-slate-600 hover:bg-slate-300 dark:hover:bg-slate-500 text-slate-700 dark:text-slate-300 rounded transition"
                        title="Copy full key ID"
                      >
                        {copiedId === key.key_id ? "✓" : "📋"}
                      </button>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600 dark:text-slate-400">
                    {new Date(key.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600 dark:text-slate-400">
                    {key.last_used
                      ? new Date(key.last_used).toLocaleDateString()
                      : "Never"}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-900 dark:text-white">
                    {key.requests_count.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm space-x-2">
                    <button
                      onClick={() => handleRotateKey(key.id)}
                      className="px-2 py-1 bg-yellow-100 dark:bg-yellow-900/30 hover:bg-yellow-200 dark:hover:bg-yellow-900/50 text-yellow-700 dark:text-yellow-300 rounded transition text-xs font-semibold"
                    >
                      Rotate
                    </button>
                    <button
                      onClick={() => handleDeleteKey(key.id)}
                      className="px-2 py-1 bg-red-100 dark:bg-red-900/30 hover:bg-red-200 dark:hover:bg-red-900/50 text-red-700 dark:text-red-300 rounded transition text-xs font-semibold"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Empty State */}
      {!loading && keys.length === 0 && (
        <div className="text-center py-12 bg-white dark:bg-slate-800 rounded-lg border-2 border-dashed border-slate-300 dark:border-slate-600">
          <p className="text-slate-600 dark:text-slate-400">No API keys yet</p>
          <button
            onClick={() => setShowNewKeyDialog(true)}
            className="mt-4 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition"
          >
            Create Your First Key
          </button>
        </div>
      )}

      {/* Info Box */}
      <div className="p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
        <h3 className="font-semibold text-blue-900 dark:text-blue-300 mb-2">
          💡 Security Tips
        </h3>
        <ul className="text-sm text-blue-800 dark:text-blue-400 space-y-1">
          <li>• Store your API keys securely and never share them</li>
          <li>• Rotate keys regularly for better security</li>
          <li>• Use different keys for different applications</li>
          <li>• Delete unused keys immediately</li>
        </ul>
      </div>
    </div>
  );
}
