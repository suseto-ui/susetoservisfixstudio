import React, { memo } from 'react';
import { CloudDownload, RefreshCw, Zap, AlertTriangle, CheckCircle2 } from 'lucide-react';

interface AutoDriverTabProps {
  unassignedDevices: Array<{
    name: string;
    instance_id: string;
    vid: string;
    pid: string;
    recommended_driver: string;
  }>;
  isScanningUnassigned: boolean;
  onScanUnassigned: () => void;
  isAutoInjectingDrivers: boolean;
  onAutoInjectAllDrivers: (force: boolean) => void;
  driverInjectionReport: any;
}

export const AutoDriverTab: React.FC<AutoDriverTabProps> = memo(function AutoDriverTab({
  unassignedDevices,
  isScanningUnassigned,
  onScanUnassigned,
  isAutoInjectingDrivers,
  onAutoInjectAllDrivers,
  driverInjectionReport
}) {
  return (
    <div className="space-y-6 font-mono">
      {/* Header & Main Auto-Inject Bar */}
      <div className="bg-[#111622] border border-[#1f293d] rounded-xl p-5 flex flex-wrap items-center justify-between gap-4 shadow-lg">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-[#00f0ff]/10 border border-[#00f0ff]/30 text-[#00f0ff] flex items-center justify-center">
            <CloudDownload className="w-5 h-5 text-[#00f0ff]" />
          </div>
          <div>
            <h3 className="font-bold text-white text-base flex items-center gap-2">
              <span>DRIVER AUTO-INJECTOR & SILENT INSTALLER</span>
              <span className="text-[11px] px-2 py-0.5 bg-[#00f0ff]/10 text-[#00f0ff] rounded border border-[#00f0ff]/30 font-bold">
                SETUPAPI & PNPUTIL
              </span>
            </h3>
            <p className="text-xs text-[#9ca3af]">
              Automatické vyhledání neznámých zařízení (Kód 28), generování WinUSB INF a tichá instalace bez restartu PC
            </p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2.5">
          <button
            onClick={onScanUnassigned}
            disabled={isScanningUnassigned}
            className="px-4 py-2 bg-[#1e293b] hover:bg-[#334155] text-white font-bold text-xs rounded-lg flex items-center gap-1.5 transition-all border border-[#334155]"
          >
            <RefreshCw className={`w-3.5 h-3.5 text-[#00f0ff] ${isScanningUnassigned ? 'animate-spin' : ''}`} />
            <span>{isScanningUnassigned ? 'Skenuji...' : 'Skenovat Code 28'}</span>
          </button>

          <button
            onClick={() => onAutoInjectAllDrivers(false)}
            disabled={isAutoInjectingDrivers}
            className="px-5 py-2 bg-gradient-to-r from-[#00f0ff] to-[#00ff9d] hover:opacity-95 text-black font-black text-xs rounded-lg flex items-center gap-1.5 transition-all shadow-[0_0_15px_rgba(0,240,255,0.3)]"
            title="Před instalací ověří DriverStore a PnP zařízení. Pokud je identický ovladač přítomen, instalaci bezpečně přeskočí."
          >
            <Zap className={`w-3.5 h-3.5 ${isAutoInjectingDrivers ? 'animate-spin' : ''}`} />
            <span>{isAutoInjectingDrivers ? 'Provádím audit a instalaci...' : '⚡ 1-Klik Tichá Instalace (s Pre-Flight)'}</span>
          </button>

          <button
            onClick={() => onAutoInjectAllDrivers(true)}
            disabled={isAutoInjectingDrivers}
            className="px-3.5 py-2 bg-[#1a2333] hover:bg-[#253248] text-[#9ca3af] hover:text-white font-bold text-xs rounded-lg flex items-center gap-1.5 transition-all border border-[#2d3b55]"
            title="Vynutí přepsání a znovuzavedení ovladače bez ohledu na stávající stav v DriverStore"
          >
            <span>Vynutit přeinstalaci</span>
          </button>
        </div>
      </div>

      {/* Unassigned Devices List */}
      <div className="bg-[#0a0d14] border border-[#1f293d] rounded-xl p-5 space-y-4 shadow-md">
        <div className="flex items-center justify-between border-b border-[#1f293d] pb-3 text-xs">
          <div className="flex items-center gap-2 text-white font-bold">
            <AlertTriangle className="w-4 h-4 text-[#ffaa00]" />
            <span>Neznámá zařízení vyžadující injekci ovladače ({unassignedDevices.length})</span>
          </div>
          <span className="text-[11px] text-[#6b7280]">Zdroj: Windows SetupAPI / CfgMgr32</span>
        </div>

        <div className="space-y-3">
          {unassignedDevices.map((dev, idx) => (
            <div key={idx} className="bg-[#111622] border border-[#1f293d] rounded-xl p-4 flex flex-wrap items-center justify-between gap-4">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="px-2 py-0.5 bg-[#ffaa00]/10 text-[#ffaa00] border border-[#ffaa00]/30 rounded text-[10px] font-bold">
                    KÓD 28
                  </span>
                  <span className="text-white font-bold text-sm">{dev.name}</span>
                </div>
                <div className="text-xs text-[#9ca3af] font-mono">
                  Instance ID: <span className="text-[#00f0ff]">{dev.instance_id}</span>
                </div>
                <div className="text-xs text-[#6b7280]">
                  VID: <strong className="text-white">{dev.vid}</strong> | PID: <strong className="text-white">{dev.pid}</strong> ➔ Doporučený ovladač: <strong className="text-[#00ff9d]">{dev.recommended_driver}</strong>
                </div>
              </div>

              <button
                onClick={() => onAutoInjectAllDrivers(false)}
                disabled={isAutoInjectingDrivers}
                className="px-3.5 py-1.5 bg-[#00f0ff]/10 hover:bg-[#00f0ff]/20 text-[#00f0ff] border border-[#00f0ff]/40 rounded-lg text-xs font-bold transition-all"
              >
                Injektovat WinUSB
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Injection Report */}
      {driverInjectionReport && (
        <div className="bg-[#07090e] border border-[#00ff9d]/40 rounded-xl p-5 space-y-3 text-xs shadow-md">
          <div className="flex items-center justify-between border-b border-[#1f293d] pb-2 text-xs">
            <span className="text-[#00ff9d] font-bold flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4" /> Výsledek instalace a pre-flight kontroly
            </span>
            <span className="text-[#00ff9d] font-bold">{driverInjectionReport.status}</span>
          </div>

          {/* Pre-Flight Metric Counters */}
          <div className="flex flex-wrap items-center gap-4 text-xs font-mono text-[#9ca3af] bg-[#0a0d14] p-3 rounded-lg border border-[#1f293d]">
            <span>Zpracováno: <strong className="text-white">{driverInjectionReport.devices_processed}</strong></span>
            <span className="text-[#374151]">·</span>
            <span>Nainstalováno nově: <strong className="text-[#00f0ff]">{driverInjectionReport.devices_installed ?? 0}</strong></span>
            <span className="text-[#374151]">·</span>
            <span>Přeskočeno (identické nalezeno): <strong className="text-[#00ff9d]">{driverInjectionReport.devices_skipped ?? 0}</strong></span>
          </div>

          <div className="space-y-2">
            {driverInjectionReport.results?.map((res: any, i: number) => {
              const isSkipped = res.install_result?.status === 'SKIPPED_IDENTICAL';
              const isInstalled = res.install_result?.status === 'INSTALLED';
              return (
                <div key={i} className="p-3 bg-[#0a0d14] rounded-lg border border-[#1f293d] space-y-1">
                  <div className="flex items-center justify-between">
                    <div className="text-white font-bold">{res.device} [VID: {res.vid}, PID: {res.pid}]</div>
                    {isSkipped ? (
                      <span className="px-2 py-0.5 bg-[#00ff9d]/10 text-[#00ff9d] border border-[#00ff9d]/30 rounded text-[10px] font-bold">
                        JIŽ INSTALOVÁNO (PŘESKOČENO)
                      </span>
                    ) : isInstalled ? (
                      <span className="px-2 py-0.5 bg-[#00f0ff]/10 text-[#00f0ff] border border-[#00f0ff]/30 rounded text-[10px] font-bold">
                        NOVĚ NAINSTALOVÁNO
                      </span>
                    ) : (
                      <span className="px-2 py-0.5 bg-[#ff3366]/10 text-[#ff3366] border border-[#ff3366]/30 rounded text-[10px] font-bold">
                        CHYBA
                      </span>
                    )}
                  </div>
                  <div className="text-[#9ca3af]">{res.install_result?.message}</div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
});
