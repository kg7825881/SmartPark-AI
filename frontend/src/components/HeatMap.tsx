'use client';

import React, { useEffect } from 'react';
import { MapContainer, TileLayer, useMap} from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import 'leaflet.heat'; 


// This sub-component safely hooks into the map canvas to draw the thermal gradients
function ThermalLayer({ points }: { points: [number, number, number][] }) {
  const map = useMap();

  useEffect(() => {
    if (!points || points.length === 0) return;

    // Normalize intensity scores (which are 0-100) to the map engine's scale
    const formattedPoints = points.map(p => [p[0], p[1], p[2] / 100]);

    // @ts-ignore - Bypass strict typescript checking for the leaflet.heat plugin injection
    const heat = L.heatLayer(formattedPoints, {
      radius: 25,
      blur: 15,
      maxZoom: 13,
      gradient: {
        0.2: '#3b82f6', // Blue (Low)
        0.5: '#10b981', // Green (Moderate)
        0.7: '#eab308', // Yellow (High)
        1.0: '#ef4444'  // Red (Severe Gridlock)
      }
    }).addTo(map);

    return () => {
      map.removeLayer(heat);
    };
  }, [map, points]);

  return null;
}

export default function HeatMap({ points }: { points: [number, number, number][] }) {
  return (
    <MapContainer center={[12.9716, 77.5946]} zoom={12} className="h-full w-full bg-[#0a0c10]">
      <TileLayer
        url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        attribution='&copy; <a href="https://carto.com/">CARTO</a>'
      />
      <ThermalLayer points={points} />
    </MapContainer>
  );
}