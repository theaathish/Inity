
![Copy of Navy Blue And Red Modern YouTube Banner](https://github.com/user-attachments/assets/8ab11e64-e790-4f86-9aed-9d417339bd2a)

# 🚀 Inity

**Intelligent Python project environment setup tool**

*Developed by Aathish at Strucureo*

Inity automates the creation of Python projects with smart defaults, virtual environments, and popular frameworks.

## 🚀 One-Command Installation

### Linux/macOS
```bash
curl -sSL https://raw.githubusercontent.com/theaathish/Inity/main/install.sh | bash
```

### Windows (PowerShell)
```powershell
iex ((New-Object System.Net.WebClient).DownloadString('https://raw.githubusercontent.com/theaathish/Inity/main/install.ps1'))
```

### Alternative Installation Methods

**Using pip (if published to PyPI):**
```bash
pip install inity
```

**Manual Installation:**
```bash
git clone https://github.com/theaathish/Inity.git
cd Inity
pip install -r requirements.txt
pip install -e .
```

## ✨ Features

- 🎯 **Interactive project creation** with beautiful CLI
- 🐍 **Automatic virtual environment** setup with multiple Python version support
- 📦 **Template-based project generation** (FastAPI, Flask, Django, etc.)
- 🔐 **Smart .env file generation** with secure defaults
- 📁 **Organized project structure**
- 🌟 **Git initialization** with initial commit
- 🎨 **Rich terminal UI** with progress indicators
- 📦 **Comprehensive package management** (PyPI, Git repos, conda, venv)
- 🐍 **Python version management** (system, conda, pyenv)
- 🔗 **Git repository package installation**

## 📖 Usage

### Create a new project

```bash
# Interactive mode (recommended)
inity create

# Quick creation with template
inity create my-api --template fastapi

# Create in specific directory
inity create my-app --dir ~/projects --template flask
```

### Package Management

```bash
# Search for packages
inity package search fastapi

# Install packages
inity package install requests pandas
inity package install --git https://github.com/user/repo.git

# Install globally or in specific environments
inity package install numpy --global
inity package install scipy --env conda:myenv

# List and manage packages
inity package list
inity package update --all
inity package uninstall old-package
```

### Available templates

```bash
# List all available templates
inity templates list

# Show template details
inity templates show fastapi
```

### Initialize existing directory

```bash
# Initialize current directory
inity init

# Initialize with specific template
inity init --template django
```

## 🎯 Available Templates

| Template | Description | Key Dependencies |
|----------|-------------|------------------|
| `basic` | Minimal Python project | - |
| `fastapi` | Modern web API | FastAPI, Uvicorn, Pydantic |
| `flask` | Web application | Flask, SQLAlchemy |
| `django` | Full-featured web framework | Django |
| `data-science` | ML/Data analysis | Pandas, NumPy, Jupyter |
| `cli` | Command-line tool | Typer, Rich |

## 🔧 Example Usage

```bash
# Create a FastAPI project
inity create my-api --template fastapi

# Navigate and run
cd my-api
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python main.py

# API will be available at http://127.0.0.1:8000
```

## 📁 Generated Project Structure

### FastAPI Project
```
my-api/
├── .env                 # Environment variables
├── .gitignore          # Git ignore rules
├── .venv/              # Virtual environment
├── main.py             # Application entry point
├── requirements.txt    # Dependencies
├── README.md          # Project documentation
└── app/
    ├── __init__.py
    ├── routers/        # API routes
    ├── models/         # Data models
    └── services/       # Business logic
```

## 🛠️ Development

```bash
# Clone and setup development environment
git clone https://github.com/strucureo/inity.git
cd inity

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .

# Run the CLI
inity --help
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Developed by **Aathish** at **Strucureo**
- Built with [Typer](https://typer.tiangolo.com/) for CLI
- Styled with [Rich](https://rich.readthedocs.io/) for beautiful terminal output
- Interactive prompts powered by [Questionary](https://questionary.readthedocs.io/)

---

*© 2024 Strucureo. All rights reserved.*
