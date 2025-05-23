"""
Ontology file discovery utilities.
"""

import os
from pathlib import Path
from typing import List


class OntologyDiscovery:
    """Discovers ontology files in a directory tree."""
    
    ONTOLOGY_EXTENSIONS = {'.owl', '.rdf', '.ttl', '.n3', '.nt'}
    
    def __init__(self, root_dir: str):
        """
        Initialize the discovery with a root directory.
        
        Args:
            root_dir: Root directory to search for ontology files
        """
        self.root_dir = Path(root_dir)
        
    def find_ontologies(self) -> List[str]:
        """
        Find all ontology files in the root directory and subdirectories.
        
        Returns:
            List of absolute paths to ontology files
        """
        ontology_files = []
        
        for file_path in self.root_dir.rglob('*'):
            if (file_path.is_file() and 
                file_path.suffix.lower() in self.ONTOLOGY_EXTENSIONS):
                ontology_files.append(str(file_path.absolute()))
        
        # Sort for consistent ordering
        ontology_files.sort()
        
        return ontology_files
    
    def is_ontology_file(self, file_path: str) -> bool:
        """
        Check if a file is an ontology file based on its extension.
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            True if the file appears to be an ontology file
        """
        return Path(file_path).suffix.lower() in self.ONTOLOGY_EXTENSIONS
    
    def get_file_info(self, file_path: str) -> dict:
        """
        Get basic information about an ontology file.
        
        Args:
            file_path: Path to the ontology file
            
        Returns:
            Dictionary with file information
        """
        path = Path(file_path)
        
        return {
            'path': str(path.absolute()),
            'name': path.name,
            'stem': path.stem,
            'suffix': path.suffix,
            'size': path.stat().st_size if path.exists() else 0,
            'relative_path': str(path.relative_to(self.root_dir))
        }
