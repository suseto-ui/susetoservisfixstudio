/**
 * Native Bridge Service (`src/services/nativeBridge.ts`).
 * Seamlessly connects the React/Tailwind cockpit to the Python native hardware engine
 * via `window.pywebview.api` or local embedded HTTP `/api/*` server.
 */

declare global {
  interface Window {
    pywebview?: {
      api: {
        scan_hardware_ports: () => Promise<any>;
        get_driver_catalog?: () => Promise<any>;
        download_and_install_drivers?: (packageId?: string) => Promise<any>;
        get_supported_socs?: () => Promise<any>;
        get_val_profiles?: () => Promise<any>;
        execute_qualcomm_loader?: (port?: string, socId?: string) => Promise<any>;
        execute_mtk_bypass?: (port?: string, chipId?: string) => Promise<any>;
        execute_espressif_sync?: (port?: string, baud?: number) => Promise<any>;
        execute_stm32_bootloader?: (port?: string, baud?: number) => Promise<any>;
        execute_mtk_nvram_repair?: (port?: string, imei1?: string, imei2?: string) => Promise<any>;
        trigger_dtr_rts?: (port?: string, chipset?: string) => Promise<any>;
        negotiate_baudrate?: (port?: string, preferredBaud?: number) => Promise<any>;
        start_streaming_dump?: (partition?: string, totalSize?: number, chunkSize?: number) => Promise<any>;
        extract_emergency_crashdump?: (port?: string, arch?: string) => Promise<any>;
        run_fault_injection_benchmark?: (port?: string, noise?: number, frameDrop?: number, hotplug?: boolean, packets?: number) => Promise<any>;
        get_telemetry_metrics?: () => Promise<any>;
        run_port_soft_reset?: (port?: string) => Promise<any>;
        run_e2e_benchmark?: (port?: string, vendor?: string) => Promise<any>;
        run_stress_test: (portName: string, baudRate?: number, packetCount?: number) => Promise<any>;
        execute_frp_wipe: (port?: string, chipset?: string) => Promise<any>;
        authenticate_dongle: () => Promise<any>;
        read_partition_hex: (partitionName?: string, offset?: number, length?: number) => Promise<any>;
        get_system_status: () => Promise<any>;
        run_master_pipeline: () => Promise<any>;
      };
    };
  }
}

export class NativeBridgeService {
  /**
   * Check if running in native desktop environment (pywebview or local desktop server)
   */
  public static isNativeDesktop(): boolean {
    if (typeof window !== 'undefined' && window.pywebview?.api) {
      return true;
    }
    if (typeof window !== 'undefined' && (window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost')) {
      return true;
    }
    return false;
  }

  /**
   * Deep diagnostic scan of USB/COM ports, drivers, and process locks
   */
  public static async scanPorts(): Promise<any> {
    if (window.pywebview?.api?.scan_hardware_ports) {
      return await window.pywebview.api.scan_hardware_ports();
    }
    const res = await fetch('/api/scan-ports', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({})
    });
    return await res.json();
  }

  /**
   * Retrieve driver package catalog
   */
  public static async getDriverCatalog(): Promise<any> {
    if (window.pywebview?.api?.get_driver_catalog) {
      return await window.pywebview.api.get_driver_catalog();
    }
    const res = await fetch('/api/driver-catalog', {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    });
    return await res.json();
  }

