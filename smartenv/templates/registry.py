from typing import Dict, Optional
from .template import ProjectTemplate

class TemplateRegistry:
    """Registry for managing project templates."""
    
    def __init__(self):
        self._templates = self._load_builtin_templates()
    
    def get_template(self, name: str) -> Optional[ProjectTemplate]:
        """Get a template by name."""
        return self._templates.get(name)
    
    def get_available_templates(self) -> Dict[str, ProjectTemplate]:
        """Get all available templates."""
        return self._templates.copy()
    
    def _load_builtin_templates(self) -> Dict[str, ProjectTemplate]:
        """Load built-in templates."""
        return {
            "basic": self._basic_template(),
            "fastapi": self._fastapi_template(),
        }
    
    def _basic_template(self) -> ProjectTemplate:
        return ProjectTemplate(
            name="basic",
            description="Basic Python project with minimal setup",
            dependencies=[],
            files={
                "main.py": '''"""Main application entry point."""

def main():
    """Main function."""
    print("Hello, {project_name}!")

if __name__ == "__main__":
    main()
''',
                "README.md": '''# {project_name_title}

{description}

## Setup

```bash
# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate

# Run the application
python main.py
```
''',
            },
            env_vars={
                "PYTHONPATH": ".",
                "ENVIRONMENT": "development"
            }
        )
    
    def _fastapi_template(self) -> ProjectTemplate:
        return ProjectTemplate(
            name="fastapi",
            description="FastAPI web application with modern structure",
            dependencies=["fastapi", "uvicorn[standard]"],
            files={
                "main.py": '''"""FastAPI application entry point."""
from fastapi import FastAPI

app = FastAPI(
    title="{project_name_title}",
    description="{description}",
    version="0.1.0"
)

@app.get("/")
async def root():
    """Root endpoint."""
    return {{"message": "Hello from {project_name_title}!"}}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
''',
                "README.md": '''# {project_name_title}

{description}

## Setup

```bash
# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## API Documentation

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
''',
            },
            env_vars={
                "ENVIRONMENT": "development",
                "HOST": "127.0.0.1",
                "PORT": "8000",
            }
        )
