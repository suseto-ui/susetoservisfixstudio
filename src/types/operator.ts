export interface CloudPayloadItem {
  id: string;
  filename: string;
  category: 'qualcomm' | 'mediatek' | 'samsung' | 'unisoc';
  sizeKB: number;
  sha256: string;
  status: 'SYNCED' | 'OUTDATED' | 'AVAILABLE';
  encryptedLocally: boolean;
}

export interface StationItem {
  id: string;
  name: string;
  hwid: string;
  user: string;
  role: 'TECHNICIAN' | 'SUPERVISOR' | 'ADMIN';
  status: 'ONLINE' | 'BUSY' | 'OFFLINE';
  lastSeen: string;
}

export interface GuideStep {
  stepNumber: number;
  totalSteps: number;
  title: string;
  ifCondition: string;
  whatAction: string;
  whyRationale: string;
  actionId: string;
  safetyRating: 'SAFE' | 'CAUTION' | 'CRITICAL_INTERLOCK';
  actionBtnText: string;
}

export interface DoctorPortItem {
  id: string;
  portName: string;
  deviceTitle: string;
  driverInfo: string;
  vidPid: string;
  chipsetMode: string;
  chipsetType: 'QUALCOMM' | 'MEDIATEK' | 'FTDI' | 'GENERIC' | 'LOCKED';
  status: 'ONLINE' | 'LOCKED' | 'DISCONNECTED';
  lockReason?: string;
  lastSeen: string;
}

export interface UsbBusEvent {
  id: string;
  type: 'CONNECT' | 'DISCONNECT';
  timestamp: string;
  deviceName: string;
  vidPid: string;
  source: 'WebUSB' | 'WebSerial' | 'SIMULATOR';
}

export interface ChecklistItem {
  id: string;
  title: string;
  description: string;
  isDone: boolean;
  isRequired: boolean;
  layer: string;
  actionKey?: string;
  conflictReason?: string;
  conflictFix?: string;
}

export interface PowerWavePoint {
  time: string;
  voltage: number;
  current: number;
}

export interface UsbPowerTelemetry {
  vbusVoltage: number;
  currentMa: number;
  powerWatts: number;
  vbusMinThreshold: number;
  vbusMaxThreshold: number;
  dPlusVoltage: number;
  dMinusVoltage: number;
  rippleNoiseMv: number;
  protocol: 'USB 2.0 (SDP)' | 'QC 3.0' | 'QC 4.0+' | 'USB-PD 3.0 PPS' | 'Samsung AFC' | 'DCP (1.5A)';
  powerStatus: 'NOMINAL' | 'VOLTAGE_DROP_WARNING' | 'OVERVOLTAGE_ALERT' | 'SHORT_CIRCUIT_PROTECTION';
  history: PowerWavePoint[];
}

export interface MtkNvramCalibrationData {
  imei1: string;
  imei2: string;
  isImei1Valid: boolean;
  isImei2Valid: boolean;
  wifiMac: string;
  bluetoothMac: string;
  basebandStatus: 'HEALTHY' | 'NULL_IMEI' | 'CORRUPTED_HEADER' | 'RESTORED';
  rfBands: {
    gsm: boolean;
    wcdma: boolean;
    lteBands: string[];
    nr5gBands: string[];
  };
  txPowerOffsetDbm: number;
  crystalAfcOffsetPpm: number;
  err0x10FixApplied: boolean;
  crc32Checksum: string;
  headerValid: boolean;
  rawNvramBuffer: Uint8Array;
}

export interface NvramHexRow {
  offset: string;
  hexBytes: string[];
  ascii: string;
}

export interface GuideTourStep {
  id: string;
  stepNumber: number;
  totalSteps: number;
  title: string;
  targetArea: string;
  description: string;
  howItRelates: string;
  recommendedAction: string;
  actionButtonLabel?: string;
  actionId?: string;
}

