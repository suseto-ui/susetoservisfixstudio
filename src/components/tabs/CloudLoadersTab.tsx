import React, { memo } from 'react';
import { UploadCloud, Download, ShieldCheck, HardDrive, RefreshCw } from 'lucide-react';
import { CloudPayloadItem } from '../../types/operator';

interface CloudLoadersTabProps {
  payloads: CloudPayloadItem[];
  onDownloadPayload: (id: string) => void;
  onRefreshCloud: () => void;
  isRefreshingCloud: boolean;
}

export const CloudLoadersTab: React.FC<CloudLoadersTabProps> = memo(function CloudLoadersTab({
  payloads,
  onDownloadPayload,
  onRefreshCloud,
  isRefreshingCloud
}) {
  return (
    <div className="space-y-6 font-mono">
      {/* Header */}
      <div className="bg-[#111622] border border-[#1f293d] rounded-xl p-5 flex flex-wrap items-center justify-between gap-4 shadow-lg">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-[#00f0ff]/10 border border-[#00f0ff]/30 text-[#00f0ff] flex items-center justify-center">
            <UploadCloud className="w-5 h-5 text-[#00f0ff]" />
          </div>
          <div>
            <h3 className="font-bold text-white text-base flex items-center gap-2">
              <span>CLOUD LOADER LIBRARY & OEM PAYLOADS</span>
              <span className="text-[11px] px-2 py-0.5 bg-[#00f0ff]/10 text-[#00f0ff] rounded border border-[#00f0ff]/30 font-bold">
                KRYPTOGRAFICKÁ INTEGRITA
              </span>
            </h3>
            <p className="text-xs text-[#9ca3af]">
              Ověřené Firehose ELF, MTK Download Agenty a Samsung PIT soubory s lokálním šifrováním v RAM
            </p>
          </div>
        </div>

        <button
          onClick={onRefreshCloud}
          disabled={isRefreshingCloud}
          className="px-4 py-2 bg-[#1e293b] hover:bg-[#334155] text-white font-bold text-xs rounded-lg flex items-center gap-1.5 transition-all border border-[#334155]"
        >
          <RefreshCw className={`w-3.5 h-3.5 text-[#00f0ff] ${isRefreshingCloud ? 'animate-spin' : ''}`} />
          <span>{isRefreshingCloud ? 'Synchronizuji...' : 'Aktualizovat knihovnu'}</span>
        </button>
      </div>

      {/* Payloads Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {payloads.map(payload => (
          <div
            key={payload.id}
            className="bg-[#0a0d14] border border-[#1f293d] rounded-xl p-5 space-y-3 shadow-md hover:border-[#2e3e5c] transition-all"
          >
            <div className="flex items-center justify-between">
              <span className="font-bold text-white text-sm truncate flex items-center gap-2">
                <HardDrive className="w-4 h-4 text-[#00f0ff]" />
                {payload.filename}
              </span>
              <span
                className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                  payload.status === 'SYNCED'
                    ? 'bg-[#00ff9d]/10 text-[#00ff9d] border-[#00ff9d]/30'
                    : 'bg-[#ffaa00]/10 text-[#ffaa00] border-[#ffaa00]/30'
                }`}
              >
                {payload.status}
              </span>
            </div>

            <div className="text-xs text-[#9ca3af] space-y-1">
              <div>Kategorie: <strong className="text-white uppercase">{payload.category}</strong></div>
              <div>Velikost: <strong className="text-white">{(payload.sizeKB / 1024).toFixed(2)} MB</strong></div>
              <div className="truncate">SHA-256: <strong className="text-[#38bdf8] font-mono">{payload.sha256}</strong></div>
            </div>

            <div className="pt-2 border-t border-[#1f293d] flex items-center justify-between">
              <span className="text-[10px] text-[#00ff9d] flex items-center gap-1">
                <ShieldCheck className="w-3.5 h-3.5" />
                {payload.encryptedLocally ? 'Šifrováno v RAM (AES-256)' : 'Veřejný loader'}
              </span>

              <button
                onClick={() => onDownloadPayload(payload.id)}
                className="px-3 py-1.5 bg-[#00f0ff]/10 hover:bg-[#00f0ff]/20 text-[#00f0ff] border border-[#00f0ff]/40 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5"
              >
                <Download className="w-3.5 h-3.5" />
                <span>Stáhnout do RAM</span>
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
});
