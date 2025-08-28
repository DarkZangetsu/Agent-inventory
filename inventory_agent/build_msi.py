"""
Script pour générer le fichier MSI de l'agent d'inventaire
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from cx_Freeze import setup, Executable

def build_msi():
    """Génère le fichier MSI de l'agent"""
    
    # Configuration de base
    base = None
    if sys.platform == "win32":
        base = "Win32GUI"
    
    # Fichiers à inclure
    include_files = [
        ("src/config.py", "config.py"),
        ("requirements.txt", "requirements.txt"),
        ("README.md", "README.md")
    ]
    
    # Packages à inclure
    packages = [
        "wmi",
        "psutil", 
        "requests",
        "gql",
        "aiohttp",
        "win32serviceutil",
        "win32service",
        "win32event",
        "servicemanager"
    ]
    
    # Exclusions
    excludes = [
        "tkinter",
        "unittest",
        "email",
        "http",
        "urllib",
        "xml",
        "pydoc"
    ]
    
    # Configuration des exécutables
    executables = [
        Executable(
            "src/inventory.py",
            base=base,
            target_name="InventoryAgent.exe",
            icon=None,  # Ajouter une icône si nécessaire
            shortcut_name="Agent d'Inventaire",
            shortcut_dir="DesktopFolder"
        ),
        Executable(
            "src/windows_service.py",
            base="Win32Service",
            target_name="InventoryAgentService.exe",
            icon=None
        )
    ]
    
    # Configuration de cx_Freeze
    setup(
        name="InventoryAgent",
        version="1.0.0",
        description="Agent d'inventaire Windows",
        author="Votre Entreprise",
        options={
            "build_exe": {
                "packages": packages,
                "excludes": excludes,
                "include_files": include_files,
                "include_msvcr": True,
            },
            "bdist_msi": {
                "data": {
                    "Shortcut": [
                        ("DesktopShortcut",        # Shortcut
                         "DesktopFolder",          # Directory_
                         "Agent d'Inventaire",     # Name
                         "TARGETDIR",              # Component_
                         "[TARGETDIR]InventoryAgent.exe", # Target
                         None,                     # Arguments
                         None,                     # Description
                         None,                     # Hotkey
                         None,                     # Icon
                         None,                     # IconIndex
                         None,                     # ShowCmd
                         "TARGETDIR"               # WkDir
                        )
                    ]
                },
                "initial_target_dir": r"[ProgramFilesFolder]\InventoryAgent",
                "target_name": "InventoryAgent-1.0.0.msi"
            }
        },
        executables=executables
    )

def build_with_pyinstaller():
    """Alternative: générer avec PyInstaller"""
    
    # Créer le fichier spec pour PyInstaller
    spec_content = """
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/inventory.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/config.py', '.'),
        ('requirements.txt', '.'),
        ('README.md', '.')
    ],
    hiddenimports=[
        'wmi',
        'psutil',
        'requests',
        'gql',
        'aiohttp',
        'win32serviceutil',
        'win32service',
        'win32event',
        'servicemanager'
    ],
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
    name='InventoryAgent',
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
"""
    
    # Écrire le fichier spec
    with open("InventoryAgent.spec", "w") as f:
        f.write(spec_content)
    
    # Exécuter PyInstaller
    subprocess.run([
        "pyinstaller",
        "--clean",
        "--onefile",
        "--name=InventoryAgent",
        "src/inventory.py"
    ])

def main():
    """Fonction principale"""
    print("Génération du fichier MSI pour l'agent d'inventaire...")
    
    # Vérifier que nous sommes sur Windows
    if sys.platform != "win32":
        print("Erreur: Ce script doit être exécuté sur Windows")
        sys.exit(1)
    
    # Vérifier les dépendances
    try:
        import cx_Freeze
        print("Utilisation de cx_Freeze pour générer le MSI...")
        build_msi()
    except ImportError:
        print("cx_Freeze non disponible, utilisation de PyInstaller...")
        build_with_pyinstaller()
    
    print("Génération terminée!")

if __name__ == "__main__":
    main()
