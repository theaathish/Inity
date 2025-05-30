"""Setup script for Inity CLI tool."""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="inity",
    version="0.3.2",
    author="Aathish",
    author_email="aathish@strucureo.dev",
    description="🚀 Intelligent Python project environment setup tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/strucureo/inity",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Tools",
        "Topic :: System :: Installation/Setup",
    ],
    python_requires=">=3.8",
    install_requires=[
        "typer[all]>=0.9.0",
        "rich>=13.0.0",
        "questionary>=1.10.0",
        "gitpython>=3.1.0",
    ],
    entry_points={
        "console_scripts": [
            "inity=smartenv.main:app",
        ],
    },
)
