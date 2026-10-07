export interface ForensicFile {
  id: string;
  name: string;
  path: string;
  size: number;
  type: 'file' | 'directory';
  deleted: boolean;
  hash?: string;
}

export interface ForensicDbTable {
  name: string;
  columns: string[];
  rows: any[][];
}
