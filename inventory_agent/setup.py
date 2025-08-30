"""
Setup cx_Freeze pour construire un MSI de service Windows
"""

from cx_Freeze import setup, Executable
from pathlib import Path
import sys

NAME = "InventoryAgent"
VERSION = "1.0.0"

# Fichiers et dossiers à inclure dans le build (sources de l'agent)
include_files = [
    ("src", "src"),
]

PY_MM = f"{sys.version_info.major}{sys.version_info.minor}"

build_exe_options = {
    "include_msvcr": True,
    "includes": [
        # pywin32 service
        "win32serviceutil", "win32service", "win32event", "servicemanager",
        # dépendances
        "requests", "psutil", "wmi", "json", "time", "socket", "logging",
    ],
    "packages": [
        "requests", "psutil", "wmi", "winreg", "threading", "datetime",
    ],
    "excludes": [
        "tkinter",
    ],
    "include_files": include_files,
    # DLL pywin32 nécessaires au runtime du service
    "bin_includes": [
        f"pywintypes{PY_MM}.dll",
        f"pythoncom{PY_MM}.dll",
    ],
    # Dossier de logs (créé par l'app elle-même au runtime)
}

bdist_msi_options = {
    "add_to_path": False,
    # Répertoire d'installation par défaut (Program Files)
    "initial_target_dir": r"[ProgramFiles64Folder]\%s" % NAME,
    # Installer pour tous les utilisateurs (nécessite élévation)
    "all_users": True,
    # Portée machine (cx_Freeze >= 6.14)
    # "install_scope": "perMachine",
    # Code d'upgrade stable (à générer et figer si vous publiez des mises à jour)
    # "upgrade_code": "{00000000-0000-0000-0000-000000000000}",
    # Pas de CustomAction MSI (cause d'erreurs DLL). Utiliser le script post-install.
}

executables = [
    Executable(
        script=str(Path("src") / "windows_service.py"),
        base="Win32Service",
        target_name=f"{NAME}Service.exe",
        # Nom/description du service sont gérés par src/config.py
    )
]

setup(
    name=NAME,
    version=VERSION,
    description="Agent d'inventaire Windows (Service)",
    options={
        "build_exe": build_exe_options,
        "bdist_msi": bdist_msi_options,
    },
    executables=executables,
)
