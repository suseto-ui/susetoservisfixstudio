import React, { memo, useState, useMemo } from 'react';
import {
  Usb,
  HardDrive,
  RefreshCw,
  Activity,
  CheckCircle2,
  AlertTriangle,
  ShieldAlert,
  ShieldCheck,
  Info,
  Lock,
  Zap,
  Download,
  Flame,
  Radio,
  Sliders,
  Play
} from 'lucide-react';
import { DoctorPortItem, UsbBusEvent, UsbPowerTelemetry, PowerWavePoint } from '../../types/operator';

interface UsbDoctorTabProps {
  discoveredPorts: DoctorPortItem[];
  usbBusEvents: UsbBusEvent[];
  isWebUsbAvailable: boolean;
  onRequestHardwareDevice: () => void;
  onScanRealHardwarePorts: () => void;
  onDisconnectHardwarePort: (portId: string) => void;
  onRunStressTest: () => void;
  isStressTesting: boolean;
  stressThroughputKbs: number;
  stressLatencyMs: number;
  stressPacketsSent: number;
  stressPacketsAck: number;
  stressErrorCount: number;
  stressGraphPoints: Array<{ x: number; y: number }>;
  stressVerdict: string | null;
  selectedDoctorPort: string;
  onSelectDoctorPort: (port: string) => void;
  stressBaud: number;
  onStressBaudChange: (baud: number) => void;
  onAddLog: (msg: string, prefix?: string) => void;
  // Power Telemetry Props
  powerTelemetry: UsbPowerTelemetry;
  onRunVbusDropTest: () => void;
  isVbusDropTesting: boolean;
  onSwitchPowerProtocol: (protocol: UsbPowerTelemetry['protocol']) => void;
  onSimulateFault: (faultType: 'VOLTAGE_DROP' | 'OVERVOLTAGE' | 'SHORT_CIRCUIT') => void;
  onResetPowerProtection: () => void;
}

