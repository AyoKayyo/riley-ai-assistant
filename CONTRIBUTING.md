# Contributing to Riley AI Assistant

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Development Setup

1. Fork and clone the repository
2. Set up Python environment:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
3. Install Ollama and download models:
```bash
ollama pull llama3.1:8b
ollama pull qwen2.5-coder:7b
```

## Code Style

- Follow PEP 8 for Python code
- Use meaningful variable names
- Add docstrings to functions and classes
- Keep functions focused and concise

## Commit Messages

Use conventional commits format:
```
type(scope): description

[optional body]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(ui): Add dark mode toggle
fix(agent): Resolve memory leak in conversation history
docs(readme): Update installation instructions
```

## Pull Request Process

1. Create a feature branch: `git checkout -b feat/your-feature`
2. Make your changes
3. Test thoroughly
4. Commit with conventional commit messages
5. Push and create a pull request
6. Wait for review

## Testing

- Add tests for new features
- Ensure existing tests pass
- Run: `pytest tests/`

## Questions?

Open an issue for discussion before starting major work.
