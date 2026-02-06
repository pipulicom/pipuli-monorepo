"use client";

import { useState, useEffect } from 'react';
import { useDebugStore, LogEntry } from '../../store/debugStore';
import { clsx } from "clsx";

export function DebugPanel() {
    const [mounted, setMounted] = useState(false);
    const { isEnabled, togglePanel, logs, clearLogs } = useDebugStore();
    const [activeTab, setActiveTab] = useState<'network' | 'state' | 'system'>('network');
    const [selectedLog, setSelectedLog] = useState<LogEntry | null>(null);

    useEffect(() => {
        // Only mount if the env var is set
        if (process.env.NEXT_PUBLIC_DEBUG_MODE === 'true') {
            setMounted(true);
        }
    }, []);

    if (!mounted) return null;

    if (!isEnabled) {
        return (
            <button
                onClick={togglePanel}
                className="fixed bottom-4 right-4 z-50 p-3 bg-slate-900 text-white rounded-full shadow-lg hover:bg-slate-800 transition-all border border-slate-700"
                title="Open Debug Panel"
            >
                🐞
            </button>
        );
    }

    return (
        <div className="fixed bottom-0 left-0 right-0 h-[60vh] bg-slate-950 text-slate-200 z-50 shadow-2xl flex flex-col font-mono text-sm border-t border-slate-800">
            {/* Header */}
            <div className="flex items-center justify-between px-4 py-2 bg-slate-900 border-b border-slate-800">
                <div className="flex space-x-4">
                    <span className="font-bold text-green-400">⚡ Debug Panel</span>
                    <div className="flex space-x-1">
                        <TabButton active={activeTab === 'network'} onClick={() => setActiveTab('network')}>Network ({logs.length})</TabButton>
                        <TabButton active={activeTab === 'state'} onClick={() => setActiveTab('state')}>State</TabButton>
                        <TabButton active={activeTab === 'system'} onClick={() => setActiveTab('system')}>System</TabButton>
                    </div>
                </div>
                <div className="flex items-center space-x-2">
                    <button onClick={clearLogs} className="px-2 py-1 text-xs hover:bg-slate-800 rounded text-slate-400 hover:text-white">Clear</button>
                    <button onClick={togglePanel} className="px-2 py-1 text-xs hover:bg-slate-800 rounded text-slate-400 hover:text-white">✕</button>
                </div>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-hidden flex">
                {activeTab === 'network' && (
                    <div className="flex-1 flex h-full">
                        {/* Log List */}
                        <div className={clsx("flex-1 overflow-y-auto border-r border-slate-800", selectedLog ? "w-1/2" : "w-full")}>
                            <table className="w-full text-left border-collapse">
                                <thead className="bg-slate-900 sticky top-0 text-slate-400 text-xs">
                                    <tr>
                                        <th className="p-2">Time</th>
                                        <th className="p-2">Method</th>
                                        <th className="p-2">Status</th>
                                        <th className="p-2">URL</th>
                                        <th className="p-2">Dur</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {logs.map((log) => (
                                        <tr
                                            key={log.id}
                                            onClick={() => setSelectedLog(log)}
                                            className={clsx(
                                                "cursor-pointer hover:bg-slate-900 border-b border-slate-900/50 text-xs",
                                                selectedLog?.id === log.id ? "bg-slate-800" : ""
                                            )}
                                        >
                                            <td className="p-2 whitespace-nowrap text-slate-500">{new Date(log.timestamp).toLocaleTimeString()}</td>
                                            <td className="p-2 font-bold">
                                                <MethodBadge method={log.method} />
                                            </td>
                                            <td className={clsx("p-2", getStatusColor(log.status))}>{log.status}</td>
                                            <td className="p-2 truncate max-w-[200px]" title={log.url}>{log.url?.replace(process.env.NEXT_PUBLIC_API_URL || '', '')}</td>
                                            <td className="p-2 text-slate-500">{log.duration ? `${log.duration}ms` : '-'}</td>
                                        </tr>
                                    ))}
                                    {logs.length === 0 && (
                                        <tr>
                                            <td colSpan={5} className="p-8 text-center text-slate-600">No requests recorded</td>
                                        </tr>
                                    )}
                                </tbody>
                            </table>
                        </div>

                        {/* Log Detail */}
                        {selectedLog && (
                            <div className="flex-1 w-1/2 h-full overflow-y-auto bg-slate-900 p-4 border-l border-slate-800">
                                <div className="flex justify-between items-start mb-4">
                                    <h3 className="text-lg font-bold text-slate-200">Request Details</h3>
                                    <button onClick={() => setSelectedLog(null)} className="text-slate-500 hover:text-white">✕</button>
                                </div>

                                <div className="space-y-4">
                                    <div>
                                        <label className="text-xs text-slate-500 uppercase tracking-wider">URL</label>
                                        <div className="break-all text-blue-300">{selectedLog.url}</div>
                                    </div>

                                    {selectedLog.data && (
                                        <div>
                                            <label className="text-xs text-slate-500 uppercase tracking-wider">Payload</label>
                                            <pre className="mt-1 p-2 bg-black rounded text-green-300 text-xs overflow-x-auto">
                                                {JSON.stringify(selectedLog.data, null, 2)}
                                            </pre>
                                        </div>
                                    )}

                                    {selectedLog.message && (
                                        <div>
                                            <label className="text-xs text-slate-500 uppercase tracking-wider">Message</label>
                                            <div className="text-red-400">{selectedLog.message}</div>
                                        </div>
                                    )}
                                </div>
                            </div>
                        )}
                    </div>
                )}

                {activeTab === 'state' && (
                    <div className="p-4 w-full h-full overflow-y-auto">
                        <div className="mb-6">
                            <h3 className="font-bold text-slate-400 mb-2">Session (Cookies/Storage)</h3>
                            <div className="p-4 bg-slate-900 rounded text-xs">
                                {/* Placeholder for session reading logic */}
                                <p className="text-slate-500 italic">Session inspection to be implemented.</p>
                            </div>
                        </div>
                    </div>
                )}

                {activeTab === 'system' && (
                    <div className="p-4 w-full h-full overflow-y-auto">
                        <h3 className="font-bold text-slate-400 mb-2">Environment</h3>
                        <pre className="p-4 bg-slate-900 rounded text-xs text-blue-300">
                            {JSON.stringify({
                                NODE_ENV: process.env.NODE_ENV,
                                DEBUG_MODE: process.env.NEXT_PUBLIC_DEBUG_MODE,
                                API_URL: process.env.NEXT_PUBLIC_API_URL,
                                VERSION: '1.0.25' // Read from context/config ideally
                            }, null, 2)}
                        </pre>
                    </div>
                )}
            </div>
        </div>
    );
}

function TabButton({ children, active, onClick }: { children: React.ReactNode, active: boolean, onClick: () => void }) {
    return (
        <button
            onClick={onClick}
            className={clsx(
                "px-3 py-1 rounded-t text-xs font-semibold transition-colors",
                active ? "bg-slate-800 text-white" : "text-slate-500 hover:text-slate-300 hover:bg-slate-800/50"
            )}
        >
            {children}
        </button>
    );
}

function MethodBadge({ method }: { method?: string }) {
    if (!method) return null;
    const colors: Record<string, string> = {
        GET: 'text-blue-400',
        POST: 'text-green-400',
        PUT: 'text-orange-400',
        DELETE: 'text-red-400',
    };
    return <span className={colors[method] || 'text-slate-400'}>{method}</span>;
}

function getStatusColor(status?: number) {
    if (!status) return 'text-slate-500';
    if (status >= 200 && status < 300) return 'text-green-400';
    if (status >= 400 && status < 500) return 'text-orange-400';
    if (status >= 500) return 'text-red-400';
    return 'text-slate-400';
}
