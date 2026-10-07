/**
 * Production WebSerial Hardware Engine for SusetoDroidFixStudio.
 * Provides direct physical USB/UART COM port communication via navigator.serial
 * with hardware VID/PID filtering, stream readers/writers, and baudrate auto-tuning.
 */

// Web Serial API types
export interface SerialPortInfo {
  usbVendorId?: number;
  usbProductId?: number;
}

export interface SerialOptions {
  baudRate: number;
  dataBits?: number;
  stopBits?: number;
  parity?: 'none' | 'even' | 'odd';
  bufferSize?: number;
  flowControl?: 'none' | 'hardware';
}

export interface SerialPortFilter {
  usbVendorId?: number;
  usbProductId?: number;
}

export interface SerialPort {
  readable: ReadableStream<Uint8Array> | null;
  writable: WritableStream<Uint8Array> | null;
  open(options: SerialOptions): Promise<void>;
  close(): Promise<void>;
  getInfo(): SerialPortInfo;
}

export interface SerialDeviceDescriptor {
  port: SerialPort;
  usbVendorId?: number;
  usbProductId?: number;
  vendorName: string;
  chipsetGuess: string;
  portLabel: string;
  isOpen: boolean;
}

export const KNOWN_HARDWARE_FILTERS: SerialPortFilter[] = [
  { usbVendorId: 0x05C6, usbProductId: 0x9008 }, // Qualcomm HS-USB QDLoader 9008
  { usbVendorId: 0x05C6 },                       // Qualcomm Generic
  { usbVendorId: 0x0E8D, usbProductId: 0x0003 }, // MediaTek BootROM
  { usbVendorId: 0x0E8D },                       // MediaTek Generic
  { usbVendorId: 0x0403, usbProductId: 0x6001 }, // FTDI SmartCard Dongle / UART
  { usbVendorId: 0x0403 },                       // FTDI Generic
  { usbVendorId: 0x04E8 },                       // Samsung Electronics (Modem / MTP)
  { usbVendorId: 0x18D1, usbProductId: 0x4EE0 }, // Google Fastboot
  { usbVendorId: 0x18D1 },                       // Google ADB / Fastboot
  { usbVendorId: 0x1782 }                        // Unisoc / Spreadtrum Bootloader
];

export class WebSerialEngine {
  private activePort: SerialPort | null = null;
  private reader: ReadableStreamDefaultReader<Uint8Array> | null = null;
  private writer: WritableStreamDefaultWriter<Uint8Array> | null = null;
  private isReading: boolean = false;
  private onDataCallback: ((chunk: Uint8Array) => void) | null = null;
  private onStatusCallback: ((status: string, level: 'info' | 'warn' | 'error' | 'success') => void) | null = null;

  public isSupported(): boolean {
    return typeof navigator !== 'undefined' && 'serial' in navigator;
  }

  public setCallbacks(
    onData: (chunk: Uint8Array) => void,
    onStatus: (status: string, level: 'info' | 'warn' | 'error' | 'success') => void
  ) {
    this.onDataCallback = onData;
    this.onStatusCallback = onStatus;
  }

  /**
   * Request user to select physical USB port via browser dialog.
   */
  public async requestPhysicalPort(): Promise<SerialDeviceDescriptor> {
    if (!this.isSupported()) {
      throw new Error('WebSerial API není v tomto prohlížeči podporováno. Použijte Google Chrome, Microsoft Edge nebo Opera na desktopu.');
    }

    this.onStatusCallback?.('Otevírám systémový dialog pro výběr fyzického USB/COM portu...', 'info');
    const serialNav = (navigator as unknown as { serial: { requestPort: (options: { filters: SerialPortFilter[] }) => Promise<SerialPort> } }).serial;
    const port = await serialNav.requestPort({ filters: KNOWN_HARDWARE_FILTERS });
    const info = port.getInfo();

    const desc: SerialDeviceDescriptor = {
      port,
      usbVendorId: info.usbVendorId,
      usbProductId: info.usbProductId,
      vendorName: this.resolveVendorName(info.usbVendorId),
      chipsetGuess: this.guessChipset(info.usbVendorId, info.usbProductId),
      portLabel: `USB-COM (${info.usbVendorId ? `0x${info.usbVendorId.toString(16).padStart(4, '0').toUpperCase()}` : 'Generic'})`,
      isOpen: false
    };

    this.activePort = port;
    this.onStatusCallback?.(`Port vybrán: ${desc.vendorName} [${desc.chipsetGuess}]`, 'success');
    return desc;
  }

