import React, { memo, useState, useMemo } from 'react';
import {
  Cpu,
  Flame,
  Radio,
  Terminal,
  Zap,
  Activity,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  Download,
  Sliders,
  Sparkles,
  RefreshCw,
  Binary,
  Wrench,
  Wifi,
  FileCode
} from 'lucide-react';
import { MtkNvramCalibrationData, NvramHexRow } from '../../types/operator';
import { NvramEngine } from '../../services/nvramEngine';

interface ValHubTabProps {
  valTargetPort: string;
  onValTargetPortChange: (port: string) => void;
  valTargetBaud: number;
  valSelectedChipset: string;
  onSelectValChipset: (chipset: string) => void;
  onTriggerDtrRtsPulse: () => void;
  onAutoBaudNegotiation: () => void;
  onValHandshake: (chipset: string) => void;
  isValRunning: boolean;
  // NVRAM Calibration State & Handlers
  nvramData: MtkNvramCalibrationData;
  onUpdateNvramField: <K extends keyof MtkNvramCalibrationData>(field: K, value: MtkNvramCalibrationData[K]) => void;
  onAutoGenerateImei: (target: 'imei1' | 'imei2') => void;
  onAutoFixLuhn: (target: 'imei1' | 'imei2') => void;
  onAutoGenerateMac: (isBt?: boolean) => void;
  onWriteNvramToDevice: () => void;
  onFixUnknownBaseband: () => void;
  isFixingBaseband: boolean;
  onExportNvramBin: () => void;
  valOutputData: any;
}

