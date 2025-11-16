import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-slate-900 dark:to-slate-800">
      <div className="flex min-h-screen flex-col items-center justify-center px-4 py-12">
        <div className="max-w-md w-full space-y-8 text-center">
          {/* Header */}
          <div>
            <h1 className="text-4xl font-bold text-slate-900 dark:text-white">
              AI Governance
            </h1>
            <p className="mt-2 text-lg text-slate-600 dark:text-slate-400">
              Admin Dashboard
            </p>
          </div>

          {/* Welcome Message */}
          <div className="rounded-lg bg-white dark:bg-slate-800 p-6 shadow-lg space-y-4">
            <p className="text-slate-700 dark:text-slate-300">
              Welcome to the AI Governance admin dashboard. Manage your API keys, configure policies, and monitor usage.
            </p>

            {/* CTA Buttons */}
            <div className="space-y-3 pt-4">
              <Link
                href="/dashboard/keys"
                className="block px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition duration-200"
              >
                View API Keys
              </Link>

              <Link
                href="/dashboard/policies"
                className="block px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-lg transition duration-200"
              >
                Manage Policies
              </Link>

              <Link
                href="/dashboard/logs"
                className="block px-6 py-3 bg-slate-600 hover:bg-slate-700 text-white font-semibold rounded-lg transition duration-200"
              >
                View Usage Logs
              </Link>
            </div>
          </div>

          {/* Quick Info */}
          <div className="grid grid-cols-3 gap-4 pt-4">
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
