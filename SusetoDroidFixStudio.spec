# -*- mode: python ; coding: utf-8 -*-
# Auto-generated Unified PyInstaller Spec for SusetoDroidFixStudio
from PyInstaller.utils.hooks import collect_all

datas = [
    ('/app/applet/db/schema.sql', 'db'),
    ('/app/applet/drivers', 'drivers'),
    ('/app/applet/bin', 'bin'),
    ('/app/applet/dist_web', 'dist_web'),
    ('/app/applet/ui', 'ui'),
    ('/app/applet/gui', 'gui'),
    ('/app/applet/core', 'core'),
    ('/app/applet/val', 'val'),
    ('/app/applet/adapters', 'adapters')
]

binaries = []

hiddenimports = [
    'webview',
    'pywebview',
    'app_webview',
    'core.native_bridge',
    'http.server',
    'PySide6',
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    'pyserial',
    'serial',
    'serial.tools.list_ports',
    'sqlite3',
    'pydantic',
    'customtkinter',
    'core.context_advisor',
    'core.protocol_engine',
    'core.frp_engine',
    'core.partition_manager',
    'core.dongle_protection',
    'core.fleet_manager',
    'core.adb_fastboot',
    'core.firmware_engine',
    'core.ai_engine',
    'core.report_generator',
    'core.one_click_automation',
    'ui.main_window',
    'ui.context_guide_wizard',
    'ui.hex_viewer_widget',
    'ui.device_tree_widget',
    'ui.flash_progress_component',
    'ui.theme_manager',
    'ui.kiosk_view',
    'ui.admin_view',
    'ui.app_router',
    'ui._ctk_compat',
    'storage.wal_ledger',
    'val.base_adapter',
    'val.esp32_adapter',
    'val.ftdi_adapter',
    'val.chipset_val',
]

try:
    tmp_datas, tmp_binaries, tmp_hidden = collect_all('PySide6')
    datas += tmp_datas
    binaries += tmp_binaries
    hiddenimports += tmp_hidden
except Exception:
    pass

block_cipher = None

a = Analysis(
    ['/app/applet/main.py'],
    pathex=['/app/applet'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter.test', 'unittest.test'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SusetoDroidFixStudio',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch='x86_64',
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SusetoDroidFixStudio',
)
