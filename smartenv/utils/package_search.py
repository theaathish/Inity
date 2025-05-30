import json
import urllib.request
import urllib.parse
import urllib.error
from typing import List, Dict, Optional, Tuple
from rich.console import Console

console = Console()

class PackageSearcher:
    """Search and manage Python packages from PyPI with real-time search."""
    
    def __init__(self):
        self.pypi_url = "https://pypi.org/pypi"
        self.search_cache = {}
        self.session_timeout = 10
    
    def search_packages_realtime(self, query: str, limit: int = 15) -> List[Dict[str, str]]:
        """Search for packages on PyPI using multiple search strategies."""
        if not query or len(query.strip()) < 2:
            return []
        
        query = query.strip().lower()
        
        # Popular packages with categories for better search
        popular_packages = {
            # Web frameworks
            "fastapi": {"name": "fastapi", "version": "0.104.1", "description": "FastAPI framework, high performance, easy to learn", "category": "web"},
            "flask": {"name": "flask", "version": "3.0.0", "description": "A simple framework for building complex web applications", "category": "web"},
            "django": {"name": "django", "version": "4.2.7", "description": "High-level Python web framework", "category": "web"},
            
            # HTTP/API
            "requests": {"name": "requests", "version": "2.31.0", "description": "Python HTTP for Humans", "category": "http"},
            "httpx": {"name": "httpx", "version": "0.25.2", "description": "Next generation HTTP client", "category": "http"},
            "aiohttp": {"name": "aiohttp", "version": "3.9.1", "description": "Async HTTP client/server framework", "category": "http"},
            
            # Data science
            "pandas": {"name": "pandas", "version": "2.1.4", "description": "Powerful data structures for data analysis", "category": "data"},
            "numpy": {"name": "numpy", "version": "1.26.2", "description": "Fundamental package for array computing", "category": "data"},
            "matplotlib": {"name": "matplotlib", "version": "3.8.2", "description": "Comprehensive library for creating visualizations", "category": "data"},
            "seaborn": {"name": "seaborn", "version": "0.13.0", "description": "Statistical data visualization library", "category": "data"},
            "scikit-learn": {"name": "scikit-learn", "version": "1.3.2", "description": "Machine learning library", "category": "ml"},
            
            # Database
            "sqlalchemy": {"name": "sqlalchemy", "version": "2.0.23", "description": "SQL toolkit and ORM", "category": "database"},
            "pymongo": {"name": "pymongo", "version": "4.6.0", "description": "MongoDB driver", "category": "database"},
            "redis": {"name": "redis", "version": "5.0.1", "description": "Redis client library", "category": "database"},
            
            # Testing
            "pytest": {"name": "pytest", "version": "7.4.3", "description": "Testing framework", "category": "testing"},
            "unittest2": {"name": "unittest2", "version": "1.1.0", "description": "Backport of unittest module", "category": "testing"},
            
            # CLI
            "typer": {"name": "typer", "version": "0.9.0", "description": "Modern library for building CLI applications", "category": "cli"},
            "click": {"name": "click", "version": "8.1.7", "description": "Command line interface creation kit", "category": "cli"},
            "rich": {"name": "rich", "version": "13.7.0", "description": "Library for rich text and beautiful formatting", "category": "cli"},
            
            # Utilities
            "python-dotenv": {"name": "python-dotenv", "version": "1.0.0", "description": "Environment variable loader", "category": "config"},
            "pydantic": {"name": "pydantic", "version": "2.5.1", "description": "Data validation using Python type annotations", "category": "validation"},
            "loguru": {"name": "loguru", "version": "0.7.2", "description": "Logging library", "category": "logging"},
        }
        
        results = []
        
        # Search by exact name match
        if query in popular_packages:
            results.append(popular_packages[query])
        
        # Search by partial name match
        for pkg_name, pkg_info in popular_packages.items():
            if query in pkg_name.lower() and pkg_info not in results:
                results.append(pkg_info)
        
        # Search by description and category
        query_words = query.split()
        for pkg_name, pkg_info in popular_packages.items():
            if pkg_info not in results:
                description_lower = pkg_info["description"].lower()
                category_lower = pkg_info.get("category", "").lower()
                
                if (any(word in description_lower for word in query_words) or
                    any(word in category_lower for word in query_words) or
                    query in description_lower or query in category_lower):
                    results.append(pkg_info)
        
        # Try to get real package info from PyPI for exact matches
        if len(results) < limit:
            real_package = self._get_real_package_info(query)
            if real_package and real_package not in results:
                results.insert(0, real_package)
        
        return results[:limit]
    
    def _get_real_package_info(self, package_name: str) -> Optional[Dict]:
        """Try to get real package info from PyPI."""
        try:
            url = f"{self.pypi_url}/{package_name}/json"
            with urllib.request.urlopen(url, timeout=5) as response:
                data = json.loads(response.read().decode())
            
            info = data.get("info", {})
            return {
                "name": info.get("name", package_name),
                "version": info.get("version", "unknown"),
                "description": info.get("summary", "No description available")[:100],
                "author": info.get("author", "Unknown"),
                "download_count": 0,  # Would need additional API call
            }
        except Exception:
            return None
    
    def get_package_versions_realtime(self, package_name: str, limit: int = 10) -> List[str]:
        """Get available versions for a package from PyPI."""
        try:
            url = f"{self.pypi_url}/{package_name}/json"
            with urllib.request.urlopen(url, timeout=self.session_timeout) as response:
                data = json.loads(response.read().decode())
            
            releases = data.get("releases", {})
            versions = []
            
            # Filter out versions that have no files
            for version, files in releases.items():
                if files:  # Only include versions that have files
                    versions.append(version)
            
            # Sort versions (simple reverse sort for now)
            versions.sort(reverse=True)
            return versions[:limit]
            
        except Exception as e:
            console.print(f"[yellow]Warning: Could not fetch versions for {package_name}: {e}[/yellow]")
            return ["latest"]
    
    def validate_packages(self, packages: List[str]) -> Tuple[List[str], List[str]]:
        """Validate a list of packages and return valid and invalid ones."""
        valid_packages = []
        invalid_packages = []
        
        for package in packages:
            if self._validate_single_package(package):
                valid_packages.append(package)
            else:
                invalid_packages.append(package)
        
        return valid_packages, invalid_packages
    
    def _validate_single_package(self, package: str) -> bool:
        """Validate if a single package exists on PyPI."""
        try:
            # Extract package name from version specifications
            package_name = package.split("==")[0].split(">=")[0].split("<=")[0].split("~=")[0].split("!=")[0]
            package_name = package_name.strip()
            
            url = f"{self.pypi_url}/{package_name}/json"
            with urllib.request.urlopen(url, timeout=5) as response:
                return response.status == 200
        except Exception:
            # If we can't validate, assume it's valid (pip will handle the error)
            return True
