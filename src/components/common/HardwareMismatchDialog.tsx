import React from 'react';
import { AlertTriangle, RefreshCw, X, ShieldAlert, Zap } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';

interface HardwareMismatchDialogProps {
  isOpen: boolean;
  onClose: () => void;
  detectedVid: string;
  detectedPid: string;
  expectedProfile: string;
  detectedChipset: string;
  onFixProfile: (newProfile: string) => void;
  onOverride: () => void;
  onDisconnect: () => void;
}

export const HardwareMismatchDialog: React.FC<HardwareMismatchDialogProps> = ({
  isOpen,
  onClose,
  detectedVid,
  detectedPid,
  expectedProfile,
  detectedChipset,
  onFixProfile,
  onOverride,
  onDisconnect
}) => {
  if (!isOpen) return null;

  const getProfileDisplayName = (p: string) => {
    switch (p) {
      case 'qualcomm': return 'Qualcomm Snapdragon (EDL)';
      case 'mediatek': return 'MediaTek Helio/Dimensity (BROM)';
      case 'samsung': return 'Samsung Exynos/LSI';
      case 'unisoc': return 'Unisoc Tiger (FDL)';
      default: return p.toUpperCase();
    }
  };

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
        {/* Backdrop */}
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
          className="absolute inset-0 bg-black/90 backdrop-blur-md"
        />

        {/* Dialog Content */}
        <motion.div
          initial={{ scale: 0.9, opacity: 0, y: 20 }}
          animate={{ scale: 1, opacity: 1, y: 0 }}
          exit={{ scale: 0.9, opacity: 0, y: 20 }}
          className="relative bg-[#0d111a] border-2 border-[#ef4444]/50 rounded-2xl max-w-lg w-full shadow-[0_0_50px_rgba(239,68,68,0.25)] overflow-hidden font-mono"
        >
          {/* Header */}
          <div className="bg-[#ef4444]/10 border-b border-[#ef4444]/20 p-4 flex items-center justify-between">
            <div className="flex items-center gap-3 text-[#ef4444]">
              <AlertTriangle className="w-6 h-6" />
              <h3 className="font-bold text-lg uppercase tracking-tight">Kritický Rozpor Hardware</h3>
            </div>
            <button onClick={onClose} className="text-[#9ca3af] hover:text-white transition-colors">
              <X className="w-5 h-5" />
            </button>
          </div>

          <div className="p-6 space-y-6">
            <div className="bg-[#1a0a0f] border border-[#ef4444]/30 rounded-xl p-4 space-y-3">
              <p className="text-sm text-[#d4d4d4] leading-relaxed">
                Detekovaný hardware na portu neodpovídá aktivnímu servisnímu profilu. Použití nesprávného protokolu může vést k chybě zápisu nebo poškození zařízení.
              </p>
              
              <div className="grid grid-cols-2 gap-4 pt-2">
                <div className="space-y-1">
                  <span className="text-[10px] text-[#6b7280] uppercase font-bold">Aktivní Profil</span>
                  <div className="bg-[#1e1e1e] p-2 rounded border border-[#333] text-[#ef4444] font-bold text-xs truncate">
                    {getProfileDisplayName(expectedProfile)}
                  </div>
                </div>
                <div className="space-y-1">
                  <span className="text-[10px] text-[#6b7280] uppercase font-bold">Detekovaný HW</span>
                  <div className="bg-[#062319] p-2 rounded border border-[#00ff9d]/30 text-[#00ff9d] font-bold text-xs truncate">
                    {detectedChipset} ({detectedVid}:{detectedPid})
                  </div>
                </div>
              </div>
            </div>

            <div className="space-y-3">
              <h4 className="text-[11px] text-[#6b7280] font-bold uppercase tracking-widest px-1">Doporučené Akce</h4>
              
              <div className="grid grid-cols-1 gap-2">
                {/* AUTO FIX */}
                <button
                  onClick={() => onFixProfile(detectedChipset.toLowerCase())}
                  className="group flex items-center justify-between p-3 bg-[#00ff9d]/10 hover:bg-[#00ff9d]/20 border border-[#00ff9d]/40 rounded-xl transition-all"
                >
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-[#00ff9d]/20 rounded-lg text-[#00ff9d]">
                      <RefreshCw className="w-4 h-4 group-hover:rotate-180 transition-transform duration-500" />
                    </div>
                    <div className="text-left">
                      <div className="text-xs font-bold text-[#00ff9d]">Opravit profil (Doporučeno)</div>
                      <div className="text-[10px] text-[#9ca3af]">Automaticky přepnout na {detectedChipset}</div>
                    </div>
                  </div>
                  <Zap className="w-4 h-4 text-[#00ff9d]" />
                </button>

                {/* OVERRIDE */}
                <button
                  onClick={onOverride}
                  className="flex items-center justify-between p-3 bg-[#1e293b] hover:bg-[#334155] border border-[#475569] rounded-xl transition-all"
                >
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-slate-700/50 rounded-lg text-slate-300">
                      <ShieldAlert className="w-4 h-4" />
                    </div>
                    <div className="text-left">
                      <div className="text-xs font-bold text-white">Pokračovat (Override)</div>
                      <div className="text-[10px] text-[#9ca3af]">Riskovat nekompatibilitu protokolů</div>
                    </div>
                  </div>
                </button>

                {/* DISCONNECT */}
                <button
                  onClick={onDisconnect}
                  className="flex items-center justify-center p-3 text-[#ef4444] hover:bg-[#ef4444]/10 rounded-xl transition-all text-xs font-bold"
                >
                  Odpojit hardware a zrušit akci
                </button>
              </div>
            </div>
          </div>

          <div className="bg-[#0d111a] border-t border-[#1f2d47] p-4 text-[9px] text-[#6b7280] text-center italic">
            Poznámka: Validace probíhá na úrovni VID (Vendor ID) v reálném čase.
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
};
