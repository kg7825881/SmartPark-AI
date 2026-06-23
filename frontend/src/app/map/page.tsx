
'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import dynamic from 'next/dynamic';

// 1. Clean dynamic import for the new heatmap (disables SSR for Leaflet)
const DynamicHeatMap = dynamic(() => import('../../components/HeatMap'), {
  ssr: false,
  loading: () => (
    <div className="h-full w-full flex items-center justify-center font-mono text-gray-400 animate-pulse">
      🔥 Igniting Thermal Geospatial Engine...
    </div>
  ),
});

// 2. Single Default Export for the Next.js Route
export default function ViolationsMapPage() {
  const [points, setPoints] = useState<[number, number, number][]>([]);
  const [loading, setLoading] = useState(true);
  const [forecastHours, setForecastHours] = useState<number>(0);

  useEffect(() => {
    async function fetchHeatmapData() {
      setLoading(true);
      try {
        const response = await fetch(`http://127.0.0.1:8000/api/heatmap-data?hours_ahead=${forecastHours}`);
        const data = await response.json();
        setPoints(data.points);
      } catch (error) {
        console.error("Failed to load heatmap data:", error);
      } finally {
        setLoading(false);
      }
    }
    fetchHeatmapData();
  }, [forecastHours]);

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#0a0c10]">
      
      {/* SIDEBAR NAVIGATION */}
      <aside className="w-64 bg-[#11141b] border-r border-gray-800 flex flex-col p-5 space-y-6 z-10 shadow-2xl shrink-0">
        <div className="flex items-center space-x-3">
          <div className="h-8 w-8 bg-purple-600 rounded-lg flex items-center justify-center font-bold text-white">S</div>
          <span className="text-xl font-bold tracking-tight text-white">SmartPark AI</span>
        </div>
        <nav className="flex-1 space-y-2 text-sm font-medium">
          <Link href="/">
            <div className="text-gray-400 hover:text-white p-3 rounded-lg cursor-pointer transition">📊 Overview</div>
          </Link>
          <Link href="/monitoring">
            <div className="text-gray-400 hover:text-white p-3 rounded-lg cursor-pointer transition">📹 Live Monitoring</div>
          </Link>
          <Link href="/map">
            <div className="bg-purple-600/10 text-purple-400 p-3 rounded-lg cursor-pointer transition">⚠️ Violations Map</div>
          </Link>
        </nav>

        {/* FORECAST TOGGLE */}
        <div className="mt-6 border-t border-gray-800 pt-5">
          <h3 className="text-xs font-bold text-gray-400 tracking-wider mb-3 uppercase">Time Engine</h3>
          <div className="flex flex-col space-y-2">
            {[0, 1, 2, 3].map((hours) => (
              <button
                key={hours}
                onClick={() => setForecastHours(hours)}
                className={`px-3 py-2 text-xs font-bold rounded-lg text-left transition-colors ${
                  forecastHours === hours 
                    ? 'bg-purple-600 text-white' 
                    : 'bg-[#1a1f2c] text-gray-400 hover:text-white hover:bg-gray-800'
                }`}
              >
                {hours === 0 ? 'Current Live Map' : `+${hours} Hour Forecast`}
              </button>
            ))}
          </div>
        </div>

        {/* MAP LEGEND */}
        <div className="mt-auto border-t border-gray-800 pt-5">
          <h3 className="text-xs font-bold text-gray-400 tracking-wider mb-3 uppercase">Thermal Legend</h3>
          <div className="space-y-2 text-xs text-gray-300">
            <div className="flex items-center space-x-2"><span className="w-3 h-3 rounded-full bg-red-500 shadow-[0_0_8px_#ef4444]"></span><span>Severe Gridlock</span></div>
            <div className="flex items-center space-x-2"><span className="w-3 h-3 rounded-full bg-yellow-500"></span><span>High Congestion</span></div>
            <div className="flex items-center space-x-2"><span className="w-3 h-3 rounded-full bg-green-500"></span><span>Moderate Activity</span></div>
            <div className="flex items-center space-x-2"><span className="w-3 h-3 rounded-full bg-blue-500"></span><span>Low Density</span></div>
          </div>
        </div>
      </aside>

      {/* FULL SCREEN HEATMAP ENGINE */}
      <main className="flex-1 relative">
        <div className="absolute inset-0 z-0">
          {/* 3. Render the dynamic map only when not loading, passing the fetched points */}
          {!loading && <DynamicHeatMap points={points} />}
        </div>
        
        {/* FLOATING HEADER OVERLAY */}
        <div className="absolute top-6 left-6 z-10 pointer-events-none">
          <h1 className="text-2xl font-bold text-white drop-shadow-md">Geospatial Violation Density</h1>
          <p className="text-gray-400 text-sm mt-1 bg-black/50 px-2 py-1 rounded inline-block backdrop-blur-sm">Displaying 5,000 highest-weighted data points across Bengaluru</p>
        </div>
      </main>

    </div>
  );
}