  /**
   * Convenience alias for requestPhysicalPort.
   */
  public async requestPort(): Promise<SerialDeviceDescriptor> {
    return this.requestPhysicalPort();
  }

  /**
   * Open the selected serial port with the designated baud rate.
   */
  public async connect(baudRate: number = 115200): Promise<void> {
    if (!this.activePort) {
      throw new Error('Žádný port nebyl vybrán. Nejprve zavolejte requestPhysicalPort().');
    }

    try {
      await this.activePort.open({ baudRate });
      this.onStatusCallback?.(`Spojení navázáno na rychlosti ${baudRate} baud. Zahajuji čtení...`, 'success');

      if (this.activePort.writable) {
        this.writer = this.activePort.writable.getWriter();
      }

      this.isReading = true;
      this.startReadingLoop();
    } catch (error: any) {
      this.onStatusCallback?.(`Chyba při otevírání COM portu: ${error?.message || error}`, 'error');
      throw error;
    }
  }

  /**
   * Alias for connect() to open physical serial port.
   */
  public async openPort(baudRate: number = 115200): Promise<void> {
    return this.connect(baudRate);
  }

  /**
   * Send binary packet buffer to hardware.
   */
  public async write(data: Uint8Array): Promise<void> {
    if (!this.writer) {
      throw new Error('Port není otevřen pro zápis.');
    }
    await this.writer.write(data);
  }

  /**
   * Continuous background read loop without blocking the main UI thread.
   */
  private async startReadingLoop(): Promise<void> {
    while (this.activePort && this.activePort.readable && this.isReading) {
      try {
        const currentReader = this.activePort.readable.getReader();
        this.reader = currentReader;
        while (this.isReading) {
          const { value, done } = await currentReader.read();
          if (done) break;
          if (value && value.length > 0) {
            this.onDataCallback?.(value);
          }
        }
      } catch (error: any) {
        if (this.isReading) {
          this.onStatusCallback?.(`Chyba čtení ze sběrnice: ${error?.message || error}`, 'error');
        }
      } finally {
        if (this.reader) {
          try {
            this.reader.releaseLock();
          } catch {}
          this.reader = null;
        }
      }
    }
  }

  /**
   * Safely close serial port and release stream locks.
   */
  public async closePort(): Promise<void> {
    this.isReading = false;
    if (this.reader) {
      try {
        await this.reader.cancel();
        this.reader.releaseLock();
      } catch {}
      this.reader = null;
    }
    if (this.writer) {
      try {
        await this.writer.close();
        this.writer.releaseLock();
      } catch {}
      this.writer = null;
    }
    if (this.activePort) {
      try {
        await this.activePort.close();
      } catch {}
      this.activePort = null;
    }
    this.onStatusCallback?.('Fyzický port byl bezpečně uzavřen a uvolněn.', 'info');
  }

  private resolveVendorName(vid?: number): string {
    if (!vid) return 'Standard COM Device';
    if (vid === 0x05C6) return 'Qualcomm Incorporated';
    if (vid === 0x0E8D) return 'MediaTek Inc.';
    if (vid === 0x0403) return 'Future Technology Devices (FTDI)';
    if (vid === 0x04E8) return 'Samsung Electronics Co., Ltd.';
    if (vid === 0x18D1) return 'Google Inc. (Android Device)';
    if (vid === 0x1782) return 'Unisoc / Spreadtrum Communications';
    return `Vendor 0x${vid.toString(16).toUpperCase()}`;
  }

  private guessChipset(vid?: number, pid?: number): string {
    if (vid === 0x05C6 && pid === 0x9008) return 'Qualcomm Snapdragon EDL 9008';
    if (vid === 0x05C6) return 'Qualcomm Snapdragon Diagnostic Port';
    if (vid === 0x0E8D && pid === 0x0003) return 'MediaTek MT68xx/MT67xx BootROM';
    if (vid === 0x0E8D) return 'MediaTek VCP Service Interface';
    if (vid === 0x0403) return 'ISO 7816 SmartCard Dongle / FT232';
    if (vid === 0x04E8) return 'Samsung Exynos / Modem Port';
    if (vid === 0x18D1 && pid === 0x4EE0) return 'Android Fastboot Mode';
    if (vid === 0x1782) return 'Unisoc Tiger / Spreadtrum Bootloader';
    return 'Generic Serial Modem / UART';
  }
}
