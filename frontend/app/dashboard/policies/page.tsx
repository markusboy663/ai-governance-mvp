"use client";

import { useState, useEffect } from "react";

interface Policy {
  id: string;
  name: string;
  description: string;
  enabled: boolean;
  violations_count: number;
}

export default function PoliciesPage() {
  const [policies, setPolicies] = useState<Policy[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchPolicies();
  }, []);

  const fetchPolicies = async () => {
    try {
      setLoading(true);
      // Fetch real data from backend API
      const response = await fetch("http://localhost:8000/api/admin/policies", {
        headers: {
          "Authorization": "Bearer test_admin_key",
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        // If backend not configured, show empty state
        if (response.status === 401 || response.status === 404) {
          setPolicies([]);
          setError("Backend not configured. Create policies to see data.");
        } else {
          throw new Error(`API error: ${response.status}`);
        }
      } else {
        const data = await response.json();
        setPolicies(data || []);
        setError(null);
      }
    } catch (err) {
      setError("Failed to load policies. Ensure backend is running on port 8000.");
      console.error(err);
      setPolicies([]);
    } finally {
      setLoading(false);
    }
  };

  const togglePolicy = async (policyId: string) => {
    try {
      // In real app: PATCH /api/policies/{policyId}
      setPolicies(
        policies.map((p) =>
          p.id === policyId ? { ...p, enabled: !p.enabled } : p
        )
      );
    } catch (err) {
      setError("Failed to update policy");
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-3xl font-bold text-slate-900 dark:text-white">
          Governance Policies
        </h2>
        <p className="mt-1 text-slate-600 dark:text-slate-400">
          Enable or disable governance policies to control AI model behavior
        </p>
      </div>

      {/* Error Message */}
      {error && (
        <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-300 rounded-lg">
          {error}
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="text-center py-8">
          <div className="animate-spin inline-block w-8 h-8 border-4 border-slate-200 dark:border-slate-700 border-t-blue-600 rounded-full"></div>
        </div>
      )}

      {/* Policies Grid */}
      {!loading && (
        <div className="space-y-4">
          {policies.map((policy) => (
            <div
              key={policy.id}
              className={`p-6 rounded-lg border-2 transition ${
                policy.enabled
                  ? "bg-white dark:bg-slate-800 border-green-200 dark:border-green-800"
                  : "bg-slate-50 dark:bg-slate-900 border-slate-200 dark:border-slate-700"
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3">
                    <h3 className="text-lg font-semibold text-slate-900 dark:text-white">
                      {policy.name}
                    </h3>
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-semibold ${
                        policy.enabled
                          ? "bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300"
                          : "bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300"
                      }`}
                    >
                      {policy.enabled ? "✓ Enabled" : "⊗ Disabled"}
                    </span>
                  </div>
                  <p className="mt-2 text-slate-600 dark:text-slate-400">
                    {policy.description}
                  </p>

                  {/* Stats */}
                  <div className="mt-4 flex items-center gap-6">
                    <div>
                      <div className="text-2xl font-bold text-red-600 dark:text-red-400">
                        {policy.violations_count}
                      </div>
                      <div className="text-sm text-slate-600 dark:text-slate-400">
                        Violations this week
                      </div>
                    </div>
                  </div>
                </div>

                {/* Toggle */}
                <label className="relative inline-flex items-center cursor-pointer ml-4">
                  <input
                    type="checkbox"
                    checked={policy.enabled}
                    onChange={() => togglePolicy(policy.id)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-slate-300 dark:bg-slate-600 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-green-600"></div>
                </label>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Info Box */}
      <div className="p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
        <h3 className="font-semibold text-blue-900 dark:text-blue-300 mb-2">
          📋 Policy Details
        </h3>
        <div className="text-sm text-blue-800 dark:text-blue-400 space-y-2">
          <p>
            <strong>PII Detection:</strong> Identifies and blocks requests
            containing sensitive personal data
          </p>
          <p>
            <strong>External Model Detection:</strong> Prevents unauthorized
            external AI model usage
          </p>
          <p>
            <strong>Rate Limiting:</strong> Enforces per-key request rate limits
            to prevent abuse
          </p>
        </div>
      </div>

      {/* Warning Box */}
      <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
        <h3 className="font-semibold text-yellow-900 dark:text-yellow-300 mb-2">
          ⚠️ Important
        </h3>
        <p className="text-sm text-yellow-800 dark:text-yellow-400">
          Disabling policies will allow requests that would normally be blocked.
          Use with caution and only in development environments.
        </p>
      </div>
    </div>
  );
}
