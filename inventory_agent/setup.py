"""
Setup script pour l'agent d'inventaire
"""

from setuptools import setup, find_packages
import os

# Lire le fichier requirements.txt
def read_requirements():
    with open('requirements.txt') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

# Lire le README
def read_readme():
    with open('README.md', 'r', encoding='utf-8') as f:
        return f.read()

setup(
    name="inventory-agent",
    version="1.0.0",
    author="Votre Entreprise",
    author_email="admin@votreentreprise.com",
    description="Agent d'inventaire Windows pour collecter les informations système et logiciels",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    install_requires=read_requirements(),
    python_requires=">=3.8",
    entry_points={
        'console_scripts': [
            'inventory-agent=src.inventory:main',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Systems Administration",
    ],
    keywords="inventory, windows, system, monitoring, agent",
    project_urls={
        "Bug Reports": "https://github.com/votreentreprise/inventory-agent/issues",
        "Source": "https://github.com/votreentreprise/inventory-agent",
    },
)
