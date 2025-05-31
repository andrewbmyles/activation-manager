# Contributing to Activation Manager

Thank you for your interest in contributing to Activation Manager! This guide will help you get started.

## 🚀 Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/activation-manager.git`
3. Create a feature branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Run tests: `pytest tests/`
6. Commit your changes: `git commit -m "feat: add your feature"`
7. Push to your fork: `git push origin feature/your-feature-name`
8. Create a Pull Request

## 📝 Code Style

### Python
- Follow PEP 8
- Use type hints for function parameters and returns
- Maximum line length: 100 characters
- Use meaningful variable names

### JavaScript/TypeScript
- Follow the Airbnb Style Guide
- Use TypeScript for all new code
- Prefer functional components with hooks in React

### Example Python Function:
```python
def search_variables(
    query: str,
    top_k: int = 50,
    filter_similar: bool = False
) -> Dict[str, Any]:
    """
    Search for variables using the query.
    
    Args:
        query: The search query string
        top_k: Maximum number of results to return
        filter_similar: Whether to filter similar results
        
    Returns:
        Dictionary containing search results and metadata
    """
    # Implementation here
```

## 🧪 Testing

All new features must include tests:

1. **Unit Tests**: Test individual functions/methods
2. **Integration Tests**: Test component interactions
3. **System Tests**: Test end-to-end workflows

### Running Tests:
```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/unit/test_search.py

# Run with coverage
pytest tests/ --cov=activation_manager
```

## 📋 Commit Message Format

We follow the Conventional Commits specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples:
```
feat(search): add similarity filtering to reduce duplicates

Implemented Jaro-Winkler algorithm to filter similar variables
and reduce redundant search results by up to 98%.

Closes #123
```

## 🔄 Pull Request Process

1. **Before Creating a PR:**
   - Ensure all tests pass
   - Update documentation if needed
   - Add tests for new functionality
   - Rebase on latest main branch

2. **PR Title Format:**
   - Use the same format as commit messages
   - Be clear and descriptive

3. **PR Description Template:**
   ```markdown
   ## Description
   Brief description of changes
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Refactoring
   - [ ] Documentation
   
   ## Testing
   - [ ] Unit tests pass
   - [ ] Integration tests pass
   - [ ] Manual testing completed
   
   ## Checklist
   - [ ] My code follows the project style guidelines
   - [ ] I have added tests for my changes
   - [ ] I have updated documentation as needed
   ```

## 🏗️ Project Structure

```
activation_manager/
├── api/              # API endpoints
├── core/             # Core business logic
├── config/           # Configuration files
├── utils/            # Utility functions
└── tests/            # Test files

src/
├── components/       # React components
├── pages/           # Page components
├── hooks/           # Custom React hooks
├── utils/           # Frontend utilities
└── types/           # TypeScript type definitions
```

## 🐛 Reporting Issues

### Bug Reports Should Include:
- Clear, descriptive title
- Steps to reproduce
- Expected behavior
- Actual behavior
- System information
- Screenshots (if applicable)

### Feature Requests Should Include:
- Clear problem statement
- Proposed solution
- Alternative solutions considered
- Mockups/examples (if applicable)

## 🤝 Code Review Guidelines

### For Authors:
- Keep PRs focused and small
- Respond to feedback constructively
- Update PR based on review comments

### For Reviewers:
- Be constructive and respectful
- Explain the reasoning behind suggestions
- Approve when requirements are met

## 📚 Additional Resources

- [Architecture Documentation](../docs/architecture/README.md)
- [API Documentation](../docs/api/README.md)
- [Deployment Guide](../docs/deployment/README.md)

## ❓ Questions?

If you have questions, please:
1. Check existing documentation
2. Search existing issues
3. Create a new issue with the "question" label

Thank you for contributing! 🎉