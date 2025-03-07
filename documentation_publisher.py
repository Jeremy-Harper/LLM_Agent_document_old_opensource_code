# src/documentation_publisher.py
import os
import logging
import json
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)

class DocumentationPublisher:
    def __init__(self, output_dir, repo_path):
        self.output_dir = output_dir
        self.repo_path = repo_path
        self.docs_dir = os.path.join(output_dir, 'docs')
        self.code_docs_dir = os.path.join(self.docs_dir, 'code')
        self.workflow_docs_dir = os.path.join(self.docs_dir, 'workflows')
        self.output_docs_dir = os.path.join(self.docs_dir, 'outputs')
        
    def publish_documentation(self, documentation):
        """Publish the generated documentation"""
        logger.info(f"Publishing documentation to {self.output_dir}")
        
        try:
            # Create output directories
            os.makedirs(self.output_dir, exist_ok=True)
            os.makedirs(self.docs_dir, exist_ok=True)
            os.makedirs(self.code_docs_dir, exist_ok=True)
            os.makedirs(self.workflow_docs_dir, exist_ok=True)
            os.makedirs(self.output_docs_dir, exist_ok=True)
            
            # Write main README
            with open(os.path.join(self.output_dir, 'README.md'), 'w') as f:
                f.write(documentation['main_readme'])
            
            # Write installation guide
            with open(os.path.join(self.docs_dir, 'installation.md'), 'w') as f:
                f.write(documentation['installation_guide'])
            
            # Write scaling guide
            with open(os.path.join(self.docs_dir, 'scaling.md'), 'w') as f:
                f.write(documentation['scaling_guide'])
            
            # Write troubleshooting guide
            with open(os.path.join(self.docs_dir, 'troubleshooting.md'), 'w') as f:
                f.write(documentation['troubleshooting_guide'])
            
            # Write workflow documentation
            for workflow_name, workflow_doc in documentation['workflow_docs'].items():
                safe_name = self._safe_filename(workflow_name)
                with open(os.path.join(self.workflow_docs_dir, f'{safe_name}.md'), 'w') as f:
                    f.write(workflow_doc)
            
            # Write output documentation
            for output_type, output_doc in documentation['output_docs'].items():
                safe_name = self._safe_filename(output_type)
                with open(os.path.join(self.output_docs_dir, f'{safe_name}.md'), 'w') as f:
                    f.write(output_doc)
            
            # Write code documentation
            for file_path, code_doc in documentation['code_docs'].items():
                # Create directory structure
                dir_path = os.path.dirname(file_path)
                if dir_path:
                    os.makedirs(os.path.join(self.code_docs_dir, dir_path), exist_ok=True)
                
                # Write documentation
                safe_name = self._safe_filename(os.path.basename(file_path))
                with open(os.path.join(self.code_docs_dir, dir_path, f'{safe_name}.md'), 'w') as f:
                    f.write(code_doc)
            
            # Create index files
            self._create_index_files(documentation)
            
            # Copy documentation to repository
            if os.path.exists(self.repo_path):
                repo_docs_dir = os.path.join(self.repo_path, 'docs')
                os.makedirs(repo_docs_dir, exist_ok=True)
                
                # Copy main README
                shutil.copy(os.path.join(self.output_dir, 'README.md'), os.path.join(self.repo_path, 'README.md'))
                
                # Copy other documentation
                for root, dirs, files in os.walk(self.docs_dir):
                    for file in files:
                        src_path = os.path.join(root, file)
                        rel_path = os.path.relpath(src_path, self.docs_dir)
                        dst_path = os.path.join(repo_docs_dir, rel_path)
                        
                        # Create directory if it doesn't exist
                        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                        
                        # Copy file
                        shutil.copy(src_path, dst_path)
            
            logger.info(f"Documentation published successfully to {self.output_dir}")
            
        except Exception as e:
            logger.error(f"Error publishing documentation: {str(e)}")
            raise
    
    def _safe_filename(self, filename):
        """Convert a string to a safe filename"""
        return filename.replace(' ', '_').replace('/', '_').replace('\\', '_').replace(':', '_')
    
    def _create_index_files(self, documentation):
        """Create index files for documentation"""
        # Create main index
        main_index = f"""# Documentation Index

## Installation and Setup
- [Installation Guide](installation.md)

## Workflows
{self._create_list_links(documentation['workflow_docs'], 'workflows')}

## Output Files
{self._create_list_links(documentation['output_docs'], 'outputs')}

## Advanced Topics
- [Scaling Guide](scaling.md)
- [Troubleshooting Guide](troubleshooting.md)

## Code Documentation
{self._create_code_list(documentation['code_docs'])}
"""
        
        with open(os.path.join(self.docs_dir, 'index.md'), 'w') as f:
            f.write(main_index)
        
        # Create workflow index
        workflow_index = f"""# Workflow Documentation

{self._create_list_links(documentation['workflow_docs'], '')}
"""
        
        with open(os.path.join(self.workflow_docs_dir, 'index.md'), 'w') as f:
            f.write(workflow_index)
        
        # Create output index
        output_index = f"""# Output Files Documentation

{self._create_list_links(documentation['output_docs'], '')}
"""
        
        with open(os.path.join(self.output_docs_dir, 'index.md'), 'w') as f:
            f.write(output_index)
    
    def _create_list_links(self, items, prefix):
        """Create a list of links from items"""
        links = []
        for name in items:
            safe_name = self._safe_filename(
safe_name = self._safe_filename(name)
            links.append(f"- [{name}]({prefix}/{safe_name}.md)")
        
        return "\n".join(links)
    
    def _create_code_list(self, code_docs):
        """Create a list of links for code documentation"""
        links = []
        
        # Group by directory
        directories = {}
        for path in code_docs:
            dir_name = os.path.dirname(path) or "root"
            if dir_name not in directories:
                directories[dir_name] = []
            directories[dir_name].append(path)
        
        # Create links
        for dir_name, files in directories.items():
            if dir_name == "root":
                links.append(f"### Root")
            else:
                links.append(f"### {dir_name}")
            
            for path in files:
                file_name = os.path.basename(path)
                safe_name = self._safe_filename(file_name)
                relative_path = os.path.join("code", path.replace(file_name, safe_name + ".md"))
                links.append(f"- [{file_name}]({relative_path})")
            
            links.append("")
        
        return "\n".join(links)
