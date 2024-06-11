# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app.py'],
    pathex=['D:/project/PyProjects/pyProject/ClientForRemote/src'],
    binaries=[],
    datas=[('D:/project/PyProjects/pyProject/.venv/Lib/site-packages/PySide6', 'PySide6'),
           ('D:/project/PyProjects/pyProject/.venv/Lib/site-packages/shiboken6','shiboken6'),],
    hiddenimports=['json', 'os', 'time', 'unittest', 'pytest','datetime',
        'logging', 'PySide6', 'enum', 're', 'pyttsx3', 'pocketsphinx', 'shiboken6'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='app',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='app',
)
