import { useState, useCallback, useMemo } from 'react';

export type LogFilterType = 'ALL' | 'INFO' | 'SUCCESS' | 'ERROR' | 'HARDWARE';

const MAX_LOGS_BUFFER = 1000;

export function useTerminalLogs(initialLogs: string[] = [
  '[SYSTEM] SusetoDroidFixStudio & EUDCP Engine v1.0-PROD Initialized.',
  '[HARDWARE] WebSerial Native Driver Layer Ready (WebUSB / CDC-ACM / FTDI).',
  '[SECURITY] SmartCard Nonce Engine Active (ISO-7816 Hardware Token).',
  '[SQLITE] WAL Audit Ledger Mounted (/var/log/eudcp_audit.db - Zero Corruption Mode).',
  '[ORCHESTRATOR] Auto-Queue Engine Active: Profiling USB Devices (Qualcomm / MTK / Samsung).'
]) {
  const [logs, setLogs] = useState<string[]>(initialLogs);
  const [logFilter, setLogFilter] = useState<LogFilterType>('ALL');

  const addLog = useCallback((message: string, prefix: string = '[SYSTEM]') => {
    const timestamp = new Date().toLocaleTimeString();
    const formatted = `${prefix} [${timestamp}] ${message}`;
    setLogs(prev => {
      const next = [...prev, formatted];
      if (next.length > MAX_LOGS_BUFFER) {
        return next.slice(next.length - MAX_LOGS_BUFFER);
      }
      return next;
    });
  }, []);

  const clearLogs = useCallback(() => {
    setLogs(['[SYSTEM] Log console buffer cleared by technician.']);
  }, []);

  const filteredLogs = useMemo(() => {
    if (logFilter === 'ALL') return logs;
    return logs.filter(log => {
      if (logFilter === 'SUCCESS') return log.includes('[SUCCESS]') || log.includes('[ÚSPĚCH]') || log.includes('[HOTOVO]') || log.includes('OK');
      if (logFilter === 'ERROR') return log.includes('[ERROR]') || log.includes('[CHYBA]') || log.includes('FAIL') || log.includes('CHYBA');
      if (logFilter === 'HARDWARE') return log.includes('[HARDWARE]') || log.includes('[USB]') || log.includes('[SERIAL]') || log.includes('[PORT]') || log.includes('DTR/RTS');
      if (logFilter === 'INFO') return !log.includes('[ERROR]') && !log.includes('FAIL');
      return true;
    });
  }, [logs, logFilter]);

  const exportLogsAsCSV = useCallback(() => {
    try {
      const csvContent = "data:text/csv;charset=utf-8," + logs.map(l => `"${l.replace(/"/g, '""')}"`).join("\n");
      const encodedUri = encodeURI(csvContent);
      const link = document.createElement("a");
      link.setAttribute("href", encodedUri);
      link.setAttribute("download", `eudcp_console_log_${Date.now()}.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      addLog("Export logu do CSV proběhl úspěšně.", "[EXPORT]");
    } catch {
      addLog("Chyba při exportu CSV logu.", "[ERROR]");
    }
  }, [logs, addLog]);

  return {
    logs,
    filteredLogs,
    logFilter,
    setLogFilter,
    addLog,
    clearLogs,
    exportLogsAsCSV
  };
}
