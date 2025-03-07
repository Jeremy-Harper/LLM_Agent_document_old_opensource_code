# LLM Code Documentation System

A system that uses LLMs to automatically document GitHub repositories, with a focus on legacy bioinformatics tools and packages.

## Overview

This system addresses a common problem in bioinformatics: legacy packages with minimal documentation that are still widely used. By applying LLM technology, it can:

1. Analyze repository structure and code
2. Identify key workflows and processing steps
3. Document output files and their contents
4. Create comprehensive user guides
5. Help identify scaling limitations and strategies

## Features

- **Repository Analysis**: Automatically clone and analyze GitHub repositories
- **Workflow Documentation**: Identify and document key processing workflows
- **Output File Analysis**: Document the purpose and structure of output files
- **Scaling Guide Generation**: Identify potential bottlenecks and suggest scaling strategies
- **Code Documentation**: Add meaningful comments and explanations to code
- **Troubleshooting Guide**: Create guides for common issues and solutions

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/llm-code-documentation.git
cd llm-code-documentation

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env to add your OpenAI API key
```

## Usage

```bash
# Basic usage
python main.py --repo-url https://github.com/example/repo.git --output-dir ./output

# Additional options
python main.py --repo-url https://github.com/example/repo.git --output-dir ./output --model gpt-4 --temp 0.2 --skip-clone
```

## Command Line Arguments

- `--repo-url`: URL of the GitHub repository to document (required)
- `--output-dir`: Directory to save documentation (default: ./output)
- `--api-key`: OpenAI API key (can also be set in .env file)
- `--model`: OpenAI model to use (default: gpt-4)
- `--temp`: Temperature for LLM generation (default: 0.2)
- `--skip-clone`: Skip cloning if repository already exists locally

## Example

Documenting a bioinformatics package:

```bash
python main.py --repo-url https://github.com/broadinstitute/inferCNV.git --output-dir ./inferCNV-docs
```

## Output Structure

The system generates documentation in the following structure:

```
output/
├── README.md
├── docs/
│   ├── index.md
│   ├── installation.md
│   ├── scaling.md
│   ├── troubleshooting.md
│   ├── code/
│   │   └── [code documentation files]
│   ├── workflows/
│   │   └── [workflow documentation files]
│   └── outputs/
│       └── [output file documentation files]
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License for personal use, see License for commercial.
