import React, { memo } from 'react';
import {
  Play,
  CheckCircle2,
  AlertTriangle,
  Flame,
  ArrowRight,
  ShieldCheck,
  CheckSquare,
  Square,
  Sparkles,
  AlertCircle,
  Wrench,
  HelpCircle,
  Zap,
  HardDrive,
  Layers,
  Unlock,
  Boxes,
  Database,
  Activity,
  Smartphone,
  Cpu,
  UploadCloud,
  Columns
} from 'lucide-react';
import { ChecklistItem, GuideStep } from '../../types/operator';

interface OperatorCentralPipelineProps {
  checklist: ChecklistItem[];
  onToggleChecklistItem: (id: string) => void;
  onExecuteAllChecklist: () => void;
  onFixConflict: (item: ChecklistItem) => void;
  activeGuide: GuideStep;
  onExecuteGuideAction: () => void;
  isActionInProgress: boolean;
  activeTab: string;
  onSelectTab: (tab: string) => void;
  onRunStep: (stepNumber: number) => void;
  activeStepNumber: number;
  isSplitScreenActive: boolean;
  onToggleSplitScreen: () => void;
  secondaryTab: string;
  onSelectSecondaryTab: (tab: string) => void;
}

export const OperatorCentralPipeline: React.FC<OperatorCentralPipelineProps> = memo(function OperatorCentralPipeline({
  checklist,
  onToggleChecklistItem,
  onExecuteAllChecklist,
  onFixConflict,
  activeGuide,
  onExecuteGuideAction,
  isActionInProgress,
  activeTab,
  onSelectTab,
  onRunStep,
  activeStepNumber,
  isSplitScreenActive,
  onToggleSplitScreen,
  secondaryTab,
  onSelectSecondaryTab
}) {
  const steps = [
    { num: 1, title: 'DETEKCE HW', desc: 'Skenování COM/USB' },
    { num: 2, title: 'PRE-FLIGHT OVLADAČŮ', desc: 'Kontrola QUSB / MTK' },
    { num: 3, title: 'HANDSHAKE & LOADER', desc: 'Sahara / BROM Auth' },
    { num: 4, title: 'ZÁLOHA GPT', desc: 'LUN0 partition table' },
    { num: 5, title: '1-KLIK ODBLOKOVÁNÍ', desc: 'FRP / Knox / Reset' }
  ];

  const completedCount = checklist.filter(c => c.isDone).length;
  const progressPct = Math.round((completedCount / checklist.length) * 100);

  const subTabs = [
    { id: 'overview', label: 'Přehled', icon: HardDrive },
    { id: 'frp', label: '1-Klik FRP', icon: Unlock },
    { id: 'partitions', label: 'Oddíly & GPT', icon: Layers },
    { id: 'fast', label: 'Fastboot', icon: Zap },
    { id: 'screen_mirror', label: 'Screen Mirror', icon: Smartphone },
    { id: 'auto_router', label: 'Auto Router', icon: Activity },
    { id: 'val_hub', label: 'VAL Hub', icon: Cpu },
    { id: 'memory_recovery', label: 'Memory Dump', icon: HardDrive },
    { id: 'usb_doctor', label: 'USB Doctor', icon: Wrench },
    { id: 'auto_driver', label: 'Ovladače', icon: Boxes },
    { id: 'fault_telemetry', label: 'Telemetrie', icon: Activity },
    { id: 'cloud', label: 'Cloud Loaders', icon: UploadCloud },
    { id: 'audit_ledger', label: 'Audit Ledger', icon: Database },
    { id: 'fleet', label: 'Fleet Lab', icon: Boxes }
  ];

  return (
    <div className="space-y-4 font-mono">
      {/* 1. DETERMINISTIC 5-STEP SERVICE WORKFLOW BAR */}
      <div
        id="tour-operator-pipeline"
        className="bg-[#101624] border border-[#1e2a42] rounded-xl p-4 shadow-lg space-y-3"
      >
        <div className="flex flex-wrap items-center justify-between gap-2 border-b border-[#1b253b] pb-2.5">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-md bg-[#00f0ff] text-black font-black flex items-center justify-center text-xs">
              ★
            </div>
            <div>
              <h2 className="text-xs font-bold text-white uppercase tracking-wider">
                STANDARDNÍ SERVISNÍ SLED OPERÁTORA (5-KROKOVÝ PIPELINE)
              </h2>
              <div className="text-[10px] text-[#9ca3af]">
                Deterministická posloupnost kroků pro bezpečný servis
              </div>
            </div>
          </div>

          <button
            onClick={() => onRunStep(activeStepNumber)}
            className="px-4 py-1.5 bg-gradient-to-r from-[#00f0ff] via-[#00ff9d] to-[#10b981] hover:opacity-95 text-black font-black text-xs rounded-lg shadow-[0_0_15px_rgba(0,240,255,0.4)] transition-all flex items-center gap-1.5"
          >
            <Play className="w-3.5 h-3.5 fill-black" />
            <span>SPUSTIT CELÝ SERVISNÍ SLED (1-KLIK)</span>
          </button>
        </div>

        {/* Step Items Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-5 gap-2">
          {steps.map((st) => {
            const isCompleted = activeStepNumber > st.num;
            const isCurrent = activeStepNumber === st.num;

            return (
              <button
                key={st.num}
                onClick={() => onRunStep(st.num)}
                className={`text-left p-2.5 rounded-xl border transition-all flex flex-col justify-between ${
                  isCompleted
                    ? 'bg-[#06241a] border-[#10b981] text-[#a7f3d0]'
                    : isCurrent
                    ? 'bg-[#122338] border-[#00f0ff] text-white shadow-[0_0_12px_rgba(0,240,255,0.3)] ring-1 ring-[#00f0ff]'
                    : 'bg-[#0e1420] border-[#182337] text-[#64748b] hover:border-[#273857] hover:text-[#94a3b8]'
                }`}
              >
                <div className="flex items-center justify-between w-full mb-1">
                  <span
                    className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-black ${
                      isCompleted
                        ? 'bg-[#10b981] text-black'
                        : isCurrent
                        ? 'bg-[#00f0ff] text-black animate-pulse'
                        : 'bg-[#1e293b] text-[#94a3b8]'
                    }`}
                  >
                    {isCompleted ? '✓' : st.num}
                  </span>
                  <span className="text-[9px] uppercase font-bold tracking-wider opacity-80">
                    {isCompleted ? 'HOTOVO' : isCurrent ? 'AKTIVNÍ' : 'ČEKÁ'}
                  </span>
                </div>
                <div>
                  <div className="text-[11px] font-bold truncate text-white">{st.title}</div>
                  <div className="text-[9px] truncate opacity-70">{st.desc}</div>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* 2. INTELLIGENT ACTION CHECKLIST WITH CONFLICT DETECTION */}
      <div
        id="tour-operator-checklist"
        className="bg-[#101624] border border-[#1e2a42] rounded-xl p-4 shadow-lg space-y-3"
      >
        <div className="flex items-center justify-between border-b border-[#1b253b] pb-2">
          <div className="flex items-center gap-2">
            <CheckSquare className="w-4 h-4 text-[#00ff9d]" />
            <div>
              <h3 className="text-xs font-bold text-white uppercase tracking-wider">
                AKČNÍ CHECKLIST TECHNIKA & KONTROLA ROZPORŮ
              </h3>
              <div className="text-[10px] text-[#9ca3af]">
                Automatické ověření prerekvizit před zápisem a odblokováním
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-[11px] text-[#9ca3af]">
              Dokončeno: <strong className="text-white">{completedCount}/{checklist.length}</strong> ({progressPct}%)
            </span>
            <button
              onClick={onExecuteAllChecklist}
              className="px-3 py-1 bg-[#162033] hover:bg-[#233350] text-[#00f0ff] border border-[#00f0ff]/40 rounded-lg text-xs font-bold transition-colors flex items-center gap-1"
            >
              <Sparkles className="w-3 h-3" />
              <span>Automaticky vyřešit a spustit</span>
            </button>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="w-full bg-[#162033] h-1.5 rounded-full overflow-hidden">
          <div
            className="bg-gradient-to-r from-[#00f0ff] to-[#00ff9d] h-full transition-all duration-300"
            style={{ width: `${progressPct}%` }}
          />
        </div>

        {/* Checklist Rows */}
        <div className="space-y-1.5">
          {checklist.map((item) => (
            <div
              key={item.id}
              className={`p-2.5 rounded-lg border transition-all flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 ${
                item.isDone
                  ? 'bg-[#062016]/40 border-[#10b981]/40 text-[#cbd5e1]'
                  : item.conflictReason
                  ? 'bg-[#291306]/50 border-[#f59e0b]/50 text-white ring-1 ring-[#f59e0b]/30'
                  : 'bg-[#0d121e] border-[#182338] text-[#94a3b8]'
              }`}
            >
              <div className="flex items-start gap-2.5 flex-1 min-w-0">
                <button
                  onClick={() => onToggleChecklistItem(item.id)}
                  className="mt-0.5 text-[#00f0ff] hover:text-[#00ff9d] transition-colors"
                >
                  {item.isDone ? (
                    <CheckSquare className="w-4 h-4 text-[#10b981]" />
                  ) : (
                    <Square className="w-4 h-4 text-[#64748b]" />
                  )}
                </button>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className={`text-xs font-bold ${item.isDone ? 'line-through text-[#6ee7b7]' : 'text-white'}`}>
                      {item.title}
                    </span>
                    <span className="text-[9px] px-1.5 py-0.2 bg-[#1b253b] text-[#38bdf8] rounded font-bold uppercase">
                      {item.layer}
                    </span>
                    {item.isRequired && (
                      <span className="text-[9px] text-[#f43f5e] bg-[#3e0f17] px-1.5 py-0.2 rounded font-bold">
                        POVINNÉ
                      </span>
                    )}
                  </div>
                  <div className="text-[11px] text-[#64748b] mt-0.5">{item.description}</div>

                  {/* Conflict Notice if present */}
                  {item.conflictReason && !item.isDone && (
                    <div className="mt-1.5 p-2 bg-[#422006] rounded border border-[#b45309] text-[10px] text-[#fed7aa] flex items-start gap-2">
                      <AlertTriangle className="w-3.5 h-3.5 text-[#f59e0b] shrink-0 mt-0.5" />
                      <div className="flex-1">
                        <div><strong className="text-[#f59e0b]">DETEKOVÁN ROZPOR:</strong> {item.conflictReason}</div>
                        {item.conflictFix && (
                          <div className="mt-0.5 text-[#a7f3d0]">
                            <strong>Řešení:</strong> {item.conflictFix}
                          </div>
                        )}
                      </div>
                      <button
                        onClick={() => onFixConflict(item)}
                        className="px-2 py-1 bg-[#f59e0b] text-black font-black rounded text-[10px] hover:bg-[#d97706] transition-colors shrink-0"
                      >
                        Opravit
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 3. CONTEXTUAL SERVICE GUIDE HUD (IF / WHAT / WHY) */}
      <div
        id="tour-operator-guide"
        className="bg-[#101624] border border-[#1e2a42] rounded-xl p-4 shadow-lg space-y-3"
      >
        <div className="flex items-center justify-between border-b border-[#1b253b] pb-2">
          <div className="flex items-center gap-2">
            <HelpCircle className="w-4 h-4 text-[#38bdf8]" />
            <h3 className="text-xs font-bold text-white uppercase tracking-wider">
              KONTEXTOVÝ ASISTENT TECHNIKA (IF / WHAT / WHY)
            </h3>
          </div>
          <span className="text-[10px] bg-[#1e293b] text-[#38bdf8] px-2 py-0.5 rounded font-bold border border-[#2d3f5e]">
            Krok {activeGuide.stepNumber} z {activeGuide.totalSteps}
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
          {/* IF Box */}
          <div className="p-3 bg-[#0d1522] rounded-lg border border-[#1a293f] space-y-1">
            <div className="text-[10px] font-bold text-[#f59e0b] uppercase tracking-wider">1. POKUD (ZJIŠTĚNÝ STAV):</div>
            <div className="text-[#cbd5e1] leading-relaxed">{activeGuide.ifCondition}</div>
          </div>

          {/* WHAT Box */}
          <div className="p-3 bg-[#0d1c24] rounded-lg border border-[#173e4a] space-y-1">
            <div className="text-[10px] font-bold text-[#00f0ff] uppercase tracking-wider">2. CO UDĚLAT (AKCE):</div>
            <div className="text-[#e2e8f0] leading-relaxed font-bold">{activeGuide.whatAction}</div>
          </div>

          {/* WHY Box */}
          <div className="p-3 bg-[#092218] rounded-lg border border-[#134e35] space-y-1">
            <div className="text-[10px] font-bold text-[#10b981] uppercase tracking-wider">3. PROČ (ZDŮVODNĚNÍ):</div>
            <div className="text-[#a7f3d0] leading-relaxed">{activeGuide.whyRationale}</div>
          </div>
        </div>

        <div className="flex items-center justify-between pt-1">
          <span className="text-[10px] text-[#64748b]">Bezpečnostní úroveň: <strong>{activeGuide.safetyRating}</strong></span>
          <button
            onClick={onExecuteGuideAction}
            disabled={isActionInProgress}
            className="px-4 py-1.5 bg-[#00f0ff] hover:bg-[#00d0de] text-black font-black text-xs rounded-lg shadow-[0_0_12px_rgba(0,240,255,0.3)] transition-all flex items-center gap-1.5"
          >
            <span>{isActionInProgress ? 'Provádím...' : activeGuide.actionBtnText}</span>
            <ArrowRight className="w-3.5 h-3.5 text-black" />
          </button>
        </div>
      </div>

      {/* 4. SUB-TAB SELECTOR NAVIGATION BAR WITH SPLIT-SCREEN CONTROLLER */}
      <div className="bg-[#101624] border border-[#1e2a42] rounded-xl p-2 shadow flex flex-wrap items-center justify-between gap-2 text-xs">
        {/* Left: Scrollable Sub-tabs list */}
        <div className="flex items-center gap-1 overflow-x-auto flex-1 pb-0.5">
          {subTabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => onSelectTab(tab.id)}
                className={`px-3 py-1.5 rounded-lg font-bold transition-all whitespace-nowrap flex items-center gap-1.5 text-[11px] ${
                  isActive
                    ? 'bg-gradient-to-r from-[#00f0ff] to-[#0099ff] text-black shadow-[0_0_10px_rgba(0,240,255,0.35)]'
                    : 'text-[#94a3b8] hover:text-white hover:bg-[#162033]'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* Right: Split Screen Toggle Button */}
        <div className="flex items-center gap-2 border-l border-[#1f2d47] pl-2 shrink-0">
          <button
            onClick={onToggleSplitScreen}
            className={`px-3 py-1.5 rounded-lg font-bold transition-all flex items-center gap-1.5 text-[11px] border ${
              isSplitScreenActive
                ? 'bg-[#00ff9d] text-black border-[#00ff9d] shadow-[0_0_12px_rgba(0,255,157,0.4)]'
                : 'bg-[#162033] hover:bg-[#22324e] text-[#cbd5e1] border-[#253654]'
            }`}
            title="Zapnout/Vypnout režim rozdělené obrazovky pro současnou diagnostiku a flashing"
          >
            <Columns className="w-3.5 h-3.5" />
            <span>{isSplitScreenActive ? 'Split-Screen: AKTIVNÍ' : 'Split-Screen (◫)'}</span>
          </button>

          {isSplitScreenActive && (
            <select
              value={secondaryTab}
              onChange={(e) => onSelectSecondaryTab(e.target.value)}
              className="bg-[#0b101b] text-[#00f0ff] text-[11px] font-bold rounded px-2 py-1 border border-[#20304c] outline-none"
              title="Vyberte modul pro pravé rozdělené okno"
            >
              <option value="screen_mirror">Screen Mirror</option>
              <option value="usb_doctor">USB Doctor</option>
              <option value="fault_telemetry">Telemetrie</option>
              <option value="val_hub">VAL Hub / NVRAM</option>
              <option value="memory_recovery">Memory Dump</option>
              <option value="auto_driver">Injektor Ovladačů</option>
              <option value="audit_ledger">Audit Ledger</option>
              <option value="cloud">Cloud Loaders</option>
              <option value="fleet">Fleet Lab</option>
            </select>
          )}
        </div>
      </div>
    </div>
  );
});
