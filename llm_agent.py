# src/llm_agent.py
import os
import logging
import json
import time
from openai import OpenAI

logger = logging.getLogger(__name__)

class LLMAgent:
    def __init__(self, api_key, model="gpt-4", temperature=0.2):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.client = OpenAI(api_key=api_key)
        self.max_retries = 3
        self.retry_delay = 5  # seconds
        
    def query(self, prompt, max_tokens=4000):
        """Query the LLM with a prompt"""
        logger.debug(f"Querying LLM with prompt: {prompt[:100]}...")
        
        for attempt in range(self.max_retries):
            try:
                # Make API call to OpenAI
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=self.temperature,
                    max_tokens=max_tokens
                )
                
                # Extract and return content
                content = response.choices[0].message.content
                return content
                
            except Exception as e:
                logger.warning(f"Error querying LLM (attempt {attempt+1}/{self.max_retries}): {str(e)}")
                if attempt < self.max_retries - 1:
                    logger.info(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    logger.error("Maximum retry attempts reached. Raising exception.")
                    raise
    
    def analyze_code(self, file_path, code_content):
        """Analyze code file and generate documentation"""
        prompt = f"""
        Analyze the following code file and generate comprehensive documentation:
        
        File: {file_path}
        
        ```
        {code_content}
        ```
        
        Please provide a JSON response with the following structure:
        {{
            "purpose": "<purpose of this file>",
            "dependencies": ["<list of dependencies>"],
            "functions": [
                {{
                    "name": "<function name>",
                    "purpose": "<purpose of this function>",
                    "parameters": [
                        {{
                            "name": "<parameter name>",
                            "type": "<parameter type>",
                            "description": "<parameter description>"
                        }}
                    ],
                    "returns": {{
                        "type": "<return type>",
                        "description": "<description of return value>"
                    }},
                    "example": "<example usage>"
                }}
            ],
            "classes": [
                {{
                    "name": "<class name>",
                    "purpose": "<purpose of this class>",
                    "attributes": [
                        {{
                            "name": "<attribute name>",
                            "type": "<attribute type>",
                            "description": "<attribute description>"
                        }}
                    ],
                    "methods": [
                        {{
                            "name": "<method name>",
                            "purpose": "<purpose of this method>",
                            "parameters": [
                                {{
                                    "name": "<parameter name>",
                                    "type": "<parameter type>",
                                    "description": "<parameter description>"
                                }}
                            ],
                            "returns": {{
                                "type": "<return type>",
                                "description": "<description of return value>"
                            }}
                        }}
                    ]
                }}
            ],
            "globals": [
                {{
                    "name": "<global variable name>",
                    "type": "<variable type>",
                    "description": "<variable description>"
                }}
            ],
            "notes": "<additional notes or caveats>"
        }}
        
        Focus on providing comprehensive and accurate documentation for the code.
        """
        
        response = self.query(prompt)
        
        try:
            return json.loads(response)
        except:
            logger.warning(f"Could not parse LLM response for code analysis: {file_path}")
            return {
                "purpose": "Could not analyze code file.",
                "dependencies": [],
                "functions": [],
                "classes": [],
                "globals": [],
                "notes": "Error during analysis."
            }
            
    def add_inline_comments(self, file_path, code_content):
        """Add inline comments to code"""
        prompt = f"""
        Add inline comments to the following code file:
        
        File: {file_path}
        
        ```
        {code_content}
        ```
        
        Please provide the code with comprehensive inline comments that explain:
        1. What each section of code does
        2. Why certain approaches were taken
        3. Potential edge cases or limitations
        4. Important variables and their purpose
        
        Do not change the functionality of the code, only add comments.
        Return only the code with added comments, no explanations outside the code.
        """
        
        response = self.query(prompt)
        
        # Extract code from response if needed
        if "```" in response:
            code_blocks = response.split("```")
            if len(code_blocks) >= 3:
                # Extract the code block (usually the second block)
                for i in range(1, len(code_blocks), 2):
                    if code_blocks[i].strip().lower().startswith(('python', 'r', 'bash', 'sh')):
                        return code_blocks[i+1].strip()
                return code_blocks[1].strip()
            return response
        else:
            return response
