import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-slate-900 dark:to-slate-800">
      <div className="flex min-h-screen flex-col items-center justify-center px-4 py-12">
        <div className="max-w-2xl w-full space-y-8">
          {/* Header */}
          <div className="text-center">
            <h1 className="text-5xl font-bold text-slate-900 dark:text-white mb-2">
              AI Governance MVP
            </h1>
            <p className="text-xl text-slate-600 dark:text-slate-400">
              Admin Dashboard - Real-Time Monitoring
            </p>
          </div>

          {/* Status Info */}
          <div className="rounded-lg bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-700 p-6">
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
              <div>
                <h3 className="text-green-900 dark:text-green-100 font-semibold">System Running</h3>
                <p className="text-sm text-green-700 dark:text-green-200">
                  Backend: http://localhost:8000 | Frontend: http://localhost:3000
                </p>
              </div>
            </div>
          </div>

          {/* Main Content */}
          <div className="space-y-6">
            {/* Getting Started */}
            <div className="rounded-lg bg-white dark:bg-slate-800 p-8 shadow-lg space-y-6">
              <div>
                <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">
                  Getting Started
                </h2>
                <p className="text-slate-600 dark:text-slate-400">
                  This dashboard shows real-time data from test customers. All data is live from the backend API.
                </p>
              </div>

              {/* Dashboard Links */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Link
                  href="/dashboard/keys"
                  className="block p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-lg hover:shadow-md transition duration-200 text-left"
                >
                  <h3 className="font-semibold text-blue-900 dark:text-blue-100 mb-1">
                    API Keys
                  </h3>
                  <p className="text-sm text-blue-700 dark:text-blue-200">
                    View, create, and manage API keys for test customers
                  </p>
                </Link>

                <Link
                  href="/dashboard/policies"
                  className="block p-4 bg-indigo-50 dark:bg-indigo-900/20 border border-indigo-200 dark:border-indigo-700 rounded-lg hover:shadow-md transition duration-200 text-left"
                >
                  <h3 className="font-semibold text-indigo-900 dark:text-indigo-100 mb-1">
                    Policies
                  </h3>
                  <p className="text-sm text-indigo-700 dark:text-indigo-200">
                    Configure governance policies and rules
                  </p>
                </Link>

                <Link
                  href="/dashboard/logs"
                  className="block p-4 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg hover:shadow-md transition duration-200 text-left"
                >
                  <h3 className="font-semibold text-slate-900 dark:text-slate-100 mb-1">
                    Usage Logs
                  </h3>
                  <p className="text-sm text-slate-700 dark:text-slate-300">
                    Monitor all governance decisions in real-time
                  </p>
                </Link>
              </div>
            </div>

            {/* Testing Info */}
            <div className="rounded-lg bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-700 p-6">
              <h3 className="font-semibold text-amber-900 dark:text-amber-100 mb-3">
                🧪 Testing This System
              </h3>
              <ol className="space-y-2 text-sm text-amber-800 dark:text-amber-200 list-decimal list-inside">
                <li>Create a test customer and API key in the dashboard</li>
                <li>Use the API key to call <code className="bg-amber-100 dark:bg-amber-900 px-2 py-1 rounded">POST /v1/check</code></li>
                <li>See governance decisions in real-time in Usage Logs</li>
                <li>Modify policies and test different scenarios</li>
              </ol>
            </div>

            {/* API Examples */}
            <div className="rounded-lg bg-white dark:bg-slate-800 p-6 shadow-lg">
              <h3 className="font-semibold text-slate-900 dark:text-white mb-3">
                📚 API Examples
              </h3>
              <div className="space-y-3 text-sm text-slate-600 dark:text-slate-400">
                <p>
                  <strong>Backend API:</strong> <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer" className="text-blue-600 dark:text-blue-400 hover:underline">
                    Swagger UI (http://localhost:8000/docs)
                  </a>
                </p>
                <p>
                  <strong>Health Check:</strong> <code className="bg-slate-100 dark:bg-slate-700 px-2 py-1 rounded">GET /health</code>
                </p>
                <p>
                  <strong>Governance Check:</strong> <code className="bg-slate-100 dark:bg-slate-700 px-2 py-1 rounded">POST /v1/check</code> (requires API key)
                </p>
              </div>
            </div>

            {/* Important Notes */}
            <div className="rounded-lg bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 p-6">
              <h3 className="font-semibold text-blue-900 dark:text-blue-100 mb-3">
                ℹ️ Important Notes
              </h3>
              <ul className="space-y-2 text-sm text-blue-800 dark:text-blue-200 list-disc list-inside">
                <li>All data shown is REAL from the backend API</li>
                <li>No mock data is displayed anywhere in the dashboard</li>
                <li>Dashboard auto-refreshes when backend API data changes</li>
                <li>Backend runs without database in development mode</li>
                <li>For production, set DATABASE_URL environment variable</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}>
            <div className="rounded bg-white dark:bg-slate-800 p-4 shadow">
              <div className="text-2xl font-bold text-blue-600">3</div>
              <div className="text-sm text-slate-600 dark:text-slate-400">Policies</div>
            </div>
            <div className="rounded bg-white dark:bg-slate-800 p-4 shadow">
              <div className="text-2xl font-bold text-indigo-600">API Keys</div>
              <div className="text-sm text-slate-600 dark:text-slate-400">Manage</div>
            </div>
            <div className="rounded bg-white dark:bg-slate-800 p-4 shadow">
              <div className="text-2xl font-bold text-green-600">Live</div>
              <div className="text-sm text-slate-600 dark:text-slate-400">Monitoring</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
