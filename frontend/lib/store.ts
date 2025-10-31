import { create } from 'zustand';

interface AppState {
  selectedCompetitionId: string | null;
  selectedParticipantId: string | null;
  setSelectedCompetition: (id: string) => void;
  setSelectedParticipant: (id: string) => void;
}

export const useAppStore = create<AppState>((set) => ({
  selectedCompetitionId: null, // Auto-select first competition
  selectedParticipantId: null, // Auto-select first participant
  setSelectedCompetition: (id) => set({ selectedCompetitionId: id }),
  setSelectedParticipant: (id) => set({ selectedParticipantId: id }),
}));