export const GUIDE_TOUR_STEPS: GuideTourStep[] = [
  {
    id: 'tour-orchestrator',
    stepNumber: 1,
    totalSteps: 6,
    title: 'Automatický Orchestrátor & Hotplug Stav',
    targetArea: 'Horní informační lišta',
    description: 'Monitoruje přítomnost hardwaru, automatickou frontu profilů a 5sekundový fallback timeout. Pokud zařízení neodpoví do 5 s na Sahara protokol, automaticky přepne na další profil (např. MediaTek BROM s DTR/RTS pulsem).',
    howItRelates: 'Řídí a synchronizuje všechna nízkoúrovňová rozhraní. Umožňuje okamžitou manuální pauzu odpočtu a přímou volbu profilu operátorem.',
    recommendedAction: 'Zkontrolujte indikátor stavu a v případě potřeby pozastavte automatický odpočet.'
  },
  {
    id: 'tour-diagnostics',
    stepNumber: 2,
    totalSteps: 6,
    title: 'Fyzické USB Rozhraní & Live Diagnostická Konzole',
    targetArea: 'Levý sloupec (Hardware Hub)',
    description: 'Zobrazuje detaily připojeného COM portu (VID:PID, Baudrate, čipset), živý PnP monitor připojených zařízení a real-time stream všech diagnostických událostí s možností filtrování.',
    howItRelates: 'Veškerá data přijatá přes WebSerial (RX/TX pakety) nebo nativní bridge se okamžitě zobrazují v konzoli a propisují do SQLite WAL ledgeru.',
    recommendedAction: 'Klikněte na "Spárovat USB Port" nebo použijte "PnP Skenovat" pro detekci nových zařízení.'
  },
  {
    id: 'tour-operator',
    stepNumber: 3,
    totalSteps: 6,
    title: 'Standardní 5-krokový Servisní Sled Operátora',
    targetArea: 'Středový sloupec (Horní panel)',
    description: 'Klíčové centrum práce technika s deterministickým sledem 5 kroků: 1. Detekce HW ➔ 2. Pre-flight ovladače ➔ 3. Handshake & Loader ➔ 4. Záloha GPT ➔ 5. 1-Klik Odblokování.',
    howItRelates: 'Garantuje bezpečný postup bez rizika znefunkčnění zařízení. Každý krok má živý status a barevnou indikaci. Lze spustit jednotlivě i jedním master tlačítkem.',
    recommendedAction: 'Spusťte kompletní servisní sled tlačítkem "SPUSTIT CELÝ SERVISNÍ SLED (1-KLIK)".'
  },
  {
    id: 'tour-checklist',
    stepNumber: 4,
    totalSteps: 6,
    title: 'Inteligentní Akční Checklist s Detekcí Rozporů',
    targetArea: 'Středový sloupec (Plovoucí widget)',
    description: 'Pracovní seznam úkolů pro technika s automatickou validací logických a praktických rozporů (např. chybějící port, neprovedená záloha nebo chybějící oprávnění).',
    howItRelates: 'Před provedením rizikové akce vás včas upozorní na chybějící kroky s přesným vysvětlením PROČ a nabídne 1-klikové automatické vyřešení.',
    recommendedAction: 'Zkontrolujte položky checklistu a klikněte na "Automaticky vyřešit a spustit".'
  },
  {
    id: 'tour-quickactions',
    stepNumber: 5,
    totalSteps: 6,
    title: 'Rychlá Operační Tlačítka & Nouzové Signály',
    targetArea: 'Pravý sloupec (Quick Actions)',
    description: 'Sada okamžitých funkčních tlačítek pro nejčastější zásahy technika: Sahara Handshake, Driver Pre-flight, DTR/RTS reset, Záloha GPT, BROM Bypass, FRP Reset a Screen Mirror.',
    howItRelates: 'Umožňuje okamžitý přístup k hardwarovým funkcím bez nutnosti přepínat mezi jednotlivými podzáložkami.',
    recommendedAction: 'Použijte kterékoliv akční tlačítko pro okamžitý hardware signál.'
  },
  {
    id: 'tour-guide',
    stepNumber: 6,
    totalSteps: 6,
    title: 'Kontextový Servisní Průvodce (IF / WHAT / WHY)',
    targetArea: 'Středový panel (Kontextový blok)',
    description: 'Interaktivní průvodce, který dynamicky podle detekovaného čipsetu a stavu zařízení generuje 3 karty: POKUD (zjištěný stav), CO UDĚLAT (přesný krok) a PROČ (bezpečnostní zdůvodnění).',
    howItRelates: 'Poskytuje technikovi jistotu a kontext pro každé servisní rozhodnutí.',
    recommendedAction: 'Přečtěte si doporučení a klikněte na akční tlačítko v kartě průvodce.'
  }
];