  /**
   * Download and install driver packages
   */
  public static async downloadDrivers(packageId?: string): Promise<any> {
    if (window.pywebview?.api?.download_and_install_drivers) {
      return await window.pywebview.api.download_and_install_drivers(packageId);
    }
    const res = await fetch('/api/download-drivers', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ package_id: packageId || 'all' })
    });
    return await res.json();
  }

  /**
   * Retrieve VAL profiles
   */
  public static async getValProfiles(): Promise<any> {
    if (window.pywebview?.api?.get_val_profiles) {
      return await window.pywebview.api.get_val_profiles();
    }
    const res = await fetch('/api/val/profiles', {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    });
    return await res.json();
  }

  /**
   * Execute Espressif ESP32/ESP8266 sync
   */
  public static async executeEspressifSync(port: string = 'COM7', baud: number = 115200): Promise<any> {
    if (window.pywebview?.api?.execute_espressif_sync) {
      return await window.pywebview.api.execute_espressif_sync(port, baud);
    }
    const res = await fetch('/api/val/espressif-sync', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ port, baud })
    });
    return await res.json();
  }

  /**
   * Execute STM32 Bootloader
   */
  public static async executeStm32Bootloader(port: string = 'COM9', baud: number = 115200): Promise<any> {
    if (window.pywebview?.api?.execute_stm32_bootloader) {
      return await window.pywebview.api.execute_stm32_bootloader(port, baud);
    }
    const res = await fetch('/api/val/stm32-bootloader', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ port, baud })
    });
    return await res.json();
  }

  /**
   * Execute MTK NVRAM / IMEI repair
   */
  public static async executeMtkNvramRepair(port: string = 'COM5', imei1: string = '860123456789012', imei2: string = ''): Promise<any> {
    if (window.pywebview?.api?.execute_mtk_nvram_repair) {
      return await window.pywebview.api.execute_mtk_nvram_repair(port, imei1, imei2);
    }
    const res = await fetch('/api/val/mtk-nvram-repair', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ port, imei1, imei2 })
    });
    return await res.json();
  }

  /**
   * Trigger DTR/RTS Hardware sequence
   */
  public static async triggerDtrRts(port: string = 'COM7', chipset: string = 'ESP32'): Promise<any> {
    if (window.pywebview?.api?.trigger_dtr_rts) {
      return await window.pywebview.api.trigger_dtr_rts(port, chipset);
    }
    const res = await fetch('/api/dtr-rts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ port, chipset })
    });
    return await res.json();
  }

  /**
   * Negotiate optimal baudrate
   */
  public static async negotiateBaudrate(port: string = 'COM3', preferredBaud: number = 921600): Promise<any> {
    if (window.pywebview?.api?.negotiate_baudrate) {
      return await window.pywebview.api.negotiate_baudrate(port, preferredBaud);
    }
    const res = await fetch('/api/negotiate-baud', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ port, preferred_baud: preferredBaud })
    });
    return await res.json();
  }

  /**
   * Start 4096B streaming memory dump
   */
  public static async startStreamingDump(partition: string = 'boot', totalSize: number = 65536, chunkSize: number = 4096): Promise<any> {
    if (window.pywebview?.api?.start_streaming_dump) {
      return await window.pywebview.api.start_streaming_dump(partition, totalSize, chunkSize);
    }
    const res = await fetch('/api/memory/streaming-dump', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ partition, total_size: totalSize, chunk_size: chunkSize })
    });
    return await res.json();
  }

  /**
   * Memory Recovery Agent: Extract volatile crashdump
   */
  public static async extractEmergencyCrashdump(port: string = 'COM3', arch: string = 'ARM64'): Promise<any> {
    if (window.pywebview?.api?.extract_emergency_crashdump) {
      return await window.pywebview.api.extract_emergency_crashdump(port, arch);
    }
    const res = await fetch('/api/memory/crashdump-recovery', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ port, architecture: arch })
    });
    return await res.json();
  }

  /**
   * Hardware Fault Injection benchmark
   */
  public static async runFaultInjectionBenchmark(
    port: string = 'COM3',
    noise: number = 15.0,
    frameDrop: number = 10.0,
    hotplug: boolean = true,
    packets: number = 40
  ): Promise<any> {
    if (window.pywebview?.api?.run_fault_injection_benchmark) {
      return await window.pywebview.api.run_fault_injection_benchmark(port, noise, frameDrop, hotplug, packets);
    }
    const res = await fetch('/api/fault-injection/benchmark', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ port, noise, frame_drop: frameDrop, hotplug, packets })
    });
    return await res.json();
  }

  /**
   * Telemetry metrics snapshot
   */
  public static async getTelemetryMetrics(): Promise<any> {
    if (window.pywebview?.api?.get_telemetry_metrics) {
      return await window.pywebview.api.get_telemetry_metrics();
    }
    const res = await fetch('/api/telemetry/metrics', {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    });
    return await res.json();
  }

  /**
   * Watchdog port soft reset
   */
  public static async runPortSoftReset(port: string = 'COM3'): Promise<any> {
    if (window.pywebview?.api?.run_port_soft_reset) {
      return await window.pywebview.api.run_port_soft_reset(port);
    }
    const res = await fetch('/api/watchdog/soft-reset', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ port })
    });
    return await res.json();
  }

  /**
   * End-to-End Diagnostic Benchmark
   */
  public static async runE2EBenchmark(port: string = 'COM3', vendor: string = 'QUALCOMM'): Promise<any> {
    if (window.pywebview?.api?.run_e2e_benchmark) {
      return await window.pywebview.api.run_e2e_benchmark(port, vendor);
    }
    const res = await fetch('/api/e2e/benchmark', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ port, vendor })
    });
    return await res.json();
  }

  /**
   * Retrieve supported Qualcomm and MTK SoCs
   */
  public static async getSupportedSocs(): Promise<any> {
    if (window.pywebview?.api?.get_supported_socs) {
      return await window.pywebview.api.get_supported_socs();
    }
    const res = await fetch('/api/socs', {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    });
    return await res.json();
  }

  /**
   * Execute Qualcomm Firehose loader injection via Sahara
   */
  public static async executeQualcommLoader(port: string = 'COM3', socId: string = 'SM8350'): Promise<any> {
    if (window.pywebview?.api?.execute_qualcomm_loader) {
      return await window.pywebview.api.execute_qualcomm_loader(port, socId);
    }
    const res = await fetch('/api/qualcomm-loader', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ port, soc_id: socId })
    });
    return await res.json();
  }

  /**
   * Execute MediaTek BROM SLA/DAA Auth Bypass
   */
  public static async executeMtkBypass(port: string = 'COM5', chipId: string = 'MT6768'): Promise<any> {
    if (window.pywebview?.api?.execute_mtk_bypass) {
      return await window.pywebview.api.execute_mtk_bypass(port, chipId);
    }
    const res = await fetch('/api/mtk-bypass', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ port, chip_id: chipId })
    });
    return await res.json();
  }

  /**
   * Run USB/UART COM port stress test with real ECHO packets
   */
  public static async runStressTest(port: string, baudRate: number = 115200, packets: number = 25): Promise<any> {
    if (window.pywebview?.api?.run_stress_test) {
      return await window.pywebview.api.run_stress_test(port, baudRate, packets);
    }
    const res = await fetch('/api/stress-test', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ port, baud_rate: baudRate, packets })
    });
    return await res.json();
  }

  /**
   * Execute 1-Click FRP Wipe
   */
  public static async executeFrpWipe(port: string = 'COM3', chipset: string = 'QUALCOMM'): Promise<any> {
    if (window.pywebview?.api?.execute_frp_wipe) {
      return await window.pywebview.api.execute_frp_wipe(port, chipset);
    }
    const res = await fetch('/api/frp-wipe', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ port, chipset })
    });
    return await res.json();
  }

  /**
   * Authenticate hardware security dongle
   */
  public static async authenticateDongle(): Promise<any> {
    if (window.pywebview?.api?.authenticate_dongle) {
      return await window.pywebview.api.authenticate_dongle();
    }
    const res = await fetch('/api/dongle-auth', {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    });
    return await res.json();
  }

  /**
   * Read partition raw bytes for Hex Viewer
   */
  public static async readPartitionHex(partition: string = 'boot', offset: number = 0, length: number = 256): Promise<any> {
    if (window.pywebview?.api?.read_partition_hex) {
      return await window.pywebview.api.read_partition_hex(partition, offset, length);
    }
    const res = await fetch('/api/hex-dump', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ partition, offset, length })
    });
    return await res.json();
  }

  /**
   * System status check
   */
  public static async getSystemStatus(): Promise<any> {
    if (window.pywebview?.api?.get_system_status) {
      return await window.pywebview.api.get_system_status();
    }
    const res = await fetch('/api/status', {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    });
    return await res.json();
  }

  /**
   * Run Master Build & Integrity Pipeline
   */
  public static async runMasterPipeline(): Promise<any> {
    if (window.pywebview?.api?.run_master_pipeline) {
      return await window.pywebview.api.run_master_pipeline();
    }
    const res = await fetch('/api/run-pipeline', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });
    return await res.json();
  }
}
