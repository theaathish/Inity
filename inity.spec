# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['smartenv/main.py'],
    pathex=[],
    binaries=[],
    datas=[('smartenv', 'smartenv')],
    hiddenimports=['smartenv', 'smartenv.commands', 'smartenv.commands.create', 'smartenv.commands.init', 'smartenv.commands.templates', 'smartenv.commands.package', 'smartenv.utils', 'smartenv.utils.python_version', 'smartenv.utils.package_search', 'smartenv.utils.package_manager', 'smartenv.utils.env_generator', 'smartenv.utils.git_utils', 'smartenv.core', 'smartenv.core.project_creator', 'smartenv.templates', 'smartenv.templates.registry', 'smartenv.templates.template'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='inity',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