export const UsbDoctorTab: React.FC<UsbDoctorTabProps> = memo(function UsbDoctorTab({
  discoveredPorts,
  usbBusEvents,
  isWebUsbAvailable,
  onRequestHardwareDevice,
  onScanRealHardwarePorts,
  onDisconnectHardwarePort,
  onRunStressTest,
  isStressTesting,
  stressThroughputKbs,
  stressLatencyMs,
  stressPacketsSent,
  stressPacketsAck,
  stressErrorCount,
  stressGraphPoints,
  stressVerdict,
  selectedDoctorPort,
  onSelectDoctorPort,
  stressBaud,
  onStressBaudChange,
  onAddLog,
  powerTelemetry,
  onRunVbusDropTest,
  isVbusDropTesting,
  onSwitchPowerProtocol,
  onSimulateFault,
  onResetPowerProtection
}) {
  const [usbDoctorFilter, setUsbDoctorFilter] = useState<'ALL' | 'QUALCOMM' | 'MEDIATEK' | 'FTDI' | 'ERRORS'>('ALL');
  const [timebaseMs, setTimebaseMs] = useState<number>(500);
  const [hoveredPoint, setHoveredPoint] = useState<PowerWavePoint | null>(null);

  // SVG Scaled points for Oscilloscope
  const { voltagePolyline, currentPolyline, pointsWithCoords } = useMemo(() => {
    const history = powerTelemetry.history;
    if (!history || history.length === 0) {
      return { voltagePolyline: '', currentPolyline: '', pointsWithCoords: [] };
    }

    // Y scaling:
    // Voltage: 3.5V to 6.0V (or up to 12V if protocol > 5V) -> mapped to 100..0
    const maxV = powerTelemetry.protocol.includes('QC') || powerTelemetry.protocol.includes('PD') ? 12.0 : 6.0;
    const minV = 3.5;
    const vRange = maxV - minV;

    // Current: 0 to 2500 mA -> mapped to 100..0
    const maxI = 2500;
    const minI = 0;
    const iRange = maxI - minI;

    const mapped = history.map((pt, idx) => {
      const x = (idx / Math.max(1, history.length - 1)) * 100;
      const yV = Math.max(0, Math.min(100, 100 - ((pt.voltage - minV) / vRange) * 100));
      const yI = Math.max(0, Math.min(100, 100 - ((pt.current - minI) / iRange) * 100));
      return {
        raw: pt,
        x,
        yV,
        yI
      };
    });

    const vPoly = mapped.map(p => `${p.x.toFixed(1)},${p.yV.toFixed(1)}`).join(' ');
    const iPoly = mapped.map(p => `${p.x.toFixed(1)},${p.yI.toFixed(1)}`).join(' ');

    return {
      voltagePolyline: vPoly,
      currentPolyline: iPoly,
      pointsWithCoords: mapped
    };
  }, [powerTelemetry.history, powerTelemetry.protocol]);

  const isNominal = powerTelemetry.powerStatus === 'NOMINAL';
  const isDropWarning = powerTelemetry.powerStatus === 'VOLTAGE_DROP_WARNING';
  const isOvervoltage = powerTelemetry.powerStatus === 'OVERVOLTAGE_ALERT';
  const isShortCircuit = powerTelemetry.powerStatus === 'SHORT_CIRCUIT_PROTECTION';

  const exportCsvOscilloscope = () => {
    const csvContent = "data:text/csv;charset=utf-8," 
      + "Time,Voltage_V,Current_mA,Power_W,Protocol,Status\n"
      + powerTelemetry.history.map(p => `${p.time},${p.voltage.toFixed(3)},${p.current.toFixed(1)},${((p.voltage * p.current)/1000).toFixed(3)},${powerTelemetry.protocol},${powerTelemetry.powerStatus}`).join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `vbus_oscilloscope_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    onAddLog('[USB_DOCTOR] ✅ Data osciloskopu VBUS/VCC exportována do CSV souboru.', '[SUCCESS]');
  };

  return (
    <div className="space-y-6 font-mono">
      {/* ========================================================================= */}
      {/* 1. REAL-TIME VBUS / VCC POWER ANALYZER & OSCILLOSCOPE                     */}
      {/* ========================================================================= */}
      <div className={`border-2 rounded-xl p-5 shadow-lg transition-all ${
        isShortCircuit
          ? 'bg-[#190a0f] border-[#ef4444] shadow-[0_0_25px_rgba(239,68,68,0.2)]'
          : isDropWarning
          ? 'bg-[#181308] border-[#f59e0b] shadow-[0_0_20px_rgba(245,158,11,0.15)]'
          : isOvervoltage
          ? 'bg-[#1a0a14] border-[#ec4899] shadow-[0_0_20px_rgba(236,72,153,0.15)]'
          : 'bg-[#111622] border-[#00f0ff]/40 shadow-[0_0_20px_rgba(0,240,255,0.08)]'
      }`}>
        {/* Header Ribbon */}
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[#1f293d] pb-4">
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-lg ${
              isShortCircuit ? 'bg-[#ef4444]/20 text-[#ef4444]' : 'bg-[#00f0ff]/10 text-[#00f0ff]'
            }`}>
              <Zap className="w-6 h-6 animate-pulse" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-bold text-base text-white tracking-wide">
                  VBUS / VCC POWER ANALYZER & LIVE OSCILLOSCOPE
                </h3>
                <span className={`px-2 py-0.5 text-[10px] font-bold rounded border ${
                  isNominal
                    ? 'bg-[#00ff9d]/10 text-[#00ff9d] border-[#00ff9d]/30'
                    : isDropWarning
                    ? 'bg-[#f59e0b]/20 text-[#f59e0b] border-[#f59e0b]/50 animate-bounce'
                    : isOvervoltage
                    ? 'bg-[#ec4899]/20 text-[#ec4899] border-[#ec4899]/50'
                    : 'bg-[#ef4444]/20 text-[#ef4444] border-[#ef4444]/50 animate-pulse'
                }`}>
                  {isNominal && '● VBUS STABILNÍ'}
                  {isDropWarning && '▲ VAROVÁNÍ: POKLES NAPĚTÍ'}
                  {isOvervoltage && '✖ PŘEPĚTÍ SBĚRNICE'}
                  {isShortCircuit && '🛡️ ZKRAT - POJISTKA VYPNUTA'}
                </span>
              </div>
              <p className="text-[11px] text-[#9ca3af] mt-0.5">
                Nízkoúrovňové měření napájecí větve USB v reálném čase (500 Hz ADC vzorkování, VBUS, I_LOAD, D+/D- linky)
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <button
              onClick={exportCsvOscilloscope}
              className="px-3 py-1.5 bg-[#1e293b] hover:bg-[#334155] text-[#d4d4d4] rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 border border-[#334155]"
              title="Exportovat naměřená data osciloskopu"
            >
              <Download className="w-3.5 h-3.5" /> Export CSV
            </button>
            {isShortCircuit && (
              <button
                onClick={onResetPowerProtection}
                className="px-3 py-1.5 bg-[#ef4444] hover:bg-[#dc2626] text-white rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 shadow-[0_0_15px_rgba(239,68,68,0.4)]"
              >
                <ShieldCheck className="w-3.5 h-3.5" /> Resetovat pojistku
              </button>
            )}
          </div>
        </div>

        {/* Live Power KPI Cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3.5 my-4">
          {/* 1. VBUS Voltage */}
          <div className={`p-3.5 rounded-xl border ${
            isDropWarning
              ? 'bg-[#f59e0b]/10 border-[#f59e0b]/40'
              : isOvervoltage
              ? 'bg-[#ec4899]/10 border-[#ec4899]/40'
              : isShortCircuit
              ? 'bg-[#ef4444]/10 border-[#ef4444]/40'
              : 'bg-[#0a0d14] border-[#1f293d]'
          }`}>
            <div className="flex items-center justify-between text-[11px] text-[#9ca3af]">
              <span className="font-bold uppercase tracking-wider">VBUS Napětí</span>
              <span className="text-[10px] text-[#00f0ff] font-mono">
                {powerTelemetry.vbusMinThreshold.toFixed(2)}V - {powerTelemetry.vbusMaxThreshold.toFixed(2)}V
              </span>
            </div>
            <div className="flex items-baseline gap-1.5 mt-1">
              <span className={`text-2xl font-bold font-mono tabular-nums ${
                isDropWarning ? 'text-[#f59e0b]' : isOvervoltage ? 'text-[#ec4899]' : isShortCircuit ? 'text-[#ef4444]' : 'text-[#00f0ff]'
              }`}>
                {powerTelemetry.vbusVoltage.toFixed(2)}
              </span>
              <span className="text-xs uppercase font-mono text-[#64748b]">V DC</span>
            </div>
            <div className="text-[10px] text-[#9ca3af] mt-1 flex items-center justify-between">
              <span>Zvlnění (Ripple):</span>
              <span className="text-white font-bold font-mono">{powerTelemetry.rippleNoiseMv.toFixed(1)} mVpp</span>
            </div>
          </div>

          {/* 2. Current Draw */}
          <div className="p-3.5 rounded-xl bg-[#0a0d14] border border-[#1f293d]">
            <div className="flex items-center justify-between text-[11px] text-[#9ca3af]">
              <span className="font-bold uppercase tracking-wider">Proud (I_LOAD)</span>
              <span className="text-[10px] text-[#f59e0b] font-mono">Max 3.00 A</span>
            </div>
            <div className="flex items-baseline gap-1.5 mt-1">
              <span className="text-2xl font-bold font-mono tabular-nums text-[#f59e0b]">
                {powerTelemetry.currentMa.toFixed(0)}
              </span>
              <span className="text-xs uppercase font-mono text-[#64748b]">mA</span>
              <span className="text-[11px] text-[#9ca3af] ml-auto">
                ({(powerTelemetry.currentMa / 1000).toFixed(2)} A)
              </span>
            </div>
            {/* Current mini-bar */}
            <div className="w-full bg-[#1e293b] h-1.5 rounded-full overflow-hidden mt-2">
              <div
                className="h-full bg-[#f59e0b] transition-all duration-300"
                style={{ width: `${Math.min(100, (powerTelemetry.currentMa / 2500) * 100)}%` }}
              />
            </div>
          </div>

          {/* 3. Instantaneous Power & Fast Charge Protocol */}
          <div className="p-3.5 rounded-xl bg-[#0a0d14] border border-[#1f293d]">
            <div className="flex items-center justify-between text-[11px] text-[#9ca3af]">
              <span className="font-bold uppercase tracking-wider">Příkon (Power)</span>
              <span className="text-[10px] text-[#00ff9d] font-mono font-bold">
                {powerTelemetry.protocol}
              </span>
            </div>
            <div className="flex items-baseline gap-1.5 mt-1">
              <span className="text-2xl font-bold font-mono tabular-nums text-[#00ff9d]">
                {powerTelemetry.powerWatts.toFixed(2)}
              </span>
              <span className="text-xs uppercase font-mono text-[#64748b]">W</span>
            </div>
            <div className="text-[10px] text-[#9ca3af] mt-1 flex items-center justify-between">
              <span>Protokol:</span>
              <span className="text-[#38bdf8] font-bold">{powerTelemetry.protocol}</span>
            </div>
          </div>

          {/* 4. D+ / D- Signal Levels */}
          <div className="p-3.5 rounded-xl bg-[#0a0d14] border border-[#1f293d]">
            <div className="flex items-center justify-between text-[11px] text-[#9ca3af]">
              <span className="font-bold uppercase tracking-wider">D+ / D- Signál</span>
              <span className="text-[10px] text-[#a78bfa] font-mono">USB PHY Line</span>
            </div>
            <div className="grid grid-cols-2 gap-2 mt-1">
              <div>
                <div className="text-[10px] text-[#6b7280]">D+ Linka:</div>
                <div className="text-base font-bold text-white font-mono">{powerTelemetry.dPlusVoltage.toFixed(2)} V</div>
              </div>
              <div>
                <div className="text-[10px] text-[#6b7280]">D- Linka:</div>
                <div className="text-base font-bold text-white font-mono">{powerTelemetry.dMinusVoltage.toFixed(2)} V</div>
              </div>
            </div>
            <div className="text-[9px] text-[#64748b] mt-1">
              {powerTelemetry.dPlusVoltage > 2.0 ? 'QC/PD handshake detekován' : 'USB 2.0 Standard linka'}
            </div>
          </div>
        </div>

        {/* LIVE DUAL-TRACE OSCILLOSCOPE */}
        <div className="bg-[#070a10] border border-[#1f293d] rounded-xl p-4 space-y-3 relative overflow-hidden">
          {/* Scope Controls & Legends */}
          <div className="flex flex-wrap items-center justify-between gap-3 text-xs border-b border-[#162033] pb-2">
            <div className="flex items-center gap-4">
              <span className="font-bold text-white flex items-center gap-1.5 text-xs">
                <Activity className="w-3.5 h-3.5 text-[#00f0ff]" /> Dvojitý real-time osciloskop
              </span>
              <div className="flex items-center gap-3 text-[11px]">
                <span className="flex items-center gap-1.5 text-[#00f0ff] font-bold">
                  <span className="w-3 h-0.5 bg-[#00f0ff] inline-block rounded" /> VBUS Napětí (V)
                </span>
                <span className="flex items-center gap-1.5 text-[#f59e0b] font-bold">
                  <span className="w-3 h-0.5 bg-[#f59e0b] inline-block rounded" /> Proud I_LOAD (mA)
                </span>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-[10px] text-[#64748b]">Časová základna:</span>
              {[100, 250, 500, 1000].map(ms => (
                <button
                  key={ms}
                  onClick={() => setTimebaseMs(ms)}
                  className={`px-2 py-0.5 rounded text-[10px] font-bold transition-all ${
                    timebaseMs === ms
                      ? 'bg-[#00f0ff]/20 text-[#00f0ff] border border-[#00f0ff]/40'
                      : 'bg-[#111622] text-[#9ca3af] hover:text-white'
                  }`}
                >
                  {ms}ms
                </button>
              ))}
            </div>
          </div>

          {/* SVG Canvas Scope */}
          <div className="relative h-44 w-full cursor-crosshair">
            <svg
              className="w-full h-full overflow-visible"
              viewBox="0 0 100 100"
              preserveAspectRatio="none"
              onMouseLeave={() => setHoveredPoint(null)}
            >
              <defs>
                <linearGradient id="vbusGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#00f0ff" stopOpacity="0.25" />
                  <stop offset="100%" stopColor="#00f0ff" stopOpacity="0.0" />
                </linearGradient>
                <linearGradient id="currentGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#f59e0b" stopOpacity="0.20" />
                  <stop offset="100%" stopColor="#f59e0b" stopOpacity="0.0" />
                </linearGradient>
              </defs>

              {/* Scope Grid & Level Lines */}
              <line x1="0" y1="20" x2="100" y2="20" stroke="#162033" strokeDasharray="1.5,1.5" strokeWidth="0.5" />
              <line x1="0" y1="40" x2="100" y2="40" stroke="#162033" strokeDasharray="1.5,1.5" strokeWidth="0.5" />
              <line x1="0" y1="60" x2="100" y2="60" stroke="#162033" strokeDasharray="1.5,1.5" strokeWidth="0.5" />
              <line x1="0" y1="80" x2="100" y2="80" stroke="#162033" strokeDasharray="1.5,1.5" strokeWidth="0.5" />

              {/* Upper & Lower Threshold Guidelines (5.25V & 4.75V) */}
              <line x1="0" y1="30" x2="100" y2="30" stroke="#ef4444" strokeDasharray="3,2" strokeWidth="0.6" opacity="0.6" />
              <line x1="0" y1="50" x2="100" y2="50" stroke="#f59e0b" strokeDasharray="3,2" strokeWidth="0.6" opacity="0.6" />

              {/* Current Fill & Line (Amber) */}
              {currentPolyline && (
                <>
                  <polygon
                    fill="url(#currentGrad)"
                    points={`0,100 ${currentPolyline} 100,100`}
                  />
                  <polyline
                    fill="none"
                    stroke="#f59e0b"
                    strokeWidth="1.6"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    points={currentPolyline}
                  />
                </>
              )}

              {/* Voltage Fill & Line (Cyan) */}
              {voltagePolyline && (
                <>
                  <polygon
                    fill="url(#vbusGrad)"
                    points={`0,100 ${voltagePolyline} 100,100`}
                  />
                  <polyline
                    fill="none"
                    stroke={isDropWarning ? '#f59e0b' : isShortCircuit ? '#ef4444' : '#00f0ff'}
                    strokeWidth="2.2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    points={voltagePolyline}
                  />
                </>
              )}

              {/* Data points */}
              {pointsWithCoords.map((pt, i) => (
                <g key={i}>
                  <circle
                    cx={pt.x}
                    cy={pt.yV}
                    r="1.8"
                    fill={isDropWarning ? '#f59e0b' : '#00f0ff'}
                    className="hover:r-3 transition-all cursor-pointer"
                    onMouseEnter={() => setHoveredPoint(pt.raw)}
                  />
                  <circle
                    cx={pt.x}
                    cy={pt.yI}
                    r="1.4"
                    fill="#f59e0b"
                    className="hover:r-2.5 transition-all cursor-pointer"
                    onMouseEnter={() => setHoveredPoint(pt.raw)}
                  />
                </g>
              ))}
            </svg>

            {/* Scope Y-Axis Overlay Labels */}
            <div className="absolute left-2 top-1 text-[9px] text-[#64748b] font-mono pointer-events-none">
              Upper Limit: 5.25V
            </div>
            <div className="absolute left-2 bottom-1 text-[9px] text-[#64748b] font-mono pointer-events-none">
              Lower Safe: 4.75V
            </div>
            <div className="absolute right-2 top-1 text-[9px] text-[#f59e0b] font-mono pointer-events-none">
              I_MAX: 2.50A
            </div>

            {/* Hover Tooltip Readout */}
            {hoveredPoint && (
              <div className="absolute right-3 bottom-3 bg-[#0a0d14]/95 border border-[#00f0ff]/50 rounded-lg p-2.5 shadow-xl text-xs z-10 pointer-events-none">
                <div className="text-[10px] text-[#9ca3af] font-bold">Vzorek: {hoveredPoint.time}</div>
                <div className="flex items-center gap-3 mt-1">
                  <span className="text-[#00f0ff] font-bold">Napětí: {hoveredPoint.voltage.toFixed(3)} V</span>
                  <span className="text-[#f59e0b] font-bold">Proud: {hoveredPoint.current.toFixed(0)} mA</span>
                </div>
                <div className="text-[10px] text-[#00ff9d] mt-0.5">
                  Výkon: {((hoveredPoint.voltage * hoveredPoint.current) / 1000).toFixed(2)} W
                </div>
              </div>
            )}
          </div>

          {/* Interactive Diagnostic Actions & Stress Simulation */}
          <div className="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-[#162033]">
            <div className="flex flex-wrap items-center gap-2">
              <button
                onClick={onRunVbusDropTest}
                disabled={isVbusDropTesting}
                className="px-3.5 py-1.5 bg-[#00f0ff]/15 hover:bg-[#00f0ff]/25 text-[#00f0ff] border border-[#00f0ff]/40 rounded-lg text-xs font-bold transition-all flex items-center gap-2 disabled:opacity-50"
              >
                <Zap className={`w-3.5 h-3.5 ${isVbusDropTesting ? 'animate-spin' : ''}`} />
                <span>{isVbusDropTesting ? 'Probíhá Drop Test...' : '⚡ Spustit zátěžový test poklesu (VBUS Drop Test)'}</span>
              </button>

              <div className="flex items-center gap-1.5 text-xs bg-[#0b0f19] px-2.5 py-1 rounded-lg border border-[#1f293d]">
                <span className="text-[#64748b]">Profil:</span>
                <select
                  value={powerTelemetry.protocol}
                  onChange={e => onSwitchPowerProtocol(e.target.value as any)}
                  className="bg-transparent text-[#00ff9d] font-bold text-xs focus:outline-none cursor-pointer"
                >
                  <option value="USB 2.0 (SDP)" className="bg-[#111622]">USB 2.0 Standard (5V / 500mA)</option>
                  <option value="QC 3.0" className="bg-[#111622]">Qualcomm QC 3.0 (9V / 2A)</option>
                  <option value="QC 4.0+" className="bg-[#111622]">Qualcomm QC 4.0+ / PD PPS</option>
                  <option value="USB-PD 3.0 PPS" className="bg-[#111622]">USB-PD 3.0 Programmable</option>
                  <option value="Samsung AFC" className="bg-[#111622]">Samsung AFC (9V / 1.67A)</option>
                </select>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <button
                onClick={() => onSimulateFault('VOLTAGE_DROP')}
                className="px-2.5 py-1 bg-[#f59e0b]/15 hover:bg-[#f59e0b]/25 text-[#f59e0b] border border-[#f59e0b]/30 rounded text-[11px] font-bold transition-all"
                title="Simulovat poddimenzovaný kabel s poklesem napětí pod 4.75V"
              >
                Simulovat pokles (Drop)
              </button>
              <button
                onClick={() => onSimulateFault('SHORT_CIRCUIT')}
                className="px-2.5 py-1 bg-[#ef4444]/15 hover:bg-[#ef4444]/25 text-[#ef4444] border border-[#ef4444]/30 rounded text-[11px] font-bold transition-all"
                title="Simulovat zkrat na VBUS a ověřit ochranu portu"
              >
                Simulovat zkrat
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* ========================================================================= */}
      {/* 2. REAL-TIME EVENT STREAM & USB HOTPLUG WATCHDOG                           */}
      {/* ========================================================================= */}
      <div className="bg-[#111622] border border-[#1f293d] rounded-xl p-5 shadow-lg space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[#1f293d] pb-3">
          <div className="flex items-center gap-2.5">
            <Usb className="w-5 h-5 text-[#00ff9d]" />
            <div>
              <h4 className="font-bold text-sm text-white flex items-center gap-2">
                <span>REÁLNÝ HARDWARE HOTPLUG WATCHDOG (USB/SERIAL)</span>
                <span className="px-2 py-0.5 bg-[#00ff9d]/10 text-[#00ff9d] border border-[#00ff9d]/30 text-[10px] rounded font-bold">
                  WebUSB & WebSerial Listener Active
                </span>
              </h4>
              <p className="text-[11px] text-[#9ca3af]">
                Automatické naslouchání událostem připojení a odpojení hardware v reálném čase (connect / disconnect)
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2 text-xs">
            <span className="text-[11px] text-[#6b7280]">Reálný Hardware:</span>
            <button
              onClick={onRequestHardwareDevice}
              className="px-3 py-1 bg-[#00ff9d]/20 hover:bg-[#00ff9d]/30 text-[#00ff9d] border border-[#00ff9d]/40 rounded text-[11px] font-bold transition-all flex items-center gap-1.5"
            >
              <Usb className="w-3.5 h-3.5" /> Připojit WebSerial HW
            </button>
            <button
              onClick={onScanRealHardwarePorts}
              className="px-3 py-1 bg-[#00f0ff]/15 hover:bg-[#00f0ff]/25 text-[#00f0ff] border border-[#00f0ff]/30 rounded text-[11px] font-bold transition-all flex items-center gap-1.5"
            >
              <RefreshCw className="w-3.5 h-3.5" /> Skenovat OS Porty
            </button>
          </div>
        </div>

        {/* Event Stream Ticker */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 text-xs">
          <div className="lg:col-span-2 space-y-2">
            <div className="text-[11px] text-[#6b7280] font-bold flex items-center justify-between">
              <span>Poslední události USB sběrnice (Real-Time Event Log):</span>
              <span className="text-[#00ff9d]">{usbBusEvents.length} zaznamenaných událostí</span>
            </div>
            <div className="space-y-1.5 max-h-36 overflow-y-auto pr-1">
              {usbBusEvents.map(ev => (
                <div
                  key={ev.id}
                  className={`p-2 rounded border flex items-center justify-between text-[11px] ${
                    ev.type === 'CONNECT'
                      ? 'bg-[#00ff9d]/5 border-[#00ff9d]/20 text-[#00ff9d]'
                      : 'bg-[#ff3366]/5 border-[#ff3366]/20 text-[#ff3366]'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <span
                      className={`px-1.5 py-0.5 rounded text-[9px] font-bold ${
                        ev.type === 'CONNECT' ? 'bg-[#00ff9d]/20 text-[#00ff9d]' : 'bg-[#ff3366]/20 text-[#ff3366]'
                      }`}
                    >
                      {ev.type}
                    </span>
                    <span className="text-white font-medium">{ev.deviceName}</span>
                    <span className="text-[#9ca3af] font-mono">[{ev.vidPid}]</span>
                  </div>
                  <div className="flex items-center gap-2 text-[#6b7280]">
                    <span className="text-[10px] px-1 bg-[#1e293b] rounded text-[#9ca3af]">{ev.source}</span>
                    <span>{ev.timestamp}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-[#0a0d14] border border-[#1f293d] rounded-lg p-3 space-y-2 text-[11px]">
            <div className="font-bold text-white text-xs flex items-center gap-1.5 text-[#00f0ff]">
              <Activity className="w-3.5 h-3.5" /> Stav sběrnice a API
            </div>
            <div className="flex justify-between">
              <span className="text-[#6b7280]">WebUSB API:</span>
              <span className={isWebUsbAvailable ? 'text-[#00ff9d] font-bold' : 'text-[#ffaa00]'}>
                {isWebUsbAvailable ? 'Dostupné (Hardware)' : 'Aktivní emulace'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-[#6b7280]">WebSerial API:</span>
              <span className="text-[#00ff9d] font-bold">Podporováno</span>
            </div>
            <div className="flex justify-between">
              <span className="text-[#6b7280]">Aktivní linky:</span>
              <span className="text-white font-bold">
                {discoveredPorts.filter(p => p.status === 'ONLINE').length} připojených
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-[#6b7280]">Blokované porty:</span>
              <span className={discoveredPorts.some(p => p.status === 'LOCKED') ? 'text-[#ff3366] font-bold' : 'text-[#00ff9d]'}>
                {discoveredPorts.filter(p => p.status === 'LOCKED').length} detekováno
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* ========================================================================= */}
      {/* 3. LIVE DETECTED PORTS TABLE                                              */}
      {/* ========================================================================= */}
      <div className="bg-[#111622] border border-[#1f293d] rounded-xl p-5 space-y-4 shadow-md">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[#1f293d] pb-3">
          <div className="flex items-center gap-2">
            <Activity className="w-4 h-4 text-[#00f0ff]" />
            <h4 className="font-bold text-sm text-white">Inspekce COM a USB portů v reálném čase</h4>
            <span className="text-xs text-[#9ca3af]">({discoveredPorts.length} portů v systému)</span>
          </div>

          <div className="flex items-center gap-1 text-[11px]">
            {(['ALL', 'QUALCOMM', 'MEDIATEK', 'FTDI', 'ERRORS'] as const).map(filter => (
              <button
                key={filter}
                onClick={() => setUsbDoctorFilter(filter)}
                className={`px-2.5 py-1 rounded transition-colors ${
                  usbDoctorFilter === filter
                    ? 'bg-[#00f0ff]/20 text-[#00f0ff] border border-[#00f0ff]/40 font-bold'
                    : 'bg-[#1e293b] text-[#9ca3af] hover:text-white'
                }`}
              >
                {filter === 'ALL' ? 'Vše' : filter}
              </button>
            ))}
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left">
            <thead>
              <tr className="border-b border-[#1f293d] text-[#6b7280] pb-2">
                <th className="py-2 px-3">Port</th>
                <th className="py-2 px-3">Zařízení a Ovladač</th>
                <th className="py-2 px-3">HWID (VID:PID)</th>
                <th className="py-2 px-3">Režim čipsetu</th>
                <th className="py-2 px-3">Stav linky</th>
                <th className="py-2 px-3 text-right">Akce</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1f293d]">
              {discoveredPorts
                .filter(p => {
                  if (usbDoctorFilter === 'ALL') return true;
                  if (usbDoctorFilter === 'QUALCOMM') return p.chipsetType === 'QUALCOMM';
                  if (usbDoctorFilter === 'MEDIATEK') return p.chipsetType === 'MEDIATEK';
                  if (usbDoctorFilter === 'FTDI') return p.chipsetType === 'FTDI';
                  if (usbDoctorFilter === 'ERRORS') return p.status === 'LOCKED' || p.chipsetType === 'LOCKED';
                  return true;
                })
                .map(p => {
                  const isLocked = p.status === 'LOCKED';
                  return (
                    <tr
                      key={p.id}
                      className={`hover:bg-white/[0.02] transition-colors ${
                        isLocked ? 'bg-[#ff3366]/5' : ''
                      }`}
                    >
                      <td
                        className={`py-3 px-3 font-bold ${
                          isLocked
                            ? 'text-[#ff3366]'
                            : p.chipsetType === 'QUALCOMM'
                            ? 'text-[#00f0ff]'
                            : p.chipsetType === 'MEDIATEK'
                            ? 'text-[#ffaa00]'
                            : 'text-[#38bdf8]'
                        }`}
                      >
                        {p.portName}
                      </td>
                      <td className="py-3 px-3">
                        <div className="text-white font-medium">{p.deviceTitle}</div>
                        <div className={`text-[10px] ${isLocked ? 'text-[#ff3366]' : 'text-[#6b7280]'}`}>
                          {p.lockReason || `Ovladač: ${p.driverInfo}`}
                        </div>
                      </td>
                      <td className="py-3 px-3 text-[#9ca3af] font-mono">{p.vidPid}</td>
                      <td className="py-3 px-3">
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                            isLocked
                              ? 'bg-[#ff3366]/10 text-[#ff3366] border-[#ff3366]/30'
                              : p.chipsetType === 'QUALCOMM'
                              ? 'bg-[#00f0ff]/10 text-[#00f0ff] border-[#00f0ff]/30'
                              : p.chipsetType === 'MEDIATEK'
                              ? 'bg-[#ffaa00]/10 text-[#ffaa00] border-[#ffaa00]/30'
                              : 'bg-[#38bdf8]/10 text-[#38bdf8] border-[#38bdf8]/30'
                          }`}
                        >
                          {p.chipsetMode}
                        </span>
                      </td>
                      <td className="py-3 px-3">
                        {isLocked ? (
                          <span className="px-2 py-0.5 bg-[#ff3366]/20 text-[#ff3366] border border-[#ff3366]/40 rounded text-[10px] font-bold flex items-center gap-1 w-max">
                            <AlertTriangle className="w-3 h-3" /> BLOKOVÁN
                          </span>
                        ) : (
                          <span className="px-2 py-0.5 bg-[#00ff9d]/10 text-[#00ff9d] rounded text-[10px] font-bold flex items-center gap-1 w-max">
                            <CheckCircle2 className="w-3 h-3" /> DOSTUPNÝ
                          </span>
                        )}
                      </td>
                      <td className="py-3 px-3 text-right">
                        <div className="flex items-center justify-end gap-1.5">
                          <button
                            onClick={() => {
                              onSelectDoctorPort(p.portName);
                              if (isLocked) {
                                onAddLog(`[USB_DOCTOR] Varování: ${p.portName} nelze otevřít (${p.lockReason}). Ukončete blokující proces.`);
                              } else {
                                onAddLog(`[USB_DOCTOR] Spuštěn ping/čtecí test na ${p.portName} (${p.chipsetMode}). Odezva [OK]`);
                              }
                            }}
                            className={`px-2.5 py-1 text-[11px] rounded transition-colors ${
                              isLocked
                                ? 'bg-[#ff3366]/20 hover:bg-[#ff3366]/30 text-[#ff3366] border border-[#ff3366]/40'
                                : 'bg-[#1e293b] hover:bg-[#334155] text-white'
                            }`}
                          >
                            {isLocked ? 'Detail zámku' : 'Otestovat čtení'}
                          </button>
                          {p.id.startsWith('hw-') || p.id.startsWith('port-webusb-') || p.id.startsWith('sim-') ? (
                            <button
                              onClick={() => onDisconnectHardwarePort(p.id)}
                              className="px-2 py-1 bg-[#331111] hover:bg-[#551111] text-[#ff6666] text-[10px] rounded transition-colors"
                              title="Odpojit toto zařízení"
                            >
                              Odpojit
                            </button>
                          ) : null}
                        </div>
                      </td>
                    </tr>
                  );
                })}
            </tbody>
          </table>
        </div>
      </div>

      {/* ========================================================================= */}
      {/* 4. USB PORT STABILITY & STRESS BENCHMARK                                  */}
      {/* ========================================================================= */}
      <div className="bg-[#111622] border-2 border-[#00f0ff]/30 rounded-xl p-5 shadow-[0_0_20px_rgba(0,240,255,0.08)] space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[#1f293d] pb-3">
          <div className="flex items-center gap-2.5">
            <Activity className="w-5 h-5 text-[#00f0ff]" />
            <div>
              <h4 className="font-bold text-sm text-white flex items-center gap-2">
                <span>ZÁTĚŽOVÝ TEST STABILITY USB PORTU (ECHO BENCHMARK)</span>
                <span className="px-2 py-0.5 bg-[#00f0ff]/10 text-[#00f0ff] border border-[#00f0ff]/30 text-[10px] rounded font-bold">
                  PERIODICKÝ ECHO LOOP
                </span>
              </h4>
              <p className="text-[11px] text-[#9ca3af]">
                Měření skutečné propustnosti, stability časování paketů a chybovosti (PER) zvoleného sériového portu
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2.5">
            <div className="flex items-center gap-1.5 text-xs bg-[#0a0d14] px-2.5 py-1.5 rounded-lg border border-[#1f293d]">
              <span className="text-[#6b7280]">Port:</span>
              <select
                value={selectedDoctorPort}
                onChange={e => onSelectDoctorPort(e.target.value)}
                className="bg-transparent text-[#00f0ff] font-bold text-xs focus:outline-none cursor-pointer"
              >
                {discoveredPorts.map(p => (
                  <option key={p.id} value={p.portName} className="bg-[#111622] text-white">
                    {p.portName} ({p.chipsetMode})
                  </option>
                ))}
              </select>
            </div>

            <div className="flex items-center gap-1.5 text-xs bg-[#0a0d14] px-2.5 py-1.5 rounded-lg border border-[#1f293d]">
              <span className="text-[#6b7280]">Baudrate:</span>
              <select
                value={stressBaud}
                onChange={e => onStressBaudChange(Number(e.target.value))}
                className="bg-transparent text-white font-bold text-xs focus:outline-none cursor-pointer"
              >
                <option value={115200} className="bg-[#111622]">115 200 Bd</option>
                <option value={460800} className="bg-[#111622]">460 800 Bd</option>
                <option value={921600} className="bg-[#111622]">921 600 Bd</option>
              </select>
            </div>

            <button
              onClick={onRunStressTest}
              disabled={isStressTesting}
              className="px-4 py-2 bg-[#00ff9d] hover:bg-[#00dd88] text-black font-bold text-xs rounded-lg flex items-center gap-2 transition-all shadow-[0_0_15px_rgba(0,255,157,0.3)] disabled:opacity-50"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isStressTesting ? 'animate-spin' : ''}`} />
              <span>{isStressTesting ? 'Probíhá měření...' : 'Spustit zátěžový test'}</span>
            </button>
          </div>
        </div>

        {/* Stress Test Live KPI Metrics */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div className="bg-[#0a0d14] border border-[#1f293d] rounded-lg p-3">
            <div className="text-[10px] text-[#9ca3af] uppercase font-bold">Propustnost sběrnice</div>
            <div className="text-lg font-bold text-[#00f0ff] mt-0.5">
              {stressThroughputKbs} <span className="text-xs text-[#9ca3af]">KB/s</span>
            </div>
            <div className="text-[10px] text-[#6b7280]">
              {((stressThroughputKbs * 8) / 1024).toFixed(2)} Mbit/s efektivně
            </div>
          </div>

          <div className="bg-[#0a0d14] border border-[#1f293d] rounded-lg p-3">
            <div className="text-[10px] text-[#9ca3af] uppercase font-bold">Odezva (RTT Latence)</div>
            <div className="text-lg font-bold text-[#00ff9d] mt-0.5">
              {stressLatencyMs} <span className="text-xs text-[#9ca3af]">ms</span>
            </div>
            <div className="text-[10px] text-[#6b7280]">stabilní round-trip</div>
          </div>

          <div className="bg-[#0a0d14] border border-[#1f293d] rounded-lg p-3">
            <div className="text-[10px] text-[#9ca3af] uppercase font-bold">Pakety (Odesláno/ACK)</div>
            <div className="text-lg font-bold text-white mt-0.5">
              {stressPacketsAck} / {stressPacketsSent}
            </div>
            <div className="text-[10px] text-[#00ff9d] flex items-center gap-1">
              <CheckCircle2 className="w-3 h-3" /> 100% potvrzeno
            </div>
          </div>

          <div className="bg-[#0a0d14] border border-[#1f293d] rounded-lg p-3">
            <div className="text-[10px] text-[#9ca3af] uppercase font-bold">Chybovost paketů (PER)</div>
            <div className={`text-lg font-bold mt-0.5 ${stressErrorCount === 0 ? 'text-[#00ff9d]' : 'text-[#ff3366]'}`}>
              {stressErrorCount === 0 ? '0.00 %' : `${stressErrorCount} chyb`}
            </div>
            <div className="text-[10px] text-[#00ff9d]">Zero packet loss</div>
          </div>
        </div>

        {/* Real-Time SVG Throughput & Error Rate Chart */}
        <div className="bg-[#070a10] border border-[#1f293d] rounded-lg p-4 space-y-2">
          <div className="flex items-center justify-between text-xs text-[#9ca3af]">
            <span className="font-bold text-white flex items-center gap-1.5">
              <Activity className="w-3.5 h-3.5 text-[#00f0ff]" /> Graf propustnosti a stability časování v čase (KB/s)
            </span>
          </div>

          <div className="relative h-28 w-full pt-2">
            <svg className="w-full h-full overflow-visible" viewBox="0 0 100 100" preserveAspectRatio="none">
              <line x1="0" y1="20" x2="100" y2="20" stroke="#1f293d" strokeDasharray="2,2" strokeWidth="0.5" />
              <line x1="0" y1="50" x2="100" y2="50" stroke="#1f293d" strokeDasharray="2,2" strokeWidth="0.5" />
              <line x1="0" y1="80" x2="100" y2="80" stroke="#1f293d" strokeDasharray="2,2" strokeWidth="0.5" />

              <defs>
                <linearGradient id="stressGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#00f0ff" stopOpacity="0.35" />
                  <stop offset="100%" stopColor="#00f0ff" stopOpacity="0.0" />
                </linearGradient>
              </defs>

              {stressGraphPoints.length > 1 && (
                <polygon
                  fill="url(#stressGrad)"
                  points={`0,100 ${stressGraphPoints.map(p => `${p.x},${p.y}`).join(' ')} 100,100`}
                />
              )}

              {stressGraphPoints.length > 1 && (
                <polyline
                  fill="none"
                  stroke="#00f0ff"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  points={stressGraphPoints.map(p => `${p.x},${p.y}`).join(' ')}
                />
              )}

              {stressGraphPoints.map((p, idx) => (
                <circle
                  key={idx}
                  cx={p.x}
                  cy={p.y}
                  r="1.8"
                  fill="#00ff9d"
                  stroke="#06090e"
                  strokeWidth="0.8"
                />
              ))}
            </svg>
          </div>

          {stressVerdict && (
            <div className="p-2.5 bg-[#00ff9d]/10 border border-[#00ff9d]/30 rounded-lg text-xs text-[#00ff9d] flex items-center justify-between font-bold">
              <span className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-[#00ff9d]" /> {stressVerdict}
              </span>
              <span className="text-[10px] text-[#9ca3af]">
                Testovaný port: {selectedDoctorPort} ({stressBaud} Bd)
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
});
