import React, { memo } from 'react';
import { Radio, FileUp, Terminal } from 'lucide-react';
import { SerialDeviceDescriptor } from '../../services/webSerialEngine';

interface OverviewTabProps {
  isPortOpen: boolean;
  pairedPort: SerialDeviceDescriptor | null;
  baudRate: number;
  onBaudRateChange: (baud: number) => void;
  onFileUpload: (e: React.ChangeEvent<HTMLInputElement>) => void;
  terminalLogs: string[];
  onClearLogs: () => void;
}

export const OverviewTab: React.FC<OverviewTabProps> = memo(function OverviewTab({
  isPortOpen,
  pairedPort,
  baudRate,
  onBaudRateChange,
  onFileUpload,
  terminalLogs,
  onClearLogs
}) {
  return (
    <div className="space-y-6 font-mono">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Physical Port Controller */}
        <div className="bg-[#111622] border border-[#1f293d] rounded-xl p-5 space-y-4 font-mono shadow-md">
          <div className="flex items-center justify-between border-b border-[#1f293d] pb-3">
            <div className="flex items-center gap-2">
              <Radio className="w-4 h-4 text-[#00f0ff]" />
              <h3 className="font-bold text-sm text-white">Physical USB Interface</h3>
            </div>
            <span
              className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                isPortOpen ? 'bg-[#00ff9d]/10 text-[#00ff9d] border border-[#00ff9d]/30' : 'bg-[#ff3366]/10 text-[#ff3366] border border-[#ff3366]/30'
              }`}
            >
              {isPortOpen ? 'ONLINE' : 'OFFLINE'}
            </span>
          </div>

          <div className="p-3 bg-[#0a0d14] rounded-lg border border-[#1f293d] text-xs space-y-2">
            <div>
              <span className="text-[#64748b]">Vendor:</span> <strong className="text-white">{pairedPort ? pairedPort.vendorName : 'Žádný port nevybrán'}</strong>
            </div>
            <div>
              <span className="text-[#64748b]">Chipset:</span> <strong className="text-[#00f0ff]">{pairedPort ? pairedPort.chipsetGuess : '--'}</strong>
            </div>
            <div>
              <span className="text-[#64748b]">VID / PID:</span>{' '}
              <strong className="text-white">
                {pairedPort?.usbVendorId
                  ? `0x${pairedPort.usbVendorId.toString(16).toUpperCase()} / 0x${pairedPort.usbProductId?.toString(16).toUpperCase()}`
                  : '--'}
              </strong>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-[#64748b]">Baudrate:</span>
              <select
                value={baudRate}
                onChange={e => onBaudRateChange(Number(e.target.value))}
                className="px-2 py-1 bg-[#111622] border border-[#1f293d] rounded text-[#00f0ff] outline-none"
              >
                <option value={115200}>115 200 Baud (Standard)</option>
                <option value={921600}>921 600 Baud (Fast High-Speed)</option>
                <option value={3000000}>3 000 000 Baud (Ultra High-Speed)</option>
              </select>
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-xs text-[#6b7280] block">Načíst lokální firmware (.bin, .mbn, .img):</label>
            <label className="flex items-center justify-center gap-2 p-3 bg-[#1e293b] hover:bg-[#334155] rounded-lg cursor-pointer text-xs font-bold text-[#00f0ff] border border-[#00f0ff]/30 transition-all">
              <FileUp className="w-4 h-4" />
              <span>Nahrát binární soubor</span>
              <input type="file" onChange={onFileUpload} className="hidden" />
            </label>
          </div>
        </div>

        {/* Right 2 Columns: Real-Time Diagnostic Terminal */}
        <div className="lg:col-span-2 bg-[#0d111a] border border-[#1f293d] rounded-xl p-5 flex flex-col font-mono shadow-md">
          <div className="flex items-center justify-between border-b border-[#1f293d] pb-3 mb-3">
            <div className="flex items-center gap-2">
              <Terminal className="w-4 h-4 text-[#00ff9d]" />
              <h3 className="font-bold text-sm text-white">Live Diagnostic Console & Event Stream</h3>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] text-[#6b7280]">Stream: Direct WebSerial I/O</span>
              <button
                onClick={onClearLogs}
                className="text-[11px] text-[#9ca3af] hover:text-white px-2 py-0.5 rounded bg-[#1f293d] hover:bg-[#2e3e57] transition-colors"
              >
                Clear
              </button>
            </div>
          </div>

          <div className="flex-1 bg-[#07090e] rounded-lg p-4 font-mono text-xs overflow-y-auto max-h-[340px] space-y-1.5 border border-[#161f30]">
            {terminalLogs.map((log, index) => {
              let color = 'text-[#d4d4d4]';
              if (log.includes('[SUCCESS]') || log.includes('[HOTOVO]') || log.includes('OK')) color = 'text-[#00ff9d] font-bold';
              if (log.includes('[FRP]') || log.includes('[PRŮVODCE]')) color = 'text-[#00f0ff]';
              if (log.includes('[CRITICAL]') || log.includes('[ERROR]') || log.includes('FAIL')) color = 'text-[#ff3366] font-bold';
              if (log.includes('[SECURITY]') || log.includes('[CRYPTO]')) color = 'text-[#ffaa00]';
              if (log.includes('[SAHARA]')) color = 'text-[#a855f7]';
              return (
                <div key={index} className={`${color} leading-relaxed break-all`}>
                  {log}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
});
