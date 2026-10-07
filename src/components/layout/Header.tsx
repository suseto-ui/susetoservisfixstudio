import React, { memo } from 'react';
import {
  Menu,
  Terminal,
  HardDrive,
  Usb,
  ShieldCheck,
  RotateCcw,
  Sparkles,
  HelpCircle,
  Activity,
  Zap,
  Monitor
} from 'lucide-react';
import { SerialDeviceDescriptor } from '../../services/webSerialEngine';

interface HeaderProps {
  isHamburgerOpen: boolean;
  onToggleHamburger: () => void;
  isConnected: boolean;
  connectedDevice: SerialDeviceDescriptor | null;
  dongleState: {
    authenticated: boolean;
    dongleId: string;
    tier: string;
    credits: number;
  };
  nativeBridgeAvailable: boolean;
  onOpenGuide: (step?: number) => void;
  onResetGuide: () => void;
  onSelfTest: () => void;
  isSelfTesting: boolean;
  isSplitScreenActive?: boolean;
  onToggleSplitScreen?: () => void;
}

export const Header: React.FC<HeaderProps> = memo(function Header({
  isHamburgerOpen,
  onToggleHamburger,
  isConnected,
  connectedDevice,
  dongleState,
  nativeBridgeAvailable,
  onOpenGuide,
  onResetGuide,
  onSelfTest,
  isSelfTesting,
  isSplitScreenActive,
  onToggleSplitScreen
}) {
  return (
    <header className="bg-[#111622] border-b border-[#1f2d47] px-4 py-2.5 flex items-center justify-between shadow-md shrink-0 select-none">
      {/* LEFT: Menu Button & Brand Title */}
      <div className="flex items-center gap-3">
        <button
          onClick={onToggleHamburger}
          className={`p-2 rounded-lg border transition-all flex items-center justify-center ${
            isHamburgerOpen
              ? 'bg-[#00f0ff] text-black border-[#00f0ff] shadow-[0_0_12px_rgba(0,240,255,0.4)]'
              : 'bg-[#1a2337] hover:bg-[#25334e] text-[#d4d4d4] border-[#2e3e5b]'
          }`}
          title="Otevřít/Zavřít panel nástrojů a navigace"
          aria-label="Menu"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-[#00f0ff] to-[#00ff9d] flex items-center justify-center text-black font-black text-xs shadow-[0_0_10px_rgba(0,240,255,0.3)]">
            EUDCP
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="text-sm font-black tracking-wider text-white">SUSETO DROID FIX STUDIO</span>
              <span className="px-1.5 py-0.2 bg-[#1f293d] text-[#00f0ff] text-[10px] font-bold rounded border border-[#00f0ff]/30">PRO v1.0</span>
            </div>
            <div className="text-[10px] text-[#9ca3af] flex items-center gap-2">
              <span>Low-Level Flashing Cockpit</span>
              <span>•</span>
              <span className="text-[#38bdf8]">Windows OS Native EXE & WebSerial Engine</span>
            </div>
          </div>
        </div>
      </div>

      {/* CENTER: Hardware Dongle & Active Connection Telemetry */}
      <div className="hidden lg:flex items-center gap-4 text-xs font-mono">
        <div className="flex items-center gap-2 px-3 py-1 bg-[#161f30] rounded-lg border border-[#24334f]">
          <HardDrive className="w-3.5 h-3.5 text-[#38bdf8]" />
          <span className="text-[#9ca3af]">PORT:</span>
          <span className={`font-bold ${isConnected ? 'text-[#00ff9d]' : 'text-[#f59e0b]'}`}>
            {isConnected && connectedDevice ? `${connectedDevice.portLabel} (${connectedDevice.chipsetGuess})` : 'AUTO-SCANNING (0x05C6 / 0x0E8D)'}
          </span>
        </div>

        <div className="flex items-center gap-2 px-3 py-1 bg-[#161f30] rounded-lg border border-[#24334f]">
          <ShieldCheck className="w-3.5 h-3.5 text-[#00ff9d]" />
          <span className="text-[#9ca3af]">SMARTCARD:</span>
          <span className="text-[#00ff9d] font-bold">
            {dongleState.authenticated ? `ID: ${dongleState.dongleId.slice(0, 8)}... (${dongleState.tier})` : 'NONCE ACTIVE'}
          </span>
        </div>

        <div className="flex items-center gap-2 px-3 py-1 bg-[#161f30] rounded-lg border border-[#24334f]">
          <Zap className="w-3.5 h-3.5 text-[#00f0ff]" />
          <span className="text-[#9ca3af]">BRIDGE:</span>
          <span className={`font-bold ${nativeBridgeAvailable ? 'text-[#00ff9d]' : 'text-[#38bdf8]'}`}>
            {nativeBridgeAvailable ? 'NATIVE C++ (RPC)' : 'WEBSERIAL v2'}
          </span>
        </div>
      </div>

      {/* RIGHT: Action Controls & Guide Trigger */}
      <div className="flex items-center gap-2">
        {onToggleSplitScreen && (
          <button
            onClick={onToggleSplitScreen}
            className={`px-2.5 py-1.5 rounded-lg text-xs font-bold transition-all border flex items-center gap-1 ${
              isSplitScreenActive
                ? 'bg-[#00ff9d] text-black border-[#00ff9d] shadow-[0_0_10px_rgba(0,255,157,0.3)]'
                : 'bg-[#161f30] hover:bg-[#212c44] text-[#cbd5e1] border-[#24334f]'
            }`}
            title="Přepnout režim rozdělené obrazovky"
          >
            <span>◫ {isSplitScreenActive ? 'Split ON' : 'Split View'}</span>
          </button>
        )}

        <button
          onClick={onSelfTest}
          disabled={isSelfTesting}
          className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 bg-[#1a2337] hover:bg-[#25334e] text-xs font-bold text-[#e2e8f0] rounded-lg border border-[#2e3e5b] transition-all"
          title="Spustit rychlou diagnostiku vnitřních subsystémů"
        >
          <Activity className={`w-3.5 h-3.5 ${isSelfTesting ? 'animate-spin text-[#00f0ff]' : 'text-[#38bdf8]'}`} />
          <span>{isSelfTesting ? 'Testuji...' : 'Self-Test HW'}</span>
        </button>

        <button
          onClick={onResetGuide}
          className="hidden sm:flex items-center gap-1 px-2.5 py-1.5 bg-[#161f30] hover:bg-[#212c44] text-[#9ca3af] hover:text-white rounded-lg border border-[#24334f] text-xs transition-colors"
          title="Restartovat interaktivního průvodce od začátku"
        >
          <RotateCcw className="w-3.5 h-3.5 text-[#00f0ff]" />
          <span className="hidden md:inline">Restart Průvodce</span>
        </button>

        <button
          onClick={() => onOpenGuide()}
          className="flex items-center gap-1.5 px-3.5 py-1.5 bg-gradient-to-r from-[#00f0ff] to-[#00ff9d] hover:opacity-95 text-black font-black text-xs rounded-lg transition-all shadow-[0_0_15px_rgba(0,240,255,0.4)]"
          title="Otevřít interaktivního průvodce ovládáním a workflow operátora"
        >
          <Sparkles className="w-4 h-4 text-black" />
          <span>PRŮVODCE PRACOVIŠTĚM</span>
        </button>
      </div>
    </header>
  );
});
