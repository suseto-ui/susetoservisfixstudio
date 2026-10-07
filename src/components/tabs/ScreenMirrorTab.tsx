import React, { memo, useState } from 'react';
import {
  Smartphone,
  Activity,
  Wifi,
  Settings,
  FolderDown,
  Terminal,
  Eye,
  Shield,
  FileCode,
  Layers,
  ChevronLeft,
  Send,
  Download
} from 'lucide-react';
import { DeviceTelemetry } from '../../services/screenMirrorEngine';

interface ScreenMirrorTabProps {
  screenTelemetry: DeviceTelemetry;
  activeScreenApp: string;
  onSelectScreenApp: (app: string) => void;
  onScreenTap: (e: React.MouseEvent<HTMLDivElement>) => void;
  screenTouchRipple: { x: number; y: number } | null;
  onScreenKeyAction: (key: string) => void;
  screenShellLogs: string[];
  screenShellCmd: string;
  onScreenShellCmdChange: (cmd: string) => void;
  onScreenShellSubmit: () => void;
  onInstallApk: (apkName: string) => void;
}

export const ScreenMirrorTab: React.FC<ScreenMirrorTabProps> = memo(function ScreenMirrorTab({
  screenTelemetry,
  activeScreenApp,
  onSelectScreenApp,
  onScreenTap,
  screenTouchRipple,
  onScreenKeyAction,
  screenShellLogs,
  screenShellCmd,
  onScreenShellCmdChange,
  onScreenShellSubmit,
  onInstallApk
}) {
  return (
    <div className="space-y-6 font-mono">
      {/* Header */}
      <div className="bg-[#111622] border border-[#1f293d] rounded-xl p-5 flex flex-wrap items-center justify-between gap-4 shadow-lg">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-[#00ff9d]/10 border border-[#00ff9d]/30 text-[#00ff9d] flex items-center justify-center">
            <Smartphone className="w-5 h-5 text-[#00ff9d]" />
          </div>
          <div>
            <h3 className="font-bold text-white text-base flex items-center gap-2">
              <span>INTERAKTIVNÍ ZRCADLENÍ & DOTYKOVÉ OVLÁDÁNÍ DISPLEJE</span>
              <span className="text-[11px] px-2 py-0.5 bg-[#00ff9d]/10 text-[#00ff9d] rounded border border-[#00ff9d]/30 font-bold">
                ADB STREAM LIVE
              </span>
            </h3>
            <p className="text-xs text-[#9ca3af]">
              Přímý dotykový přenos myší s ADB souřadnicemi, ovládací tlačítka, živý ADB Shell a 1-klik instalace APK balíčků
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="px-2.5 py-1 bg-[#00ff9d]/10 text-[#00ff9d] border border-[#00ff9d]/30 rounded text-xs font-bold flex items-center gap-1.5">
            <Activity className="w-3.5 h-3.5" /> 60 FPS Stream
          </span>
          <span className="px-2.5 py-1 bg-[#00f0ff]/10 text-[#00f0ff] border border-[#00f0ff]/30 rounded text-xs font-bold">
            {screenTelemetry.resolution}
          </span>
        </div>
      </div>

      {/* Main Mirror Cockpit (Interactive Mockup + Tools) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Interactive Phone Screen */}
        <div className="lg:col-span-5 flex flex-col items-center">
          <div className="w-[320px] sm:w-[350px] bg-[#000000] border-4 border-[#2b3548] rounded-[40px] shadow-[0_0_35px_rgba(0,0,0,0.8)] overflow-hidden flex flex-col relative select-none">
            {/* Smartphone Top Notch / Speaker */}
            <div className="h-6 bg-[#000000] flex items-center justify-center relative">
              <div className="w-20 h-3 bg-[#1e293b] rounded-full" />
              <div className="w-2.5 h-2.5 bg-[#0f172a] rounded-full absolute right-16 border border-[#334155]" />
            </div>

            {/* Android Status Bar */}
            <div className="bg-[#050811] px-5 py-1 flex items-center justify-between text-[10px] text-[#9ca3af] font-mono border-b border-white/5">
              <span>14:35</span>
              <div className="flex items-center gap-2">
                <span>5G</span>
                <Wifi className="w-3 h-3 text-[#00ff9d]" />
                <span className="text-[#00ff9d] font-bold">{screenTelemetry.battery_level_pct}%</span>
              </div>
            </div>

            {/* Interactive Screen Viewport (Click to Tap) */}
            <div
              onClick={onScreenTap}
              className="h-[520px] bg-gradient-to-b from-[#0a1120] via-[#070b14] to-[#0a1120] relative cursor-crosshair overflow-hidden p-4 flex flex-col justify-between"
            >
              {/* Ripple on Click */}
              {screenTouchRipple && (
                <div
                  className="absolute w-8 h-8 rounded-full bg-[#00f0ff]/50 border-2 border-white pointer-events-none animate-ping -translate-x-1/2 -translate-y-1/2 z-30"
                  style={{ left: screenTouchRipple.x, top: screenTouchRipple.y }}
                />
              )}

              {/* Active App Header */}
              <div className="p-3 bg-white/5 rounded-xl border border-white/10 text-center space-y-1 backdrop-blur-sm">
                <div className="text-[10px] text-[#6b7280] uppercase tracking-wider">Aktivní aplikace</div>
                <div className="text-white font-bold text-xs">{activeScreenApp}</div>
              </div>

              {/* Quick Interactive App Icons */}
              <div className="grid grid-cols-3 gap-3 my-auto">
                {[
                  { name: 'Nastavení', icon: Settings, color: 'text-[#00f0ff]', bg: 'bg-[#00f0ff]/10' },
                  { name: 'Správce souborů', icon: FolderDown, color: 'text-[#ffaa00]', bg: 'bg-[#ffaa00]/10' },
                  { name: 'Terminál', icon: Terminal, color: 'text-[#00ff9d]', bg: 'bg-[#00ff9d]/10' },
                  { name: 'Fotoaparát', icon: Eye, color: 'text-[#ff3366]', bg: 'bg-[#ff3366]/10' },
                  { name: 'Bezpečnost', icon: Shield, color: 'text-[#a855f7]', bg: 'bg-[#a855f7]/10' },
                  { name: 'Vývojář', icon: FileCode, color: 'text-[#38bdf8]', bg: 'bg-[#38bdf8]/10' }
                ].map((app, i) => {
                  const Icon = app.icon;
                  return (
                    <button
                      key={i}
                      onClick={(e) => {
                        e.stopPropagation();
                        onSelectScreenApp(app.name);
                      }}
                      className="p-3 rounded-2xl bg-white/5 hover:bg-white/15 border border-white/10 flex flex-col items-center gap-1.5 transition-all active:scale-95"
                    >
                      <div className={`w-9 h-9 rounded-xl ${app.bg} flex items-center justify-center ${app.color}`}>
                        <Icon className="w-5 h-5" />
                      </div>
                      <span className="text-[10px] text-[#cbd5e1] font-medium truncate w-full text-center">{app.name}</span>
                    </button>
                  );
                })}
              </div>

              {/* Hint text */}
              <div className="text-center text-[10px] text-[#6b7280] py-1 bg-black/40 rounded-lg">
                👆 Klikněte kamkoliv na displej pro dotyk
              </div>
            </div>

            {/* Android Navigation Bar (Back / Home / Recents) */}
            <div className="h-12 bg-[#050811] border-t border-white/10 flex items-center justify-around px-6">
              <button
                onClick={() => onScreenKeyAction('APP_SWITCH')}
                className="p-2 text-[#9ca3af] hover:text-white transition-colors"
                title="Přehled aplikací (Recent Apps)"
              >
                <Layers className="w-4 h-4" />
              </button>
              <button
                onClick={() => onScreenKeyAction('HOME')}
                className="p-2 text-[#9ca3af] hover:text-white transition-colors"
                title="Domovská obrazovka (Home)"
              >
                <div className="w-3.5 h-3.5 rounded-full border-2 border-[#9ca3af]" />
              </button>
              <button
                onClick={() => onScreenKeyAction('BACK')}
                className="p-2 text-[#9ca3af] hover:text-white transition-colors"
                title="Zpět (Back)"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        {/* Right Column: Device Telemetry, ADB Shell & 1-Click APK Installer */}
        <div className="lg:col-span-7 space-y-5">
          {/* Telemetry Matrix */}
          <div className="bg-[#0a0d14] border border-[#1f293d] rounded-xl p-5 space-y-3">
            <div className="flex items-center justify-between border-b border-[#1f293d] pb-2 text-xs">
              <span className="text-[#00f0ff] font-bold flex items-center gap-1.5">
                <Smartphone className="w-4 h-4" /> Telemetrie připojeného zařízení
              </span>
              <span className="text-[#00ff9d] font-bold">ADB ONLINE (Authorized)</span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs">
              <div className="p-2.5 bg-[#111622] rounded-lg border border-[#1f293d]">
                <div className="text-[#6b7280] text-[10px]">Model</div>
                <div className="text-white font-bold truncate">{screenTelemetry.model}</div>
              </div>
              <div className="p-2.5 bg-[#111622] rounded-lg border border-[#1f293d]">
                <div className="text-[#6b7280] text-[10px]">Verze Androidu</div>
                <div className="text-[#00ff9d] font-bold">{screenTelemetry.android_version}</div>
              </div>
              <div className="p-2.5 bg-[#111622] rounded-lg border border-[#1f293d]">
                <div className="text-[#6b7280] text-[10px]">Bezpečnostní záplata</div>
                <div className="text-white font-bold">{screenTelemetry.security_patch}</div>
              </div>
              <div className="p-2.5 bg-[#111622] rounded-lg border border-[#1f293d]">
                <div className="text-[#6b7280] text-[10px]">Baterie & Teplota</div>
                <div className="text-[#ffaa00] font-bold">{screenTelemetry.battery_level_pct}% ({screenTelemetry.battery_temp_c}°C)</div>
              </div>
              <div className="p-2.5 bg-[#111622] rounded-lg border border-[#1f293d]">
                <div className="text-[#6b7280] text-[10px]">Rozlišení & DPI</div>
                <div className="text-white font-bold">{screenTelemetry.resolution} ({screenTelemetry.density_dpi} dpi)</div>
              </div>
              <div className="p-2.5 bg-[#111622] rounded-lg border border-[#1f293d]">
                <div className="text-[#6b7280] text-[10px]">SELinux Režim</div>
                <div className="text-[#00ff9d] font-bold">{screenTelemetry.selinux_mode}</div>
              </div>
            </div>
          </div>

          {/* Live ADB Shell Terminal */}
          <div className="bg-[#0a0d14] border border-[#1f293d] rounded-xl p-5 space-y-3">
            <div className="flex items-center justify-between border-b border-[#1f293d] pb-2 text-xs">
              <span className="text-white font-bold flex items-center gap-1.5">
                <Terminal className="w-4 h-4 text-[#00ff9d]" /> Interaktivní ADB Shell konzole
              </span>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => onScreenKeyAction('POWER')}
                  className="px-2 py-0.5 bg-[#ff3366]/10 text-[#ff3366] border border-[#ff3366]/30 rounded text-[10px] font-bold"
                >
                  Power Klíč
                </button>
                <button
                  onClick={() => onScreenKeyAction('VOLUME_UP')}
                  className="px-2 py-0.5 bg-[#1e293b] text-white rounded text-[10px]"
                >
                  Vol +
                </button>
                <button
                  onClick={() => onScreenKeyAction('VOLUME_DOWN')}
                  className="px-2 py-0.5 bg-[#1e293b] text-white rounded text-[10px]"
                >
                  Vol -
                </button>
              </div>
            </div>

            <div className="h-36 bg-[#050811] rounded-lg p-3 text-xs overflow-y-auto space-y-1 border border-[#161f30]">
              {screenShellLogs.map((log, i) => (
                <div key={i} className="text-[#cbd5e1] leading-relaxed break-all font-mono">
                  {log}
                </div>
              ))}
            </div>

            {/* Shell Input Row */}
            <div className="flex items-center gap-2">
              <input
                type="text"
                value={screenShellCmd}
                onChange={e => onScreenShellCmdChange(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && onScreenShellSubmit()}
                placeholder="Zadejte ADB příkaz (např. dumpsys battery, getprop, pm list packages)..."
                className="flex-1 px-3 py-2 bg-[#111622] border border-[#1f293d] rounded-lg text-xs text-white placeholder-[#6b7280] focus:outline-none focus:border-[#00f0ff]"
              />
              <button
                onClick={onScreenShellSubmit}
                className="px-4 py-2 bg-[#00f0ff] hover:bg-[#33f3ff] text-black font-bold text-xs rounded-lg transition-all flex items-center gap-1"
              >
                <Send className="w-3.5 h-3.5" /> Odeslat
              </button>
            </div>
          </div>

          {/* 1-Click APK Installer Panel */}
          <div className="bg-[#0a0d14] border border-[#1f293d] rounded-xl p-5 space-y-3 text-xs">
            <div className="flex items-center justify-between border-b border-[#1f293d] pb-2">
              <span className="font-bold text-white flex items-center gap-1.5">
                <FolderDown className="w-4 h-4 text-[#ffaa00]" /> 1-Klik Rychlá instalace servisních APK balíčků
              </span>
              <span className="text-[11px] text-[#6b7280]">adb install -r -d</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {[
                { name: 'Magisk_v27.0_Root.apk', desc: 'Root & SuperSU Manažer' },
                { name: 'FactoryTest_Diag_v4.apk', desc: 'Hardwarová diagnostika displeje a senzorů' },
                { name: 'ForensicDump_Agent_v2.apk', desc: 'Extraktor zpráv, kontaktů a logů' },
                { name: 'QuickShortcutMaker_v2.apk', desc: 'Přímý spouštěč skrytých nastavení' }
              ].map((apk, i) => (
                <div key={i} className="p-3 bg-[#111622] rounded-lg border border-[#1f293d] flex items-center justify-between gap-2">
                  <div className="overflow-hidden">
                    <div className="text-white font-bold truncate">{apk.name}</div>
                    <div className="text-[10px] text-[#6b7280] truncate">{apk.desc}</div>
                  </div>
                  <button
                    onClick={() => onInstallApk(apk.name)}
                    className="px-2.5 py-1 bg-[#ffaa00]/10 hover:bg-[#ffaa00]/20 text-[#ffaa00] border border-[#ffaa00]/30 rounded text-[10px] font-bold whitespace-nowrap transition-colors"
                  >
                    Instalovat
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
});
