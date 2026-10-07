import React, { memo } from 'react';
import {
  X,
  Compass,
  Zap,
  Terminal,
  Database,
  Layers,
  FileCode,
  HardDrive,
  ShieldCheck,
  Smartphone,
  Sliders,
  Boxes,
  Lock,
  Unlock,
  Activity,
  UploadCloud,
  Cpu,
  RefreshCw
} from 'lucide-react';

interface HamburgerDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  activeTab: string;
  onSelectTab: (tabId: string) => void;
  onOpenGuide: (stepNumber?: number) => void;
}

export const HamburgerDrawer: React.FC<HamburgerDrawerProps> = memo(function HamburgerDrawer({
  isOpen,
  onClose,
  activeTab,
  onSelectTab,
  onOpenGuide
}) {
  if (!isOpen) return null;

  const navCategories = [
    {
      title: 'OPERÁTORSKÉ PRACOVIŠTĚ & FLASHING',
      items: [
        { id: 'overview', label: 'Hlavní Panel Operátora', icon: Compass, desc: 'Kompletní přehled a 3-sloupcový cockpit' },
        { id: 'frp', label: '1-Klik FRP & OEM Odemčení', icon: Unlock, desc: 'Bypass Google Account, Knox a MiCloud' },
        { id: 'partitions', label: 'Správce Oddílů & RAW Flash', icon: Layers, desc: 'Čtení a zápis GPT/LUN0 partition tabulky' },
        { id: 'fast', label: 'Fastboot Flasher & Slot A/B', icon: Zap, desc: 'Skenování, flashing a přepínání slotů' },
        { id: 'auto_router', label: 'Zero-Conf Auto Router', icon: Activity, desc: 'Automatická HW sonda a servisní rozhodnutí' }
      ]
    },
    {
      title: 'POKROČILÉ HARDWARE NÁSTROJE & PROTOKOLY',
      items: [
        { id: 'screen_mirror', label: 'Zrcadlení & Dotyk Displeje', icon: Smartphone, desc: 'Live 60 FPS přenos, ADB Shell a instalace APK' },
        { id: 'val_hub', label: 'VAL Hub & Oprava NVRAM', icon: Cpu, desc: 'Unifikované protokoly a obnova IMEI 1/2' },
        { id: 'memory_recovery', label: 'Memory Dump & Crashdump', icon: HardDrive, desc: '4KB blokový streaming a záchrana registrů' },
        { id: 'usb_doctor', label: 'USB Port Doctor & FTDI', icon: HardDrive, desc: 'Detekce uvíznutých portů a zátěžový test' },
        { id: 'auto_driver', label: 'Injektor Ovladačů', icon: Boxes, desc: 'Pre-flight verifikace QUSB / MTK VCOM' },
        { id: 'fault_telemetry', label: 'Telemetrie Závad & Watchdog', icon: Activity, desc: 'Analýza I/O zpoždění a resilience test' }
      ]
    },
    {
      title: 'ENTERPRISE, AUDIT & CLOUD',
      items: [
        { id: 'cloud', label: 'Knihovna Cloud Loaderů', icon: UploadCloud, desc: 'Šifrované Firehose ELF a MTK DA balíčky' },
        { id: 'audit_ledger', label: 'SQLite WAL Audit Ledger', icon: Database, desc: 'Kryptograficky podepsané servisní záznamy' },
        { id: 'fleet', label: 'Fleet Lab (Multi-Station)', icon: Boxes, desc: 'Správa flotily stanic a sdílení relací' }
      ]
    }
  ];

  return (
    <div className="fixed inset-0 z-40 bg-black/70 backdrop-blur-sm flex transition-all">
      <div className="w-80 sm:w-96 bg-[#0f1523] border-r border-[#1f2d47] h-full flex flex-col shadow-2xl overflow-y-auto animate-in slide-in-from-left duration-200">
        {/* Drawer Header */}
        <div className="p-4 bg-[#141c2e] border-b border-[#1f2d47] flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-lg bg-[#00f0ff] text-black font-black flex items-center justify-center text-xs">
              EUDCP
            </div>
            <div>
              <div className="text-xs font-bold text-white uppercase tracking-wider">NAVIGAČNÍ MENU STUDIA</div>
              <div className="text-[10px] text-[#9ca3af]">Všech 14 servisních modulů a nástrojů</div>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg bg-[#1e293b] hover:bg-[#334155] text-[#9ca3af] hover:text-white transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Drawer Content */}
        <div className="p-4 space-y-6 flex-1">
          {/* Guide Quick Launch Banner */}
          <div className="p-3.5 bg-gradient-to-br from-[#102436] to-[#0d1b2a] rounded-xl border border-[#00f0ff]/40 space-y-2 shadow-[0_0_15px_rgba(0,240,255,0.15)]">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-bold text-[#00f0ff] uppercase">Potřebujete se zorientovat?</span>
              <span className="text-[10px] bg-[#00f0ff]/20 text-[#00f0ff] px-1.5 py-0.5 rounded font-bold">KROKOVÝ PRŮVODCE</span>
            </div>
            <p className="text-xs text-[#94a3b8]">
              Spusťte interaktivního průvodce, který vás provede klíčovými prvky pracoviště a logikou kroků.
            </p>
            <button
              onClick={() => {
                onClose();
                onOpenGuide();
              }}
              className="w-full py-2 bg-gradient-to-r from-[#00f0ff] to-[#00ff9d] text-black font-black text-xs rounded-lg hover:opacity-90 transition-all flex items-center justify-center gap-1.5"
            >
              <span>Spustit Průvodce Cockpitem</span>
            </button>
          </div>

          {/* Navigation Categories */}
          {navCategories.map(cat => (
            <div key={cat.title} className="space-y-2">
              <div className="text-[10px] font-bold text-[#64748b] tracking-wider uppercase px-2">
                {cat.title}
              </div>
              <div className="space-y-1">
                {cat.items.map(item => {
                  const Icon = item.icon;
                  const isActive = activeTab === item.id;
                  return (
                    <button
                      key={item.id}
                      onClick={() => {
                        onSelectTab(item.id);
                        onClose();
                      }}
                      className={`w-full text-left p-2.5 rounded-xl border transition-all flex items-start gap-3 ${
                        isActive
                          ? 'bg-[#18263e] border-[#00f0ff] text-white shadow-[0_0_10px_rgba(0,240,255,0.2)]'
                          : 'bg-[#121929] hover:bg-[#1a243a] border-[#1e2a42] text-[#cbd5e1]'
                      }`}
                    >
                      <div className={`p-2 rounded-lg mt-0.5 ${isActive ? 'bg-[#00f0ff] text-black' : 'bg-[#1e293b] text-[#38bdf8]'}`}>
                        <Icon className="w-4 h-4" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="text-xs font-bold truncate flex items-center justify-between">
                          <span>{item.label}</span>
                          {isActive && <span className="w-2 h-2 rounded-full bg-[#00f0ff]" />}
                        </div>
                        <div className="text-[11px] text-[#64748b] truncate mt-0.5">{item.desc}</div>
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
        </div>

        {/* Drawer Footer */}
        <div className="p-4 bg-[#0a0f18] border-t border-[#1a2438] text-[10px] text-[#64748b] flex items-center justify-between">
          <span>EUDCP Studio v1.0 PRO</span>
          <span className="text-[#38bdf8]">Windows OS Native Kiosk</span>
        </div>
      </div>

      <div className="flex-1" onClick={onClose} />
    </div>
  );
});
