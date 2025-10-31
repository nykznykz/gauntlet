'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { invocationApi } from '@/lib/api';
import { useAppStore } from '@/lib/store';
import { LLMInvocation, LLMInvocationList } from '@/types';
import { format } from 'date-fns';
import { CheckCircle, XCircle, AlertCircle, Clock, ChevronDown, ChevronUp } from 'lucide-react';

export function InvocationLogs() {
  const selectedParticipantId = useAppStore((state) => state.selectedParticipantId);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [expandedId, setExpandedId] = useState<string | null>(null);

  // Fetch invocation logs
  const { data, isLoading, error } = useQuery({
    queryKey: ['invocations', selectedParticipantId, statusFilter],
    queryFn: async () => {
      if (!selectedParticipantId) return null;
      const response = await invocationApi.list(selectedParticipantId, {
        limit: 50,
        status: statusFilter || undefined,
      });
      return response.data as LLMInvocationList;
    },
    enabled: !!selectedParticipantId,
    refetchInterval: 10000,
  });

  const toggleExpanded = (id: string) => {
    setExpandedId(expandedId === id ? null : id);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="w-4 h-4 text-green-600" />;
      case 'error':
        return <XCircle className="w-4 h-4 text-red-600" />;
      case 'invalid_response':
        return <AlertCircle className="w-4 h-4 text-yellow-600" />;
      case 'timeout':
        return <Clock className="w-4 h-4 text-orange-600" />;
      default:
        return <Clock className="w-4 h-4 text-gray-600" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success':
        return 'text-green-600';
      case 'error':
        return 'text-red-600';
      case 'invalid_response':
        return 'text-yellow-600';
      case 'timeout':
        return 'text-orange-600';
      default:
        return 'text-gray-600';
    }
  };

  const formatTime = (timestamp: string) => {
    try {
      return format(new Date(timestamp), 'MM/dd HH:mm:ss');
    } catch {
      return timestamp;
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="text-gray-500">Loading invocation logs...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="text-red-500">Error loading invocation logs</div>
      </div>
    );
  }

  if (!data || !data.invocations || data.invocations.length === 0) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="text-gray-500">No invocation logs yet</div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Filter Controls */}
      <div className="flex gap-2 items-center">
        <label className="text-sm text-gray-600 dark:text-gray-400">Filter by status:</label>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-3 py-1 border border-gray-300 dark:border-zinc-700 rounded-md bg-white dark:bg-zinc-800 text-sm"
        >
          <option value="">All</option>
          <option value="success">Success</option>
          <option value="error">Error</option>
          <option value="invalid_response">Invalid Response</option>
          <option value="timeout">Timeout</option>
        </select>
        <div className="text-sm text-gray-500 ml-auto">
          Total: {data.total} invocations
        </div>
      </div>

      {/* Invocation List */}
      <div className="space-y-2">
        {data.invocations.map((invocation) => (
          <div
            key={invocation.id}
            className="border border-gray-200 dark:border-zinc-800 rounded-lg overflow-hidden"
          >
            {/* Summary Row */}
            <button
              onClick={() => toggleExpanded(invocation.id)}
              className="w-full px-4 py-3 flex items-center gap-4 hover:bg-gray-50 dark:hover:bg-zinc-800/50 transition-colors"
            >
              <div className="flex items-center gap-2">
                {getStatusIcon(invocation.status)}
                <span className={`text-sm font-medium ${getStatusColor(invocation.status)}`}>
                  {invocation.status.toUpperCase()}
                </span>
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                {formatTime(invocation.invocation_time)}
              </div>
              {invocation.response_time_ms && (
                <div className="text-sm text-gray-500">
                  {invocation.response_time_ms}ms
                </div>
              )}
              {invocation.prompt_tokens && invocation.response_tokens && (
                <div className="text-sm text-gray-500">
                  Tokens: {invocation.prompt_tokens} / {invocation.response_tokens}
                </div>
              )}
              <div className="ml-auto">
                {expandedId === invocation.id ? (
                  <ChevronUp className="w-4 h-4" />
                ) : (
                  <ChevronDown className="w-4 h-4" />
                )}
              </div>
            </button>

            {/* Expanded Details */}
            {expandedId === invocation.id && (
              <div className="border-t border-gray-200 dark:border-zinc-800 p-4 space-y-4 bg-gray-50 dark:bg-zinc-900/50">
                {/* Prompt */}
                <div>
                  <h4 className="text-sm font-semibold mb-2 text-gray-700 dark:text-gray-300">
                    Prompt Sent to LLM:
                  </h4>
                  <pre className="bg-white dark:bg-zinc-800 p-3 rounded-md text-xs overflow-x-auto whitespace-pre-wrap border border-gray-200 dark:border-zinc-700">
                    {invocation.prompt_text}
                  </pre>
                </div>

                {/* Response */}
                {invocation.response_text && (
                  <div>
                    <h4 className="text-sm font-semibold mb-2 text-gray-700 dark:text-gray-300">
                      LLM Response:
                    </h4>
                    <pre className="bg-white dark:bg-zinc-800 p-3 rounded-md text-xs overflow-x-auto whitespace-pre-wrap border border-gray-200 dark:border-zinc-700">
                      {invocation.response_text}
                    </pre>
                  </div>
                )}

                {/* Parsed Decision */}
                {invocation.parsed_decision && (
                  <div>
                    <h4 className="text-sm font-semibold mb-2 text-gray-700 dark:text-gray-300">
                      Parsed Trading Decision:
                    </h4>
                    <pre className="bg-white dark:bg-zinc-800 p-3 rounded-md text-xs overflow-x-auto whitespace-pre-wrap border border-gray-200 dark:border-zinc-700">
                      {JSON.stringify(invocation.parsed_decision, null, 2)}
                    </pre>
                  </div>
                )}

                {/* Error Message */}
                {invocation.error_message && (
                  <div>
                    <h4 className="text-sm font-semibold mb-2 text-red-600 dark:text-red-400">
                      Error:
                    </h4>
                    <div className="bg-red-50 dark:bg-red-900/20 p-3 rounded-md text-sm text-red-700 dark:text-red-300 border border-red-200 dark:border-red-800">
                      {invocation.error_message}
                    </div>
                  </div>
                )}

                {/* Metadata */}
                <div className="grid grid-cols-2 gap-4 pt-2 border-t border-gray-200 dark:border-zinc-800">
                  <div>
                    <span className="text-xs text-gray-500">Invocation ID:</span>
                    <div className="text-xs font-mono mt-1">{invocation.id}</div>
                  </div>
                  {invocation.estimated_cost && (
                    <div>
                      <span className="text-xs text-gray-500">Estimated Cost:</span>
                      <div className="text-xs font-mono mt-1">${invocation.estimated_cost}</div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Pagination hint */}
      {data.total > data.limit && (
        <div className="text-center text-sm text-gray-500 pt-4">
          Showing {data.invocations.length} of {data.total} invocations
        </div>
      )}
    </div>
  );
}
