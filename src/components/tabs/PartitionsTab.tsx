import React, { memo } from 'react';
import { Layers, Lock, Unlock, ShieldAlert, X, Binary } from 'lucide-react';
import { ParsedGptPartition, GptHeaderInfo } from '../../services/gptParser';

interface PartitionsTabProps {
  gptInfo: GptHeaderInfo;
  selectedPartition: ParsedGptPartition;
  onSelectPartition: (p: ParsedGptPartition) => void;
  interlockAlert: string | null;
  onClearInterlockAlert: () => void;
  onPartitionAction: (action: 'READ' | 'WRITE' | 'ERASE') => void;
  onBackupGpt: () => void;
  hexOffset: string;
  onHexOffsetChange: (offset: string) => void;
  onExportBinaryDump: () => void;
  hexDumpRows: Array<{ addr: string; hexBytes: string; asciiChars: string }>;
}

export const PartitionsTab: React.FC<PartitionsTabProps> = memo(function PartitionsTab({
  gptInfo,
  selectedPartition,
  onSelectPartition,
  interlockAlert,
  onClearInterlockAlert,
  onPartitionAction,
  onBackupGpt,
  hexOffset,
  onHexOffsetChange,
  onExportBinaryDump,
  hexDumpRows
}) {
  return (
    <div className="space-y-6 font-mono">
      {interlockAlert && (
        <div className="bg-[#ff3366]/10 border border-[#ff3366] text-[#ff3366] p-4 rounded-xl flex items-start gap-3 text-xs shadow-lg">
          <ShieldAlert className="w-5 h-5 shrink-0 mt-0.5" />
          <div className="flex-1">{interlockAlert}</div>
          <button onClick={onClearInterlockAlert} className="text-[#ff3366] hover:text-white">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Partition Table List */}
        <div className="bg-[#111622] border border-[#1f293d] rounded-xl p-5 space-y-4 shadow-md">
          <div className="flex items-center justify-between border-b border-[#1f293d] pb-3">
            <div className="flex items-center gap-2">
              <Layers className="w-4 h-4 text-[#00f0ff]" />
              <h3 className="font-bold text-sm text-white">GPT Tabulka ({gptInfo.partitions.length} oddílů)</h3>
            </div>
            <button
              onClick={onBackupGpt}
              className="text-[11px] px-2.5 py-1 bg-[#1e293b] hover:bg-[#334155] text-[#00f0ff] rounded transition-colors"
            >
              Zálohovat GPT
            </button>
          </div>

          <div className="space-y-1.5 max-h-[420px] overflow-y-auto pr-1">
            {gptInfo.partitions.map(part => (
              <div
                key={part.id}
                onClick={() => onSelectPartition(part)}
                className={`p-2.5 rounded-lg border text-xs cursor-pointer transition-all flex items-center justify-between ${
                  selectedPartition.id === part.id
                    ? 'bg-[#00f0ff]/10 border-[#00f0ff] text-white shadow-[0_0_10px_rgba(0,240,255,0.2)]'
                    : 'bg-[#0a0d14] border-[#1f293d] text-[#9ca3af] hover:border-[#374151]'
                }`}
              >
                <div className="flex items-center gap-2">
                  {part.isProtected ? (
                    <Lock className="w-3.5 h-3.5 text-[#ff3366]" />
                  ) : (
                    <Unlock className="w-3.5 h-3.5 text-[#00ff9d]" />
                  )}
                  <span className="font-bold text-white">{part.name}</span>
                </div>
                <div className="text-[11px] text-[#6b7280]">{part.sizeMB} MB</div>
              </div>
            ))}
          </div>

          <div className="pt-3 border-t border-[#1f293d] grid grid-cols-3 gap-2">
            <button
              onClick={() => onPartitionAction('READ')}
              className="py-2 bg-[#1e293b] hover:bg-[#334155] text-white text-xs font-bold rounded transition-colors"
            >
              Číst
            </button>
            <button
              onClick={() => onPartitionAction('WRITE')}
              className="py-2 bg-[#0e639c] hover:bg-[#1177bb] text-white text-xs font-bold rounded transition-colors"
            >
              Zapsat
            </button>
            <button
              onClick={() => onPartitionAction('ERASE')}
              className="py-2 bg-[#ff3366]/20 hover:bg-[#ff3366]/30 text-[#ff3366] text-xs font-bold rounded transition-colors border border-[#ff3366]/40"
            >
              Smazat
            </button>
          </div>
        </div>

        {/* Interactive Hex Viewer */}
        <div className="lg:col-span-2 bg-[#0d111a] border border-[#1f293d] rounded-xl p-5 flex flex-col shadow-md">
          <div className="flex flex-wrap items-center justify-between border-b border-[#1f293d] pb-3 mb-3 gap-2">
            <div className="flex items-center gap-2">
              <Binary className="w-4 h-4 text-[#00ff9d]" />
              <h3 className="font-bold text-sm text-white">Live Hex / Memory Stream Inspector</h3>
            </div>
            <div className="flex items-center gap-2">
              <input
                type="text"
                value={hexOffset}
                onChange={e => onHexOffsetChange(e.target.value)}
                placeholder="0x00000000"
                className="px-2 py-1 bg-[#111622] border border-[#1f293d] rounded text-xs text-[#00f0ff] w-28 outline-none"
              >
              </input>
              <button
                onClick={onExportBinaryDump}
                className="px-2.5 py-1 bg-[#00ff9d]/10 text-[#00ff9d] border border-[#00ff9d]/30 rounded text-xs font-bold hover:bg-[#00ff9d]/20 transition-colors"
              >
                Exportovat .bin
              </button>
            </div>
          </div>

          <div className="flex-1 bg-[#07090e] rounded-lg p-3 text-xs overflow-x-auto border border-[#161f30] max-h-[440px]">
            <div className="text-[#6b7280] pb-2 border-b border-[#1a2333] mb-2 flex justify-between">
              <span>Offset</span>
              <span>00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F</span>
              <span>ASCII Decoded</span>
            </div>
            {hexDumpRows.map((row, idx) => (
              <div key={idx} className="flex justify-between py-0.5 hover:bg-white/5 transition-colors">
                <span className="text-[#00f0ff]">{row.addr}</span>
                <span className="text-[#d4d4d4] font-medium tracking-wider">{row.hexBytes}</span>
                <span className="text-[#00ff9d] font-bold">{row.asciiChars}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
});
