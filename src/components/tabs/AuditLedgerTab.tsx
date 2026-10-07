import React, { memo } from 'react';
import { Database, ShieldCheck, CheckCircle2, Key, Download } from 'lucide-react';
import { StationItem } from '../../types/operator';

interface AuditLedgerTabProps {
  walAuditEntries: Array<{
    id: string;
    timestamp: string;
    operator: string;
    action: string;
    targetChip: string;
    status: 'COMMITTED' | 'ROLLED_BACK';
    signature: string;
  }>;
  dongleState: {
    authenticated: boolean;
    dongleId: string;
    tier: string;
    credits: number;
  };
  stations: StationItem[];
  onVerifyLedgerTamper: () => void;
  onExportAuditReport: () => void;
}

export const AuditLedgerTab: React.FC<AuditLedgerTabProps> = memo(function AuditLedgerTab({
  walAuditEntries,
  dongleState,
  stations,
  onVerifyLedgerTamper,
  onExportAuditReport
}) {
  return (
    <div className="space-y-6 font-mono">
      {/* Header */}
      <div className="bg-[#111622] border border-[#1f293d] rounded-xl p-5 flex flex-wrap items-center justify-between gap-4 shadow-lg">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-[#00ff9d]/10 border border-[#00ff9d]/30 text-[#00ff9d] flex items-center justify-center">
            <Database className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-bold text-white text-base flex items-center gap-2">
              <span>SQLITE WAL AUDIT LEDGER & SMARTCARD SECURITY</span>
              <span className="text-[11px] px-2 py-0.5 bg-[#00ff9d]/10 text-[#00ff9d] rounded border border-[#00ff9d]/30 font-bold">
                TAMPER-PROOF LEDGER
              </span>
            </h3>
            <p className="text-xs text-[#9ca3af]">
              Kryptograficky podepsané servisní záznamy, ochrana proti manipulaci s auditními logy a ISO-7816 token
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={onVerifyLedgerTamper}
            className="px-3.5 py-2 bg-[#1e293b] hover:bg-[#334155] text-white font-bold text-xs rounded-lg flex items-center gap-1.5 transition-all border border-[#334155]"
          >
            <ShieldCheck className="w-3.5 h-3.5 text-[#00ff9d]" />
            Ověřit integritu WAL
          </button>
          <button
            onClick={onExportAuditReport}
            className="px-3.5 py-2 bg-[#00f0ff] hover:bg-[#33f3ff] text-black font-bold text-xs rounded-lg flex items-center gap-1.5 transition-all shadow-[0_0_15px_rgba(0,240,255,0.3)]"
          >
            <Download className="w-3.5 h-3.5" />
            Exportovat forenzní audit
          </button>
        </div>
      </div>

      {/* SmartCard Status Box */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-[#0a0d14] border border-[#1f293d] rounded-xl p-4 space-y-1">
          <div className="text-[#6b7280] text-[10px]">SmartCard Dongle ID</div>
          <div className="text-white font-bold text-sm truncate">{dongleState.dongleId}</div>
          <div className="text-[10px] text-[#00ff9d]">Úroveň: {dongleState.tier}</div>
        </div>
        <div className="bg-[#0a0d14] border border-[#1f293d] rounded-xl p-4 space-y-1">
          <div className="text-[#6b7280] text-[10px]">Kredity / Autorizace</div>
          <div className="text-[#00f0ff] font-bold text-sm">{dongleState.credits} operací</div>
          <div className="text-[10px] text-[#9ca3af]">Kryptografický Nonce aktivní</div>
        </div>
        <div className="bg-[#0a0d14] border border-[#1f293d] rounded-xl p-4 space-y-1">
          <div className="text-[#6b7280] text-[10px]">Aktivní technické stanice</div>
          <div className="text-white font-bold text-sm">{stations.length} registrováno</div>
          <div className="text-[10px] text-[#00ff9d]">Zero Corruption WAL Režim</div>
        </div>
      </div>

      {/* Transactions Table */}
      <div className="bg-[#111622] border border-[#1f293d] rounded-xl p-5 space-y-4 shadow-md">
        <div className="flex items-center justify-between border-b border-[#1f293d] pb-3 text-xs">
          <span className="font-bold text-white">Poslední zapsané transakce v SQLite WAL</span>
          <span className="text-[#6b7280]">{walAuditEntries.length} záznamů</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left">
            <thead>
              <tr className="border-b border-[#1f293d] text-[#6b7280] pb-2">
                <th className="py-2 px-3">Čas</th>
                <th className="py-2 px-3">Operátor</th>
                <th className="py-2 px-3">Provedená akce</th>
                <th className="py-2 px-3">Cílový čip</th>
                <th className="py-2 px-3">Stav</th>
                <th className="py-2 px-3 font-mono">Digitální podpis (HMAC-SHA256)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1f293d]">
              {walAuditEntries.map((row) => (
                <tr key={row.id} className="hover:bg-white/[0.02] transition-colors">
                  <td className="py-2.5 px-3 text-[#9ca3af]">{row.timestamp}</td>
                  <td className="py-2.5 px-3 text-white font-bold">{row.operator}</td>
                  <td className="py-2.5 px-3 text-[#00f0ff]">{row.action}</td>
                  <td className="py-2.5 px-3 text-[#38bdf8]">{row.targetChip}</td>
                  <td className="py-2.5 px-3">
                    <span className="px-2 py-0.5 bg-[#00ff9d]/10 text-[#00ff9d] border border-[#00ff9d]/30 rounded text-[10px] font-bold">
                      {row.status}
                    </span>
                  </td>
                  <td className="py-2.5 px-3 text-[#64748b] font-mono text-[10px] truncate max-w-xs">
                    {row.signature}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
});
