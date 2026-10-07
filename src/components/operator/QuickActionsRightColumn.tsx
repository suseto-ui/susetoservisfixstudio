import React, { memo } from 'react';
import {
  Zap,
  HardDrive,
  RotateCcw,
  CheckCircle2,
  AlertTriangle,
  Play,
  Unlock,
  ShieldCheck,
  Smartphone,
  Layers,
  Wrench,
  Boxes,
  Database,
  Radio,
  FileCode
} from 'lucide-react';

interface QuickActionsRightColumnProps {
  onSaharaHandshake: () => void;
  onDriverPreflight: () => void;
  onDtrRtsReset: () => void;
  onBackupGpt: () => void;
  onMtkBypass: () => void;
  onFrpBypass: () => void;
  onScreenMirror: () => void;
  onDongleAuth: () => void;
  onSlotSwitch: () => void;
  onBusStressTest: () => void;
  isActionRunning: boolean;
  selectedProfile: string;
  smartCardStatus: string;
  walAuditEntriesCount: number;
}

export const QuickActionsRightColumn: React.FC<QuickActionsRightColumnProps> = memo(function QuickActionsRightColumn({
  onSaharaHandshake,
  onDriverPreflight,
  onDtrRtsReset,
  onBackupGpt,
  onMtkBypass,
  onFrpBypass,
  onScreenMirror,
  onDongleAuth,
  onSlotSwitch,
  onBusStressTest,
  isActionRunning,
  selectedProfile,
  smartCardStatus,
  walAuditEntriesCount
}) {
  return (
    <aside
      id="tour-quickactions-column"
      className="lg:col-span-3 flex flex-col gap-3 font-mono"
    >
      {/* 1. QUICK ACTION HARDWARE BUTTONS GRID */}
      <div className="bg-[#101624] border border-[#1e2a42] rounded-xl p-3.5 space-y-3 shadow-lg">
        <div className="flex items-center justify-between border-b border-[#1b253b] pb-2">
          <div className="flex items-center gap-2">
            <Zap className="w-4 h-4 text-[#f59e0b]" />
            <h3 className="text-xs font-bold text-white uppercase tracking-wider">RYCHLÁ OPERAČNÍ TLAČÍTKA</h3>
          </div>
          <span className="text-[10px] bg-[#291e0a] text-[#f59e0b] px-1.5 py-0.2 rounded font-bold border border-[#f59e0b]/30">
            1-KLIK HW
          </span>
        </div>

        <div className="grid grid-cols-2 gap-2 text-xs">
          <button
            onClick={onSaharaHandshake}
            disabled={isActionRunning}
            className="p-2.5 bg-[#141d2e] hover:bg-[#1f2d47] border border-[#233350] hover:border-[#00f0ff] rounded-lg text-left transition-all group flex flex-col justify-between"
          >
            <div className="text-[#00f0ff] font-bold flex items-center justify-between">
              <span>Sahara Ping</span>
              <Radio className="w-3.5 h-3.5 opacity-70 group-hover:opacity-100" />
            </div>
            <span className="text-[10px] text-[#64748b] mt-1">Hello / Nonce</span>
          </button>

          <button
            onClick={onDriverPreflight}
            disabled={isActionRunning}
            className="p-2.5 bg-[#141d2e] hover:bg-[#1f2d47] border border-[#233350] hover:border-[#38bdf8] rounded-lg text-left transition-all group flex flex-col justify-between"
          >
            <div className="text-[#38bdf8] font-bold flex items-center justify-between">
              <span>Driver Sken</span>
              <Boxes className="w-3.5 h-3.5 opacity-70 group-hover:opacity-100" />
            </div>
            <span className="text-[10px] text-[#64748b] mt-1">QUSB / VCOM</span>
          </button>

          <button
            onClick={onDtrRtsReset}
            disabled={isActionRunning}
            className="p-2.5 bg-[#141d2e] hover:bg-[#1f2d47] border border-[#233350] hover:border-[#f59e0b] rounded-lg text-left transition-all group flex flex-col justify-between"
          >
            <div className="text-[#f59e0b] font-bold flex items-center justify-between">
              <span>DTR/RTS Reset</span>
              <RotateCcw className="w-3.5 h-3.5 opacity-70 group-hover:opacity-100" />
            </div>
            <span className="text-[10px] text-[#64748b] mt-1">Hard Restart</span>
          </button>

          <button
            onClick={onBackupGpt}
            disabled={isActionRunning}
            className="p-2.5 bg-[#141d2e] hover:bg-[#1f2d47] border border-[#233350] hover:border-[#10b981] rounded-lg text-left transition-all group flex flex-col justify-between"
          >
            <div className="text-[#10b981] font-bold flex items-center justify-between">
              <span>Záloha GPT</span>
              <Layers className="w-3.5 h-3.5 opacity-70 group-hover:opacity-100" />
            </div>
            <span className="text-[10px] text-[#64748b] mt-1">LUN0 Header</span>
          </button>

          <button
            onClick={onMtkBypass}
            disabled={isActionRunning}
            className="p-2.5 bg-[#141d2e] hover:bg-[#1f2d47] border border-[#233350] hover:border-[#eab308] rounded-lg text-left transition-all group flex flex-col justify-between"
          >
            <div className="text-[#eab308] font-bold flex items-center justify-between">
              <span>BROM Bypass</span>
              <Zap className="w-3.5 h-3.5 opacity-70 group-hover:opacity-100" />
            </div>
            <span className="text-[10px] text-[#64748b] mt-1">SLA / DAA Auth</span>
          </button>

          <button
            onClick={onFrpBypass}
            disabled={isActionRunning}
            className="p-2.5 bg-[#141d2e] hover:bg-[#1f2d47] border border-[#233350] hover:border-[#f43f5e] rounded-lg text-left transition-all group flex flex-col justify-between"
          >
            <div className="text-[#f43f5e] font-bold flex items-center justify-between">
              <span>FRP Wipe</span>
              <Unlock className="w-3.5 h-3.5 opacity-70 group-hover:opacity-100" />
            </div>
            <span className="text-[10px] text-[#64748b] mt-1">Google Erase</span>
          </button>

          <button
            onClick={onScreenMirror}
            disabled={isActionRunning}
            className="p-2.5 bg-[#141d2e] hover:bg-[#1f2d47] border border-[#233350] hover:border-[#a855f7] rounded-lg text-left transition-all group flex flex-col justify-between"
          >
            <div className="text-[#a855f7] font-bold flex items-center justify-between">
              <span>Screen Mirror</span>
              <Smartphone className="w-3.5 h-3.5 opacity-70 group-hover:opacity-100" />
            </div>
            <span className="text-[10px] text-[#64748b] mt-1">Live Display</span>
          </button>

          <button
            onClick={onDongleAuth}
            disabled={isActionRunning}
            className="p-2.5 bg-[#141d2e] hover:bg-[#1f2d47] border border-[#233350] hover:border-[#00ff9d] rounded-lg text-left transition-all group flex flex-col justify-between"
          >
            <div className="text-[#00ff9d] font-bold flex items-center justify-between">
              <span>Dongle Auth</span>
              <ShieldCheck className="w-3.5 h-3.5 opacity-70 group-hover:opacity-100" />
            </div>
            <span className="text-[10px] text-[#64748b] mt-1">SmartCard v1</span>
          </button>
        </div>
      </div>

      {/* 2. CHIPSET CONTEXT RECOMMENDATION CARD */}
      <div className="bg-[#101624] border border-[#1e2a42] rounded-xl p-3.5 space-y-2.5 shadow-lg">
        <div className="flex items-center justify-between border-b border-[#1b253b] pb-2">
          <div className="flex items-center gap-2">
            <FileCode className="w-4 h-4 text-[#38bdf8]" />
            <h3 className="text-xs font-bold text-white uppercase tracking-wider">DOPORUČENÝ PROTOKOL</h3>
          </div>
          <span className="text-[10px] bg-[#102436] text-[#38bdf8] px-1.5 py-0.2 rounded font-bold">
            {selectedProfile.toUpperCase()}
          </span>
        </div>

        <div className="text-[11px] text-[#cbd5e1] space-y-2">
          {selectedProfile === 'qualcomm' ? (
            <>
              <p className="leading-relaxed">
                Zařízení v režimu <strong>Qualcomm EDL 9008</strong> vyžaduje primární Sahara handshake a následný Firehose ELF loader (NPRG / Prog).
              </p>
              <div className="p-2 bg-[#091522] rounded border border-[#152e47] text-[10px] space-y-1">
                <div className="text-[#38bdf8] font-bold">Tip pro technika:</div>
                <div className="text-[#94a3b8]">
                  Při chybě timeoutu (0x05C6) proveďte hardware testpoint na GND s baterií odpojenou.
                </div>
              </div>
            </>
          ) : selectedProfile === 'mediatek' ? (
            <>
              <p className="leading-relaxed">
                Čipsety <strong>MediaTek Helio/Dimensity</strong> vyžadují bypass SLA/DAA ochrany před odesláním Download Agenta (DA).
              </p>
              <div className="p-2 bg-[#1c1507] rounded border border-[#45340a] text-[10px] space-y-1">
                <div className="text-[#f59e0b] font-bold">Tip pro technika:</div>
                <div className="text-[#94a3b8]">
                  Držte Vol- a Vol+ během zasouvání USB kabelu pro stabilní zachycení BROM režimu.
                </div>
              </div>
            </>
          ) : (
            <>
              <p className="leading-relaxed">
                Režim <strong>Samsung Download / Odin</strong> využívá PIT partition tabulku a CSC region payload.
              </p>
              <div className="p-2 bg-[#1a0f28] rounded border border-[#3c1c5e] text-[10px] space-y-1">
                <div className="text-[#c084fc] font-bold">Tip pro technika:</div>
                <div className="text-[#94a3b8]">
                  Pro odblokování FRP stačí přepsat oddíl <code>persistent</code> na 0x00.
                </div>
              </div>
            </>
          )}
        </div>
      </div>

      {/* 3. AUDIT & STATION STATUS PANEL */}
      <div className="bg-[#101624] border border-[#1e2a42] rounded-xl p-3.5 space-y-2 shadow-lg text-[11px]">
        <div className="flex items-center justify-between border-b border-[#1b253b] pb-2">
          <div className="flex items-center gap-2">
            <Database className="w-4 h-4 text-[#00ff9d]" />
            <h3 className="text-xs font-bold text-white uppercase tracking-wider">STAV PRACOVIŠTĚ & AUDIT</h3>
          </div>
          <span className="text-[10px] text-[#10b981] font-bold">WAL OK</span>
        </div>

        <div className="space-y-1 text-[#94a3b8]">
          <div className="flex justify-between">
            <span>SmartCard Token:</span>
            <span className="text-white font-bold">{smartCardStatus}</span>
          </div>
          <div className="flex justify-between">
            <span>Audit záznamů:</span>
            <span className="text-[#00f0ff] font-bold">{walAuditEntriesCount} operací</span>
          </div>
          <div className="flex justify-between">
            <span>Režim běhu:</span>
            <span className="text-[#00ff9d] font-bold">Hybrid Desktop Kiosk</span>
          </div>
        </div>
      </div>
    </aside>
  );
});
