/**
 * Production Qualcomm Sahara & Firehose Protocol Engine for SusetoDroidFixStudio.
 * Implements physical binary Sahara frame construction (Commands 0x01..0x08)
 * and Firehose XML transaction packaging.
 */

export enum SaharaCommand {
  CMD_HELLO = 0x01,
  CMD_HELLO_RESP = 0x02,
  CMD_READ_DATA = 0x03,
  CMD_END_IMAGE_TX = 0x04,
  CMD_DONE = 0x05,
  CMD_DONE_RESP = 0x06,
  CMD_RESET = 0x07,
  CMD_RESET_RESP = 0x08,
}

export interface SaharaPacket {
  cmd: SaharaCommand;
  length: number;
  data: Uint8Array;
}

export class SaharaEngine {
  /**
   * Build binary Sahara Hello Response packet (Command 0x02, Length 48 bytes).
   */
  public static buildHelloResponse(imageId: number = 0x0D, status: number = 0x00): Uint8Array {
    const buffer = new ArrayBuffer(48);
    const view = new DataView(buffer);

    view.setUint32(0, SaharaCommand.CMD_HELLO_RESP, true); // Command 0x02
    view.setUint32(4, 48, true);                           // Length 48 bytes
    view.setUint32(8, 0x02, true);                         // Sahara Protocol Version 2
    view.setUint32(12, 0x01, true);                        // Version Compatible
    view.setUint32(16, status, true);                      // Status (0 = OK)
    view.setUint32(20, imageId, true);                     // Image ID (0x0D = Firehose MBN)
    view.setUint32(24, 0x00, true);                        // Reserved
    view.setUint32(28, 0x00, true);                        // Reserved

    return new Uint8Array(buffer);
  }

  /**
   * Build binary Sahara Done packet (Command 0x05, Length 8 bytes).
   */
  public static buildDonePacket(): Uint8Array {
    const buffer = new ArrayBuffer(8);
    const view = new DataView(buffer);
    view.setUint32(0, SaharaCommand.CMD_DONE, true);
    view.setUint32(4, 8, true);
    return new Uint8Array(buffer);
  }

  /**
   * Build binary Sahara Reset packet (Command 0x07, Length 8 bytes).
   */
  public static buildResetPacket(): Uint8Array {
    const buffer = new ArrayBuffer(8);
    const view = new DataView(buffer);
    view.setUint32(0, SaharaCommand.CMD_RESET, true);
    view.setUint32(4, 8, true);
    return new Uint8Array(buffer);
  }

  /**
   * Parse incoming binary Sahara packet from device UART/USB buffer.
   */
  public static parsePacket(raw: Uint8Array): SaharaPacket | null {
    if (raw.length < 8) return null;
    const view = new DataView(raw.buffer, raw.byteOffset, raw.byteLength);
    const cmd = view.getUint32(0, true) as SaharaCommand;
    const length = view.getUint32(4, true);

    return {
      cmd,
      length,
      data: raw.subarray(8)
    };
  }

  /**
   * Construct Firehose XML command for reading/writing memory blocks.
   */
  public static buildFirehoseEraseCommand(sectorStart: number, numSectors: number, partitionName: string): string {
    return `<?xml version="1.0" ?><data><erase SECTOR_SIZE_IN_BYTES="512" num_partition_sectors="${numSectors}" start_sector="${sectorStart}" filename="" label="${partitionName}"/></data>`;
  }

  public static buildFirehoseProgramCommand(sectorStart: number, numSectors: number, partitionName: string, filename: string): string {
    return `<?xml version="1.0" ?><data><program SECTOR_SIZE_IN_BYTES="512" num_partition_sectors="${numSectors}" start_sector="${sectorStart}" filename="${filename}" label="${partitionName}"/></data>`;
  }
}