export const ValHubTab: React.FC<ValHubTabProps> = memo(function ValHubTab({
  valTargetPort,
  onValTargetPortChange,
  valTargetBaud,
  valSelectedChipset,
  onSelectValChipset,
  onTriggerDtrRtsPulse,
  onAutoBaudNegotiation,
  onValHandshake,
  isValRunning,
  nvramData,
  onUpdateNvramField,
  onAutoGenerateImei,
  onAutoFixLuhn,
  onAutoGenerateMac,
  onWriteNvramToDevice,
  onFixUnknownBaseband,
  isFixingBaseband,
  onExportNvramBin,
  valOutputData
}) {
  const [selectedHexView, setSelectedHexView] = useState<'APCFG0' | 'MD1_NVRAM' | 'PROTECT_F'>('APCFG0');

  // Generate live hex rows from the serialized binary buffer
  const hexRows: NvramHexRow[] = useMemo(() => {
    return NvramEngine.generateHexRows(nvramData.rawNvramBuffer, 128);
  }, [nvramData.rawNvramBuffer]);

  return (
    <div className="space-y-6 font-mono">
      {/* ========================================================================= */}
      {/* 1. VAL HEADER & HARDWARE TUNING BAR                                      */}
      {/* ========================================================================= */}
      <div className="bg-[#111622] border border-[#1f293d] rounded-xl p-5 flex flex-wrap items-center justify-between gap-4 shadow-lg">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-[#00f0ff]/10 border border-[#00f0ff]/30 text-[#00f0ff] flex items-center justify-center">
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-bold text-white text-base flex items-center gap-2">
              <span>VENDOR & MODEL LAYER (VAL)</span>
              <span className="text-[11px] px-2 py-0.5 bg-[#00f0ff]/10 text-[#00f0ff] rounded border border-[#00f0ff]/30 font-bold">
                UNIFIED OEM PROTOCOLS
              </span>
            </h3>
            <p className="text-xs text-[#9ca3af]">
              Unifikované bootloader sekvence pro Qualcomm, MediaTek BROM, Espressif (ESP32) i STM32 DFU
            </p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <select
            value={valTargetPort}
            onChange={e => onValTargetPortChange(e.target.value)}
            className="px-3 py-2 bg-[#07090e] border border-[#1f293d] rounded-lg text-xs text-[#00f0ff] font-bold outline-none cursor-pointer"
          >
            <option value="COM3">COM3 (Qualcomm 9008)</option>
            <option value="COM5">COM5 (MediaTek BROM)</option>
            <option value="COM7">COM7 (Espressif ESP32)</option>
            <option value="COM9">COM9 (STM32 VCP / DFU)</option>
          </select>

          <button
            onClick={onTriggerDtrRtsPulse}
            className="px-3.5 py-2 bg-[#ffaa00]/10 hover:bg-[#ffaa00]/20 text-[#ffaa00] border border-[#ffaa00]/30 rounded-lg text-xs font-bold flex items-center gap-1.5 transition-all"
          >
            <Zap className="w-3.5 h-3.5" />
            ⚡ DTR/RTS Reset Pulse
          </button>

          <button
            onClick={onAutoBaudNegotiation}
            className="px-3.5 py-2 bg-[#00ff9d]/10 hover:bg-[#00ff9d]/20 text-[#00ff9d] border border-[#00ff9d]/30 rounded-lg text-xs font-bold flex items-center gap-1.5 transition-all"
          >
            <Activity className="w-3.5 h-3.5" />
            Auto-Baud ({valTargetBaud} Bd)
          </button>
        </div>
      </div>

      {/* ========================================================================= */}
      {/* 2. 4 MULTI-VENDOR CHIPSET ACTION CARDS                                    */}
      {/* ========================================================================= */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* 1. Qualcomm */}
        <div
          className={`p-5 rounded-xl border transition-all ${
            valSelectedChipset === 'QUALCOMM'
              ? 'bg-[#0a192f] border-[#00f0ff] shadow-[0_0_20px_rgba(0,240,255,0.2)]'
              : 'bg-[#0a0d14] border-[#1f293d] hover:border-[#334155]'
          }`}
        >
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2 text-[#00f0ff] font-bold text-sm">
              <Cpu className="w-4 h-4" />
              <span>Qualcomm EDL</span>
            </div>
            <span className="text-[10px] px-1.5 py-0.5 bg-[#00f0ff]/10 text-[#00f0ff] rounded border border-[#00f0ff]/30 font-bold">
              VID: 05C6:9008
            </span>
          </div>
          <p className="text-xs text-[#9ca3af] mb-4">
            Sahara Protocol v2, Firehose MBN loader injection a streaming XML rawprogram dispatch.
          </p>
          <button
            onClick={() => {
              onSelectValChipset('QUALCOMM');
              onValHandshake('QUALCOMM');
            }}
            disabled={isValRunning}
            className="w-full py-2 bg-[#00f0ff] hover:bg-[#33f3ff] text-black font-bold text-xs rounded-lg transition-all disabled:opacity-50"
          >
            {isValRunning && valSelectedChipset === 'QUALCOMM' ? 'Odesílám Sahara...' : 'Spustit Sahara Handshake'}
          </button>
        </div>

        {/* 2. MediaTek */}
        <div
          className={`p-5 rounded-xl border transition-all ${
            valSelectedChipset === 'MEDIATEK'
              ? 'bg-[#0a192f] border-[#00ff9d] shadow-[0_0_20px_rgba(0,255,157,0.2)]'
              : 'bg-[#0a0d14] border-[#1f293d] hover:border-[#334155]'
          }`}
        >
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2 text-[#00ff9d] font-bold text-sm">
              <Flame className="w-4 h-4" />
              <span>MediaTek BROM</span>
            </div>
            <span className="text-[10px] px-1.5 py-0.5 bg-[#00ff9d]/10 text-[#00ff9d] rounded border border-[#00ff9d]/30 font-bold">
              VID: 0E8D:0003
            </span>
          </div>
          <p className="text-xs text-[#9ca3af] mb-4">
            BROM SLA/DAA exploit handshake, escape z preloader bootloopu a obnova NVRAM/IMEI.
          </p>
          <button
            onClick={() => {
              onSelectValChipset('MEDIATEK');
              onValHandshake('MEDIATEK');
            }}
            disabled={isValRunning}
            className="w-full py-2 bg-[#00ff9d] hover:bg-[#33ffaa] text-black font-bold text-xs rounded-lg transition-all disabled:opacity-50"
          >
            {isValRunning && valSelectedChipset === 'MEDIATEK' ? 'Bypassuji SLA...' : 'Spustit BROM Bypass'}
          </button>
        </div>

        {/* 3. Espressif ESP32 */}
        <div
          className={`p-5 rounded-xl border transition-all ${
            valSelectedChipset === 'ESPRESSIF'
              ? 'bg-[#0a192f] border-[#ffaa00] shadow-[0_0_20px_rgba(255,170,0,0.2)]'
              : 'bg-[#0a0d14] border-[#1f293d] hover:border-[#334155]'
          }`}
        >
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2 text-[#ffaa00] font-bold text-sm">
              <Radio className="w-4 h-4" />
              <span>Espressif ESP32</span>
            </div>
            <span className="text-[10px] px-1.5 py-0.5 bg-[#ffaa00]/10 text-[#ffaa00] rounded border border-[#ffaa00]/30 font-bold">
              VID: 10C4:EA60
            </span>
          </div>
          <p className="text-xs text-[#9ca3af] mb-4">
            ROM Bootloader Sync (0x08), SLIP framing, čtení MAC adresy a SPI Flash 16MB attach.
          </p>
          <button
            onClick={() => {
              onSelectValChipset('ESPRESSIF');
              onValHandshake('ESPRESSIF');
            }}
            disabled={isValRunning}
            className="w-full py-2 bg-[#ffaa00] hover:bg-[#ffbb33] text-black font-bold text-xs rounded-lg transition-all disabled:opacity-50"
          >
            {isValRunning && valSelectedChipset === 'ESPRESSIF' ? 'Synchronizuji ROM...' : 'ESP32 ROM Sync (0x08)'}
          </button>
        </div>

        {/* 4. STM32 DFU */}
        <div
          className={`p-5 rounded-xl border transition-all ${
            valSelectedChipset === 'STM32'
              ? 'bg-[#0a192f] border-[#3b82f6] shadow-[0_0_20px_rgba(59,130,246,0.2)]'
              : 'bg-[#0a0d14] border-[#1f293d] hover:border-[#334155]'
          }`}
        >
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2 text-[#3b82f6] font-bold text-sm">
              <Terminal className="w-4 h-4" />
              <span>STM32 DFU / VCP</span>
            </div>
            <span className="text-[10px] px-1.5 py-0.5 bg-[#3b82f6]/10 text-[#3b82f6] rounded border border-[#3b82f6]/30 font-bold">
              VID: 0483:5740
            </span>
          </div>
          <p className="text-xs text-[#9ca3af] mb-4">
            USART/DFU Bootloader init (0x7F to 0x79 ACK), inspekce PID/GID a čtení Option Bytes.
          </p>
          <button
            onClick={() => {
              onSelectValChipset('STM32');
              onValHandshake('STM32');
            }}
            disabled={isValRunning}
            className="w-full py-2 bg-[#3b82f6] hover:bg-[#60a5fa] text-white font-bold text-xs rounded-lg transition-all disabled:opacity-50"
          >
            {isValRunning && valSelectedChipset === 'STM32' ? 'Inicializuji DFU...' : 'STM32 Init (0x7F)'}
          </button>
        </div>
      </div>

      {/* ========================================================================= */}
      {/* 3. INTERACTIVE MEDIATEK NVRAM & NVDATA WORKBENCH                         */}
      {/* ========================================================================= */}
      <div className="bg-[#111622] border-2 border-[#00ff9d]/30 rounded-xl p-5 space-y-5 shadow-[0_0_25px_rgba(0,255,157,0.08)]">
        {/* Workbench Header */}
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[#1f293d] pb-3">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-[#00ff9d]/10 text-[#00ff9d] border border-[#00ff9d]/30">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <h4 className="font-bold text-sm text-white flex items-center gap-2">
                <span>MEDIATEK NVRAM & NVDATA KALIBRÁTOR (BASEBAND REPAIR)</span>
                <span className={`px-2 py-0.5 text-[10px] font-bold rounded border ${
                  nvramData.basebandStatus === 'HEALTHY' || nvramData.basebandStatus === 'RESTORED'
                    ? 'bg-[#00ff9d]/10 text-[#00ff9d] border-[#00ff9d]/30'
                    : 'bg-[#ef4444]/15 text-[#ef4444] border-[#ef4444]/40 animate-pulse'
                }`}>
                  {nvramData.basebandStatus === 'HEALTHY' && '● BASEBAND NOMINÁLNÍ'}
                  {nvramData.basebandStatus === 'RESTORED' && '● BASEBAND OBNOVEN (CRC32 OK)'}
                  {nvramData.basebandStatus === 'NULL_IMEI' && '✖ CHYBÍ IMEI / NULL BASEBAND'}
                  {nvramData.basebandStatus === 'CORRUPTED_HEADER' && '▲ POŠKOZENÁ HLAVIČKA APCFG0'}
                </span>
              </h4>
              <p className="text-[11px] text-[#9ca3af]">
                Rekonstrukce oddílů nvram (0x02D88000), nvdata (0x04000000), nvcfg a protect_f/s s Luhn validací
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2 text-xs">
            <button
              onClick={onExportNvramBin}
              className="px-3 py-1.5 bg-[#1e293b] hover:bg-[#334155] text-[#d4d4d4] rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 border border-[#334155]"
              title="Stáhnout binární obraz NVRAM bloku"
            >
              <Download className="w-3.5 h-3.5" /> Záloha .BIN
            </button>

            <button
              onClick={onFixUnknownBaseband}
              disabled={isFixingBaseband}
              className="px-3.5 py-1.5 bg-[#ffaa00] hover:bg-[#ffbb33] text-black rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 shadow-[0_0_12px_rgba(255,170,0,0.3)] disabled:opacity-50"
            >
              <Wrench className={`w-3.5 h-3.5 ${isFixingBaseband ? 'animate-spin' : ''}`} />
              <span>{isFixingBaseband ? 'Opravuji Baseband...' : '🛠️ 1-Klik Fix Unknown Baseband'}</span>
            </button>
          </div>
        </div>

        {/* Section A: Device Identifiers (IMEI 1, IMEI 2, Wi-Fi MAC, BT MAC) */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* IMEI 1 */}
          <div className="bg-[#0a0d14] border border-[#1f293d] rounded-xl p-4 space-y-2">
            <div className="flex items-center justify-between text-xs">
              <label className="text-white font-bold flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-[#00ff9d]" /> Primární IMEI 1 (15 číslic):
              </label>
              <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
                nvramData.isImei1Valid
                  ? 'bg-[#00ff9d]/10 text-[#00ff9d] border border-[#00ff9d]/30'
                  : 'bg-[#ef4444]/15 text-[#ef4444] border border-[#ef4444]/40'
              }`}>
                {nvramData.isImei1Valid ? '✓ LUHN PLATNÝ' : '✖ NEPLATNÝ KONTROLNÍ SOUČET'}
              </span>
            </div>

            <div className="flex items-center gap-2">
              <input
                type="text"
                maxLength={15}
                value={nvramData.imei1}
                onChange={e => onUpdateNvramField('imei1', e.target.value.replace(/\D/g, '').slice(0, 15))}
                className="flex-1 px-3 py-2 bg-[#111622] border border-[#1f293d] rounded-lg text-[#00ff9d] font-bold text-sm tracking-wider outline-none focus:border-[#00ff9d]"
                placeholder="864521048891234"
              />
              <button
                onClick={() => onAutoFixLuhn('imei1')}
                className="px-2.5 py-2 bg-[#1e293b] hover:bg-[#334155] text-[#00f0ff] rounded-lg text-xs font-bold"
                title="Dopočítat správnou Luhn kontrolní číslici"
              >
                Opravit Luhn
              </button>
              <button
                onClick={() => onAutoGenerateImei('imei1')}
                className="px-2.5 py-2 bg-[#1e293b] hover:bg-[#334155] text-white rounded-lg text-xs font-bold"
                title="Vygenerovat platný IMEI"
              >
                Generovat
              </button>
            </div>
            <div className="text-[10px] text-[#64748b]">
              TAC (Typový kód): {nvramData.imei1.slice(0, 8) || 'N/A'} | SNR: {nvramData.imei1.slice(8, 14) || 'N/A'} | CD: {nvramData.imei1.slice(14) || '0'}
            </div>
          </div>

          {/* IMEI 2 */}
          <div className="bg-[#0a0d14] border border-[#1f293d] rounded-xl p-4 space-y-2">
            <div className="flex items-center justify-between text-xs">
              <label className="text-white font-bold flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-[#00f0ff]" /> Sekundární IMEI 2 (Dual SIM):
              </label>
              <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
                nvramData.isImei2Valid
                  ? 'bg-[#00ff9d]/10 text-[#00ff9d] border border-[#00ff9d]/30'
                  : 'bg-[#ef4444]/15 text-[#ef4444] border border-[#ef4444]/40'
              }`}>
                {nvramData.isImei2Valid ? '✓ LUHN PLATNÝ' : '✖ NEPLATNÝ KONTROLNÍ SOUČET'}
              </span>
            </div>

            <div className="flex items-center gap-2">
              <input
                type="text"
                maxLength={15}
                value={nvramData.imei2}
                onChange={e => onUpdateNvramField('imei2', e.target.value.replace(/\D/g, '').slice(0, 15))}
                className="flex-1 px-3 py-2 bg-[#111622] border border-[#1f293d] rounded-lg text-[#00f0ff] font-bold text-sm tracking-wider outline-none focus:border-[#00f0ff]"
                placeholder="864521048891235"
              />
              <button
                onClick={() => onAutoFixLuhn('imei2')}
                className="px-2.5 py-2 bg-[#1e293b] hover:bg-[#334155] text-[#00f0ff] rounded-lg text-xs font-bold"
                title="Dopočítat správnou Luhn kontrolní číslici"
              >
                Opravit Luhn
              </button>
              <button
                onClick={() => onAutoGenerateImei('imei2')}
                className="px-2.5 py-2 bg-[#1e293b] hover:bg-[#334155] text-white rounded-lg text-xs font-bold"
                title="Vygenerovat platný IMEI"
              >
                Generovat
              </button>
            </div>
            <div className="text-[10px] text-[#64748b]">
              TAC (Typový kód): {nvramData.imei2.slice(0, 8) || 'N/A'} | SNR: {nvramData.imei2.slice(8, 14) || 'N/A'} | CD: {nvramData.imei2.slice(14) || '0'}
            </div>
          </div>

          {/* Wi-Fi MAC Address */}
          <div className="bg-[#0a0d14] border border-[#1f293d] rounded-xl p-4 space-y-2">
            <div className="flex items-center justify-between text-xs">
              <label className="text-white font-bold flex items-center gap-1.5">
                <Wifi className="w-3.5 h-3.5 text-[#38bdf8]" /> Wi-Fi MAC Adresa (WLAN NVRAM):
              </label>
              <button
                onClick={() => onAutoGenerateMac(false)}
                className="text-[10px] text-[#38bdf8] hover:underline"
              >
                Generovat OUI MAC
              </button>
            </div>

            <input
              type="text"
              value={nvramData.wifiMac}
              onChange={e => onUpdateNvramField('wifiMac', NvramEngine.formatMacAddress(e.target.value))}
              className="w-full px-3 py-2 bg-[#111622] border border-[#1f293d] rounded-lg text-white font-mono font-bold text-sm tracking-widest outline-none focus:border-[#38bdf8]"
              placeholder="70:4D:7B:A1:B2:C3"
            />
            <div className="text-[10px] text-[#64748b] flex items-center justify-between">
              <span>Oprava NVRAM Err 0x10:</span>
              <span className="text-[#00ff9d] font-bold">Aktivní binární patch</span>
            </div>
          </div>

          {/* Bluetooth MAC Address */}
          <div className="bg-[#0a0d14] border border-[#1f293d] rounded-xl p-4 space-y-2">
            <div className="flex items-center justify-between text-xs">
              <label className="text-white font-bold flex items-center gap-1.5">
                <Radio className="w-3.5 h-3.5 text-[#a78bfa]" /> Bluetooth BD_ADDR (BT Controller):
              </label>
              <button
                onClick={() => onAutoGenerateMac(true)}
                className="text-[10px] text-[#a78bfa] hover:underline"
              >
                Generovat BT MAC
              </button>
            </div>

            <input
              type="text"
              value={nvramData.bluetoothMac}
              onChange={e => onUpdateNvramField('bluetoothMac', NvramEngine.formatMacAddress(e.target.value))}
              className="w-full px-3 py-2 bg-[#111622] border border-[#1f293d] rounded-lg text-white font-mono font-bold text-sm tracking-widest outline-none focus:border-[#a78bfa]"
              placeholder="00:1A:7D:DA:71:02"
            />
            <div className="text-[10px] text-[#64748b] flex items-center justify-between">
              <span>Bluetooth OUI Vendor:</span>
              <span className="text-[#a78bfa] font-bold">MediaTek Wireless SoC</span>
            </div>
          </div>
        </div>

        {/* Section B: Radio & RF Tuning (Bands, Tx Power, AFC Offset) */}
        <div className="bg-[#0a0d14] border border-[#1f293d] rounded-xl p-4 space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-2 border-b border-[#162033] pb-2">
            <div className="flex items-center gap-2 text-white font-bold text-xs">
              <Radio className="w-4 h-4 text-[#ffaa00]" />
              <span>RF RÁDIOVÁ KALIBRACE & PÁSMA (BASEBAND BAND MASK)</span>
            </div>
            <div className="flex items-center gap-3 text-xs">
              <span className="text-[#64748b]">CRC32 Hash:</span>
              <span className="text-[#00ff9d] font-bold font-mono">{nvramData.crc32Checksum}</span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
            {/* 1. Band Checkboxes */}
            <div className="space-y-2">
              <div className="text-[11px] text-[#9ca3af] font-bold">Aktivní frekvenční pásma:</div>
              <div className="space-y-1.5">
                <label className="flex items-center gap-2 cursor-pointer text-white">
                  <input
                    type="checkbox"
                    checked={nvramData.rfBands.gsm}
                    onChange={e => onUpdateNvramField('rfBands', { ...nvramData.rfBands, gsm: e.target.checked })}
                    className="rounded border-[#1f293d] text-[#00ff9d]"
                  />
                  <span>GSM Quad-band (850/900/1800/1900)</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer text-white">
                  <input
                    type="checkbox"
                    checked={nvramData.rfBands.wcdma}
                    onChange={e => onUpdateNvramField('rfBands', { ...nvramData.rfBands, wcdma: e.target.checked })}
                    className="rounded border-[#1f293d] text-[#00ff9d]"
                  />
                  <span>WCDMA / 3G HSPA+ (B1/B2/B5/B8)</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer text-[#00f0ff] font-bold">
                  <input
                    type="checkbox"
                    checked={true}
                    readOnly
                    className="rounded border-[#1f293d] text-[#00f0ff]"
                  />
                  <span>LTE FDD/TDD (B1, B3, B7, B20, B28)</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer text-[#00ff9d] font-bold">
                  <input
                    type="checkbox"
                    checked={true}
                    readOnly
                    className="rounded border-[#1f293d] text-[#00ff9d]"
                  />
                  <span>5G Sub-6GHz NR (N78 / N28 NSA)</span>
                </label>
              </div>
            </div>

            {/* 2. Tx Power Offset */}
            <div className="space-y-2 bg-[#111622] p-3 rounded-lg border border-[#162033]">
              <div className="flex justify-between items-center text-[11px]">
                <span className="text-[#9ca3af] font-bold">Tx Power Offset:</span>
                <span className="text-[#00ff9d] font-bold font-mono">{nvramData.txPowerOffsetDbm > 0 ? `+${nvramData.txPowerOffsetDbm}` : nvramData.txPowerOffsetDbm} dBm</span>
              </div>
              <input
                type="range"
                min="-2.0"
                max="2.0"
                step="0.1"
                value={nvramData.txPowerOffsetDbm}
                onChange={e => onUpdateNvramField('txPowerOffsetDbm', parseFloat(e.target.value))}
                className="w-full accent-[#00ff9d] cursor-pointer"
              />
              <p className="text-[10px] text-[#64748b]">
                Jemné doladění výkonu vysílače pro eliminaci přehřívání RF front-endu.
              </p>
            </div>

            {/* 3. Crystal AFC Frequency Offset */}
            <div className="space-y-2 bg-[#111622] p-3 rounded-lg border border-[#162033]">
              <div className="flex justify-between items-center text-[11px]">
                <span className="text-[#9ca3af] font-bold">Crystal AFC Offset:</span>
                <span className="text-[#00f0ff] font-bold font-mono">{nvramData.crystalAfcOffsetPpm > 0 ? `+${nvramData.crystalAfcOffsetPpm}` : nvramData.crystalAfcOffsetPpm} ppm</span>
              </div>
              <input
                type="range"
                min="-20"
                max="20"
                step="1"
                value={nvramData.crystalAfcOffsetPpm}
                onChange={e => onUpdateNvramField('crystalAfcOffsetPpm', parseInt(e.target.value, 10))}
                className="w-full accent-[#00f0ff] cursor-pointer"
              />
              <p className="text-[10px] text-[#64748b]">
                Kompenzace teplotního driftu 26MHz TCXO oscilátoru pro stabilní příjem signálu.
              </p>
            </div>
          </div>
        </div>

        {/* Section C: Live Binary NVRAM Structure Inspector (Hex Dump) */}
        <div className="bg-[#070a10] border border-[#1f293d] rounded-xl p-4 space-y-3">
          <div className="flex flex-wrap items-center justify-between gap-3 text-xs border-b border-[#162033] pb-2">
            <div className="flex items-center gap-2 text-white font-bold">
              <Binary className="w-4 h-4 text-[#00f0ff]" />
              <span>ŽIVÝ INSPEKTOR STRUKTURY NVRAM (512 BAJTŮ BINÁRNÍ RÁMEC)</span>
            </div>

            <div className="flex items-center gap-1.5 text-[11px]">
              {(['APCFG0', 'MD1_NVRAM', 'PROTECT_F'] as const).map(view => (
                <button
                  key={view}
                  onClick={() => setSelectedHexView(view)}
                  className={`px-2.5 py-1 rounded transition-all ${
                    selectedHexView === view
                      ? 'bg-[#00f0ff]/20 text-[#00f0ff] border border-[#00f0ff]/40 font-bold'
                      : 'bg-[#111622] text-[#9ca3af] hover:text-white'
                  }`}
                >
                  {view}
                </button>
              ))}
            </div>
          </div>

          {/* Hex Dump Rows View */}
          <div className="bg-[#040609] p-3 rounded-lg border border-[#162033] overflow-x-auto text-xs font-mono text-[#9ca3af] max-h-52 overflow-y-auto">
            <div className="text-[#64748b] border-b border-[#162033] pb-1 mb-1 grid grid-cols-12 gap-2 text-[10px] font-bold">
              <span className="col-span-2">Offset</span>
              <span className="col-span-6">00 01 02 03 04 05 06 07  08 09 0A 0B 0C 0D 0E 0F</span>
              <span className="col-span-4">ASCII Dekódování</span>
            </div>
            <div className="space-y-0.5">
              {hexRows.map((row, idx) => (
                <div key={idx} className="grid grid-cols-12 gap-2 hover:bg-white/[0.03] py-0.5 rounded">
                  <span className="col-span-2 text-[#00f0ff] font-bold">{row.offset}</span>
                  <span className="col-span-6 text-[#d4d4d4] font-mono tracking-wide">
                    {row.hexBytes.slice(0, 8).join(' ')} &nbsp; {row.hexBytes.slice(8, 16).join(' ')}
                  </span>
                  <span className="col-span-4 text-[#00ff9d] font-mono whitespace-pre">
                    {row.ascii}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Section D: Master Action Execution Bar */}
        <div className="flex flex-wrap items-center justify-between gap-3 pt-2">
          <div className="text-xs text-[#9ca3af]">
            Cílový zápis: <span className="text-white font-bold">/dev/block/by-name/nvram</span> + synchronizace <span className="text-white font-bold">/nvdata</span>
          </div>

          <button
            onClick={onWriteNvramToDevice}
            disabled={isValRunning || !nvramData.isImei1Valid}
            className="px-6 py-2.5 bg-[#00ff9d] hover:bg-[#00dd88] text-black font-bold text-xs rounded-xl flex items-center gap-2 transition-all shadow-[0_0_20px_rgba(0,255,157,0.35)] disabled:opacity-50"
          >
            <CheckCircle2 className="w-4 h-4" />
            <span>{isValRunning ? 'Zapisuji NVRAM blok...' : '⚡ Zapsat & Kalibrovat NVRAM do Zařízení'}</span>
          </button>
        </div>
      </div>

      {/* ========================================================================= */}
      {/* 4. LIVE VAL RESPONSE INSPECTOR                                            */}
      {/* ========================================================================= */}
      {valOutputData && (
        <div className="bg-[#07090e] border border-[#00f0ff]/40 rounded-xl p-5 space-y-3 shadow-md">
          <div className="flex items-center justify-between border-b border-[#1f293d] pb-2 text-xs">
            <span className="text-[#00f0ff] font-bold flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-[#00ff9d]" /> Odpověď nízkoúrovňového VAL protokolu ({valOutputData.vendor})
            </span>
            <span className="text-[#6b7280]">Stav: {valOutputData.status}</span>
          </div>
          <pre className="text-xs text-[#00ff9d] overflow-x-auto bg-[#040609] p-3 rounded-lg border border-[#161f30]">
            {JSON.stringify(valOutputData, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
});
