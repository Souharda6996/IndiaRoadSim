"use client";

import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    AreaChart,
    Area
} from "recharts";

interface StatsProps {
    vehicleCount: number;
    averageSpeed: number;
    history: any[];
}

const StatsPanel = ({ vehicleCount, averageSpeed, history }: StatsProps) => {
    return (
        <div className="flex flex-col gap-4 p-4 text-white h-full overflow-y-auto bg-slate-900/50 backdrop-blur-md">
            <div className="grid grid-cols-2 gap-4">
                <div className="p-3 bg-slate-800/50 rounded-lg border border-slate-700">
                    <div className="text-xs text-slate-400 uppercase tracking-wider">Active Agents</div>
                    <div className="text-2xl font-bold text-sky-400">{vehicleCount}</div>
                </div>
                <div className="p-3 bg-slate-800/50 rounded-lg border border-slate-700">
                    <div className="text-xs text-slate-400 uppercase tracking-wider">Avg Speed</div>
                    <div className="text-2xl font-bold text-emerald-400">{(averageSpeed * 3.6).toFixed(1)} <span className="text-sm font-normal">km/h</span></div>
                </div>
            </div>

            <div className="flex-1 min-h-[200px] p-3 bg-slate-800/50 rounded-lg border border-slate-700">
                <div className="text-xs text-slate-400 uppercase tracking-wider mb-2">Traffic Flow Density</div>
                <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={history}>
                        <defs>
                            <linearGradient id="colorSpeed" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.3} />
                                <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0} />
                            </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                        <XAxis dataKey="time" hide />
                        <YAxis hide domain={['auto', 'auto']} />
                        <Tooltip
                            contentStyle={{ background: '#0f172a', border: '1px solid #334155', borderRadius: '8px' }}
                            itemStyle={{ color: '#0ea5e9' }}
                        />
                        <Area
                            type="monotone"
                            dataKey="count"
                            stroke="#0ea5e9"
                            fillOpacity={1}
                            fill="url(#colorSpeed)"
                            isAnimationActive={false}
                        />
                    </AreaChart>
                </ResponsiveContainer>
            </div>

            <div className="flex-1 min-h-[200px] p-3 bg-slate-800/50 rounded-lg border border-slate-700">
                <div className="text-xs text-slate-400 uppercase tracking-wider mb-2">Congestion Index</div>
                <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={history}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                        <XAxis dataKey="time" hide />
                        <YAxis hide />
                        <Tooltip
                            contentStyle={{ background: '#0f172a', border: '1px solid #334155', borderRadius: '8px' }}
                            itemStyle={{ color: '#10b981' }}
                        />
                        <Line
                            type="monotone"
                            dataKey="speed"
                            stroke="#10b981"
                            strokeWidth={2}
                            dot={false}
                            isAnimationActive={false}
                        />
                    </LineChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
};

export default StatsPanel;
