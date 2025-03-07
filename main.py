# main.py
import os
import argparse
import logging
from dotenv import load_dotenv
from src.repository_handler import RepositoryHandler
from src.documentation_generator import DocumentationGenerator
from src.workflow_analyzer import WorkflowAnalyzer
from src.output_analyzer import OutputAnalyzer
from src.documentation_publisher import DocumentationPublisher

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("documentation_system.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def parse_arguments():
    parser = argparse.ArgumentParser(description='LLM-powered code documentation system')
    parser.add_argument('--repo-url', type=str, required=True, help='GitHub repository URL')
    parser.add_argument('--output-dir', type=str, default='./output', help='Output directory for documentation')
    parser.add_argument('--api-key', type=str, help='OpenAI API key (optional, can use environment variable)')
    parser.add_argument('--model', type=str, default='gpt-4', help='OpenAI model to use')
    parser.add_argument('--temp', type=float, default=0.2, help='Temperature for LLM generation')
    parser.add_argument('--skip-clone', action='store_true', help='Skip cloning if repository already exists locally')
    return parser.parse_args()

def main():
    args = parse_arguments()
    
    # Use API key from arguments or environment variable
    api_key = args.api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("No OpenAI API key provided. Set OPENAI_API_KEY environment variable or use --api-key")
        return
    
    try:
        # Clone and analyze repository
        repo_handler = RepositoryHandler(args.repo_url, args.skip_clone)
        repo_path = repo_handler.clone_repository()
        repo_structure = repo_handler.analyze_repository_structure()
        
        # Analyze workflow and code
        workflow_analyzer = WorkflowAnalyzer(repo_path, api_key, args.model, args.temp)
        workflow_analysis = workflow_analyzer.analyze_workflow()
        
        # Analyze outputs if they exist
        output_analyzer = OutputAnalyzer(repo_path, api_key, args.model, args.temp)
        output_analysis = output_analyzer.analyze_outputs()
        
        # Generate documentation
        documentation_generator = DocumentationGenerator(
            repo_path, 
            repo_structure, 
            workflow_analysis, 
            output_analysis,
            api_key, 
            args.model, 
            args.temp
        )
        documentation = documentation_generator.generate_documentation()
        
        # Publish documentation
        publisher = DocumentationPublisher(args.output_dir, repo_path)
        publisher.publish_documentation(documentation)
        
        logger.info(f"Documentation successfully generated and saved to {args.output_dir}")
        
    except Exception as e:
        logger.error(f"Error in documentation process: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()
