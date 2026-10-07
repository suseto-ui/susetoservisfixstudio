import React, { memo } from 'react';
import { Zap, RefreshCw, Play, Activity, AlertTriangle, CheckCircle2 } from 'lucide-react';

interface FaultTelemetryTabProps {
  onPortSoftReset: () => void;
  isWatchdogResetting: boolean;
  onRunE2EBenchmark: () => void;
  isE2ERunning: boolean;
  telemetryData: {
    current_rtt_ms: number;
    average_rtt_ms: number;
    jitter_ms: number;
    packet_loss_pct: number;
    sparkline_data: number[];
  };
  faultNoisePct: number;
  onFaultNoisePctChange: (val: number) => void;
  faultDropPct: number;
  onFaultDropPctChange: (val: number) => void;
  faultHotplugSim: boolean;
  onFaultHotplugSimChange: (val: boolean) => void;
  onRunFaultBenchmark: () => void;
  isFaultTesting: boolean;
  faultResult: any;
  e2eResult: any;
}

export const FaultTelemetryTab: React.FC<FaultTelemetryTabProps> = memo(function FaultTelemetryTab({
  onPortSoftReset,
  isWatchdogResetting,
  onRunE2EBenchmark,
  isE2ERunning,
  telemetryData,
  faultNoisePct,
  onFaultNoisePctChange,
  faultDropPct,
  onFaultDropPctChange,
  faultHotplugSim,
  onFaultHotplugSimChange,
  onRunFaultBenchmark,
  isFaultTesting,
  faultResult,
  e2eResult
}) {
  return (
    <div className="space-y-6 font-mono">
      {/* Header & Quick E2E Button */}
      <div className="bg-[#111622] border border-[#1f293d] rounded-xl p-5 flex flex-wrap items-center justify-between gap-4 shadow-lg">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-[#ffaa00]/10 border border-[#ffaa00]/30 text-[#ffaa00] flex items-center justify-center">
            <Zap className="w-5 h-5 text-[#ffaa00]" />
          </div>
          <div>
            <h3 className="font-bold text-white text-base flex items-center gap-2">
              <span>HARDWARE FAULT INJECTION & RTT TELEMETRY STUDIO</span>
              <span className="text-[11px] px-2 py-0.5 bg-[#ffaa00]/10 text-[#ffaa00] rounded border border-[#ffaa00]/30 font-bold">
                RESILIENCE LAB
              </span>
            </h3>
            <p className="text-xs text-[#9ca3af]">
              Simulace šumu sběrnice, výpadků rámců, hotplug odpojení, živá RTT latence a Watchdog soft-reset
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={onPortSoftReset}
            disabled={isWatchdogResetting}
            className="px-3.5 py-2 bg-[#1e293b] hover:bg-[#334155] text-white font-bold text-xs rounded-lg flex items-center gap-1.5 transition-all border border-[#334155]"
          >
            <RefreshCw className={`w-3.5 h-3.5 text-[#00ff9d] ${isWatchdogResetting ? 'animate-spin' : ''}`} />
            Watchdog Soft-Reset
          </button>

          <button
            onClick={onRunE2EBenchmark}
            disabled={isE2ERunning}
            className="px-4 py-2 bg-[#00f0ff] hover:bg-[#33f3ff] text-black font-bold text-xs rounded-lg flex items-center gap-1.5 transition-all shadow-[0_0_15px_rgba(0,240,255,0.3)]"
          >
            <Play className={`w-3.5 h-3.5 ${isE2ERunning ? 'animate-spin' : ''}`} />
            {isE2ERunning ? 'Běží E2E Test...' : '🚀 Spustit E2E Diagnostickou Sadu'}
          </button>
        </div>
      </div>

      {/* Live RTT Latency Sparkline Gauge */}
      <div className="bg-[#0a0d14] border border-[#1f293d] rounded-xl p-5 space-y-4 shadow-md">
        <div className="flex flex-wrap items-center justify-between border-b border-[#1f293d] pb-3 gap-2 text-xs">
          <div className="flex items-center gap-2 text-white font-bold">
            <Activity className="w-4 h-4 text-[#00ff9d]" />
            <span>Real-Time RTT (Round-Trip Time) Telemetrie & Latence</span>
          </div>
          <div className="flex items-center gap-4 text-[#9ca3af]">
            <span>Aktuální: <strong className="text-[#00ff9d]">{telemetryData.current_rtt_ms} ms</strong></span>
            <span>Průměr: <strong className="text-[#00f0ff]">{telemetryData.average_rtt_ms} ms</strong></span>
            <span>Jitter: <strong className="text-[#ffaa00]">{telemetryData.jitter_ms} ms</strong></span>
            <span>Ztrátovost: <strong className="text-white">{telemetryData.packet_loss_pct}%</strong></span>
          </div>
        </div>

        {/* Sparkline Visualizer */}
        <div className="h-24 w-full bg-[#07090e] rounded-lg p-2 border border-[#161f30] relative overflow-hidden flex items-end gap-1.5">
          {telemetryData.sparkline_data.map((val: number, idx: number) => {
            const heightPct = Math.min(100, Math.max(10, (val / 3.0) * 80));
            return (
              <div
                key={idx}
                className="flex-1 bg-gradient-to-t from-[#00f0ff] to-[#00ff9d] rounded-t transition-all duration-300 opacity-85 hover:opacity-100"
                style={{ height: `${heightPct}%` }}
                title={`Vzorek #${idx + 1}: ${val} ms`}
              />
            );
          })}
        </div>
      </div>

      {/* Fault Injection Simulator Controls */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-[#0a0d14] border border-[#1f293d] rounded-xl p-5 space-y-4 text-xs shadow-md">
          <div className="flex items-center gap-2 text-[#ffaa00] font-bold text-sm border-b border-[#1f293d] pb-2">
            <AlertTriangle className="w-4 h-4" />
            <span>Nastavení simulace chyb</span>
          </div>

          <div className="space-y-3">
            <div>
              <div className="flex justify-between mb-1">
                <span className="text-[#9ca3af]">Šum na lince (Bit-Flips):</span>
                <span className="text-[#00f0ff] font-bold">{faultNoisePct} %</span>
              </div>
              <input
                type="range"
                min="0"
                max="40"
                value={faultNoisePct}
                onChange={e => onFaultNoisePctChange(Number(e.target.value))}
                className="w-full accent-[#00f0ff]"
              />
            </div>

            <div>
              <div className="flex justify-between mb-1">
                <span className="text-[#9ca3af]">Výpadky rámců (Packet Drops):</span>
                <span className="text-[#ffaa00] font-bold">{faultDropPct} %</span>
              </div>
              <input
                type="range"
                min="0"
                max="30"
                value={faultDropPct}
                onChange={e => onFaultDropPctChange(Number(e.target.value))}
                className="w-full accent-[#ffaa00]"
              />
            </div>

            <div className="flex items-center justify-between pt-1">
              <span className="text-[#9ca3af]">Simulovat Hotplug odpojení:</span>
              <input
                type="checkbox"
                checked={faultHotplugSim}
                onChange={e => onFaultHotplugSimChange(e.target.checked)}
                className="w-4 h-4 accent-[#ff3366] rounded"
              />
            </div>

            <button
              onClick={onRunFaultBenchmark}
              disabled={isFaultTesting}
              className="w-full mt-2 py-2.5 bg-[#ffaa00] hover:bg-[#ffbb33] text-black font-bold rounded-lg transition-all"
            >
              {isFaultTesting ? 'Testuji odolnost...' : '⚡ Spustit Fault Injection Test'}
            </button>
          </div>
        </div>

        {/* Fault Benchmark Results */}
        <div className="lg:col-span-2 bg-[#0a0d14] border border-[#1f293d] rounded-xl p-5 space-y-3 text-xs shadow-md">
          <div className="flex items-center justify-between border-b border-[#1f293d] pb-2">
            <span className="font-bold text-white">Výsledky testu odolnosti sběrnice</span>
            {faultResult && (
              <span className="px-2 py-0.5 bg-[#00ff9d]/10 text-[#00ff9d] border border-[#00ff9d]/30 rounded font-bold">
                Skóre: {faultResult.bus_stability_score_pct} %
              </span>
            )}
          </div>

          {faultResult ? (
            <div className="space-y-3">
              <div className="grid grid-cols-3 gap-2">
                <div className="p-2.5 bg-[#07090e] rounded border border-[#1f293d]">
                  <div className="text-[#6b7280] text-[10px]">Odesláno paketů</div>
                  <div className="text-white font-bold">{faultResult.total_packets_sent}</div>
                </div>
                <div className="p-2.5 bg-[#07090e] rounded border border-[#1f293d]">
                  <div className="text-[#6b7280] text-[10px]">Opraveno šumem</div>
                  <div className="text-[#00f0ff] font-bold">{faultResult.corrupted_noise_packets}</div>
                </div>
                <div className="p-2.5 bg-[#07090e] rounded border border-[#1f293d]">
                  <div className="text-[#6b7280] text-[10px]">Auto-Retransmisí</div>
                  <div className="text-[#00ff9d] font-bold">{faultResult.auto_retransmissions}</div>
                </div>
              </div>

              <div className="p-3 bg-[#040609] rounded border border-[#161f30] space-y-1">
                <div className="text-[#9ca3af] font-bold mb-1">Události zachycené Watchdogem:</div>
                {faultResult.fault_log_events?.map((ev: string, i: number) => (
                  <div key={i} className="text-[#cbd5e1]">{ev}</div>
                ))}
              </div>
            </div>
          ) : (
            <div className="py-10 text-center text-[#6b7280]">
              Klikněte na &quot;Spustit Fault Injection Test&quot; pro zahájení zátěžové simulace.
            </div>
          )}
        </div>
      </div>

      {/* E2E Benchmark Suite Results */}
      {e2eResult && (
        <div className="bg-[#07090e] border border-[#00f0ff]/40 rounded-xl p-5 space-y-4 shadow-md">
          <div className="flex items-center justify-between border-b border-[#1f293d] pb-2 text-xs">
            <span className="text-[#00f0ff] font-bold flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-[#00ff9d]" /> Výsledek End-to-End diagnostické sady
            </span>
            <span className="text-[#00ff9d] font-bold">{e2eResult.verdict}</span>
          </div>

          <div className="space-y-2">
            {e2eResult.steps?.map((step: any) => (
              <div key={step.step} className="p-2.5 bg-[#0a0d14] rounded border border-[#1f293d] flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  <span className="w-5 h-5 rounded-full bg-[#00ff9d]/10 text-[#00ff9d] flex items-center justify-center font-bold text-[10px]">
                    {step.step}
                  </span>
                  <span className="text-white font-medium">{step.name}</span>
                </div>
                <span className="text-[#9ca3af]">{step.details}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
});
