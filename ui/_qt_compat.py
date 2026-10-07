"""
PySide6 Compatibility & Headless Virtualization Layer.
Enables execution under native PySide6 on Windows 11 x64,
with zero-dependency fallback for headless container testing environments.
"""

from __future__ import annotations

import sys
from typing import Any, Callable, Dict, List, Optional

try:
    from PySide6 import QtCore, QtGui, QtWidgets
    from PySide6.QtCore import Qt, QTimer, Signal, Slot, QObject, QPoint
    from PySide6.QtGui import QColor, QFont, QPainter, QPen, QBrush, QAction
    from PySide6.QtWidgets import (
        QApplication,
        QMainWindow,
        QWidget,
        QAbstractScrollArea,
        QTreeWidget,
        QTreeWidgetItem,
        QStatusBar,
        QLabel,
        QPushButton,
        QLineEdit,
        QProgressBar,
        QHBoxLayout,
        QVBoxLayout,
        QSplitter,
        QMenu,
        QFileDialog,
        QMessageBox,
        QTabWidget,
        QGroupBox,
        QScrollArea,
        QTextEdit,
        QFormLayout,
    )
    PYSIDE6_AVAILABLE = True

except ImportError:
    PYSIDE6_AVAILABLE = False

    class _QtNamespace:
        LeftButton = 1
        RightButton = 2
        ScrollBarAsNeeded = 0
        ScrollBarAlwaysOn = 1
        ScrollBarAlwaysOff = 2
        Horizontal = 1
        Vertical = 2
        AlignLeft = 0x0001
        AlignRight = 0x0002
        AlignCenter = 0x0004
        CustomContextMenu = 3
        ItemIsEnabled = 1
        ItemIsSelectable = 2

    Qt = _QtNamespace()

    class Signal:
        def __init__(self, *types):
            self._slots: List[Callable] = []

        def connect(self, slot: Callable) -> None:
            self._slots.append(slot)

        def disconnect(self, slot: Optional[Callable] = None) -> None:
            if slot in self._slots:
                self._slots.remove(slot)
            elif slot is None:
                self._slots.clear()

        def emit(self, *args, **kwargs) -> None:
            for s in list(self._slots):
                try:
                    s(*args, **kwargs)
                except Exception:
                    pass

    def Slot(*types):
        def decorator(fn):
            return fn
        return decorator

    class QObject:
        def __init__(self, parent: Optional[Any] = None) -> None:
            self._parent = parent

    class QTimer(QObject):
        def __init__(self, parent: Optional[Any] = None) -> None:
            super().__init__(parent)
            self.timeout = Signal()
            self.is_active = False

        def start(self, msec: int = 1000) -> None:
            self.is_active = True

        def stop(self) -> None:
            self.is_active = False

    class QPoint:
        def __init__(self, x: int = 0, y: int = 0) -> None:
            self.x = x
            self.y = y

    class QColor:
        def __init__(self, r: Any = 0, g: int = 0, b: int = 0, a: int = 255) -> None:
            self._color = r

    class QFont:
        def __init__(self, family: str = "Courier", pointSize: int = 10, weight: int = -1) -> None:
            self.family = family
            self.pointSize = pointSize
            self.bold = False

        def setPointSize(self, size: int) -> None:
            self.pointSize = size

        def setBold(self, bold: bool) -> None:
            self.bold = bold

    class QPen:
        def __init__(self, *args) -> None:
            pass

    class QBrush:
        def __init__(self, *args) -> None:
            pass

    class QPainter:
        def __init__(self, *args) -> None:
            pass
        def begin(self, *args): return True
        def end(self): pass
        def setPen(self, *args): pass
        def setBrush(self, *args): pass
        def setFont(self, *args): pass
        def drawText(self, *args): pass
        def fillRect(self, *args): pass

    class QAction(QObject):
        def __init__(self, text: str = "", parent: Optional[Any] = None) -> None:
            super().__init__(parent)
            self.text = text
            self.triggered = Signal()

    class QWidget(QObject):
        def __init__(self, parent: Optional[Any] = None) -> None:
            super().__init__(parent)
            self._layout = None
            self._style = ""
            self._enabled = True
            self.customContextMenuRequested = Signal()

        def setLayout(self, layout: Any) -> None:
            self._layout = layout

        def layout(self) -> Any:
            return self._layout

        def setMinimumSize(self, width: int, height: int) -> None:
            pass

        def setObjectName(self, name: str) -> None:
            self._object_name = name

        def objectName(self) -> str:
            return getattr(self, "_object_name", "")

        def setToolTip(self, tip: str) -> None:
            self._tooltip = tip

        def toolTip(self) -> str:
            return getattr(self, "_tooltip", "")

        def setStyleSheet(self, style: str) -> None:
            self._style = style

        def setEnabled(self, enabled: bool) -> None:
            self._enabled = enabled

        def isEnabled(self) -> bool:
            return self._enabled

        def update(self) -> None:
            pass

        def setWindowTitle(self, title: str) -> None:
            self._window_title = title

        def windowTitle(self) -> str:
            return getattr(self, "_window_title", "")

        def resize(self, width: int, height: int) -> None:
            pass

        def show(self) -> None:
            pass

        def setContextMenuPolicy(self, policy: Any) -> None:
            pass

        def mapToGlobal(self, pos: Any) -> Any:
            return pos



    class QMainWindow(QWidget):
        def __init__(self, parent: Optional[Any] = None) -> None:
            super().__init__(parent)
            self._central_widget = None
            self._status_bar = None
            self._window_title = ""

        def setCentralWidget(self, widget: Any) -> None:
            self._central_widget = widget

        def centralWidget(self) -> Any:
            return self._central_widget

        def setStatusBar(self, status_bar: Any) -> None:
            self._status_bar = status_bar

        def statusBar(self) -> Any:
            if self._status_bar is None:
                self._status_bar = QStatusBar(self)
            return self._status_bar

        def setWindowTitle(self, title: str) -> None:
            self._window_title = title

        def windowTitle(self) -> str:
            return self._window_title

        def resize(self, width: int, height: int) -> None:
            pass

        def show(self) -> None:
            pass

    class QAbstractScrollArea(QWidget):
        def __init__(self, parent: Optional[Any] = None) -> None:
            super().__init__(parent)
            self._viewport = QWidget(self)

        def viewport(self) -> QWidget:
            return self._viewport

        def verticalScrollBar(self) -> Any:
            class _ScrollBar:
                def __init__(self):
                    self.valueChanged = Signal()
                    self._val = 0
                    self._max = 100
                def setRange(self, mn, mx): self._max = mx
                def setValue(self, v): self._val = v; self.valueChanged.emit(v)
                def value(self): return self._val
                def setSingleStep(self, s): pass
                def setPageStep(self, p): pass
            return _ScrollBar()

    class QTreeWidgetItem:
        def __init__(self, parent_or_strings: Any = None, strings: Optional[List[str]] = None) -> None:
            self._parent = None
            self._children: List[QTreeWidgetItem] = []
            self._text: Dict[int, str] = {}
            self._data: Dict[int, Any] = {}

            if isinstance(parent_or_strings, list):
                for idx, val in enumerate(parent_or_strings):
                    self._text[idx] = str(val)
            elif strings:
                for idx, val in enumerate(strings):
                    self._text[idx] = str(val)

            if hasattr(parent_or_strings, "addTopLevelItem"):
                parent_or_strings.addTopLevelItem(self)
            elif hasattr(parent_or_strings, "addChild"):
                parent_or_strings.addChild(self)


        def addChild(self, item: QTreeWidgetItem) -> None:
            item._parent = self
            self._children.append(item)

        def child(self, index: int) -> Optional[QTreeWidgetItem]:
            if 0 <= index < len(self._children):
                return self._children[index]
            return None

        def childCount(self) -> int:
            return len(self._children)

        def setText(self, col: int, text: str) -> None:
            self._text[col] = text

        def text(self, col: int) -> str:
            return self._text.get(col, "")

        def setData(self, col: int, role: int, value: Any) -> None:
            self._data[(col, role)] = value

        def data(self, col: int, role: int) -> Any:
            return self._data.get((col, role), None)

        def setExpanded(self, expanded: bool) -> None:
            pass

    class QTreeWidget(QWidget):
        def __init__(self, parent: Optional[Any] = None) -> None:
            super().__init__(parent)
            self._items: List[QTreeWidgetItem] = []
            self._headers: List[str] = []
            self.itemClicked = Signal()
            self.itemSelectionChanged = Signal()

        def setHeaderLabels(self, labels: List[str]) -> None:
            self._headers = labels

        def addTopLevelItem(self, item: QTreeWidgetItem) -> None:
            self._items.append(item)

        def clear(self) -> None:
            self._items.clear()

        def topLevelItemCount(self) -> int:
            return len(self._items)

        def topLevelItem(self, index: int) -> Optional[QTreeWidgetItem]:
            if 0 <= index < len(self._items):
                return self._items[index]
            return None

        def currentItem(self) -> Optional[QTreeWidgetItem]:
            return self._items[0] if self._items else None

    class QStatusBar(QWidget):
        def __init__(self, parent: Optional[Any] = None) -> None:
            super().__init__(parent)
            self._permanent_widgets: List[QWidget] = []
            self._message = ""

        def showMessage(self, message: str, timeout: int = 0) -> None:
            self._message = message

        def currentMessage(self) -> str:
            return self._message

        def addWidget(self, widget: QWidget, stretch: int = 0) -> None:
            self._permanent_widgets.append(widget)

        def addPermanentWidget(self, widget: QWidget, stretch: int = 0) -> None:
            self._permanent_widgets.append(widget)


    class QLabel(QWidget):
        def __init__(self, text: str = "", parent: Optional[Any] = None) -> None:
            super().__init__(parent)
            self._text = text
            self._word_wrap = False
            self._font = None

        def setText(self, text: str) -> None:
            self._text = text

        def text(self) -> str:
            return self._text

        def setWordWrap(self, wrap: bool) -> None:
            self._word_wrap = wrap

        def setFont(self, font: Any) -> None:
            self._font = font

    class QPushButton(QWidget):
        def __init__(self, text: str = "", parent: Optional[Any] = None) -> None:
            super().__init__(parent)
            self._text = text
            self.clicked = Signal()

        def setText(self, text: str) -> None:
            self._text = text

        def text(self) -> str:
            return self._text

    class QLineEdit(QWidget):
        def __init__(self, text: str = "", parent: Optional[Any] = None) -> None:
            super().__init__(parent)
            self._text = text
            self._placeholder = ""
            self.textChanged = Signal()
            self.returnPressed = Signal()

        def setText(self, text: str) -> None:
            self._text = text
            self.textChanged.emit(text)

        def text(self) -> str:
            return self._text

        def setPlaceholderText(self, text: str) -> None:
            self._placeholder = text

        def placeholderText(self) -> str:
            return self._placeholder

    class QProgressBar(QWidget):
        def __init__(self, parent: Optional[Any] = None) -> None:
            super().__init__(parent)
            self._value = 0
            self._min = 0
            self._max = 100
        def setRange(self, min_val: int, max_val: int) -> None:
            self._min = min_val
            self._max = max_val
        def setValue(self, val: int) -> None:
            self._value = val
        def value(self) -> int:
            return self._value
        def setFixedHeight(self, h: int) -> None:
            pass

    class QHBoxLayout:
        def __init__(self, parent: Optional[Any] = None) -> None:
            self._widgets: List[Any] = []
        def addWidget(self, w: Any, stretch: int = 0, alignment: Any = None) -> None: self._widgets.append(w)
        def addLayout(self, l: Any) -> None: pass
        def addStretch(self, stretch: int = 0) -> None: pass
        def setContentsMargins(self, *args) -> None: pass
        def setSpacing(self, s: int) -> None: pass
        def count(self) -> int: return len(self._widgets)
        def takeAt(self, index: int) -> Any:
            if 0 <= index < len(self._widgets):
                w = self._widgets.pop(index)
                class _Item:
                    def __init__(self, widget): self._w = widget
                    def widget(self): return self._w
                return _Item(w)
            return None

    class QVBoxLayout:
        def __init__(self, parent: Optional[Any] = None) -> None:
            self._widgets: List[Any] = []
        def addWidget(self, w: Any, stretch: int = 0, alignment: Any = None) -> None: self._widgets.append(w)
        def addLayout(self, l: Any) -> None: pass
        def addStretch(self, stretch: int = 0) -> None: pass
        def setContentsMargins(self, *args) -> None: pass
        def setSpacing(self, s: int) -> None: pass
        def count(self) -> int: return len(self._widgets)
        def takeAt(self, index: int) -> Any:
            if 0 <= index < len(self._widgets):
                w = self._widgets.pop(index)
                class _Item:
                    def __init__(self, widget): self._w = widget
                    def widget(self): return self._w
                return _Item(w)
            return None

    class QSplitter(QWidget):
        def __init__(self, orientation: Any = None, parent: Optional[Any] = None) -> None:
            super().__init__(parent)
            self._widgets: List[QWidget] = []
        def addWidget(self, w: QWidget) -> None: self._widgets.append(w)
        def setSizes(self, sizes: List[int]) -> None: pass
        def setStretchFactor(self, index: int, factor: int) -> None: pass

    class QMenu(QWidget):
        def __init__(self, title: str = "", parent: Optional[Any] = None) -> None:
            super().__init__(parent)
            self._actions: List[QAction] = []
        def addAction(self, text_or_action: Any) -> QAction:
            if isinstance(text_or_action, str):
                act = QAction(text_or_action, self)
            else:
                act = text_or_action
            self._actions.append(act)
            return act
        def exec(self, point: Any = None) -> Any: pass
        def exec_(self, point: Any = None) -> Any: pass

    class QFileDialog:
        @staticmethod
        def getSaveFileName(parent=None, caption="", dir="", filter="") -> tuple[str, str]:
            return "dump.bin", "Binary Files (*.bin)"
        @staticmethod
        def getOpenFileName(parent=None, caption="", dir="", filter="") -> tuple[str, str]:
            return "dump.bin", "Binary Files (*.bin)"

    class QMessageBox:
        @staticmethod
        def information(parent, title, text): pass
        @staticmethod
        def warning(parent, title, text): pass
        @staticmethod
        def critical(parent, title, text): pass

    class QTabWidget(QWidget):
        def __init__(self, parent: Optional[Any] = None) -> None:
            super().__init__(parent)
            self._tabs: List[tuple[Any, str]] = []

        def addTab(self, widget: Any, label: str) -> int:
            self._tabs.append((widget, label))
            return len(self._tabs) - 1

        def currentIndex(self) -> int:
            return 0

        def setCurrentIndex(self, index: int) -> None:
            pass

    class QGroupBox(QWidget):
        def __init__(self, title: str = "", parent: Optional[Any] = None) -> None:
            super().__init__(parent)
            self._title = title

    class QScrollArea(QWidget):
        def __init__(self, parent: Optional[Any] = None) -> None:
            super().__init__(parent)
            self._widget = None
        def setWidget(self, w: QWidget) -> None:
            self._widget = w
        def setWidgetResizable(self, resizable: bool) -> None:
            pass

    class QTextEdit(QWidget):
        def __init__(self, parent: Optional[Any] = None) -> None:
            super().__init__(parent)
            self._text = ""
        def setReadOnly(self, ro: bool) -> None: pass
        def setPlainText(self, text: str) -> None: self._text = text
        def toPlainText(self) -> str: return self._text
        def append(self, text: str) -> None: self._text += "\n" + text

    class QFormLayout:
        def __init__(self, parent: Optional[Any] = None) -> None:
            self._rows: List[tuple[Any, Any]] = []
        def addRow(self, label: Any, field: Any) -> None: self._rows.append((label, field))

    class QApplication:
        _instance = None
        def __init__(self, argv: List[str]) -> None:
            QApplication._instance = self
        @staticmethod
        def instance() -> Optional[QApplication]:
            return QApplication._instance
        def exec(self) -> int: return 0
        def exec_(self) -> int: return 0

