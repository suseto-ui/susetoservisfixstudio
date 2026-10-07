import React, { memo } from 'react';
import { HardDrive, AlertTriangle, Binary, Play } from 'lucide-react';

interface MemoryRecoveryTabProps {
  onExtractCrashdump: () => void;
  isCrashdumping: boolean;
  streamDumpPartition: string;
  onStreamDumpPartitionChange: (part: string) => void;
  streamDumpSizeKB: number;
  onStreamDumpSizeKBChange: (size: number) => void;
  onStartStreamingDump: () => void;
  isStreamingDump: boolean;
  streamingProgress: {
    bytes: number;
    total: number;
    speedKbs: number;
    crc32: string;
  } | null;
  streamDumpResult: any;
  crashdumpResult: any;
}

export const MemoryRecoveryTab: React.FC<MemoryRecoveryTabProps> = memo(function MemoryRecoveryTab({
  onExtractCrashdump,
  isCrashdumping,
  streamDumpPartition,
  onStreamDumpPartitionChange,
  streamDumpSizeKB,
  onStreamDumpSizeKBChange,
  onStartStreamingDump,
  isStreamingDump,
  streamingProgress,
  streamDumpResult,
  crashdumpResult
}) {
  return (
    <div className="space-y-6 font-mono">
      {/* Header */}
      <div className="bg-[#111622] border border-[#1f293d] rounded-xl p-5 flex flex-wrap items-center justify-between gap-4 shadow-lg">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-[#00ff9d]/10 border border-[#00ff9d]/30 text-[#00ff9d] flex items-center justify-center">
            <HardDrive className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-bold text-white text-base flex items-center gap-2">
              <span>MEMORY RECOVERY AGENT & 4KB STREAM DUMP</span>
              <span className="text-[11px] px-2 py-0.5 bg-[#00ff9d]/10 text-[#00ff9d] rounded border border-[#00ff9d]/30 font-bold">
                STREAMING I/O
              </span>
            </h3>
            <p className="text-xs text-[#9ca3af]">
              Nouzová záchrana RAM a registrů CPU před restartem + blokové čtení paměti (4096 B) s měřením kB/s a CRC32
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={onExtractCrashdump}
            disabled={isCrashdumping}
            className="px-4 py-2 bg-[#ff3366] hover:bg-[#ff4d79] text-white font-bold text-xs rounded-lg flex items-center gap-1.5 transition-all shadow-[0_0_15px_rgba(255,51,102,0.3)]"
          >
            <AlertTriangle className={`w-3.5 h-3.5 ${isCrashdumping ? 'animate-spin' : ''}`} />
            <span>{isCrashdumping ? 'Vytahuji Crashdump...' : '🚨 Nouzová extrakce RAM & Registrů'}</span>
          </button>
        </div>
      </div>

      {/* 4KB Block Streaming Dump Cockpit */}
      <div className="bg-[#0a0d14] border border-[#1f293d] rounded-xl p-5 space-y-4 shadow-md">
        <div className="flex flex-wrap items-center justify-between border-b border-[#1f293d] pb-3 gap-3">
          <div className="flex items-center gap-2 text-white font-bold text-sm">
            <Binary className="w-4 h-4 text-[#00f0ff]" />
            <span>Blokový Streaming Dump (4096 B na sektor)</span>
          </div>
          <div className="flex flex-wrap items-center gap-3 text-xs">
            <div className="flex items-center gap-1.5">
              <span className="text-[#9ca3af]">Oddíl:</span>
              <select
                value={streamDumpPartition}
                onChange={e => onStreamDumpPartitionChange(e.target.value)}
                className="px-2.5 py-1 bg-[#111622] border border-[#1f293d] rounded text-[#00f0ff] font-bold outline-none"
              >
                <option value="boot">boot (Kernel Image)</option>
                <option value="recovery">recovery</option>
                <option value="persist">persist (Sensors & DRM)</option>
                <option value="nvram">nvram (Radio Calibration)</option>
              </select>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="text-[#9ca3af]">Velikost:</span>
              <select
                value={streamDumpSizeKB}
                onChange={e => onStreamDumpSizeKBChange(Number(e.target.value))}
                className="px-2.5 py-1 bg-[#111622] border border-[#1f293d] rounded text-[#00ff9d] font-bold outline-none"
              >
                <option value="32">32 KB (8 bloků)</option>
                <option value="64">64 KB (16 bloků)</option>
                <option value="256">256 KB (64 bloků)</option>
                <option value="1024">1024 KB (256 bloků)</option>
              </select>
            </div>
            <button
              onClick={onStartStreamingDump}
              disabled={isStreamingDump}
              className="px-4 py-1.5 bg-[#00f0ff] hover:bg-[#33f3ff] text-black font-bold rounded flex items-center gap-1.5 shadow-[0_0_10px_rgba(0,240,255,0.3)] transition-all"
            >
              <Play className="w-3.5 h-3.5" />
              <span>{isStreamingDump ? 'Čtu bloky...' : 'Zahájit Streaming Dump'}</span>
            </button>
          </div>
        </div>

        {/* Live Progress & Speedometer */}
        {streamingProgress && (
          <div className="p-4 bg-[#07090e] rounded-lg border border-[#161f30] space-y-3">
            <div className="flex flex-wrap items-center justify-between text-xs gap-2">
              <span className="text-[#9ca3af]">
                Streamováno: <strong className="text-white">{streamingProgress.bytes}</strong> / {streamingProgress.total} B
              </span>
              <span className="text-[#00ff9d] font-bold">
                Rychlost: {streamingProgress.speedKbs} kB/s ({(streamingProgress.speedKbs / 1024).toFixed(2)} MB/s)
              </span>
              <span className="text-[#00f0ff] font-mono font-bold">
                CRC32: {streamingProgress.crc32}
              </span>
            </div>
            <div className="w-full bg-[#161f30] h-2.5 rounded-full overflow-hidden">
              <div
                className="bg-gradient-to-r from-[#00f0ff] to-[#00ff9d] h-full transition-all duration-150"
                style={{ width: `${Math.min(100, (streamingProgress.bytes / streamingProgress.total) * 100)}%` }}
              />
            </div>
          </div>
        )}

        {/* Dump Result & Integrity Checksums */}
        {streamDumpResult && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2 text-xs">
            <div className="p-3 bg-[#07090e] rounded border border-[#1f293d]">
              <div className="text-[#6b7280]">Výstupní soubor:</div>
              <div className="text-white font-bold truncate mt-0.5">{streamDumpResult.file_name}</div>
            </div>
            <div className="p-3 bg-[#07090e] rounded border border-[#1f293d]">
              <div className="text-[#6b7280]">Kontrolní součet CRC32:</div>
              <div className="text-[#00ff9d] font-bold mt-0.5">{streamDumpResult.checksums.crc32}</div>
            </div>
            <div className="p-3 bg-[#07090e] rounded border border-[#1f293d]">
              <div className="text-[#6b7280]">SHA-256 Integrita:</div>
              <div className="text-[#00f0ff] font-bold truncate mt-0.5">{streamDumpResult.checksums.sha256}</div>
            </div>
          </div>
        )}
      </div>

      {/* Emergency Crashdump & Registers Inspection */}
      {crashdumpResult && (
        <div className="bg-[#0a0d14] border border-[#ff3366]/40 rounded-xl p-5 space-y-4 shadow-md">
          <div className="flex items-center justify-between border-b border-[#1f293d] pb-3 text-xs">
            <span className="text-[#ff3366] font-bold flex items-center gap-2">
              <AlertTriangle className="w-4 h-4" /> Zachycený stav zhavarovaného CPU (ID: {crashdumpResult.dump_id})
            </span>
            <span className="text-[#9ca3af]">Velikost RAM: {crashdumpResult.ram_size_bytes} B</span>
          </div>

          <div className="p-3 bg-[#1f0f14] rounded border border-[#ff3366]/30 text-xs text-[#ff99aa]">
            <strong>Důvod havárie (Kernel Panic):</strong> {crashdumpResult.panic_reason}
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
            {Object.entries(crashdumpResult.registers || {}).map(([k, v]) => (
              <div key={k} className="p-2 bg-[#07090e] rounded border border-[#1f293d]">
                <div className="text-[#6b7280] text-[10px]">{k}</div>
                <div className="text-[#00ff9d] font-bold truncate">{String(v)}</div>
              </div>
            ))}
          </div>

          <div className="space-y-1">
            <div className="text-xs text-[#9ca3af] font-bold">Call Stack Backtrace:</div>
            <div className="p-3 bg-[#040609] rounded border border-[#161f30] text-xs text-[#00f0ff] space-y-1">
              {crashdumpResult.call_stack?.map((frame: string, idx: number) => (
                <div key={idx}># {frame}</div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
});
