/**
 * MediaTek NVRAM & NVDATA Engine (`src/services/nvramEngine.ts`).
 * Handles binary serialization of MTK NVRAM calibration structures,
 * Luhn IMEI validation, WiFi/Bluetooth MAC formatters, and CRC32 calculation.
 */

import { MtkNvramCalibrationData, NvramHexRow } from '../types/operator';

export class NvramEngine {
  /**
   * Calculate Luhn checksum digit for a 14-digit IMEI base.
   */
  public static calculateLuhnChecksum(imei14: string): number {
    const clean = imei14.replace(/\D/g, '').slice(0, 14);
    if (clean.length < 14) return 0;

    let sum = 0;
    // Process from right to left
    for (let i = 13; i >= 0; i--) {
      let digit = parseInt(clean.charAt(i), 10);
      // Double every second digit from right (even positions)
      if ((14 - i) % 2 === 0) {
        digit *= 2;
        if (digit > 9) digit -= 9;
      }
      sum += digit;
    }
    return (10 - (sum % 10)) % 10;
  }

  /**
   * Validate full 15-digit IMEI with Luhn algorithm.
   */
  public static validateImei(imei: string): boolean {
    const clean = imei.replace(/\D/g, '');
    if (clean.length !== 15) return false;

    const base14 = clean.slice(0, 14);
    const expectedCheck = this.calculateLuhnChecksum(base14);
    const actualCheck = parseInt(clean.charAt(14), 10);
    return expectedCheck === actualCheck;
  }

  /**
   * Generate a valid 15-digit test/service IMEI (Type Allocation Code: 86452104).
   */
  public static generateValidImei(seedOffset: number = 0): string {
    const tac = '86452104';
    const serial = String(889100 + (seedOffset % 900000)).padStart(6, '0');
    const base14 = `${tac}${serial}`;
    const checkDigit = this.calculateLuhnChecksum(base14);
    return `${base14}${checkDigit}`;
  }

  /**
   * Format MAC address with colons (XX:XX:XX:XX:XX:XX).
   */
  public static formatMacAddress(raw: string): string {
    const clean = raw.replace(/[^0-9A-Fa-f]/g, '').slice(0, 12).toUpperCase();
    const parts: string[] = [];
    for (let i = 0; i < clean.length; i += 2) {
      parts.push(clean.slice(i, i + 2));
    }
    return parts.join(':');
  }

  /**
   * Generate random valid MediaTek Wi-Fi / BT MAC (OUI: 00:1A:7D or 70:4D:7B).
   */
  public static generateMacAddress(isBt: boolean = false): string {
    const prefix = isBt ? '00:1A:7D' : '70:4D:7B';
    const b1 = Math.floor(Math.random() * 256).toString(16).padStart(2, '0').toUpperCase();
    const b2 = Math.floor(Math.random() * 256).toString(16).padStart(2, '0').toUpperCase();
    const b3 = Math.floor(Math.random() * 256).toString(16).padStart(2, '0').toUpperCase();
    return `${prefix}:${b1}:${b2}:${b3}`;
  }

  /**
   * Calculate CRC32 checksum for a binary buffer.
   */
  public static calculateCrc32(buffer: Uint8Array): string {
    let crc = 0 ^ (-1);
    for (let i = 0; i < buffer.length; i++) {
      let byte = buffer[i];
      for (let j = 0; j < 8; j++) {
        const mask = -(crc & 1);
        crc = (crc >>> 1) ^ (0xEDB88320 & mask);
        byte = byte >>> 1;
      }
    }
    const finalCrc = ((crc ^ (-1)) >>> 0).toString(16).toUpperCase().padStart(8, '0');
    return `0x${finalCrc}`;
  }

