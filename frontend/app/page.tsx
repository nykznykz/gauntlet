'use client';

import { EquityChart } from "@/components/dashboard/EquityChart";
import { CompetitionStats } from "@/components/dashboard/CompetitionStats";
import { Positions } from "@/components/dashboard/Positions";
import { Trades } from "@/components/dashboard/Trades";
import { InvocationLogs } from "@/components/dashboard/InvocationLogs";

export default function DashboardPage() {
  return (
    <div className="container mx-auto px-4 py-6 space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold mb-1">Portfolio Dashboard</h1>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Monitor real-time performance, positions, and trading activity
        </p>
      </div>

      {/* Competition Stats Header */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        <CompetitionStats />
      </div>

      {/* Equity Chart */}
      <div className="bg-white dark:bg-zinc-900 rounded-lg shadow-sm border border-gray-200 dark:border-zinc-800 p-6">
        <h2 className="text-xl font-semibold mb-4">Portfolio Equity Over Time</h2>
        <EquityChart />
      </div>

      {/* Positions and Trades */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-zinc-900 rounded-lg shadow-sm border border-gray-200 dark:border-zinc-800 p-6">
          <h2 className="text-xl font-semibold mb-4">Open Positions</h2>
          <Positions />
        </div>
        <div className="bg-white dark:bg-zinc-900 rounded-lg shadow-sm border border-gray-200 dark:border-zinc-800 p-6">
          <h2 className="text-xl font-semibold mb-4">Recent Trades</h2>
          <Trades />
        </div>
      </div>

      {/* LLM Invocation Logs */}
      <div className="bg-white dark:bg-zinc-900 rounded-lg shadow-sm border border-gray-200 dark:border-zinc-800 p-6">
        <h2 className="text-xl font-semibold mb-4">LLM Invocation Logs</h2>
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
          View the exact prompts sent to the LLM and their responses
        </p>
        <InvocationLogs />
      </div>
    </div>
  );
}
