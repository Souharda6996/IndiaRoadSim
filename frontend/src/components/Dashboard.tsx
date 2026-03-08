"use client";

import dynamic from "next/dynamic";
import { useEffect, useState, useRef } from "react";
import { Activity, Map as MapIcon, Settings, AlertTriangle, Shield, Navigation } from "lucide-react";
import StatsPanel from "./StatsPanel";

// Dynamic import for Leaflet map to avoid SSR issues
const Map = dynamic(() => import("./Map"), {
    ssr: false,
    loading: () => <div className="w-full h-full bg-slate-900 flex items-center justify-center text-slate-500">Loading Satellite Data...</div>
});

const Dashboard = () => {
    const [vehicles, setVehicles] = useState<any[]>([]);
    const [mapData, setMapData] = useState<any>(null);
    const [history, setHistory] = useState<any[]>([]);
    const ws = useRef<WebSocket | null>(null);

    useEffect(() => {
        // 1. Fetch Static Map Data
        fetch("http://localhost:8000/api/map")
            .then(res => res.json())
            .then(data => setMapData(data))
            .catch(err => console.error("Failed to load map:", err));

        // 2. Setup WebSocket for Live Traffic
        ws.current = new WebSocket("ws://localhost:8000/ws/traffic");
        ws.current.onmessage = (event) => {
            const data = JSON.parse(event.data);
            const newVehicles = data.vehicles || [];
            setVehicles(newVehicles);

            // Update history for graphs (keep last 50 points)
            setHistory(prev => {
                const newPoint = {
                    time: new Date().toLocaleTimeString(),
                    count: newVehicles.length,
                    speed: newVehicles.reduce((acc: number, v: any) => acc + v.speed, 0) / (newVehicles.length || 1)
                };
                const updated = [...prev, newPoint];
                return updated.slice(-50);
            });
        };

        return () => {
            ws.current?.close();
        };
    }, []);

    const avgSpeed = vehicles.length > 0
        ? vehicles.reduce((acc: number, v: any) => acc + v.speed, 0) / vehicles.length
        : 0;

    return (
        <div className="flex h-screen w-screen bg-black overflow-hidden font-sans text-slate-200">
            {/* Sidebar - Controls */}
            <aside className="w-72 bg-slate-950 border-r border-slate-800 flex flex-col z-20">
                <div className="p-6 border-b border-slate-800">
                    <div className="flex items-center gap-2 mb-1">
                        <div className="w-8 h-8 rounded bg-sky-600 flex items-center justify-center">
                            <Activity className="w-5 h-5 text-white" />
                        </div>
                        <h1 className="text-xl font-bold tracking-tight bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">
                            TRAFFISIM AI
                        </h1>
                    </div>
                    <p className="text-[10px] text-slate-500 uppercase tracking-widest font-semibold font-mono">
                        Digital Twin • Indian Road Network
                    </p>
                </div>

                <nav className="flex-1 p-4 space-y-6 overflow-y-auto">
                    <div>
                        <label className="text-[10px] text-slate-500 uppercase font-bold mb-3 block px-2">Primary Controls</label>
                        <div className="space-y-1">
                            <button className="w-full flex items-center gap-3 px-3 py-2 rounded-lg bg-sky-600/10 text-sky-400 text-sm font-medium border border-sky-600/20">
                                <MapIcon className="w-4 h-4" /> Live Simulation
                            </button>
                            <button className="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-slate-900 text-slate-400 text-sm font-medium transition-colors">
                                <Navigation className="w-4 h-4" /> Map Modeler
                            </button>
                            <button className="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-slate-900 text-slate-400 text-sm font-medium transition-colors">
                                <Shield className="w-4 h-4" /> AI Optimizer
                            </button>
                        </div>
                    </div>

                    <div>
                        <label className="text-[10px] text-slate-500 uppercase font-bold mb-3 block px-2">Simulation Settings</label>
                        <div className="px-2 space-y-4">
                            <div className="space-y-2">
                                <div className="flex justify-between text-xs">
                                    <span>Target Density</span>
                                    <span className="text-sky-400">High</span>
                                </div>
                                <div className="h-1 w-full bg-slate-800 rounded-full overflow-hidden">
                                    <div className="h-full w-4/5 bg-sky-500"></div>
                                </div>
                            </div>
                            <div className="flex items-center justify-between text-xs">
                                <span>Weak Lane Discipline</span>
                                <div className="w-10 h-5 bg-emerald-600 rounded-full relative">
                                    <div className="absolute right-1 top-1 w-3 h-3 bg-white rounded-full"></div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="p-4 bg-orange-950/20 border border-orange-900/30 rounded-xl space-y-2">
                        <div className="flex items-center gap-2 text-orange-500 text-xs font-bold uppercase">
                            <AlertTriangle className="w-3 h-3" /> Quick Events
                        </div>
                        <div className="grid grid-cols-2 gap-2">
                            <button className="text-[10px] py-1 bg-slate-900 hover:bg-slate-800 border border-slate-800 rounded">Accident</button>
                            <button className="text-[10px] py-1 bg-slate-900 hover:bg-slate-800 border border-slate-800 rounded">Protest</button>
                            <button className="text-[10px] py-1 bg-slate-900 hover:bg-slate-800 border border-slate-800 rounded">Road Work</button>
                            <button className="text-[10px] py-1 bg-slate-900 hover:bg-slate-800 border border-slate-800 rounded">Pothole</button>
                        </div>
                    </div>
                </nav>

                <div className="p-4 border-t border-slate-800">
                    <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-slate-800 flex items-center justify-center text-xs text-slate-400">SM</div>
                        <div>
                            <div className="text-xs font-bold text-white leading-none">Souharda M.</div>
                            <div className="text-[10px] text-slate-500">SIH Participant</div>
                        </div>
                    </div>
                </div>
            </aside>

            {/* Main View Port */}
            <main className="flex-1 relative">
                <Map vehicles={vehicles} mapData={mapData} />

                {/* Overlays */}
                <div className="absolute bottom-6 right-6 z-20 w-80 max-h-[calc(100%-3rem)] bg-slate-950/80 backdrop-blur-xl border border-slate-800 rounded-2xl shadow-2xl overflow-hidden flex flex-col">
                    <div className="p-4 border-b border-slate-800 flex justify-between items-center">
                        <h3 className="text-xs font-bold uppercase tracking-widest text-slate-400">Live Analytics</h3>
                        <div className="flex gap-1">
                            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                            <span className="text-[10px] font-mono text-emerald-500 uppercase font-bold leading-none">Realtime</span>
                        </div>
                    </div>
                    <div className="flex-1">
                        <StatsPanel vehicleCount={vehicles.length} averageSpeed={avgSpeed} history={history} />
                    </div>
                </div>
            </main>
        </div>
    );
};

export default Dashboard;
