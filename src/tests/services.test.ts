import { describe, it, expect } from 'vitest';
import { NvramEngine } from '../services/nvramEngine';

describe('NvramEngine', () => {
  it('should validate IMEI with Luhn', () => {
    const validImei = NvramEngine.generateValidImei();
    expect(NvramEngine.validateImei(validImei)).toBe(true);
    expect(NvramEngine.validateImei('123456789012345')).toBe(false);
  });
});
