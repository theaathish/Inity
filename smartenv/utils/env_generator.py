import secrets
import string
from pathlib import Path
from typing import Dict

class EnvGenerator:
    """Generate .env files with smart defaults."""
    
    def __init__(self, project_path: Path):
        self.project_path = project_path
    
    def generate_env_file(self, env_vars: Dict[str, str]):
        """Generate a .env file with the provided variables."""
        env_path = self.project_path / ".env"
        
        lines = ["# Environment variables for the project", ""]
        
        for key, value in env_vars.items():
            # Generate secure values for certain keys
            if "secret" in key.lower() or "key" in key.lower():
                if value in ["your-secret-key-here", "django-insecure-change-me", "django-insecure-change-me-in-production"]:
                    value = self._generate_secret_key()
            
            lines.append(f"{key}={value}")
        
        env_path.write_text("\n".join(lines) + "\n", encoding='utf-8')
    
    def _generate_secret_key(self, length: int = 50) -> str:
        """Generate a secure random secret key."""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))
