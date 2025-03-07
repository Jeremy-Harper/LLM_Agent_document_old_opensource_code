# src/workflow_analyzer.py
import os
import logging
import json
from pathlib import Path
from openai import OpenAI
from src.llm_agent import LLMAgent

logger = logging.getLogger(__name__)

class WorkflowAnalyzer:
    def __init__(self, repo_path, api_key, model="gpt-4", temperature=0.2):
        self.repo_path = repo_path
        self.llm_agent = LLMAgent(api_key, model, temperature)
        
    def analyze_workflow(self):
        """Analyze the workflow of the repository"""
        logger.info(f"Analyzing workflow for repository at {self.repo_path}")
        
        try:
            # Get all analysis-related files
            analysis_files = self._get_analysis_files()
            
            # Analyze entry points
            entry_points = self._analyze_entry_points(analysis_files)
            
            # Analyze workflows
            workflows = self._analyze_workflows(analysis_files, entry_points)
            
            # Analyze scaling limitations
            scaling_limitations = self._analyze_scaling_limitations(workflows)
            
            # Analyze potential bottlenecks
            bottlenecks = self._analyze_bottlenecks(workflows)
            
            # Aggregate results
            workflow_analysis = {
                'entry_points': entry_points,
                'workflows': workflows,
                'scaling_limitations': scaling_limitations,
                'bottlenecks': bottlenecks
            }
            
            logger.info(f"Workflow analysis complete. Found {len(workflows)} workflows.")
            return workflow_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing workflow: {str(e)}")
            raise
    
    def _get_analysis_files(self):
        """Get all analysis-related files in the repository"""
        analysis_files = []
        
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
                
                # Only include code files
                if self._is_code_file(file):
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        try:
                            content = f.read()
                            analysis_files.append({
                                'path': rel_path,
                                'content': content
                            })
                        except:
                            # Skip files that can't be read
                            continue
        
        return analysis_files
    
    def _is_binary_file(self, file_path):
        """Check if a file is binary"""
        try:
            with open(file_path, 'r') as f:
                f.read(1024)
                return False
        except UnicodeDecodeError:
            return True
    
    def _is_code_file(self, filename):
        """Check if a file is a code file"""
        ext = os.path.splitext(filename)[1].lower()
        return ext in ['.py', '.r', '.rmd', '.sh', '.bash', '.c', '.cpp', '.h', '.hpp', '.java', '.js', '.ts']
    
    def _analyze_entry_points(self, analysis_files):
        """Analyze entry points in the codebase"""
        entry_points = []
        
        # Find files that look like entry points
        potential_entry_points = []
        for file in analysis_files:
            if 'main' in file['path'].lower() or 'run' in file['path'].lower() or 'app' in file['path'].lower():
                potential_entry_points.append(file)
        
        # If no potential entry points found, use all analysis files
        if not potential_entry_points:
            potential_entry_points = analysis_files
        
        # Analyze each potential entry point
        for file in potential_entry_points:
            prompt = f"""
            Analyze the following code file and determine if it's an entry point for a workflow or analysis:
            
            File: {file['path']}
            
            ```
            {file['content']}
            ```
            
            Please provide a JSON response with the following structure:
            {{
                "is_entry_point": true/false,
                "main_function": "<name of main function if exists>",
                "accepts_arguments": true/false,
                "description": "<brief description of what this entry point does>",
                "expected_inputs": ["<list of expected inputs>"],
                "expected_outputs": ["<list of expected outputs>"]
            }}
            
            Focus on identifying whether this file is designed to be executed directly or imported as a module.
            """
            
            response = self.llm_agent.query(prompt)
            
            try:
                entry_point_analysis = json.loads(response)
                if entry_point_analysis.get('is_entry_point', False):
                    entry_points.append({
                        'path': file['path'],
                        'main_function': entry_point_analysis.get('main_function', ''),
                        'accepts_arguments': entry_point_analysis.get('accepts_arguments', False),
                        'description': entry_point_analysis.get('description', ''),
                        'expected_inputs': entry_point_analysis.get('expected_inputs', []),
                        'expected_outputs': entry_point_analysis.get('expected_outputs', [])
                    })
            except:
                logger.warning(f"Could not parse LLM response for entry point analysis: {file['path']}")
        
        return entry_points
    
    def _analyze_workflows(self, analysis_files, entry_points):
        """Analyze workflows based on entry points"""
        workflows = []
        
        for entry_point in entry_points:
            # Get the entry point file
            entry_file = next((f for f in analysis_files if f['path'] == entry_point['path']), None)
            if not entry_file:
                continue
            
            # Analyze the workflow
            prompt = f"""
            Analyze the following code to identify a complete workflow. This is identified as an entry point.
            
            Entry point file: {entry_file['path']}
            Entry point description: {entry_point['description']}
            
            ```
            {entry_file['content']}
            ```
            
            Please provide a JSON response with the following structure:
            {{
                "workflow_name": "<descriptive name for this workflow>",
                "steps": [
                    {{
                        "step_number": 1,
                        "name": "<step name>",
                        "description": "<what this step does>",
                        "code_reference": "<function or class responsible>",
                        "inputs": ["<list of inputs>"],
                        "outputs": ["<list of outputs>"],
                        "potential_failures": ["<common failure points>"]
                    }}
                ],
                "execution_flow": "<description of how the steps connect>",
                "estimated_runtime": "<estimated runtime for different data sizes>",
                "resource_requirements": "<memory, CPU, disk space requirements>"
            }}
            
            Focus on identifying the logical steps in the workflow, potential failure points, and resource requirements.
            """
            
            response = self.llm_agent.query(prompt)
            
            try:
                workflow_analysis = json.loads(response)
                workflow_analysis['entry_point'] = entry_point['path']
                workflows.append(workflow_analysis)
            except:
                logger.warning(f"Could not parse LLM response for workflow analysis: {entry_point['path']}")
        
        return workflows
    
    def _analyze_scaling_limitations(self, workflows):
        """Analyze scaling limitations of the workflows"""
        if not workflows:
            return {}
        
        # Combine workflow information for analysis
        workflows_info = json.dumps(workflows, indent=2)
        
        prompt = f"""
        Analyze the following workflows to identify scaling limitations:
        
        {workflows_info}
        
        Please provide a JSON response with the following structure:
        {{
            "data_size_limitations": "<description of data size limitations>",
            "memory_limitations": "<description of memory limitations>",
            "processing_time_limitations": "<description of processing time limitations>",
            "suggested_workarounds": [
                {{
                    "limitation": "<specific limitation>",
                    "workaround": "<suggested workaround>",
                    "implementation_difficulty": "easy/medium/hard"
                }}
            ]
        }}
        
        Focus on identifying bottlenecks and limitations when dealing with larger datasets.
        """
        
        response = self.llm_agent.query(prompt)
        
        try:
            scaling_limitations = json.loads(response)
            return scaling_limitations
        except:
            logger.warning("Could not parse LLM response for scaling limitations analysis")
            return {}
    
    def _analyze_bottlenecks(self, workflows):
        """Analyze potential bottlenecks in the workflows"""
        if not workflows:
            return []
        
        # Combine workflow information for analysis
        workflows_info = json.dumps(workflows, indent=2)
        
        prompt = f"""
        Analyze the following workflows to identify potential bottlenecks:
        
        {workflows_info}
        
        Please provide a JSON response with a list of bottlenecks with the following structure:
        [
            {{
                "location": "<specific step or function>",
                "description": "<description of the bottleneck>",
                "impact": "<impact on overall performance>",
                "potential_solutions": ["<list of potential solutions>"]
            }}
        ]
        
        Focus on identifying performance bottlenecks that would impact large dataset processing.
        """
        
        response = self.llm_agent.query(prompt)
        
        try:
            bottlenecks = json.loads(response)
            return bottlenecks
        except:
            logger.warning("Could not parse LLM response for bottlenecks analysis")
            return []
