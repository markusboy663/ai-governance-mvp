"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import React from "react";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();

  const isActive = (href: string) => pathname === href;

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900">
      {/* Header */}
      <header className="border-b border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
              AI Governance
            </h1>
            <p className="text-sm text-slate-600 dark:text-slate-400">
              Admin Dashboard
            </p>
          </div>
          <Link
            href="/"
            className="text-sm px-4 py-2 text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white"
          >
            Back to Home
          </Link>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex space-x-8">
          <Link
            href="/dashboard/keys"
            className={`py-4 px-1 border-b-2 font-medium text-sm transition ${
              isActive("/dashboard/keys")
                ? "border-blue-500 text-blue-600 dark:text-blue-400"
                : "border-transparent text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white"
            }`}
          >
            API Keys
          </Link>
          <Link
            href="/dashboard/policies"
            className={`py-4 px-1 border-b-2 font-medium text-sm transition ${
              isActive("/dashboard/policies")
                ? "border-blue-500 text-blue-600 dark:text-blue-400"
                : "border-transparent text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white"
            }`}
          >
            Policies
          </Link>
          <Link
            href="/dashboard/logs"
            className={`py-4 px-1 border-b-2 font-medium text-sm transition ${
              isActive("/dashboard/logs")
                ? "border-blue-500 text-blue-600 dark:text-blue-400"
                : "border-transparent text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white"
            }`}
          >
            Usage Logs
          </Link>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>

      {/* Footer */}
      <footer className="mt-12 border-t border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 text-center text-sm text-slate-600 dark:text-slate-400">
          <p>AI Governance Dashboard © 2025</p>
        </div>
      </footer>
    </div>
  );
}
