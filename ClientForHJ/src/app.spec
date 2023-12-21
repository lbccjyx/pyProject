# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app.py'],
    pathex=['D:/project/PyProjects/pyProject/ClientForRemote/src'],  # 您的项目路径
    binaries=[],
    datas=[('D:/project/PyProjects/pyProject/.venv/Lib/site-packages/PySide6', 'PySide6'),
            ('D:/project/PyProjects/pyProject/.venv/Lib/site-packages/shiboken6','shiboken6')
        ],  # 您的 PySide6 库的路径
    hiddenimports=['json', 'os', 'time', 'unittest', 'pytest','datetime',
        'logging', 'PySide6', 'enum', 're', 'pyttsx3', 'pocketsphinx', 'shiboken6'],  # 您的项目依赖的模块或库
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
    a.binaries,
    a.datas,
    [],
    name='app',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
