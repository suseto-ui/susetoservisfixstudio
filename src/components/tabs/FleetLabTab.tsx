import React, { memo } from 'react';
import { Boxes, UserCheck, Wifi, Activity, Shield } from 'lucide-react';
import { StationItem } from '../../types/operator';

interface FleetLabTabProps {
  stations: StationItem[];
  remoteSessionId: string;
  isRemoteActive: boolean;
  onToggleRemoteSession: () => void;
  onConnectStation: (stationId: string) => void;
}

export const FleetLabTab: React.FC<FleetLabTabProps> = memo(function FleetLabTab({
  stations,
  remoteSessionId,
  isRemoteActive,
  onToggleRemoteSession,
  onConnectStation
}) {
  return (
    <div className="space-y-6 font-mono">
      {/* Header */}
      <div className="bg-[#111622] border border-[#1f293d] rounded-xl p-5 flex flex-wrap items-center justify-between gap-4 shadow-lg">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-[#00f0ff]/10 border border-[#00f0ff]/30 text-[#00f0ff] flex items-center justify-center">
            <Boxes className="w-5 h-5 text-[#00f0ff]" />
          </div>
          <div>
            <h3 className="font-bold text-white text-base flex items-center gap-2">
              <span>FLEET LAB & MULTI-STATION MANAGEMENT</span>
              <span className="text-[11px] px-2 py-0.5 bg-[#00f0ff]/10 text-[#00f0ff] rounded border border-[#00f0ff]/30 font-bold">
                ENTERPRISE LAB
              </span>
            </h3>
            <p className="text-xs text-[#9ca3af]">
              Vzdálené sdílení USB relací, koordinace servisních stanic a řízení rolí (Supervisor / Technician)
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={onToggleRemoteSession}
            className={`px-4 py-2 font-bold text-xs rounded-lg flex items-center gap-2 transition-all ${
              isRemoteActive
                ? 'bg-[#00ff9d] text-black shadow-[0_0_15px_rgba(0,255,157,0.3)]'
                : 'bg-[#1e293b] text-white hover:bg-[#334155] border border-[#334155]'
            }`}
          >
            <Wifi className="w-3.5 h-3.5" />
            <span>{isRemoteActive ? `Relace aktivní: ${remoteSessionId}` : 'Zahájit vzdálené sdílení'}</span>
          </button>
        </div>
      </div>

      {/* Stations List */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {stations.map(st => (
          <div
            key={st.id}
            className="bg-[#0a0d14] border border-[#1f293d] rounded-xl p-5 space-y-3 shadow-md"
          >
            <div className="flex items-center justify-between">
              <span className="font-bold text-white text-sm truncate flex items-center gap-2">
                <UserCheck className="w-4 h-4 text-[#00ff9d]" />
                {st.name}
              </span>
              <span
                className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                  st.status === 'ONLINE'
                    ? 'bg-[#00ff9d]/10 text-[#00ff9d] border-[#00ff9d]/30'
                    : st.status === 'BUSY'
                    ? 'bg-[#ffaa00]/10 text-[#ffaa00] border-[#ffaa00]/30'
                    : 'bg-[#64748b]/10 text-[#64748b] border-[#64748b]/30'
                }`}
              >
                {st.status}
              </span>
            </div>

            <div className="text-xs text-[#9ca3af] space-y-1">
              <div>Operátor: <strong className="text-white">{st.user}</strong></div>
              <div>HWID: <strong className="text-[#38bdf8] font-mono">{st.hwid}</strong></div>
              <div>Role: <strong className="text-[#00f0ff]">{st.role}</strong></div>
              <div>Aktivita: <strong className="text-[#9ca3af]">{st.lastSeen}</strong></div>
            </div>

            <div className="pt-2 border-t border-[#1f293d] flex items-center justify-between">
              <span className="text-[10px] text-[#6b7280]">P2P WebRTC Šifrování</span>
              <button
                onClick={() => onConnectStation(st.id)}
                className="px-3 py-1.5 bg-[#1e293b] hover:bg-[#334155] text-white border border-[#334155] rounded-lg text-xs font-bold transition-all"
              >
                Připojit k relaci
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
});
