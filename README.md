# TRO Backend

FastAPI application with strict type checking and modern Python practices.

## Getting Started

### Prerequisites

- Python 3.11+
- Docker and Docker Compose

### Installation

#### Using Docker Compose (Recommended)

```bash
docker-compose up --build
```

#### Using Local Python

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Verify you're using the venv Python (should show path to .venv)
which python  # On Windows: where python
which pip     # On Windows: where pip

# Install dependencies using the venv's pip
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

**Note**: If you encounter "externally-managed-environment" error, make sure:
1. The virtual environment is properly activated (you should see `(.venv)` in your prompt)
2. Use `python -m pip` instead of just `pip` to ensure you're using the venv's pip
3. If the issue persists, try recreating the venv: `rm -rf .venv && python3 -m venv .venv`

### Access the Application

- **API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health

## VS Code / Cursor Extensions

Recommended extensions for optimal development experience:

1. **Pylance** (`ms-python.vscode-pylance`) - IntelliSense, type checking, and navigation
2. **Python** (`ms-python.python`) - Python language support
3. **Mypy Type Checker** (`ms-python.mypy-type-checker`) - Real-time type checking
4. **Black Formatter** (`ms-python.black-formatter`) - Code formatting
5. **Ruff** (`astral-sh.ruff-vscode`) - Fast linter

Fallback venv corrupto

# Elimina el venv existente
rm -rf .venv

# Crea uno nuevo
python3 -m venv .venv

# Actívalo
source .venv/bin/activate

# Instala las dependencias
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"