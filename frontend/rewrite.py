import os

filepath = r'c:\Users\ojhav\OneDrive\Desktop\Hackathon\SmartPark-AI-main\frontend\src\app\page.tsx'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

return_idx = content.find('  return (')

if return_idx != -1:
    before_return = content[:return_idx]
    
    new_return = """  // Lifecycle Distribution math
  const lifecycleCounts = lifecycles.reduce((acc, l) => {
    acc[l.lifecycle_stage] = (acc[l.lifecycle_stage] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);
  const totalLifecycles = lifecycles.length || 1;

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#0a0c10]">
      
      {/* LEFT SIDEBAR NAVIGATION */}
      <aside className="w-64 bg-[#11141b] border-r border-gray-800 flex flex-col p-5 space-y-6 shrink-0 z-10">
        <div className="flex items-center space-x-3">
          <div className="h-8 w-8 bg-purple-600 rounded-lg flex items-center justify-center font-bold text-white">S</div>
          <span className="text-xl font-bold tracking-tight text-white">SmartPark AI</span>
        </div>
        <nav className="flex-1 space-y-2 text-sm font-medium">
          <Link href="/">
            <div className="bg-purple-600/10 text-purple-400 p-3 rounded-lg cursor-pointer transition">📊 Executive Dashboard</div>
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
      <main className="flex-1 flex flex-col overflow-y-auto p-8 space-y-8 bg-gradient-to-b from-[#0a0c10] to-[#0d1017]">
        
        <header className="flex justify-between items-center pb-4 border-b border-gray-800/50">
          <div>
            <h1 className="text-3xl font-bold text-white tracking-tight">EXECUTIVE COMMAND CENTER</h1>
            <p className="text-gray-400 mt-2 text-sm font-medium tracking-wide">UNIFIED OPERATIONAL VIEW FOR CITY AUTHORITIES</p>
          </div>
          <div className="text-right">
            <div className="text-xs text-gray-500 uppercase tracking-widest font-bold mb-1">System Status</div>
            <div className="flex items-center space-x-2">
              <span className="relative flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500 shadow-[0_0_8px_#10b981]"></span>
              </span>
              <span className="text-emerald-400 font-bold text-sm tracking-widest">LIVE</span>
            </div>
          </div>
        </header>

        {/* TOP SECTION: Large KPI Cards */}
        <section className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-[#11141b] border border-gray-800 rounded-xl p-6 shadow-lg relative overflow-hidden group hover:border-gray-600 transition-colors">
            <div className="absolute -right-4 -top-4 w-24 h-24 bg-blue-500/5 rounded-full blur-2xl group-hover:bg-blue-500/10 transition-colors"></div>
            <p className="text-xs font-bold text-gray-500 tracking-wider uppercase mb-2">Total Violations</p>
            <h3 className="text-4xl font-bold text-white font-mono tracking-tight">
              {metrics?.total_violations ? Number(metrics.total_violations.replace(/,/g, '')).toLocaleString('en-IN') : '0'}
            </h3>
          </div>
          <div className="bg-[#11141b] border border-gray-800 rounded-xl p-6 shadow-lg relative overflow-hidden group hover:border-cyan-900/50 transition-colors">
            <div className="absolute -right-4 -top-4 w-24 h-24 bg-cyan-500/5 rounded-full blur-2xl group-hover:bg-cyan-500/10 transition-colors"></div>
            <p className="text-xs font-bold text-gray-500 tracking-wider uppercase mb-2">Active Hotspots</p>
            <h3 className="text-4xl font-bold text-cyan-400 font-mono tracking-tight">{metrics?.active_hotspots || '0'}</h3>
          </div>
          <div className="bg-[#11141b] border border-red-900/40 rounded-xl p-6 shadow-lg relative overflow-hidden">
            <div className="absolute inset-0 bg-red-500/5"></div>
            <div className="absolute -right-4 -top-4 w-24 h-24 bg-red-500/20 rounded-full blur-2xl"></div>
            <p className="text-xs font-bold text-red-400/80 tracking-wider uppercase mb-2 relative z-10">Critical Junctions</p>
            <h3 className="text-4xl font-bold text-red-500 font-mono tracking-tight relative z-10">{junctions.filter(j => j.risk_tier === 'Critical').length}</h3>
          </div>
          <div className="bg-[#11141b] border border-purple-900/40 rounded-xl p-6 shadow-lg relative overflow-hidden">
            <div className="absolute inset-0 bg-purple-500/5"></div>
            <div className="absolute -right-4 -top-4 w-24 h-24 bg-purple-500/20 rounded-full blur-2xl"></div>
            <p className="text-xs font-bold text-purple-400/80 tracking-wider uppercase mb-2 relative z-10">Predicted Critical</p>
            <h3 className="text-4xl font-bold text-purple-400 font-mono tracking-tight relative z-10">{forecasts.filter(f => f.predicted_risk_tier === 'Critical').length}</h3>
          </div>
        </section>

        {/* MIDDLE SECTION: CITY STATUS (Hero area) */}
        <section className="bg-[#161a23] border border-gray-800 rounded-xl p-6 flex flex-col md:flex-row justify-between items-center gap-6 shadow-[0_10px_30px_rgba(0,0,0,0.5)]">
          <div className="flex flex-col items-center md:items-start text-center md:text-left w-full md:w-1/4">
            <span className="text-xs font-bold text-gray-500 uppercase tracking-widest mb-2 flex items-center"><span className="mr-2">🔥</span> Highest Risk</span>
            <span className="text-xl font-bold text-white truncate w-full" title={junctions[0]?.junction_name}>{junctions[0]?.junction_name || 'Loading...'}</span>
          </div>
          <div className="hidden md:block h-12 w-px bg-gray-800"></div>
          <div className="flex flex-col items-center md:items-start text-center md:text-left w-full md:w-1/4">
            <span className="text-xs font-bold text-gray-500 uppercase tracking-widest mb-2 flex items-center"><span className="mr-2">🔮</span> Highest Forecast</span>
            <span className="text-xl font-bold text-purple-400 truncate w-full" title={[...forecasts].sort((a,b)=>b.forecast_score - a.forecast_score)[0]?.junction_name}>{[...forecasts].sort((a,b)=>b.forecast_score - a.forecast_score)[0]?.junction_name || 'Loading...'}</span>
          </div>
          <div className="hidden md:block h-12 w-px bg-gray-800"></div>
          <div className="flex flex-col items-center md:items-start text-center md:text-left w-full md:w-1/4">
            <span className="text-xs font-bold text-gray-500 uppercase tracking-widest mb-2 flex items-center"><span className="mr-2">🚨</span> Top Target</span>
            <span className="text-xl font-bold text-red-500 truncate w-full" title={enforcements[0]?.junction_name}>{enforcements[0]?.junction_name || 'Loading...'}</span>
          </div>
          <div className="hidden md:block h-12 w-px bg-gray-800"></div>
          <div className="flex flex-col items-center md:items-start text-center md:text-left w-full md:w-1/4">
            <span className="text-xs font-bold text-gray-500 uppercase tracking-widest mb-2 flex items-center"><span className="mr-2">🧬</span> Most Critical Lifecycle</span>
            <span className="text-xl font-bold text-orange-400 truncate w-full" title={lifecycles.find(l=>l.lifecycle_stage==='Critical')?.junction_name || lifecycles[0]?.junction_name}>{lifecycles.find(l=>l.lifecycle_stage==='Critical')?.junction_name || lifecycles[0]?.junction_name || 'Loading...'}</span>
          </div>
        </section>

        {/* COMMAND CENTER SECTION: Top 10 Enforcement Actions */}
        <section className="bg-[#11141b] border border-red-900/40 rounded-xl shadow-[0_0_20px_rgba(220,38,38,0.05)] overflow-hidden flex flex-col">
          <div className="px-6 py-4 border-b border-gray-800/50 bg-[#141821]">
            <h2 className="text-sm font-bold tracking-widest text-red-500 flex items-center">
              <span className="mr-3 text-lg">🚨</span> TOP 10 ACTIVE DISPATCH TARGETS
            </h2>
          </div>
          <div className="p-6 overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-gray-800 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  <th className="pb-4 w-20 text-center">Priority</th>
                  <th className="pb-4">Junction</th>
                  <th className="pb-4">Action</th>
                  <th className="pb-4">Reasoning Context</th>
                  <th className="pb-4 text-right">Forecast Risk</th>
                </tr>
              </thead>
              <tbody className="text-sm divide-y divide-gray-800/50 text-gray-300">
                {enforcements.slice(0, 10).map((e, i) => (
                  <tr key={i} className={`transition-all duration-200 ${e.priority_level === 1 ? 'bg-red-950/20 hover:bg-red-900/30' : 'hover:bg-[#161a23]'}`}>
                    <td className="py-4 text-center">
                      <span className={`inline-flex items-center justify-center w-8 h-8 rounded-full text-sm font-bold ${
                        e.priority_level === 1 ? 'bg-red-500 text-white shadow-[0_0_12px_#ef4444]' :
                        e.priority_level === 2 ? 'bg-orange-500 text-white shadow-[0_0_8px_#f97316]' :
                        e.priority_level === 3 ? 'bg-yellow-500 text-black' :
                        'bg-gray-800 text-gray-400'
                      }`}>
                        {e.priority_level}
                      </span>
                    </td>
                    <td className="py-4 font-bold text-white px-3 max-w-[250px] truncate" title={e.junction_name}>{e.junction_name}</td>
                    <td className={`py-4 font-bold tracking-wide ${e.priority_level === 1 ? 'text-red-400' : 'text-gray-300'}`}>{e.recommended_action}</td>
                    <td className="py-4 text-xs text-gray-400 max-w-md">{e.reason}</td>
                    <td className="py-4 font-mono font-bold text-right text-purple-400 text-base">{e.forecast_score}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {/* STRATEGIC INTELLIGENCE SECTION */}
        <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* Top Junction Risks */}
          <div className="bg-[#11141b] border border-gray-800 rounded-xl p-6 shadow-lg">
            <h2 className="text-xs font-bold tracking-widest text-gray-500 uppercase mb-6 flex items-center"><span className="w-2 h-2 bg-red-500 rounded-full mr-2"></span> Top Junction Risks</h2>
            <div className="space-y-5">
              {junctions.slice(0, 5).map((j, i) => (
                <div key={i} className="flex justify-between items-center group">
                  <div className="truncate mr-4 text-sm font-medium text-gray-300 group-hover:text-white transition-colors">{j.junction_name}</div>
                  <div className="flex items-center space-x-4 shrink-0">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-black uppercase tracking-wider ${
                      j.risk_tier === 'Critical' ? 'bg-red-500/10 text-red-400 border border-red-500/20' :
                      j.risk_tier === 'High' ? 'bg-orange-500/10 text-orange-400 border border-orange-500/20' : 
                      'bg-yellow-500/10 text-yellow-400 border border-yellow-500/20'
                    }`}>{j.risk_tier}</span>
                    <span className="text-sm font-mono font-bold text-white w-10 text-right">{j.risk_score}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Top Forecast Risks */}
          <div className="bg-[#11141b] border border-gray-800 rounded-xl p-6 shadow-lg">
            <h2 className="text-xs font-bold tracking-widest text-gray-500 uppercase mb-6 flex items-center"><span className="w-2 h-2 bg-purple-500 rounded-full mr-2"></span> Top Forecast Risks</h2>
            <div className="space-y-5">
              {[...forecasts].sort((a,b)=>b.forecast_score - a.forecast_score).slice(0, 5).map((f, i) => (
                <div key={i} className="flex justify-between items-center group">
                  <div className="truncate mr-4 text-sm font-medium text-gray-300 group-hover:text-white transition-colors">{f.junction_name}</div>
                  <div className="flex items-center space-x-4 shrink-0">
                    <span className="text-xs text-cyan-400 font-medium">Vol: {f.expected_violation_volume}</span>
                    <span className="text-sm font-mono font-bold text-purple-400 w-10 text-right">{f.forecast_score}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Lifecycle Distribution */}
          <div className="bg-[#11141b] border border-gray-800 rounded-xl p-6 shadow-lg flex flex-col">
            <h2 className="text-xs font-bold tracking-widest text-gray-500 uppercase mb-6 flex items-center"><span className="w-2 h-2 bg-orange-500 rounded-full mr-2"></span> Lifecycle Distribution</h2>
            <div className="flex-1 flex flex-col justify-center space-y-6">
              {[
                { stage: 'Critical', color: 'bg-red-500', text: 'text-red-400' },
                { stage: 'Persistent', color: 'bg-orange-500', text: 'text-orange-400' },
                { stage: 'Growing', color: 'bg-yellow-500', text: 'text-yellow-400' },
                { stage: 'Emerging', color: 'bg-blue-500', text: 'text-blue-400' }
              ].map((item, i) => {
                const count = lifecycleCounts[item.stage] || 0;
                const percentage = Math.round((count / totalLifecycles) * 100);
                return (
                  <div key={i} className="group">
                    <div className="flex justify-between items-end mb-2">
                      <span className={`text-xs font-black uppercase tracking-wider ${item.text}`}>{item.stage}</span>
                      <span className="text-xs font-mono text-gray-400 group-hover:text-white transition-colors">{count} ({percentage}%)</span>
                    </div>
                    <div className="w-full h-1.5 bg-gray-800/80 rounded-full overflow-hidden">
                      <div className={`h-full ${item.color} shadow-[0_0_8px_currentColor]`} style={{ width: `${percentage}%` }}></div>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>

        </section>
      </main>
    </div>
  );
}
"""
    
    new_content = before_return + new_return
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
