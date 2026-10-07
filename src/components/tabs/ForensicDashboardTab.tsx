import React, { memo, useState } from 'react';
import { Search, Database, FileText, HardDrive, RefreshCw } from 'lucide-react';
import { ForensicFile, ForensicDbTable } from '../../types/forensic';

interface ForensicDashboardTabProps {
  files: ForensicFile[];
  selectedFile: ForensicFile | null;
  onSelectFile: (file: ForensicFile) => void;
  dbTables: ForensicDbTable[];
  onAnalyzeDb: (file: ForensicFile) => void;
  isAnalyzing: boolean;
}

export const ForensicDashboardTab: React.FC<ForensicDashboardTabProps> = memo(function ForensicDashboardTab({
  files,
  selectedFile,
  onSelectFile,
  dbTables,
  onAnalyzeDb,
  isAnalyzing
}) {
  return (
    <div className="grid grid-cols-12 gap-4 h-[calc(100vh-160px)]">
      {/* Souborový strom */}
      <div className="col-span-4 bg-[#111622] border border-[#1f293d] rounded-xl p-4 overflow-y-auto">
        <h4 className="text-white font-bold mb-3 flex items-center gap-2">
          <HardDrive className="w-4 h-4 text-[#00f0ff]" /> Souborový systém (Dump)
        </h4>
        <div className="space-y-1">
          {files.map(file => (
            <button
              key={file.id}
              onClick={() => onSelectFile(file)}
              className={`w-full text-left px-3 py-2 rounded text-xs flex items-center justify-between ${
                selectedFile?.id === file.id ? 'bg-[#00f0ff]/20 text-[#00f0ff]' : 'text-[#9ca3af] hover:bg-[#1e293b]'
              }`}
            >
              <span className="flex items-center gap-2">
                {file.type === 'directory' ? '📁' : '📄'} {file.name}
              </span>
              {file.deleted && <span className="text-[10px] text-[#ef4444] font-bold">SMAZANÝ</span>}
            </button>
          ))}
        </div>
      </div>

      {/* Detail a analýza */}
      <div className="col-span-8 bg-[#111622] border border-[#1f293d] rounded-xl p-4 flex flex-col gap-4 overflow-hidden">
        {selectedFile ? (
          <>
            <div className="flex items-center justify-between">
              <h4 className="text-white font-bold">{selectedFile.name}</h4>
              <button
                onClick={() => onAnalyzeDb(selectedFile)}
                disabled={isAnalyzing}
                className="px-3 py-1.5 bg-[#00ff9d]/10 hover:bg-[#00ff9d]/20 text-[#00ff9d] border border-[#00ff9d]/30 rounded text-xs font-bold"
              >
                {isAnalyzing ? 'Analyzuji...' : 'Analyzovat SQLite'}
              </button>
            </div>
            {dbTables.length > 0 && (
              <div className="flex-1 overflow-y-auto">
                {dbTables.map(table => (
                  <div key={table.name} className="mb-4">
                    <h5 className="text-[#00f0ff] font-bold text-sm mb-2">{table.name}</h5>
                    <table className="w-full text-[10px] text-white">
                      <thead>
                        <tr className="bg-[#1e293b]">
                          {table.columns.map(col => <th key={col} className="p-2 border border-[#1f293d]">{col}</th>)}
                        </tr>
                      </thead>
                      <tbody>
                        {table.rows.map((row, i) => (
                          <tr key={i} className="hover:bg-[#1e293b]">
                            {row.map((cell, j) => <td key={j} className="p-2 border border-[#1f293d]">{String(cell)}</td>)}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ))}
              </div>
            )}
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center text-[#6b7280] text-sm">
            Vyberte soubor pro analýzu
          </div>
        )}
      </div>
    </div>
  );
});
