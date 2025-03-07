# src/documentation_generator.py
import os
import logging
import json
import glob
from pathlib import Path
from openai import OpenAI
from src.llm_agent import LLMAgent

logger = logging.getLogger(__name__)

class DocumentationGenerator:
    def __init__(self, repo_path, repo_structure, workflow_analysis, output_analysis, api_key, model="gpt-4", temperature=0.2):
        self.repo_path = repo_path
        self.repo_structure = repo_structure
        self.workflow_analysis = workflow_analysis
        self.output_analysis = output_analysis
        self.llm_agent = LLMAgent(api_key, model, temperature)
        
    def generate_documentation(self):
        """Generate comprehensive documentation for the repository"""
        logger.info(f"Generating documentation for repository at {self.repo_path}")
        
        try:
            # Generate main readme
            main_readme = self._generate_main_readme()
            
            # Generate installation guide
            installation_guide = self._generate_installation_guide()
            
            # Generate workflow documentation
            workflow_docs = self._generate_workflow_docs()
            
            # Generate output documentation
            output_docs = self._generate_output_docs()
            
            # Generate scaling guide
            scaling_guide = self._generate_scaling_guide()
            
            # Generate troubleshooting guide
            troubleshooting_guide = self._generate_troubleshooting_guide()
            
            # Generate code documentation
            code_docs = self._generate_code_docs()
            
            # Create documentation structure
            documentation = {
                'main_readme': main_readme,
                'installation_guide': installation_guide,
                'workflow_docs': workflow_docs,
                'output_docs': output_docs,
                'scaling_guide': scaling_guide,
                'troubleshooting_guide': troubleshooting_guide,
                'code_docs': code_docs
            }
            
            logger.info(f"Documentation generation complete.")
            return documentation
            
        except Exception as e:
            logger.error(f"Error generating documentation: {str(e)}")
            raise
    
    def _generate_main_readme(self):
        """Generate the main README file"""
        logger.info("Generating main README")
        
        # Create a summary of the repository
        repo_summary = {
            'name': self.repo_structure['name'],
            'languages': self.repo_structure['languages'],
            'entry_points': self.repo_structure['entry_points'],
            'workflows': [w['workflow_name'] for w in self.workflow_analysis.get('workflows', [])]
        }
        
        prompt = f"""
        Generate a comprehensive README.md file for the following repository:
        
        Repository Summary: {json.dumps(repo_summary, indent=2)}
        
        The README should include the following sections:
        1. Introduction and Purpose
        2. Overview of Features
        3. Installation Instructions
        4. Quick Start Guide
        5. Detailed Usage Guide
        6. Workflow Overview
        7. Output Files Guide
        8. Scaling Considerations
        9. Troubleshooting
        10. Contributing Guidelines
        
        Format the README in Markdown. Make it comprehensive, clear, and user-friendly.
        Focus on helping users understand what the software does and how to use it effectively.
        """
        
        response = self.llm_agent.query(prompt)
        return response
    
    def _generate_installation_guide(self):
        """Generate an installation guide"""
        logger.info("Generating installation guide")
        
        # Get dependency information
        dependencies = self.repo_structure['dependencies']
        
        prompt = f"""
        Generate a comprehensive installation guide for the following repository:
        
        Repository Name: {self.repo_structure['name']}
        Dependencies: {json.dumps(dependencies, indent=2)}
        
        The installation guide should include the following sections:
        1. System Requirements
        2. Prerequisites
        3. Step-by-Step Installation Instructions
        4. Verification Steps
        5. Common Installation Issues and Solutions
        
        Format the guide in Markdown. Make it comprehensive, clear, and user-friendly.
        Include specific commands for installation where possible.
        """
        
        response = self.llm_agent.query(prompt)
        return response
    
    def _generate_workflow_docs(self):
        """Generate workflow documentation"""
        logger.info("Generating workflow documentation")
        
        workflows = self.workflow_analysis.get('workflows', [])
        workflow_docs = {}
        
        for workflow in workflows:
            workflow_name = workflow['workflow_name']
            
            prompt = f"""
            Generate comprehensive documentation for the following workflow:
            
            Workflow: {json.dumps(workflow, indent=2)}
            
            The documentation should include the following sections:
            1. Overview and Purpose
            2. Inputs and Prerequisites
            3. Step-by-Step Guide
            4. Expected Outputs
            5. Performance Considerations
            6. Common Issues and Solutions
            
            Format the documentation in Markdown. Make it comprehensive, clear, and user-friendly.
            Focus on helping users understand each step of the workflow and how to use it effectively.
            """
            
            response = self.llm_agent.query(prompt)
            workflow_docs[workflow_name] = response
        
        return workflow_docs
    
    def _generate_output_docs(self):
        """Generate output documentation"""
        logger.info("Generating output documentation")
        
        output_files = self.output_analysis.get('files', [])
        output_docs = {}
        
        # Group output files by type
        file_types = {}
        for file in output_files:
            file_type = file.get('file_type', 'unknown')
            if file_type in file_types:
                file_types[file_type].append(file)
            else:
                file_types[file_type] = [file]
        
        # Generate documentation for each file type
        for file_type, files in file_types.items():
            prompt = f"""
            Generate comprehensive documentation for the following output file type:
            
            File Type: {file_type}
            Files: {json.dumps(files, indent=2)}
            
            The documentation should include the following sections:
            1. Overview and Purpose
            2. File Format and Structure
            3. Column/Field Descriptions
            4. Interpretation Guide
            5. Examples of Use
            6. Related Files
            
            Format the documentation in Markdown. Make it comprehensive, clear, and user-friendly.
            Focus on helping users understand what information is in these files and how to use it.
            """
            
            response = self.llm_agent.query(prompt)
            output_docs[file_type] = response
        
        return output_docs
    
    def _generate_scaling_guide(self):
        """Generate a scaling guide"""
        logger.info("Generating scaling guide")
        
        scaling_limitations = self.workflow_analysis.get('scaling_limitations', {})
        bottlenecks = self.workflow_analysis.get('bottlenecks', [])
        
        prompt = f"""
        Generate a comprehensive scaling guide for the following repository:
        
        Repository Name: {self.repo_structure['name']}
        Scaling Limitations: {json.dumps(scaling_limitations, indent=2)}
        Bottlenecks: {json.dumps(bottlenecks, indent=2)}
        
        The scaling guide should include the following sections:
        1. Overview of Scaling Challenges
        2. Data Size Considerations
        3. Memory Management
        4. Processing Time Optimization
        5. Chunking Strategies
        6. Parallelization Options
        7. Hardware Recommendations
        8. Monitoring and Optimization
        
        Format the guide in Markdown. Make it comprehensive, clear, and user-friendly.
        Focus on helping users scale the software to handle larger datasets efficiently.
        """
        
        response = self.llm_agent.query(prompt)
        return response
    
    def _generate_troubleshooting_guide(self):
        """Generate a troubleshooting guide"""
        logger.info("Generating troubleshooting guide")
        
        # Extract potential failure points from workflows
        failure_points = []
        for workflow in self.workflow_analysis.get('workflows', []):
            for step in workflow.get('steps', []):
                failure_points.extend(step.get('potential_failures', []))
        
        prompt = f"""
        Generate a comprehensive troubleshooting guide for the following repository:
        
        Repository Name: {self.repo_structure['name']}
        Potential Failure Points: {json.dumps(failure_points, indent=2)}
        
        The troubleshooting guide should include the following sections:
        1. Common Issues and Solutions
        2. Error Message Interpretation
        3. Debugging Strategies
        4. Log File Analysis
        5. Performance Troubleshooting
        6. Installation Issues
        7. Data Format Problems
        8. Getting Help
        
        Format the guide in Markdown. Make it comprehensive, clear, and user-friendly.
        Focus on helping users diagnose and resolve common issues.
        """
        
        response = self.llm_agent.query(prompt)
        return response
    
    def _generate_code_docs(self):
        """Generate code documentation"""
        logger.info("Generating code documentation")
        
        # Get all code files
        code_files = []
        for file in self.repo_structure['files']:
            if file['type'] in ['python', 'r', 'shell', 'c++', 'java', 'javascript']:
                file_path = os.path.join(self.repo_path, file['path'])
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    try:
                        content = f.read()
                        code_files.append({
                            'path': file['path'],
                            'type': file['type'],
                            'content': content
                        })
                    except:
                        # Skip files that can't be read
                        continue
        
        # Generate documentation for each code file
        code_docs = {}
        for file in code_files:
            prompt = f"""
            Generate comprehensive documentation for the following code file:
            
            File: {file['path']}
            Type: {file['type']}
            
            ```
            {file['content']}
            ```
            
            The documentation should include the following sections:
            1. Overview and Purpose
            2. Functions and Classes
            3. Parameters and Return Values
            4. Dependencies
            5. Usage Examples
            6. Notes and Limitations
            
            Format the documentation in Markdown. Focus on helping users understand what the code does and how to use it.
            """
            
            response = self.llm_agent.query(prompt)
            code_docs[file['path']] = response
        
        return code_docs
