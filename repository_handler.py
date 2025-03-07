# src/repository_handler.py
import os
import logging
import subprocess
import json
from git import Repo
from pathlib import Path

logger = logging.getLogger(__name__)

class RepositoryHandler:
    def __init__(self, repo_url, skip_clone=False):
        self.repo_url = repo_url
        self.skip_clone = skip_clone
        self.repo_name = self._extract_repo_name()
        self.repo_path = os.path.join(os.getcwd(), 'repos', self.repo_name)
        
    def _extract_repo_name(self):
        """Extract repository name from URL"""
        return self.repo_url.split('/')[-1].replace('.git', '')
    
    def clone_repository(self):
        """Clone the repository and return the path"""
        if os.path.exists(self.repo_path) and self.skip_clone:
            logger.info(f"Using existing repository at {self.repo_path}")
            return self.repo_path
            
        logger.info(f"Cloning repository {self.repo_url} to {self.repo_path}")
        try:
            if os.path.exists(self.repo_path):
                # Remove existing repository
                import shutil
                shutil.rmtree(self.repo_path)
                
            # Create parent directory if it doesn't exist
            os.makedirs(os.path.dirname(self.repo_path), exist_ok=True)
            
            # Clone repository
            Repo.clone_from(self.repo_url, self.repo_path)
            logger.info(f"Repository cloned successfully to {self.repo_path}")
            return self.repo_path
        except Exception as e:
            logger.error(f"Error cloning repository: {str(e)}")
            raise
    
    def analyze_repository_structure(self):
        """Analyze the repository structure and return a structured representation"""
        logger.info(f"Analyzing repository structure at {self.repo_path}")
        
        try:
            repo_structure = {
                'name': self.repo_name,
                'path': self.repo_path,
                'files': [],
                'languages': {},
                'entry_points': [],
                'dependencies': []
            }
            
            # Get all files in the repository
            for root, dirs, files in os.walk(self.repo_path):
                # Skip .git directory
                if '.git' in dirs:
                    dirs.remove('.git')
                
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, self.repo_path)
                    
                    # Skip binary files and very large files
                    if self._is_binary_file(file_path) or os.path.getsize(file_path) > 1000000:
                        continue
                    
                    # Determine file type
                    file_type = self._determine_file_type(file)
                    
                    # Add file to structure
                    repo_structure['files'].append({
                        'path': rel_path,
                        'type': file_type,
                        'size': os.path.getsize(file_path)
                    })
                    
                    # Update language statistics
                    if file_type in repo_structure['languages']:
                        repo_structure['languages'][file_type] += 1
                    else:
                        repo_structure['languages'][file_type] = 1
            
            # Identify potential entry points
            repo_structure['entry_points'] = self._identify_entry_points(repo_structure['files'])
            
            # Identify dependencies
            repo_structure['dependencies'] = self._identify_dependencies()
            
            logger.info(f"Repository analysis complete. Found {len(repo_structure['files'])} files.")
            return repo_structure
            
        except Exception as e:
            logger.error(f"Error analyzing repository structure: {str(e)}")
            raise
    
    def _is_binary_file(self, file_path):
        """Check if a file is binary"""
        try:
            with open(file_path, 'r') as f:
                f.read(1024)
                return False
        except UnicodeDecodeError:
            return True
    
    def _determine_file_type(self, filename):
        """Determine file type based on extension"""
        ext = os.path.splitext(filename)[1].lower()
        if ext in ['.py']:
            return 'python'
        elif ext in ['.r', '.rmd']:
            return 'r'
        elif ext in ['.sh', '.bash']:
            return 'shell'
        elif ext in ['.c', '.cpp', '.cc', '.h', '.hpp']:
            return 'c++'
        elif ext in ['.java']:
            return 'java'
        elif ext in ['.js', '.ts']:
            return 'javascript'
        elif ext in ['.md', '.markdown']:
            return 'markdown'
        elif ext in ['.json']:
            return 'json'
        elif ext in ['.yml', '.yaml']:
            return 'yaml'
        elif ext in ['.txt']:
            return 'text'
        elif ext in ['.csv', '.tsv']:
            return 'data'
        else:
            return 'other'
    
    def _identify_entry_points(self, files):
        """Identify potential entry points in the codebase"""
        entry_points = []
        
        for file in files:
            # Common entry point patterns
            if file['path'].endswith('main.py') or file['path'].endswith('run.py') or file['path'].endswith('app.py'):
                entry_points.append(file['path'])
            elif file['path'].startswith('bin/') and file['type'] in ['python', 'r', 'shell']:
                entry_points.append(file['path'])
            elif file['path'].endswith('setup.py'):
                entry_points.append(file['path'])
        
        return entry_points
    
    def _identify_dependencies(self):
        """Identify dependencies of the repository"""
        dependencies = {
            'python': [],
            'r': [],
            'system': []
        }
        
        # Check for Python dependencies
        if os.path.exists(os.path.join(self.repo_path, 'requirements.txt')):
            with open(os.path.join(self.repo_path, 'requirements.txt'), 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        dependencies['python'].append(line)
        
        # Check for R dependencies in DESCRIPTION file
        if os.path.exists(os.path.join(self.repo_path, 'DESCRIPTION')):
            with open(os.path.join(self.repo_path, 'DESCRIPTION'), 'r') as f:
                content = f.read()
                if 'Imports:' in content:
                    imports_section = content.split('Imports:')[1].split('\n\n')[0]
                    for line in imports_section.split('\n'):
                        line = line.strip().split(',')[0]
                        if line:
                            dependencies['r'].append(line)
        
        return dependencies
