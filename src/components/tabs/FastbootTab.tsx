import React, { memo } from 'react';
import { Zap, Layers, CheckCircle2 } from 'lucide-react';
import { FASTBOOT_PARTITION_CATALOG } from '../../services/fastbootEngine';

interface FastbootTabProps {
  fastbootActiveSlot: 'a' | 'b';
  onSlotSwitch: (slot: 'a' | 'b') => void;
  fastbootSelectedPartition: string;
  onSelectPartition: (part: string) => void;
  onFlashPartition: (partName: string) => void;
  isFastbootFlashing: boolean;
  fastbootLogMsg: string | null;
}

export const FastbootTab: React.FC<FastbootTabProps> = memo(function FastbootTab({
  fastbootActiveSlot,
  onSlotSwitch,
  fastbootSelectedPartition,
  onSelectPartition,
  onFlashPartition,
  isFastbootFlashing,
  fastbootLogMsg
}) {
  return (
    <div className="space-y-6 font-mono">
      {/* Header */}
      <div className="bg-[#111622] border border-[#1f293d] rounded-xl p-5 flex flex-wrap items-center justify-between gap-4 shadow-lg">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-[#00f0ff]/10 border border-[#00f0ff]/30 text-[#00f0ff] flex items-center justify-center">
            <Zap className="w-5 h-5 text-[#00f0ff]" />
          </div>
          <div>
            <h3 className="font-bold text-white text-base flex items-center gap-2">
              <span>FASTBOOT FLASH WIZARD & A/B SLOT SWITCHER</span>
              <span className="text-[11px] px-2 py-0.5 bg-[#00f0ff]/10 text-[#00f0ff] rounded border border-[#00f0ff]/30 font-bold">
                FASTBOOT ENGINE
              </span>
            </h3>
            <p className="text-xs text-[#9ca3af]">
              Zápis systémových oddílů (boot, recovery, vbmeta, super), správa bootovacích slotů A/B a odemykání bootloaderu
            </p>
          </div>
        </div>

        {/* Slot Switcher Buttons */}
        <div className="flex items-center gap-2 bg-[#0a0d14] p-1.5 rounded-lg border border-[#1f293d]">
          <span className="text-xs text-[#6b7280] px-2">Aktivní slot:</span>
          <button
            onClick={() => onSlotSwitch('a')}
            className={`px-3 py-1 text-xs font-bold rounded transition-all ${
              fastbootActiveSlot === 'a'
                ? 'bg-[#00f0ff] text-black shadow-[0_0_10px_rgba(0,240,255,0.4)]'
                : 'bg-[#1e293b] text-[#9ca3af] hover:text-white'
            }`}
          >
            Slot A
          </button>
          <button
            onClick={() => onSlotSwitch('b')}
            className={`px-3 py-1 text-xs font-bold rounded transition-all ${
              fastbootActiveSlot === 'b'
                ? 'bg-[#00f0ff] text-black shadow-[0_0_10px_rgba(0,240,255,0.4)]'
                : 'bg-[#1e293b] text-[#9ca3af] hover:text-white'
            }`}
          >
            Slot B
          </button>
        </div>
      </div>

      {/* Fastboot Partition Catalog */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {FASTBOOT_PARTITION_CATALOG.map(part => (
          <div
            key={part.name}
            onClick={() => onSelectPartition(part.name)}
            className={`p-4 rounded-xl border transition-all cursor-pointer space-y-2.5 ${
              fastbootSelectedPartition === part.name
                ? 'bg-[#00f0ff]/10 border-[#00f0ff] shadow-[0_0_15px_rgba(0,240,255,0.2)]'
                : 'bg-[#0a0d14] border-[#1f293d] hover:border-[#374151]'
            }`}
          >
            <div className="flex items-center justify-between">
              <span className="text-sm font-bold text-white flex items-center gap-1.5">
                <Layers className="w-4 h-4 text-[#00f0ff]" /> {part.label}
              </span>
              <span
                className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                  part.critical
                    ? 'bg-[#ff3366]/10 text-[#ff3366] border border-[#ff3366]/30'
                    : 'bg-[#00ff9d]/10 text-[#00ff9d] border border-[#00ff9d]/30'
                }`}
              >
                {part.critical ? 'KRITICKÝ' : 'VOLITELNÝ'}
              </span>
            </div>

            <div className="text-xs text-[#9ca3af]">{part.description}</div>
            <div className="flex items-center justify-between text-xs text-[#6b7280] pt-1 border-t border-[#1f293d]">
              <span>
                Oddíl: <strong className="text-white">{part.name}_{fastbootActiveSlot}</strong>
              </span>
              <span>Velikost: ~{part.typicalSizeMB} MB</span>
            </div>

            <button
              onClick={(e) => {
                e.stopPropagation();
                onFlashPartition(part.name);
              }}
              disabled={isFastbootFlashing}
              className="w-full mt-2 py-2 bg-[#1e293b] hover:bg-[#334155] text-[#00f0ff] border border-[#00f0ff]/30 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-1.5"
            >
              <Zap className="w-3.5 h-3.5" />
              <span>Flashovat {part.name}</span>
            </button>
          </div>
        ))}
      </div>

      {/* Fastboot Flash Output */}
      {fastbootLogMsg && (
        <div className="p-4 bg-[#00ff9d]/10 border border-[#00ff9d]/40 rounded-xl text-xs text-[#00ff9d] font-bold flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-[#00ff9d]" />
          <span>{fastbootLogMsg}</span>
        </div>
      )}
    </div>
  );
});
