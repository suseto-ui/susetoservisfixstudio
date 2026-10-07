"""
Dynamic Hex Viewer Widget for SusetoDroidFixStudio.
Provides interactive binary memory inspection, address offsets (0x00000000),
hexadecimal byte layout, ASCII interpretation, searching, and partition dump export.
"""

from __future__ import annotations

import os
from typing import List, Optional

from ui._qt_compat import (
    QWidget,
    QAbstractScrollArea,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QMessageBox,
    Signal,
    Slot,
    QPainter,
    QColor,
    QFont,
    QPen,
    Qt,
)


class HexViewerWidget(QWidget):
    """
    High-performance binary block and partition dump visualizer.
    Displays memory in 16-byte rows with Offset | Hex Bytes | ASCII Decoded view.
    """

    data_modified = Signal()
    dump_exported = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._data = bytearray()
        self._bytes_per_row = 16
        self._highlighted_indices: List[int] = []

        self._init_ui()

    def _init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)

        # Toolbar: Search Bar + Jump Address + Export Dump Button
        toolbar = QHBoxLayout()
        toolbar.setSpacing(6)

        self.lbl_search = QLabel("Search:")
        toolbar.addWidget(self.lbl_search)

        self.input_search = QLineEdit()
        self.input_search.setPlaceholderText("ASCII text or hex (e.g. 'ANDROID' or '0x5F')")
        self.input_search.returnPressed.connect(self._on_search_clicked)
        toolbar.addWidget(self.input_search, stretch=1)

        self.btn_search = QPushButton("Find Next")
        self.btn_search.clicked.connect(self._on_search_clicked)
        toolbar.addWidget(self.btn_search)

        self.btn_export = QPushButton("Export Partition Dump")
        self.btn_export.setStyleSheet("background-color: #0e639c; color: white; font-weight: bold;")
        self.btn_export.clicked.connect(self._on_export_clicked)
        toolbar.addWidget(self.btn_export)

        main_layout.addLayout(toolbar)

        # Inner Text/Hex Display Area
        self.display_label = QLabel()
        self.display_label.setStyleSheet(
            "font-family: 'Consolas', 'Courier New', monospace; "
            "font-size: 12px; background-color: #1e1e1e; color: #d4d4d4; padding: 8px;"
        )
        main_layout.addWidget(self.display_label, stretch=1)

        # Status Summary Footer
        self.lbl_info = QLabel("Buffer: 0 Bytes | Block: None")
        self.lbl_info.setStyleSheet("color: #888888; font-size: 11px;")
        main_layout.addWidget(self.lbl_info)

        self.setStyleSheet("background-color: #252526; color: #cccccc;")

    def load_binary_data(self, data: bytes, block_name: str = "RAM_DUMP") -> None:
        """Load binary byte buffer into viewer and format output."""
        self._data = bytearray(data)
        self._highlighted_indices.clear()
        self._refresh_view()
        self.lbl_info.setText(f"Buffer: {len(self._data):,} Bytes | Block: {block_name}")

    def get_binary_data(self) -> bytes:
        """Return the current raw binary data buffer."""
        return bytes(self._data)

    def _refresh_view(self) -> None:
        """Format the binary data into 16-byte aligned Hex + ASCII view."""
        if not self._data:
            self.display_label.setText("No binary data loaded.")
            return

        lines: List[str] = []
        header = "OFFSET    00 01 02 03 04 05 06 07  08 09 0A 0B 0C 0D 0E 0F  | ASCII"
        separator = "-" * 74
        lines.append(header)
        lines.append(separator)

        max_rows = min(len(self._data) // self._bytes_per_row + 1, 256)  # Display up to 256 rows preview
        for row in range(max_rows):
            offset = row * self._bytes_per_row
            chunk = self._data[offset : offset + self._bytes_per_row]
            if not chunk:
                break

            # Format 16 bytes as hex
            hex_parts_1 = " ".join(f"{b:02X}" for b in chunk[:8])
            hex_parts_2 = " ".join(f"{b:02X}" for b in chunk[8:])
            hex_str = f"{hex_parts_1:<23}  {hex_parts_2:<23}"

            # Format ASCII
            ascii_str = "".join(chr(b) if 32 <= b <= 126 else "." for b in chunk)
            lines.append(f"{offset:08X}  {hex_str} | {ascii_str}")

        if len(self._data) > max_rows * self._bytes_per_row:
            remaining = len(self._data) - (max_rows * self._bytes_per_row)
            lines.append(f"... [{remaining:,} additional bytes truncated for display performance] ...")

        self.display_label.setText("\n".join(lines))

    def search(self, query: str) -> List[int]:
        """
        Search for ASCII string or hex sequence in loaded binary buffer.
        Returns matching byte offset indices.
        """
        if not query or not self._data:
            return []

        pattern: bytes
        query_strip = query.strip()
        if query_strip.startswith("0x") or query_strip.startswith("0X"):
            try:
                hex_digits = query_strip[2:].replace(" ", "")
                pattern = bytes.fromhex(hex_digits)
            except ValueError:
                pattern = query.encode("utf-8", errors="ignore")
        else:
            pattern = query.encode("utf-8", errors="ignore")

        matches: List[int] = []
        idx = self._data.find(pattern)
        while idx != -1:
            matches.append(idx)
            idx = self._data.find(pattern, idx + 1)

        self._highlighted_indices = matches
        return matches

    def _on_search_clicked(self) -> None:
        query = self.input_search.text().strip()
        matches = self.search(query)
        if matches:
            first_match = matches[0]
            self.lbl_info.setText(
                f"Search: Found {len(matches)} occurrences for '{query}' (First at 0x{first_match:08X})"
            )
        else:
            self.lbl_info.setText(f"Search: No matches found for '{query}'")

    def _on_export_clicked(self) -> None:
        if not self._data:
            QMessageBox.warning(self, "Export Dump", "No binary buffer is currently loaded.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Partition Dump", "partition_dump.bin", "Binary Files (*.bin);;All Files (*.*)"
        )
        if file_path:
            success = self.export_dump(file_path)
            if success:
                QMessageBox.information(self, "Export Dump", f"Successfully exported {len(self._data):,} bytes to:\n{file_path}")

    def export_dump(self, destination_path: str) -> bool:
        """Write loaded memory buffer to physical storage file."""
        try:
            os.makedirs(os.path.dirname(os.path.abspath(destination_path)), exist_ok=True)
            with open(destination_path, "wb") as f:
                f.write(self._data)
            self.dump_exported.emit(destination_path)
            return True
        except Exception as exc:
            self.lbl_info.setText(f"Export Error: {exc}")
            return False
