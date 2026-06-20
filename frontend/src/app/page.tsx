'use client';

import React, { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import Link from 'next/link';

// --- CLEAN DYNAMIC IMPORT (Safely loads the isolated map) ---
const MapComponent = dynamic(() => import('../components/Map'), { ssr: false });

interface MetricSummary {
  total_violations: string;
  active_hotspots: string;
  avg_congestion: string;
  enforcement_score: string;
}

interface RecommendationItem {
  location: string;
  congestion_score: number;
  priority_score: number;
  status: string;
  latitude: number;
  longitude: number;
}

// Analytics Trend Time-Series Dataset for the Recharts component
const hourlyData = [
  { hour: '08:00', violations: 140 },
  { hour: '12:00', violations: 420 },
  { hour: '17:00', violations: 890 }, // Evening peak traffic crunch spike
  { hour: '21:00', violations: 310 }
];

export default function Dashboard() {
  const [metrics, setMetrics] = useState<MetricSummary | null>(null);
  const [recommendations, setRecommendations] = useState<RecommendationItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchDashboardData() {
      try {
        const response = await fetch('https://smartpark-backend-vtrh.onrender.com/api/dashboard-summary');
        const data = await response.json();
        if (!data.error) {
          setMetrics(data.metrics);
          setRecommendations(data.recommendations);
        }
      } catch (error) {
        console.error("Failed to connect to backend engine server:", error);
      } finally {
        setLoading(false);
      }
    }

    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 10000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="h-screen w-screen bg-[#0a0c10] flex items-center justify-center text-gray-400 font-mono animate-pulse">
        🔄 Initializing SmartPark Data Engine & Parsing Historical Records...
      </div>
    );
  }

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
            <div className="bg-purple-600/10 text-purple-400 p-3 rounded-lg cursor-pointer">📊 Overview</div>
          </Link>
          <Link href="/monitoring">
            <div className="text-gray-400 hover:text-white p-3 rounded-lg cursor-pointer transition">📹 Live Monitoring</div>
          </Link>
          <Link href="/map">
            <div className="text-gray-400 hover:text-white p-3 rounded-lg cursor-pointer transition">⚠️ Violations Map</div>
          </Link>
        </nav>
      </aside>

      {/* DASHBOARD CONTAINER BODY */}
      <main className="flex-1 flex flex-col overflow-y-auto p-6 space-y-6">
        
        <header className="flex justify-between items-center pb-2 border-b border-gray-800">
          <h1 className="text-2xl font-bold text-white">Parking Congestion Intelligence Platform</h1>
        </header>

        {/* 4-COLUMN METRIC CARDS OVERVIEW */}
        <section className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-[#11141b] border border-gray-800 rounded-xl p-5 shadow-lg">
            <p className="text-xs font-semibold text-gray-400 tracking-wider uppercase">Total Violations</p>
            <h3 className="text-2xl font-bold mt-2 text-purple-400">
              {metrics?.total_violations ? Number(metrics.total_violations.replace(/,/g, '')).toLocaleString('en-IN') : '0'}
            </h3>
          </div>
          <div className="bg-[#11141b] border border-gray-800 rounded-xl p-5 shadow-lg">
            <p className="text-xs font-semibold text-gray-400 tracking-wider uppercase">Active Hotspots (DBSCAN)</p>
            <h3 className="text-2xl font-bold mt-2 text-cyan-400">{metrics?.active_hotspots}</h3>
          </div>
          <div className="bg-[#11141b] border border-gray-800 rounded-xl p-5 shadow-lg">
            <p className="text-xs font-semibold text-gray-400 tracking-wider uppercase">Avg Congestion Score</p>
            <h3 className="text-2xl font-bold mt-2 text-red-400">{metrics?.avg_congestion}</h3>
          </div>
          <div className="bg-[#11141b] border border-gray-800 rounded-xl p-5 shadow-lg">
            <p className="text-xs font-semibold text-gray-400 tracking-wider uppercase">Enforcement Score</p>
            <h3 className="text-2xl font-bold mt-2 text-emerald-400">{metrics?.enforcement_score}</h3>
          </div>
        </section>

        {/* METRICS & MAP VISUAL SECTION */}
        <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          
          {/* VISUAL CELL A: RECHARTS HOURLY PEAK TREND GRAPH */}
          <div className="bg-[#11141b] border border-gray-800 rounded-xl p-5 flex flex-col h-[380px]">
            <h2 className="text-sm font-bold tracking-wide text-gray-200 mb-3">LIVE CONGESTION INTENSITY TREND</h2>
            <div className="flex-1 bg-[#1a1f2c] rounded-lg border border-gray-700 p-4 relative">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={hourlyData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorViolations" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#a855f7" stopOpacity={0.4}/>
                      <stop offset="95%" stopColor="#a855f7" stopOpacity={0.0}/>
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="hour" stroke="#6b7280" fontSize={11} tickLine={false} />
                  <YAxis stroke="#6b7280" fontSize={11} tickLine={false} />
                  <Tooltip contentStyle={{ backgroundColor: '#11141b', borderColor: '#374151', borderRadius: '8px', color: '#fff' }} />
                  <Area type="monotone" dataKey="violations" stroke="#a855f7" strokeWidth={2} fillOpacity={1} fill="url(#colorViolations)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* VISUAL CELL B: DYNAMIC GEOSPATIAL MAP LEAFLET INFRASTRUCTURE */}
          <div className="bg-[#11141b] border border-gray-800 rounded-xl p-5 flex flex-col h-[380px]">
            <h2 className="text-sm font-bold tracking-wide text-gray-200 mb-3">GEOSPATIAL SPATIAL CLUSTER INDEX</h2>
            <div className="flex-1 rounded-lg border border-gray-700 overflow-hidden relative z-0">
              {/* Injecting the safely isolated Map Component here */}
              <MapComponent recommendations={recommendations} />
            </div>
          </div>
        </section>

        {/* DYNAMIC RECOMMENDATIONS ENGINE TABLE */}
        <section className="bg-[#11141b] border border-gray-800 rounded-xl p-5">
          <h2 className="text-sm font-bold tracking-wide text-gray-200 mb-4">🤖 TARGETED ENFORCEMENT RECOMMENDATIONS</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-gray-800 text-xs font-semibold text-gray-400 uppercase tracking-wider">
                  <th className="pb-3">Location Context</th>
                  <th className="pb-3">Congestion Score</th>
                  <th className="pb-3">Priority Action Index</th>
                  <th className="pb-3">Status</th>
                  <th className="pb-3 text-right">Action Target</th>
                </tr>
              </thead>
              <tbody className="text-sm divide-y divide-gray-800 text-gray-300">
                {recommendations.map((h, i) => (
                  <tr key={i} className="hover:bg-[#161a23] transition-colors">
                    <td className="py-3.5 font-medium text-white max-w-xs truncate">{h.location}</td>
                    <td className="py-3.5">{h.congestion_score}</td>
                    <td className="py-3.5 font-bold text-purple-400">{h.priority_score}</td>
                    <td className="py-3.5">
                      <span className={`px-2 py-0.5 rounded text-xs font-semibold ${
                        h.status === 'Severe' ? 'bg-red-500/10 text-red-400' : 'bg-orange-500/10 text-orange-400'
                      }`}>
                        {h.status}
                      </span>
                    </td>
                    <td className="py-3.5 text-right">
                      <button 
                        onClick={() => alert(`🚨 Tow-truck dispatch command sent for: ${h.location}`)}
                        className="bg-purple-600/20 hover:bg-purple-600 text-purple-400 hover:text-white border border-purple-500/30 text-xs font-semibold px-3 py-1.5 rounded-lg transition-all duration-150"
                      >
                        Deploy Unit
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </main>
    </div>
  );
}