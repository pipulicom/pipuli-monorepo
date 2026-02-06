import { create } from 'zustand';

export type LogType = 'request' | 'response' | 'error' | 'info';

export interface LogEntry {
    id: string;
    timestamp: number;
    type: LogType;
    method?: string;
    url?: string;
    status?: number;
    duration?: number;
    data?: any;
    message?: string;
}

interface DebugStore {
    isEnabled: boolean;
    logs: LogEntry[];
    togglePanel: () => void;
    addLog: (log: Omit<LogEntry, 'id' | 'timestamp'>) => void;
    clearLogs: () => void;
}

export const useDebugStore = create<DebugStore>((set) => ({
    isEnabled: false,
    logs: [],
    togglePanel: () => set((state) => ({ isEnabled: !state.isEnabled })),
    addLog: (log) =>
        set((state) => ({
            logs: [
                {
                    ...log,
                    id: Math.random().toString(36).substring(7),
                    timestamp: Date.now(),
                },
                ...state.logs,
            ].slice(0, 100), // Keep last 100 logs
        })),
    clearLogs: () => set({ logs: [] }),
}));
