'use client';

import React, { useEffect } from 'react';
import { MapContainer, TileLayer, CircleMarker, Tooltip } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

interface ClusterItem {
  cluster_id: number;
  latitude: number;
  longitude: number;
  size: number;
  avg_congestion: number;
  avg_priority: number;
  location: string;
}

export default function Map({ clusters = [] }: { clusters?: ClusterItem[] }) {
  // Use a `useEffect` to ensure this only runs on the client side
  useEffect(() => {
    // Delete the default icon URL getter so Leaflet doesn't try to resolve local paths
    delete (L.Icon.Default.prototype as any)._getIconUrl;

    L.Icon.Default.mergeOptions({
      iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
      iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
      shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
    });
  }, []);

  return (
    <MapContainer center={[12.9716, 77.5946]} zoom={11} className="h-full w-full bg-[#0a0c10]">
      <TileLayer
        url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        attribution='&copy; <a href="https://carto.com/">CARTO</a>'
      />
      {clusters.map((cluster) => {
        // Calculate circle marker properties
        const radius = Math.min(25, Math.max(8, cluster.size * 0.4));
        const color = cluster.avg_congestion > 75 ? '#8b5cf6' : // Purple color scheme matches layout
                      cluster.avg_congestion > 50 ? '#a78bfa' : '#c084fc';
        
        return (
          <CircleMarker
            key={cluster.cluster_id}
            center={[cluster.latitude, cluster.longitude]}
            radius={radius}
            fillColor={color}
            color={color}
            weight={1.5}
            opacity={0.8}
            fillOpacity={0.45}
          >
            <Tooltip direction="top" offset={[0, -5]} opacity={0.95} className="custom-tooltip">
              <div className="p-3 text-xs leading-normal font-sans">
                <p className="font-bold text-[#c084fc] mb-1 truncate max-w-[200px]">{cluster.location}</p>
                <div className="space-y-1 text-gray-300 font-mono">
                  <div className="flex justify-between space-x-4">
                    <span>Violations:</span>
                    <span className="font-bold text-white">{cluster.size}</span>
                  </div>
                  <div className="flex justify-between space-x-4">
                    <span>Avg Congestion:</span>
                    <span className="font-bold text-white">{cluster.avg_congestion}%</span>
                  </div>
                  <div className="flex justify-between space-x-4">
                    <span>Priority Score:</span>
                    <span className="font-bold text-white">{cluster.avg_priority}</span>
                  </div>
                </div>
              </div>
            </Tooltip>
          </CircleMarker>
        );
      })}
    </MapContainer>
  );
}