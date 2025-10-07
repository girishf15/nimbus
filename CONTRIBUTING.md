# Contributing to Nimbus - A Document Mind

Thank you for your interest in contributing to Nimbus! We welcome contributions from the community and are grateful for any help you can provide in making this Document Mind even smarter.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Pull Request Process](#pull-request-process)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Features](#suggesting-features)

## 📜 Code of Conduct

This project adheres to a Code of Conduct that all contributors are expected to follow. Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.

## 🤝 How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce** the issue
- **Expected behavior** vs. **actual behavior**
- **Screenshots** if applicable
- **Environment details** (OS, Python version, etc.)
- **Error messages** or logs

### Suggesting Features

Feature suggestions are tracked as GitLab issues. When suggesting a feature:

- **Use a clear title** describing the feature
- **Provide detailed explanation** of the feature and its benefits
- **Explain why this would be useful** to most users
- **List alternatives** you've considered

### Code Contributions

1. **Fork the repository** and create a branch for your feature
2. **Write clear, commented code** following our coding standards
3. **Add or update tests** as needed
4. **Update documentation** to reflect changes
5. **Submit a pull request** with a clear description

## 🛠️ Development Setup

### Prerequisites

- Python 3.12 or higher
- Docker and Docker Compose
- Ollama with required models
- Git

### Setup Steps

1. **Clone your fork:**
```bash
git clone https://github.com/YOUR_USERNAME/nimbus.git
cd nimbus
```

2. **Create virtual environment:**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Start database:**
```bash
docker compose up -d
```

5. **Copy environment configuration:**
```bash
cp .env.example .env
# Edit .env with your settings
```

6. **Run the application:**
```bash
python app.py
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=apps --cov-report=html

# Run specific test file
pytest tests/test_chat.py
```

## 📝 Coding Standards

### Python Style Guide

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Use meaningful variable and function names
- Maximum line length: 120 characters
- Use type hints where applicable

### Code Formatting

We use the following tools for code quality:

```bash
# Format code with black
black .

# Check style with flake8
flake8 apps/

# Sort imports with isort
isort .
```

### Documentation

- Add docstrings to all functions, classes, and modules
- Use Google-style docstrings
- Update README.md for user-facing changes
- Comment complex logic

Example docstring:
```python
def parse_document(file_path: str, parser_type: str = 'pymupdf') -> str:
    """
    Parse a document and extract text content.
    
    Args:
        file_path: Path to the document file
        parser_type: Type of parser to use (pymupdf, pdfplumber, ocr)
        
    Returns:
        Extracted text from the document
        
    Raises:
        ValueError: If parser_type is not supported
        FileNotFoundError: If file_path does not exist
    """
    pass
```

### Commit Messages

Follow conventional commit format:

```
type(scope): subject

body

footer
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Example:
```
feat(chat): add support for streaming responses

Implement streaming API for Ollama chat completions to improve
user experience with real-time response generation.

Closes #123
```

## 🔄 Pull Request Process

1. **Update documentation** for any user-facing changes
2. **Add tests** for new functionality
3. **Ensure all tests pass** locally before submitting
4. **Update CHANGELOG.md** with your changes
5. **Reference related issues** in the PR description
6. **Request review** from maintainers

### PR Checklist

- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] Tests added/updated and passing
- [ ] No new warnings introduced
- [ ] CHANGELOG.md updated

### PR Review Process

- Maintainers will review your PR within 5-7 days
- Address any requested changes
- Once approved, a maintainer will merge your PR
- Your contribution will be recognized in the release notes

## 🐛 Reporting Bugs

### Before Submitting

- Check the [issue tracker](https://gitlab.com/YOUR_ORG/nimbus/-/issues)
- Check if the issue is already fixed in the latest version
- Collect debugging information

### Bug Report Template

```markdown
**Description:**
A clear description of the bug

**Steps to Reproduce:**
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior:**
What should happen

**Actual Behavior:**
What actually happens

**Environment:**
- OS: [e.g., Ubuntu 22.04]
- Python version: [e.g., 3.12.0]
- Nimbus version: [e.g., 1.0.0]
- Ollama version: [e.g., 0.1.17]

**Logs/Screenshots:**
Attach relevant logs or screenshots

**Additional Context:**
Any other information that might be helpful
```

## 💡 Suggesting Features

### Feature Request Template

```markdown
**Feature Description:**
Clear description of the proposed feature

**Problem it Solves:**
What problem does this feature address?

**Proposed Solution:**
How should this feature work?

**Alternatives Considered:**
What other approaches did you consider?

**Additional Context:**
Mockups, examples, or relevant resources
```

## 🎯 Areas for Contribution

We especially welcome contributions in these areas:

### High Priority
- Performance optimizations
- Additional document parsers
- Test coverage improvements
- Documentation enhancements

### Medium Priority
- UI/UX improvements
- Additional embedding models support
- Export/import functionality
- Internationalization

### Good First Issues
- Look for issues labeled `good first issue`
- Documentation improvements
- Code cleanup and refactoring
- Adding type hints

## 📚 Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Ollama Documentation](https://github.com/ollama/ollama)
- [pgvector Documentation](https://github.com/pgvector/pgvector)

## 🙏 Recognition

Contributors will be recognized in:
- CHANGELOG.md for each release
- README.md contributors section
- Project documentation

Thank you for contributing to Nimbus - A Document Mind! 🧠📄
