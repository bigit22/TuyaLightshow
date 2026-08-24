# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_all

datas = []
binaries = []
hiddenimports = [
    'soundcard',
    'cffi',
    'pydantic_settings',
    'tinytuya',
    'PyQt6',
    'tomli_w',
]

tmp_datas, tmp_binaries, tmp_hidden = collect_all('soundcard')
datas.extend(tmp_datas)
binaries.extend(tmp_binaries)
hiddenimports.extend(tmp_hidden)

block_cipher = None

a = Analysis(
    ['src/tuyalight/__main__.py'],
    pathex=['src'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='TuyaLightshow',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Окно консоли скрыто
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
