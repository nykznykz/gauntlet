'use client';

import { useState, useEffect } from 'react';
import { ChevronDown } from 'lucide-react';
import { competitionApi, participantApi } from '@/lib/api';
import { useAppStore } from '@/lib/store';

interface Competition {
  id: string;
  name: string;
  status: string;
}

interface Participant {
  id: string;
  name: string;
  llm_model: string;
  status: string;
}

export function CompetitionSelector() {
  const [competitions, setCompetitions] = useState<Competition[]>([]);
  const [participants, setParticipants] = useState<Participant[]>([]);
  const [loading, setLoading] = useState(true);

  // Use global store instead of local state
  const selectedCompetition = useAppStore((state) => state.selectedCompetitionId);
  const selectedParticipant = useAppStore((state) => state.selectedParticipantId);
  const setSelectedCompetition = useAppStore((state) => state.setSelectedCompetition);
  const setSelectedParticipant = useAppStore((state) => state.setSelectedParticipant);

  useEffect(() => {
    async function fetchData() {
      setLoading(true);

      // Fetch competitions
      const compResponse = await competitionApi.list();
      if (compResponse.data?.competitions && compResponse.data.competitions.length > 0) {
        setCompetitions(compResponse.data.competitions);
        const firstComp = compResponse.data.competitions[0];

        // Only set if not already set
        if (!selectedCompetition) {
          setSelectedCompetition(firstComp.id);
        }

        // Fetch participants for the selected or first competition
        const competitionToFetch = selectedCompetition || firstComp.id;
        const partResponse = await participantApi.list(competitionToFetch);
        if (partResponse.data && Array.isArray(partResponse.data)) {
          setParticipants(partResponse.data);

          // Only set if not already set
          if (!selectedParticipant && partResponse.data.length > 0) {
            setSelectedParticipant(partResponse.data[0].id);
          }
        }
      }

      setLoading(false);
    }

    fetchData();
  }, []);

  // Fetch participants when competition changes
  useEffect(() => {
    if (!selectedCompetition) return;

    async function fetchParticipants(competitionId: string) {
      const response = await participantApi.list(competitionId);
      if (response.data && Array.isArray(response.data)) {
        setParticipants(response.data);
        if (response.data.length > 0) {
          setSelectedParticipant(response.data[0].id);
        }
      }
    }
    fetchParticipants(selectedCompetition);
  }, [selectedCompetition, setSelectedParticipant]);

  const currentCompetition = competitions.find(c => c.id === selectedCompetition);
  const currentParticipant = participants.find(p => p.id === selectedParticipant);

  if (loading || competitions.length === 0) {
    return null; // Hide selector if no competitions
  }

  return (
    <div className="bg-white dark:bg-zinc-900 border-b border-gray-200 dark:border-zinc-800">
      <div className="container mx-auto px-4 py-3">
        <div className="flex items-center gap-4">
          {/* Competition Selector */}
          <div className="flex items-center gap-2">
            <label className="text-sm font-medium text-gray-600 dark:text-gray-400">
              Competition:
            </label>
            <div className="relative">
              <select
                value={selectedCompetition || ''}
                onChange={(e) => setSelectedCompetition(e.target.value)}
                className="appearance-none bg-gray-50 dark:bg-zinc-800 border border-gray-300 dark:border-zinc-700 rounded-md px-3 py-1.5 pr-8 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {competitions.map((comp) => (
                  <option key={comp.id} value={comp.id}>
                    {comp.name}
                  </option>
                ))}
              </select>
              <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500 pointer-events-none" />
            </div>
            <span className={`text-xs px-2 py-0.5 rounded ${
              currentCompetition?.status === 'active'
                ? 'bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-400'
                : currentCompetition?.status === 'completed'
                ? 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-400'
                : 'bg-blue-100 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400'
            }`}>
              {currentCompetition?.status.toUpperCase()}
            </span>
          </div>

          {/* Divider */}
          <div className="h-6 w-px bg-gray-300 dark:bg-zinc-700" />

          {/* Participant Selector */}
          {participants.length > 0 && (
            <div className="flex items-center gap-2">
              <label className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Viewing:
              </label>
              <div className="relative">
                <select
                  value={selectedParticipant || ''}
                  onChange={(e) => setSelectedParticipant(e.target.value)}
                  className="appearance-none bg-gray-50 dark:bg-zinc-800 border border-gray-300 dark:border-zinc-700 rounded-md px-3 py-1.5 pr-8 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {participants.map((participant) => (
                    <option key={participant.id} value={participant.id}>
                      {participant.name}
                    </option>
                  ))}
                </select>
                <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500 pointer-events-none" />
              </div>
              {currentParticipant?.status === 'liquidated' && (
                <span className="text-xs px-2 py-0.5 rounded bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-400">
                  LIQUIDATED
                </span>
              )}
            </div>
          )}

          {/* Info Text */}
          {currentParticipant && (
            <div className="ml-auto text-sm text-gray-500 dark:text-gray-500">
              Tracking <span className="font-semibold text-foreground">{currentParticipant.name}</span>'s performance
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
