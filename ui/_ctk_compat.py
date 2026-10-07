"""
CustomTkinter Headless & Native Compatibility Layer (`ui/_ctk_compat.py`).
Enables native CustomTkinter UI execution on Windows while providing a robust,
dependency-free virtual widget engine for headless and CI testing environments.
"""

from __future__ import annotations

import logging
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger("ui._ctk_compat")

CUSTOMTKINTER_AVAILABLE = False
ctk = None

try:
    import customtkinter as _ctk  # type: ignore[import-untyped]
    ctk = _ctk
    CUSTOMTKINTER_AVAILABLE = True
except (ImportError, Exception):
    CUSTOMTKINTER_AVAILABLE = False


if not CUSTOMTKINTER_AVAILABLE:
    class _VirtualWidget:
        """Lightweight virtual widget recording properties for headless testing."""
        def __init__(self, master: Any = None, **kwargs: Any) -> None:
            self.master = master
            self._properties: Dict[str, Any] = dict(kwargs)
            self._children: List[Any] = []
            if master and hasattr(master, "_children") and isinstance(master._children, list):
                master._children.append(self)

        def configure(self, **kwargs: Any) -> None:
            self._properties.update(kwargs)

        def cget(self, key: str) -> Any:
            return self._properties.get(key)

        def __getitem__(self, key: str) -> Any:
            return self._properties.get(key)

        def __setitem__(self, key: str, value: Any) -> None:
            self._properties[key] = value

        def pack(self, **kwargs: Any) -> None:
            self._properties.update(kwargs)

        def pack_forget(self) -> None:
            pass

        def grid(self, **kwargs: Any) -> None:
            self._properties.update(kwargs)

        def grid_forget(self) -> None:
            pass

        def winfo_children(self) -> List[Any]:
            return list(self._children)

        def destroy(self) -> None:
            if self.master and hasattr(self.master, "_children") and isinstance(self.master._children, list):
                if self in self.master._children:
                    self.master._children.remove(self)
            self._children.clear()

        def bind(self, sequence: str, func: Callable[..., Any], add: Optional[str] = None) -> None:
            self._properties[f"bind_{sequence}"] = func

        def unbind(self, sequence: str) -> None:
            self._properties.pop(f"bind_{sequence}", None)

        def focus_set(self) -> None:
            pass

        def after(self, ms: int, func: Callable[..., Any], *args: Any) -> str:
            if callable(func):
                try:
                    func(*args)
                except Exception:
                    pass
            return "after_id_widget"

    class _VirtualWindow(_VirtualWidget):
        def __init__(self, **kwargs: Any) -> None:
            super().__init__(None, **kwargs)
            self._title = "Application"
            self._geometry = "1024x768"

        def title(self, title_text: Optional[str] = None) -> str:
            if title_text is not None:
                self._title = title_text
            return self._title

        def geometry(self, geom_str: Optional[str] = None) -> str:
            if geom_str is not None:
                self._geometry = geom_str
            return self._geometry

        def grid_columnconfigure(self, index: int, **kwargs: Any) -> None:
            pass

        def grid_rowconfigure(self, index: int, **kwargs: Any) -> None:
            pass

        def withdraw(self) -> None:
            pass

        def deiconify(self) -> None:
            pass

        def after(self, ms: int, func: Callable[..., Any], *args: Any) -> str:
            return "after_id_1"

        def mainloop(self) -> None:
            pass

    class _VirtualToplevel(_VirtualWindow):
        def __init__(self, master: Any = None, **kwargs: Any) -> None:
            super().__init__(**kwargs)
            self.master = master
            self._transient = None

        def transient(self, master: Any) -> None:
            self._transient = master

        def grab_set(self) -> None:
            pass

        def grab_release(self) -> None:
            pass

    class _VirtualFrame(_VirtualWidget):
        def grid_columnconfigure(self, index: int, **kwargs: Any) -> None:
            pass

        def grid_rowconfigure(self, index: int, **kwargs: Any) -> None:
            pass

    class _VirtualLabel(_VirtualWidget):
        @property
        def text(self) -> str:
            return str(self._properties.get("text", ""))

    class _VirtualButton(_VirtualWidget):
        def invoke(self) -> Any:
            cmd = self._properties.get("command")
            if callable(cmd):
                return cmd()
            return None

    class _VirtualEntry(_VirtualWidget):
        def __init__(self, master: Any = None, **kwargs: Any) -> None:
            super().__init__(master, **kwargs)
            self._text = ""

        def get(self) -> str:
            return self._text

        def insert(self, index: Any, string: str) -> None:
            self._text += string

        def delete(self, first: Any, last: Any = None) -> None:
            self._text = ""

    class _VirtualProgressBar(_VirtualWidget):
        def __init__(self, master: Any = None, **kwargs: Any) -> None:
            super().__init__(master, **kwargs)
            self._value: float = 0.0

        def set(self, value: float) -> None:
            self._value = max(0.0, min(1.0, value))

        def get(self) -> float:
            return self._value

    class _VirtualTabview(_VirtualWidget):
        def __init__(self, master: Any = None, **kwargs: Any) -> None:
            super().__init__(master, **kwargs)
            self._tabs: Dict[str, _VirtualFrame] = {}
            self._current_tab: Optional[str] = None

        def add(self, name: str) -> _VirtualFrame:
            frame = _VirtualFrame(self)
            self._tabs[name] = frame
            if self._current_tab is None:
                self._current_tab = name
            return frame

        def tab(self, name: str) -> _VirtualFrame:
            if name not in self._tabs:
                self.add(name)
            return self._tabs[name]

        def set(self, name: str) -> None:
            self._current_tab = name

        def get(self) -> Optional[str]:
            return self._current_tab

    class _VirtualTextbox(_VirtualWidget):
        def __init__(self, master: Any = None, **kwargs: Any) -> None:
            super().__init__(master, **kwargs)
            self._content: List[str] = []

        def insert(self, index: str, text: str) -> None:
            self._content.append(text)

        def delete(self, start: str, end: str) -> None:
            self._content.clear()

        def get(self, start: str = "1.0", end: str = "end") -> str:
            return "".join(self._content)

    class _VirtualOptionMenu(_VirtualWidget):
        def __init__(self, master: Any = None, values: Optional[List[str]] = None, **kwargs: Any) -> None:
            super().__init__(master, values=values or [], **kwargs)
            self._values = values or []
            self._selected = self._values[0] if self._values else ""

        def set(self, val: str) -> None:
            self._selected = val

        def get(self) -> str:
            return self._selected

    class _CtkShimModule:
        CTk = _VirtualWindow
        CTkToplevel = _VirtualToplevel
        CTkFrame = _VirtualFrame
        CTkLabel = _VirtualLabel
        CTkButton = _VirtualButton
        CTkEntry = _VirtualEntry
        CTkProgressBar = _VirtualProgressBar
        CTkTabview = _VirtualTabview
        CTkTextbox = _VirtualTextbox
        CTkScrollableFrame = _VirtualFrame
        CTkOptionMenu = _VirtualOptionMenu

        @staticmethod
        def set_appearance_mode(mode: str) -> None:
            pass

        @staticmethod
        def set_default_color_theme(theme: str) -> None:
            pass

    ctk = _CtkShimModule()
