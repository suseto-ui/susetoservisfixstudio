import React, { memo } from 'react';
import { Activity, RefreshCw, Cpu, Zap, Play, CheckCircle2 } from 'lucide-react';

interface AutoRouterTabProps {
  autoRouterData: any;
  isAutoRouting: boolean;
  onRunZeroConfRouter: () => void;
  onExecuteRouterAction: () => void;
  isExecutingRouterAction: boolean;
  routerActionResult: any;
}

export const AutoRouterTab: React.FC<AutoRouterTabProps> = memo(function AutoRouterTab({
  autoRouterData,
  isAutoRouting,
  onRunZeroConfRouter,
  onExecuteRouterAction,
  isExecutingRouterAction,
  routerActionResult
}) {
  return (
    <div className="space-y-6 font-mono">
      {/* Router Header */}
      <div className="bg-[#111622] border border-[#1f293d] rounded-xl p-5 flex flex-wrap items-center justify-between gap-4 shadow-lg">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-[#00ff9d]/10 border border-[#00ff9d]/30 text-[#00ff9d] flex items-center justify-center">
            <Activity className="w-5 h-5 text-[#00ff9d]" />
          </div>
          <div>
            <h3 className="font-bold text-white text-base flex items-center gap-2">
              <span>AUTO STATE ROUTER & ZERO-CONF PROBE</span>
              <span className="text-[11px] px-2 py-0.5 bg-[#00ff9d]/10 text-[#00ff9d] rounded border border-[#00ff9d]/30 font-bold">
                AUTOMATICKÝ SERVISNÍ POSTUP
              </span>
            </h3>
            <p className="text-xs text-[#9ca3af]">
              Automatický stavový automat: vyslání sondy, detekce režimu a vygenerování optimálního 1-klik kroku pro technika
            </p>
          </div>
        </div>

        <button
          onClick={onRunZeroConfRouter}
          disabled={isAutoRouting}
          className="px-5 py-2 bg-[#00f0ff] hover:bg-[#33f3ff] text-black font-black text-xs rounded-lg flex items-center gap-2 transition-all shadow-[0_0_15px_rgba(0,240,255,0.3)]"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isAutoRouting ? 'animate-spin' : ''}`} />
          <span>{isAutoRouting ? 'Analyzuji hardware...' : '🔍 Spustit Zero-Conf Sken'}</span>
        </button>
      </div>

      {/* Auto-Router Decision Card */}
      {autoRouterData && (
        <div className="bg-gradient-to-r from-[#0d1624] via-[#09111c] to-[#0d1624] border-2 border-[#00f0ff]/40 rounded-2xl p-6 shadow-[0_0_25px_rgba(0,240,255,0.15)] space-y-5">
          <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[#1f293d] pb-3">
            <div className="space-y-1">
              <span className="text-[10px] text-[#6b7280] uppercase tracking-wider font-bold">Zjištěný stav zařízení</span>
              <div className="text-lg text-white font-black flex items-center gap-2">
                <Cpu className="w-5 h-5 text-[#00f0ff]" />
                <span>{autoRouterData.description || 'Detekované zařízení'}</span>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <span className="px-3 py-1 bg-[#00f0ff]/10 text-[#00f0ff] border border-[#00f0ff]/30 rounded-full font-bold text-xs">
                Režim: {autoRouterData.mode}
              </span>
              <span className="px-3 py-1 bg-[#00ff9d]/10 text-[#00ff9d] border border-[#00ff9d]/30 rounded-full font-bold text-xs">
                {autoRouterData.driver_status}
              </span>
            </div>
          </div>

          {/* Probe Metadata */}
          {autoRouterData.probe_data && (
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
              <div className="p-3 bg-[#07090e] rounded-lg border border-[#1f293d]">
                <div className="text-[#6b7280] text-[10px]">Protokol</div>
                <div className="text-[#00f0ff] font-bold">{autoRouterData.probe_data.protocol}</div>
              </div>
              <div className="p-3 bg-[#07090e] rounded-lg border border-[#1f293d]">
                <div className="text-[#6b7280] text-[10px]">Cílový SoC</div>
                <div className="text-white font-bold">{autoRouterData.probe_data.soc_target}</div>
              </div>
              <div className="p-3 bg-[#07090e] rounded-lg border border-[#1f293d]">
                <div className="text-[#6b7280] text-[10px]">Paměť</div>
                <div className="text-[#00ff9d] font-bold">{autoRouterData.probe_data.storage_detected}</div>
              </div>
              <div className="p-3 bg-[#07090e] rounded-lg border border-[#1f293d]">
                <div className="text-[#6b7280] text-[10px]">Sektor</div>
                <div className="text-[#ffaa00] font-bold">{autoRouterData.probe_data.sector_size} B</div>
              </div>
            </div>
          )}

          {/* Recommended Action Card */}
          {autoRouterData.recommendation && (
            <div className="bg-[#071927] border border-[#00f0ff]/50 rounded-xl p-5 space-y-3">
              <div className="flex items-center gap-2 text-[#00f0ff] text-xs font-black">
                <Zap className="w-4 h-4" />
                <span>DOPORUČENÝ SERVISNÍ KROK PRO TECHNIKA (ZERO-CONF DECISION):</span>
              </div>
              <div className="text-white font-bold text-base">
                {autoRouterData.recommendation.action_title}
              </div>
              <p className="text-xs text-[#cbd5e1] leading-relaxed">
                {autoRouterData.recommendation.description}
              </p>

              <div className="pt-2 flex flex-wrap items-center justify-between gap-3">
                <span className="text-[11px] text-[#9ca3af]">
                  Odhadovaný čas: <strong className="text-white">{autoRouterData.recommendation.estimated_time_sec} s</strong> | Bezpečnost: <strong className="text-[#00ff9d]">{autoRouterData.recommendation.risk_level}</strong>
                </span>

                <button
                  onClick={onExecuteRouterAction}
                  disabled={isExecutingRouterAction}
                  className="px-6 py-2.5 bg-gradient-to-r from-[#00f0ff] to-[#00ff9d] hover:opacity-95 text-black font-black text-xs rounded-lg transition-all shadow-[0_0_15px_rgba(0,240,255,0.4)] flex items-center gap-2"
                >
                  <Play className={`w-3.5 h-3.5 ${isExecutingRouterAction ? 'animate-spin' : ''}`} />
                  <span>{isExecutingRouterAction ? 'Provádím operaci...' : autoRouterData.recommendation.button_text || '⚡ Provést doporučenou operaci'}</span>
                </button>
              </div>
            </div>
          )}

          {/* Execution Result */}
          {routerActionResult && (
            <div className="p-4 bg-[#00ff9d]/10 border border-[#00ff9d]/40 rounded-xl text-xs text-[#00ff9d] space-y-1 font-bold">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-[#00ff9d]" /> {routerActionResult.title}: {routerActionResult.status}
              </div>
              <div className="text-white font-normal">{routerActionResult.verdict}</div>
            </div>
          )}
        </div>
      )}
    </div>
  );
});
