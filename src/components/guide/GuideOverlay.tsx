import React, { memo } from 'react';
import { Sparkles, Database, RotateCcw, X, ArrowRight, ChevronLeft, ChevronRight, Check } from 'lucide-react';
import { GUIDE_TOUR_STEPS } from '../../types/operator';

interface GuideOverlayProps {
  isOpen: boolean;
  onClose: () => void;
  currentStep: number;
  onStepChange: (step: number) => void;
  onActionTrigger?: (actionId?: string) => void;
}

export const GuideOverlay: React.FC<GuideOverlayProps> = memo(function GuideOverlay({
  isOpen,
  onClose,
  currentStep,
  onStepChange,
  onActionTrigger
}) {
  if (!isOpen) return null;

  const step = GUIDE_TOUR_STEPS[currentStep] || GUIDE_TOUR_STEPS[0];
  const progressPct = Math.round(((currentStep + 1) / GUIDE_TOUR_STEPS.length) * 100);

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 transition-all">
      <div className="bg-gradient-to-b from-[#111728] via-[#0d121f] to-[#0a0e1a] border-2 border-[#00f0ff] rounded-2xl max-w-2xl w-full shadow-[0_0_50px_rgba(0,240,255,0.35)] overflow-hidden font-mono text-[#d4d4d4] space-y-0 relative">
        {/* Header Bar */}
        <div className="px-6 py-4 bg-[#141c2e] border-b border-[#1f2d47] flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#00f0ff] to-[#00ff9d] flex items-center justify-center text-black font-black shadow-[0_0_15px_rgba(0,240,255,0.4)]">
              <Sparkles className="w-5 h-5 text-black" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs text-[#00f0ff] font-bold tracking-widest uppercase">INTERAKTIVNÍ PRŮVODCE PRACOVIŠTĚM</span>
                <span className="px-2 py-0.5 bg-[#00f0ff]/15 text-[#00f0ff] border border-[#00f0ff]/30 text-[10px] font-bold rounded">
                  Krok {step.stepNumber} z {step.totalSteps}
                </span>
                <span className="hidden sm:inline-flex items-center gap-1 text-[9px] text-[#00ff9d] bg-[#062319] px-1.5 py-0.5 rounded border border-[#153e2b]">
                  <Database className="w-2.5 h-2.5" /> Uloženo v localStorage
                </span>
              </div>
              <h3 className="text-base font-bold text-white mt-0.5">{step.title}</h3>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {currentStep > 0 && (
              <button
                onClick={() => onStepChange(0)}
                className="hidden sm:flex items-center gap-1 px-2.5 py-1 text-[10px] text-[#9ca3af] hover:text-white bg-[#1e293b] hover:bg-[#2e3e57] rounded-lg transition-colors border border-[#334155]"
                title="Restartovat průvodce od 1. kroku"
              >
                <RotateCcw className="w-3 h-3 text-[#00f0ff]" />
                <span>Od začátku</span>
              </button>
            )}
            <button
              onClick={onClose}
              className="w-8 h-8 rounded-lg bg-[#1e293b] hover:bg-[#334155] text-[#9ca3af] hover:text-white flex items-center justify-center transition-colors border border-[#334155]"
              title="Zavřít průvodce"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="w-full bg-[#162033] h-1.5">
          <div
            className="bg-gradient-to-r from-[#00f0ff] to-[#00ff9d] h-full transition-all duration-300 shadow-[0_0_10px_rgba(0,240,255,0.5)]"
            style={{ width: `${progressPct}%` }}
          />
        </div>

        {/* Body Content */}
        <div className="p-6 space-y-4">
          {/* Target Location Tag */}
          <div className="flex items-center gap-2 text-xs">
            <span className="text-[#6b7280]">Oblast v aplikaci:</span>
            <span className="px-2.5 py-1 bg-[#1a253b] text-[#38bdf8] border border-[#38bdf8]/30 rounded-md font-bold flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-[#38bdf8] animate-ping" />
              {step.targetArea}
            </span>
          </div>

          {/* Description Box */}
          <div className="p-4 bg-[#141b2d] rounded-xl border border-[#22314e] text-sm text-[#cbd5e1] leading-relaxed">
            {step.description}
          </div>

          {/* Relates To Box */}
          <div className="p-4 bg-[#101926] rounded-xl border border-[#1e293b] space-y-1.5">
            <div className="text-[11px] font-bold text-[#00f0ff] uppercase tracking-wider flex items-center gap-1.5">
              <span>⚡</span> Jak to navazuje na další kroky operátora:
            </div>
            <p className="text-xs text-[#94a3b8] leading-relaxed">{step.howItRelates}</p>
          </div>

          {/* Recommended Action */}
          <div className="p-4 bg-[#0d2218] rounded-xl border border-[#10b981]/30 flex items-start gap-3">
            <div className="w-7 h-7 rounded-lg bg-[#10b981]/20 flex items-center justify-center shrink-0 text-[#10b981] mt-0.5">
              <ArrowRight className="w-4 h-4" />
            </div>
            <div className="flex-1">
              <div className="text-xs font-bold text-[#34d399] uppercase tracking-wider">Doporučený krok operátora</div>
              <p className="text-xs text-[#a7f3d0] mt-0.5">{step.recommendedAction}</p>
            </div>
          </div>
        </div>

        {/* Step Indicator Dots */}
        <div className="px-6 py-2 bg-[#0d1322] border-t border-[#1a2337] flex items-center justify-center gap-2">
          {GUIDE_TOUR_STEPS.map((s, idx) => (
            <button
              key={s.id}
              onClick={() => onStepChange(idx)}
              className={`h-2 rounded-full transition-all ${
                idx === currentStep
                  ? 'w-8 bg-[#00f0ff] shadow-[0_0_8px_rgba(0,240,255,0.7)]'
                  : idx < currentStep
                  ? 'w-2 bg-[#10b981]'
                  : 'w-2 bg-[#334155] hover:bg-[#475569]'
              }`}
              title={`Přejít na krok ${s.stepNumber}: ${s.title}`}
            />
          ))}
        </div>

        {/* Footer Navigation Controls */}
        <div className="px-6 py-4 bg-[#141c2e] border-t border-[#1f2d47] flex items-center justify-between">
          <button
            onClick={() => onStepChange(Math.max(0, currentStep - 1))}
            disabled={currentStep === 0}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all border ${
              currentStep === 0
                ? 'opacity-40 cursor-not-allowed bg-[#111827] text-[#6b7280] border-[#1f2937]'
                : 'bg-[#1e293b] hover:bg-[#334155] text-white border-[#334155]'
            }`}
          >
            <ChevronLeft className="w-4 h-4" />
            <span>Předchozí krok</span>
          </button>

          <div className="flex items-center gap-3">
            <button
              onClick={onClose}
              className="text-xs text-[#9ca3af] hover:text-white transition-colors underline-offset-4 hover:underline"
            >
              Přeskočit průvodce
            </button>

            {currentStep < GUIDE_TOUR_STEPS.length - 1 ? (
              <button
                onClick={() => onStepChange(currentStep + 1)}
                className="flex items-center gap-1.5 px-4 py-2 bg-gradient-to-r from-[#00f0ff] to-[#00ff9d] text-black font-black text-xs rounded-lg hover:opacity-90 transition-all shadow-[0_0_15px_rgba(0,240,255,0.35)]"
              >
                <span>Další krok</span>
                <ChevronRight className="w-4 h-4 text-black" />
              </button>
            ) : (
              <button
                onClick={onClose}
                className="flex items-center gap-1.5 px-5 py-2 bg-[#10b981] hover:bg-[#059669] text-black font-black text-xs rounded-lg transition-all shadow-[0_0_15px_rgba(16,185,129,0.4)]"
              >
                <Check className="w-4 h-4 text-black" />
                <span>Rozumím, jít do cockpitů</span>
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
});
