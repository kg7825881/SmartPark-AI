'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';

interface LogEntry {
  id: string;
  timestamp: string;
  message: string;
  confidence: number;
}

export default function LiveMonitoring() {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [cameraErrors, setCameraErrors] = useState<Record<number, boolean>>({});

  // Fetch real-time logs from the running camera stream backend
  useEffect(() => {
    async function fetchAlerts() {
      try {
        const res = await fetch('http://localhost:8000/api/live-alerts');
        if (res.ok) {
          const data = await res.json();
          if (data.logs) {
            setLogs((prev) => {
              if (JSON.stringify(prev) !== JSON.stringify(data.logs)) {
                return data.logs;
              }
              return prev;
            });
          }
        }
      } catch (err) {
        console.error("Error fetching live alerts:", err);
      }
    }
    
    fetchAlerts();
    const interval = setInterval(fetchAlerts, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#0a0c10]">

      {/* COLUMN 1: LEFT SIDEBAR NAVIGATION */}
      <aside className="w-64 bg-[#11141b] border-r border-gray-800 flex flex-col p-5 space-y-6 shrink-0">
        <div className="flex items-center space-x-3">
          <div className="h-8 w-8 bg-purple-600 rounded-lg flex items-center justify-center font-bold text-white">S</div>
          <span className="text-xl font-bold tracking-tight text-white">SmartPark AI</span>
        </div>
        <nav className="flex-1 space-y-2 text-sm font-medium">
          <Link href="/">
            <div className="text-gray-400 hover:text-white p-3 rounded-lg cursor-pointer transition">📊 Overview</div>
          </Link>
          <Link href="/monitoring">
            <div className="bg-purple-600/10 text-purple-400 p-3 rounded-lg cursor-pointer transition">📹 Live Monitoring</div>
          </Link>
          <Link href="/map">
            <div className="text-gray-400 hover:text-white p-3 rounded-lg cursor-pointer transition">⚠️ Violations Map</div>
          </Link>
        </nav>
      </aside>

      {/* DASHBOARD CONTAINER BODY */}
      <main className="flex-1 flex flex-col overflow-y-auto p-6 space-y-6">
        <header className="flex justify-between items-center pb-2 border-b border-gray-800">
          <h1 className="text-2xl font-bold text-white">Live Edge-Inference Feeds</h1>
          <div className="flex items-center space-x-2">
            <span className="relative flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
            </span>
            <span className="text-sm font-mono text-green-400">System Online</span>
          </div>
        </header>

        <section className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-full pb-4">

          {/* CAMERA GRID (Takes up 2/3 of the screen) */}
          <div className="lg:col-span-2 grid grid-cols-2 gap-4">
            {[1, 2, 3, 4].map((cam) => (
              <div key={cam} className="bg-[#11141b] border border-gray-800 rounded-xl overflow-hidden relative flex flex-col">
                <div className="absolute top-3 left-3 flex items-center space-x-2 z-10 bg-black/50 px-2 py-1 rounded">
                  <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></div>
                  <span className="text-[10px] font-mono text-white tracking-widest">CAM 0{cam} - REC</span>
                </div>
                {/* Real Live Processed Camera Feed */}
                <div className="flex-1 bg-black flex items-center justify-center relative overflow-hidden">
                  {cameraErrors[cam] ? (
                    <div className="absolute inset-0 bg-[#0d0f12] flex flex-col items-center justify-center space-y-2 p-6 text-center z-20">
                      <span className="relative flex h-3 w-3">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-500 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-3 w-3 bg-red-600"></span>
                      </span>
                      <span className="text-[11px] font-mono text-red-500 tracking-wider font-bold">CCTV FEED DISCONNECTED</span>
                      <span className="text-[9px] font-mono text-gray-500">ATTEMPTING AUTOMATIC RECONNECT...</span>
                    </div>
                  ) : (
                    <img 
                      src={`http://localhost:8000/api/video-feed/${cam}`} 
                      alt={`CAM 0${cam}`}
                      className="w-full h-full object-cover"
                      onError={() => {
                        setCameraErrors(prev => ({ ...prev, [cam]: true }));
                        setTimeout(() => {
                          setCameraErrors(prev => ({ ...prev, [cam]: false }));
                        }, 4000);
                      }}
                    />
                  )}
                  <div className="absolute inset-0 pointer-events-none bg-gradient-to-b from-transparent via-purple-500/5 to-transparent opacity-30"></div>
                </div>
              </div>
            ))}
          </div>

          {/* AI INFERENCE TERMINAL (Takes up 1/3 of the screen) */}
          <div className="bg-[#11141b] border border-gray-800 rounded-xl p-5 flex flex-col h-full overflow-hidden">
            <h2 className="text-sm font-bold tracking-wide text-gray-200 mb-4 border-b border-gray-800 pb-2">
              AI INFERENCE LOG
            </h2>
            <div className="flex-1 overflow-y-auto font-mono text-xs space-y-3 pr-2 custom-scrollbar">
              {logs.length === 0 ? (
                <div className="text-gray-500 text-center py-10">[ Waiting for live alerts... ]</div>
              ) : (
                logs.map((log) => (
                  <div key={log.id} className="p-3 bg-[#161a23] rounded border border-gray-800/50 hover:border-purple-500/30 transition-colors animate-fade-in-down">
                    <div className="flex justify-between text-gray-500 mb-1">
                      <span>{log.timestamp}</span>
                      <span className={log.confidence > 95 ? 'text-green-400' : 'text-orange-400'}>
                        {log.confidence}% CONF
                      </span>
                    </div>
                    <p className="text-gray-300 leading-relaxed">{log.message}</p>
                  </div>
                ))
              )}
            </div>
          </div>

        </section>
      </main>
    </div>
  );
}