  /**
   * Serialize calibration data into a real 512-byte MediaTek NVRAM binary block (APCFG0 / MD1_NVRAM).
   */
  public static serializeNvramBlock(data: Partial<MtkNvramCalibrationData>): Uint8Array {
    const buf = new Uint8Array(512);

    // 1. Magic Header "MTK_NVRAM_V1\0\0" (14 bytes)
    const headerStr = 'MTK_NVRAM_V1';
    for (let i = 0; i < headerStr.length; i++) {
      buf[i] = headerStr.charCodeAt(i);
    }
    buf[12] = 0x02; // Version major
    buf[13] = 0x00; // Version minor

    // 2. Block Size: 512 bytes (offset 14..15)
    buf[14] = 0x00;
    buf[15] = 0x02;

    // 3. IMEI 1 Block (offset 16..31) - ASCII 15 digits + null
    const imei1 = (data.imei1 || '864521048891234').slice(0, 15);
    for (let i = 0; i < imei1.length; i++) {
      buf[16 + i] = imei1.charCodeAt(i);
    }

    // 4. IMEI 2 Block (offset 32..47) - ASCII 15 digits + null
    const imei2 = (data.imei2 || '864521048891235').slice(0, 15);
    for (let i = 0; i < imei2.length; i++) {
      buf[32 + i] = imei2.charCodeAt(i);
    }

    // 5. WiFi MAC Address (offset 48..53) - 6 raw bytes
    const wifiMacParts = (data.wifiMac || '70:4D:7B:A1:B2:C3').split(':');
    for (let i = 0; i < 6; i++) {
      buf[48 + i] = parseInt(wifiMacParts[i] || '00', 16);
    }

    // 6. Bluetooth MAC Address (offset 56..61) - 6 raw bytes
    const btMacParts = (data.bluetoothMac || '00:1A:7D:DA:71:02').split(':');
    for (let i = 0; i < 6; i++) {
      buf[56 + i] = parseInt(btMacParts[i] || '00', 16);
    }

    // 7. RF Band Mask (offset 64..79)
    buf[64] = data.rfBands?.gsm ? 0x0F : 0x00; // GSM Quadband
    buf[65] = data.rfBands?.wcdma ? 0x1F : 0x00; // WCDMA bands
    buf[66] = 0xFF; // LTE Low bands (B1, B3, B7, B20, B28)
    buf[67] = 0x03; // 5G NR bands (N78)

    // 8. RF Calibrations (Tx Offset, Crystal AFC, Err 0x10 Fix)
    buf[80] = Math.round(((data.txPowerOffsetDbm || 0) + 10) * 10);
    buf[81] = Math.round(((data.crystalAfcOffsetPpm || 0) + 50));
    buf[82] = data.err0x10FixApplied ? 0xA5 : 0x00;

    // 9. Padding pattern with 0xAA / 0x55 in payload section
    for (let i = 96; i < 504; i++) {
      buf[i] = (i % 2 === 0) ? 0xAA : 0x55;
    }

    // 10. CRC32 at offset 508..511
    const crc = this.calculateCrc32(buf.subarray(0, 508));
    const crcNum = parseInt(crc.replace('0x', ''), 16);
    buf[508] = (crcNum >>> 24) & 0xFF;
    buf[509] = (crcNum >>> 16) & 0xFF;
    buf[510] = (crcNum >>> 8) & 0xFF;
    buf[511] = crcNum & 0xFF;

    return buf;
  }

  /**
   * Convert binary buffer into formatted Hex Dump Rows for inspection.
   */
  public static generateHexRows(buffer: Uint8Array, maxBytes: number = 256): NvramHexRow[] {
    const rows: NvramHexRow[] = [];
    const limit = Math.min(buffer.length, maxBytes);

    for (let i = 0; i < limit; i += 16) {
      const offset = `0x${i.toString(16).toUpperCase().padStart(8, '0')}`;
      const hexBytes: string[] = [];
      let ascii = '';

      for (let j = 0; j < 16; j++) {
        if (i + j < limit) {
          const byte = buffer[i + j];
          hexBytes.push(byte.toString(16).toUpperCase().padStart(2, '0'));
          ascii += (byte >= 32 && byte <= 126) ? String.fromCharCode(byte) : '.';
        } else {
          hexBytes.push('  ');
          ascii += ' ';
        }
      }

      rows.push({
        offset,
        hexBytes,
        ascii
      });
    }

    return rows;
  }
}
