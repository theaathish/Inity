from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class ProjectTemplate:
    """Represents a project template configuration."""
    name: str
    description: str
    dependencies: List[str] = field(default_factory=list)
    files: Dict[str, str] = field(default_factory=dict)
    env_vars: Dict[str, str] = field(default_factory=dict)
    folders: List[str] = field(default_factory=list)
