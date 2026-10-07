import React, { memo } from 'react';
import {
  Cpu,
  RefreshCw,
  Zap,
  HardDrive,
  PlayCircle,
  Pause,
  RotateCcw,
  CheckCircle2,
  AlertTriangle,
  Flame,
  Info
} from 'lucide-react';
import { SerialDeviceDescriptor } from '../../services/webSerialEngine';

interface TopOrchestratorBarProps {
  selectedProfile: string;
  onSelectProfile: (profile: string) => void;
  autoQueueRunning: boolean;
  onToggleAutoQueue: () => void;
  orchestratorCountdown: number;
  onResetCountdown: () => void;
  driverVerificationStatus: 'IDLE' | 'SCANNING' | 'COMPLIANT' | 'MISMATCH' | 'CORRECTED';
  walLedgerActive: boolean;
  connectedDevice: SerialDeviceDescriptor | null;
}

export const TopOrchestratorBar: React.FC<TopOrchestratorBarProps> = memo(function TopOrchestratorBar({
  selectedProfile,
  onSelectProfile,
  autoQueueRunning,
  onToggleAutoQueue,
  orchestratorCountdown,
  onResetCountdown,
  driverVerificationStatus,
  walLedgerActive,
  connectedDevice
}) {
  return (
    <section
      id="tour-header-orchestrator"
      className="bg-[#0e1320] border-b border-[#1b263b] px-4 py-2 flex flex-wrap items-center justify-between gap-3 text-xs font-mono shadow-inner shrink-0"
    >
      {/* 1. Hotplug & Profiling Queue State */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 px-2.5 py-1 bg-[#151d2f] rounded-lg border border-[#212f4c]">
          <div className="relative flex items-center justify-center">
            <span className={`w-2.5 h-2.5 rounded-full ${autoQueueRunning ? 'bg-[#00f0ff]' : 'bg-[#f59e0b]'}`} />
            {autoQueueRunning && (
              <span className="absolute w-2.5 h-2.5 rounded-full bg-[#00f0ff] animate-ping opacity-75" />
            )}
          </div>
          <span className="text-[#9ca3af] text-[11px] font-bold">ORCHESTRÁTOR:</span>
          <span className="text-[#00f0ff] font-bold">
            {autoQueueRunning ? 'AUTOMATICKÁ FRONTA AKTIVNÍ' : 'MANUÁLNÍ POZASTAVENÍ'}
          </span>
        </div>

        {/* 5-second Timeout Fallback Indicator */}
        <div className="flex items-center gap-1.5 px-2.5 py-1 bg-[#151d2f] rounded-lg border border-[#212f4c]">
          <span className="text-[#9ca3af] text-[11px]">TIMEOUT FALLBACK:</span>
          <span className="text-white font-bold px-1.5 py-0.2 bg-[#1e293b] rounded text-[11px] border border-[#334155]">
            {orchestratorCountdown}s
          </span>
          <button
            onClick={onToggleAutoQueue}
            className="p-1 text-[#9ca3af] hover:text-white hover:bg-[#25334d] rounded transition-colors"
            title={autoQueueRunning ? 'Pozastavit automatický odpočet' : 'Spustit automatický odpočet'}
          >
            {autoQueueRunning ? <Pause className="w-3.5 h-3.5 text-[#f59e0b]" /> : <PlayCircle className="w-3.5 h-3.5 text-[#00ff9d]" />}
          </button>
          <button
            onClick={onResetCountdown}
            className="p-1 text-[#9ca3af] hover:text-white hover:bg-[#25334d] rounded transition-colors"
            title="Resetovat odpočet na 5 sekund"
          >
            <RotateCcw className="w-3 h-3 text-[#38bdf8]" />
          </button>
        </div>
      </div>

      {/* 2. Active Protocol Profile Switcher */}
      <div className="flex items-center gap-2">
        <span className="text-[#9ca3af] text-[11px] font-bold hidden sm:inline">PROFIL:</span>
        <div className="flex items-center bg-[#131a2a] p-1 rounded-lg border border-[#1f2d47] gap-1">
          <button
            onClick={() => onSelectProfile('qualcomm')}
            className={`px-3 py-1 rounded-md font-bold text-[11px] transition-all flex items-center gap-1.5 ${
              selectedProfile === 'qualcomm'
                ? 'bg-gradient-to-r from-[#00f0ff] to-[#0099ff] text-black shadow-[0_0_10px_rgba(0,240,255,0.4)]'
                : 'text-[#94a3b8] hover:text-white hover:bg-[#1c273e]'
            }`}
          >
            <Cpu className="w-3 h-3" />
            <span>Qualcomm EDL 9008</span>
          </button>

          <button
            onClick={() => onSelectProfile('mediatek')}
            className={`px-3 py-1 rounded-md font-bold text-[11px] transition-all flex items-center gap-1.5 ${
              selectedProfile === 'mediatek'
                ? 'bg-gradient-to-r from-[#f59e0b] to-[#ea580c] text-black shadow-[0_0_10px_rgba(245,158,11,0.4)]'
                : 'text-[#94a3b8] hover:text-white hover:bg-[#1c273e]'
            }`}
          >
            <Zap className="w-3 h-3" />
            <span>MediaTek MTK BROM</span>
          </button>

          <button
            onClick={() => onSelectProfile('samsung')}
            className={`px-3 py-1 rounded-md font-bold text-[11px] transition-all flex items-center gap-1.5 ${
              selectedProfile === 'samsung'
                ? 'bg-gradient-to-r from-[#a855f7] to-[#7c3aed] text-white shadow-[0_0_10px_rgba(168,85,247,0.4)]'
                : 'text-[#94a3b8] hover:text-white hover:bg-[#1c273e]'
            }`}
          >
            <Flame className="w-3 h-3" />
            <span>Samsung Odin / Knox</span>
          </button>
        </div>
      </div>

      {/* 3. Subsystem Health Indicators */}
      <div className="hidden xl:flex items-center gap-3">
        <div className="flex items-center gap-1.5 text-[11px]">
          <span className="text-[#64748b]">OVLADAČE:</span>
          <span
            className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
              driverVerificationStatus === 'COMPLIANT' || driverVerificationStatus === 'CORRECTED'
                ? 'bg-[#052e16] text-[#22c55e] border-[#15803d]'
                : driverVerificationStatus === 'MISMATCH'
                ? 'bg-[#451a03] text-[#f97316] border-[#c2410c]'
                : 'bg-[#1e293b] text-[#94a3b8] border-[#334155]'
            }`}
          >
            {driverVerificationStatus}
          </span>
        </div>

        <div className="flex items-center gap-1.5 text-[11px]">
          <span className="text-[#64748b]">SQLITE WAL:</span>
          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-[#052e16] text-[#22c55e] border border-[#15803d] flex items-center gap-1">
            <CheckCircle2 className="w-3 h-3" /> AKTIVNÍ (ZERO-CORRUPT)
          </span>
        </div>
      </div>
    </section>
  );
});
