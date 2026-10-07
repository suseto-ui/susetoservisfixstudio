import React, { memo } from 'react';
import { Flame } from 'lucide-react';
import { ParsedGptPartition } from '../../services/gptParser';

interface FrpUnlockTabProps {
  selectedPartition: ParsedGptPartition;
  activeChipset: 'qualcomm' | 'mediatek' | 'samsung' | 'unisoc';
  onSelectChipset: (chipset: 'qualcomm' | 'mediatek' | 'samsung' | 'unisoc') => void;
  isFRPInProgress: boolean;
  frpProgress: number;
  onExecute1ClickFRP: () => void;
}

export const FrpUnlockTab: React.FC<FrpUnlockTabProps> = memo(function FrpUnlockTab({
  selectedPartition,
  activeChipset,
  onSelectChipset,
  isFRPInProgress,
  frpProgress,
  onExecute1ClickFRP
}) {
  return (
    <div className="bg-[#111622] border border-[#1f293d] rounded-xl p-6 space-y-6 font-mono shadow-md">
      <div className="flex flex-wrap items-center justify-between border-b border-[#1f293d] pb-4 gap-3">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Flame className="w-5 h-5 text-[#ff3366]" />
            Reálný 1-Click FRP & Bootloader Service Engine
          </h2>
          <p className="text-xs text-[#6b7280] mt-1">
            Bezpečný výmaz persistentních bloků Google/OEM účtu s kontrolou bezpečnostních pojistek (Security Interlock).
          </p>
        </div>
        <div className="px-3 py-1 bg-[#00f0ff]/10 text-[#00f0ff] border border-[#00f0ff]/30 rounded text-xs font-bold">
          Aktivní cíl: {selectedPartition.name} ({selectedPartition.sizeMB} MB)
        </div>
      </div>

      {/* Chipset Selection Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {[
          { id: 'qualcomm', label: 'Qualcomm Snapdragon', mode: 'EDL 9008 (Firehose)' },
          { id: 'mediatek', label: 'MediaTek Dimensity/Helio', mode: 'BROM (DAA/SLA Bypass)' },
          { id: 'samsung', label: 'Samsung Exynos/Qualcomm', mode: 'MTP / Modem AT (*#0*#)' },
          { id: 'unisoc', label: 'Unisoc / Spreadtrum', mode: 'FDL1 / FDL2 Bootloader' }
        ].map(chip => (
          <button
            key={chip.id}
            onClick={() => onSelectChipset(chip.id as any)}
            className={`p-4 rounded-xl border text-left transition-all ${
              activeChipset === chip.id
                ? 'bg-[#00f0ff]/10 border-[#00f0ff] text-white shadow-[0_0_15px_rgba(0,240,255,0.2)]'
                : 'bg-[#0a0d14] border-[#1f293d] text-[#6b7280] hover:border-[#374151]'
            }`}
          >
            <div className="text-xs font-bold text-white">{chip.label}</div>
            <div className="text-[11px] text-[#00f0ff] mt-1">{chip.mode}</div>
          </button>
        ))}
      </div>

      {/* Execution Box */}
      <div className="bg-[#0a0d14] border border-[#1f293d] rounded-xl p-6 space-y-4">
        {isFRPInProgress && (
          <div className="space-y-2">
            <div className="flex justify-between text-xs text-[#00f0ff]">
              <span>Probíhá fyzický zápis nulového vzoru do sektoru {selectedPartition.startSector}...</span>
              <span>{frpProgress}%</span>
            </div>
            <div className="w-full bg-[#1f293d] h-2.5 rounded-full overflow-hidden">
              <div
                className="bg-gradient-to-r from-[#00f0ff] to-[#00ff9d] h-full transition-all duration-300"
                style={{ width: `${frpProgress}%` }}
              />
            </div>
          </div>
        )}

        <div className="pt-2 flex flex-wrap gap-4 items-center justify-between">
          <div className="text-xs text-[#6b7280]">
            Hardwarová pojistka: <strong className="text-[#00ff9d]">AKTIVNÍ</strong> (Bootloader oddíly jsou chráněny)
          </div>
          <button
            disabled={isFRPInProgress}
            onClick={onExecute1ClickFRP}
            className="px-6 py-3 bg-gradient-to-r from-[#ff3366] to-[#ffaa00] text-black font-black text-sm rounded-lg hover:opacity-95 transition-all shadow-[0_0_15px_rgba(255,51,102,0.4)] disabled:opacity-50 flex items-center gap-2"
          >
            <Flame className="w-4 h-4" />
            <span>{isFRPInProgress ? 'Vynulovávám FRP...' : '⚡ Spustit 1-Click FRP výmaz'}</span>
          </button>
        </div>
      </div>
    </div>
  );
});
