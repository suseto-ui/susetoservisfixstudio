import React, { memo } from 'react';
import {
  Usb,
  HardDrive,
  RefreshCw,
  Zap,
  Terminal,
  Filter,
  Download,
  RotateCcw,
  CheckCircle2,
  AlertTriangle,
  Radio,
  Sliders,
  Sparkles
} from 'lucide-react';
import { SerialDeviceDescriptor } from '../../services/webSerialEngine';
import { DoctorPortItem, UsbBusEvent } from '../../types/operator';
import { LogFilterType } from '../../hooks/useTerminalLogs';

interface DiagnosticLeftColumnProps {
  isConnected: boolean;
  connectedDevice: SerialDeviceDescriptor | null;
  baudRate: number;
  onBaudRateChange: (baud: number) => void;
  onConnectSerial: () => void;
  onDisconnectSerial: () => void;
  onPnpScan: () => void;
  isScanningPnp: boolean;
  doctorPorts: DoctorPortItem[];
  recentUsbEvents: UsbBusEvent[];
  filteredLogs: string[];
  logFilter: LogFilterType;
  onSetLogFilter: (filter: LogFilterType) => void;
  onClearLogs: () => void;
  onExportLogsCSV: () => void;
  terminalEndRef: React.RefObject<HTMLDivElement | null>;
}

