import { render, screen } from '@testing-library/react';
import { App } from '../App';
import { describe, it, expect, vi } from 'vitest';

vi.mock('../services/webSerialEngine', () => ({
  WebSerialEngine: class {
    requestPhysicalPort = vi.fn();
    requestAndOpenPort = vi.fn();
    connect = vi.fn();
  },
  SerialDeviceDescriptor: vi.fn()
}));

describe('App UI', () => {
  it('renders the application', () => {
    render(<App />);
    expect(screen.getByText(/SUSETO DROID FIX STUDIO/i)).toBeInTheDocument();
  });
});
