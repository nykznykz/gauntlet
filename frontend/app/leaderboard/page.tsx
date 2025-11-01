'use client';

import { LeaderboardTable } from "@/components/leaderboard/LeaderboardTable";
import { PerformanceCharts } from "@/components/leaderboard/PerformanceCharts";

export default function LeaderboardPage() {
  return (
    <div className="container mx-auto px-4 py-6 space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold mb-2">Leaderboard</h1>
          <p className="text-gray-600 dark:text-gray-400">
            Competition rankings and performance statistics
          </p>
        </div>
      </div>

      {/* Performance Charts */}
      <div className="bg-white dark:bg-zinc-900 rounded-lg shadow-sm border border-gray-200 dark:border-zinc-800 p-6">
        <h2 className="text-xl font-semibold mb-4">Performance Comparison</h2>
        <PerformanceCharts />
      </div>

      {/* Leaderboard Table */}
      <div className="bg-white dark:bg-zinc-900 rounded-lg shadow-sm border border-gray-200 dark:border-zinc-800 p-6">
        <h2 className="text-xl font-semibold mb-4">Rankings</h2>
        <LeaderboardTable />
      </div>
    </div>
  );
}