export const DiagnosticLeftColumn: React.FC<DiagnosticLeftColumnProps> = memo(function DiagnosticLeftColumn({
  isConnected,
  connectedDevice,
  baudRate,
  onBaudRateChange,
  onConnectSerial,
  onDisconnectSerial,
  onPnpScan,
  isScanningPnp,
  doctorPorts,
  recentUsbEvents,
  filteredLogs,
  logFilter,
  onSetLogFilter,
  onClearLogs,
  onExportLogsCSV,
  terminalEndRef
}) {
  return (
    <aside
      id="tour-diagnostic-column"
      className="lg:col-span-3 flex flex-col gap-3 font-mono"
    >
      {/* 1. PHYSICAL USB INTERFACE CONTROLLER CARD */}
      <div className="bg-[#101624] border border-[#1e2a42] rounded-xl p-3.5 space-y-3 shadow-lg">
        <div className="flex items-center justify-between border-b border-[#1b253b] pb-2">
          <div className="flex items-center gap-2">
            <Usb className="w-4 h-4 text-[#00f0ff]" />
            <h3 className="text-xs font-bold text-white uppercase tracking-wider">FYZICKÉ USB ROZHRANÍ</h3>
          </div>
          <span
            className={`px-2 py-0.5 rounded text-[10px] font-black border ${
              isConnected
                ? 'bg-[#064e3b] text-[#34d399] border-[#059669]'
                : 'bg-[#451a03] text-[#fbbf24] border-[#d97706]'
            }`}
          >
            {isConnected ? 'PŘIPOJENO' : 'ODPOJENO'}
          </span>
        </div>

        {/* Port Status Info */}
        <div className="bg-[#0b0f19] p-2.5 rounded-lg border border-[#162033] space-y-1.5 text-[11px]">
          <div className="flex justify-between items-center">
            <span className="text-[#64748b]">Port / Link:</span>
            <span className="text-white font-bold">{connectedDevice ? connectedDevice.portLabel : 'WebSerial CDC-ACM'}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-[#64748b]">Detekovaný HWID:</span>
            <span className="text-[#38bdf8] font-bold">
              {connectedDevice?.usbVendorId && connectedDevice?.usbProductId
                ? `VID:0x${connectedDevice.usbVendorId.toString(16).toUpperCase()} PID:0x${connectedDevice.usbProductId.toString(16).toUpperCase()}`
                : 'VID:05C6 PID:9008'}
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-[#64748b]">Čipset režim:</span>
            <span className="text-[#00ff9d] font-bold">{connectedDevice ? connectedDevice.chipsetGuess : 'Qualcomm Sahara EDL'}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-[#64748b]">Baudrate:</span>
            <select
              value={baudRate}
              onChange={(e) => onBaudRateChange(Number(e.target.value))}
              className="bg-[#162033] text-white text-[11px] rounded px-1.5 py-0.5 border border-[#2a3c5a] outline-none"
            >
              <option value={115200}>115200 (Std EDL)</option>
              <option value={921600}>921600 (High Speed)</option>
              <option value={1500000}>1500000 (MTK Max)</option>
              <option value={3000000}>3000000 (Nitro DMA)</option>
            </select>
          </div>
        </div>

        {/* Connect / Disconnect Buttons */}
        <div className="grid grid-cols-2 gap-2">
          {!isConnected ? (
            <button
              onClick={onConnectSerial}
              className="col-span-2 py-2 bg-gradient-to-r from-[#00f0ff] to-[#00a3ff] text-black font-black text-xs rounded-lg hover:opacity-95 transition-all shadow-[0_0_15px_rgba(0,240,255,0.3)] flex items-center justify-center gap-1.5"
            >
              <Usb className="w-3.5 h-3.5 text-black" />
              <span>SPÁROVAT USB PORT</span>
            </button>
          ) : (
            <button
              onClick={onDisconnectSerial}
              className="col-span-2 py-2 bg-[#dc2626] hover:bg-[#b91c1c] text-white font-bold text-xs rounded-lg transition-all flex items-center justify-center gap-1.5"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>ODPOJIT ZAŘÍZENÍ</span>
            </button>
          )}

          <button
            onClick={onPnpScan}
            disabled={isScanningPnp}
            className="col-span-2 py-1.5 bg-[#172033] hover:bg-[#22304d] text-[#cbd5e1] font-bold text-[11px] rounded-lg border border-[#263757] transition-all flex items-center justify-center gap-1.5"
          >
            <RefreshCw className={`w-3 h-3 text-[#00f0ff] ${isScanningPnp ? 'animate-spin' : ''}`} />
            <span>{isScanningPnp ? 'Skenuji PnP sběrnici...' : 'PnP Skenovat Porty'}</span>
          </button>
        </div>
      </div>

      {/* 2. REAL-TIME DIAGNOSTIC CONSOLE */}
      <div className="bg-[#101624] border border-[#1e2a42] rounded-xl p-3 flex-1 flex flex-col min-h-[340px] shadow-lg">
        <div className="flex items-center justify-between border-b border-[#1b253b] pb-2 mb-2">
          <div className="flex items-center gap-2">
            <Terminal className="w-4 h-4 text-[#00ff9d]" />
            <h3 className="text-xs font-bold text-white uppercase tracking-wider">DIAGNOSTICKÁ KONZOLE</h3>
          </div>
          <div className="flex items-center gap-1">
            <button
              onClick={onExportLogsCSV}
              className="p-1 rounded bg-[#162033] hover:bg-[#253554] text-[#94a3b8] hover:text-white transition-colors"
              title="Exportovat logy do CSV"
            >
              <Download className="w-3 h-3" />
            </button>
            <button
              onClick={onClearLogs}
              className="p-1 rounded bg-[#162033] hover:bg-[#253554] text-[#94a3b8] hover:text-white transition-colors"
              title="Vymazat výpis konzole"
            >
              <RotateCcw className="w-3 h-3" />
            </button>
          </div>
        </div>

        {/* Filter Badges */}
        <div className="flex items-center gap-1 mb-2 overflow-x-auto pb-1 text-[10px]">
          {(['ALL', 'INFO', 'SUCCESS', 'ERROR', 'HARDWARE'] as LogFilterType[]).map((flt) => (
            <button
              key={flt}
              onClick={() => onSetLogFilter(flt)}
              className={`px-2 py-0.5 rounded font-bold transition-all ${
                logFilter === flt
                  ? 'bg-[#00f0ff] text-black shadow-[0_0_8px_rgba(0,240,255,0.4)]'
                  : 'bg-[#162033] text-[#64748b] hover:text-[#94a3b8]'
              }`}
            >
              {flt}
            </button>
          ))}
        </div>

        {/* Terminal Log Output Window */}
        <div className="bg-[#080c14] rounded-lg p-2.5 flex-1 overflow-y-auto font-mono text-[11px] space-y-1 border border-[#141b2b] select-text max-h-[380px]">
          {filteredLogs.length === 0 ? (
            <div className="text-[#475569] italic py-8 text-center">Žádné záznamy pro vybraný filtr...</div>
          ) : (
            filteredLogs.map((log, index) => {
              const isErr = log.includes('[ERROR]') || log.includes('[CHYBA]') || log.includes('FAIL');
              const isSucc = log.includes('[SUCCESS]') || log.includes('[ÚSPĚCH]') || log.includes('[HOTOVO]') || log.includes('OK');
              const isHw = log.includes('[HARDWARE]') || log.includes('[USB]') || log.includes('[PORT]');
              const isSec = log.includes('[SECURITY]') || log.includes('[SMARTCARD]');

              return (
                <div
                  key={index}
                  className={`leading-tight break-all ${
                    isErr
                      ? 'text-[#f87171] font-bold bg-[#450a0a]/30 p-1 rounded'
                      : isSucc
                      ? 'text-[#4ade80]'
                      : isHw
                      ? 'text-[#38bdf8]'
                      : isSec
                      ? 'text-[#fbbf24]'
                      : 'text-[#94a3b8]'
                  }`}
                >
                  {log}
                </div>
              );
            })
          )}
          <div ref={terminalEndRef} />
        </div>

        {/* Live Status Tag */}
        <div className="mt-2 pt-1.5 border-t border-[#162033] flex items-center justify-between text-[10px] text-[#64748b]">
          <span className="flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-[#10b981] animate-pulse" />
            <span>Event Stream: LIVE</span>
          </span>
          <span>Buffer: {filteredLogs.length} řádků</span>
        </div>
      </div>
    </aside>
  );
});
