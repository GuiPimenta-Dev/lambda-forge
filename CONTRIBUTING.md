# Contributing to Lambda Forge

Thank you for your interest in contributing to Lambda Forge! We welcome contributions of all kinds, including bug fixes, new features, documentation improvements, and discussions.

## Getting Started

1. **Fork the Repository**: Click the "Fork" button at the top of the repository.
2. **Clone Your Fork**:
   ```sh
   git clone https://github.com/GuiPimenta-Dev/lambda-forge.git
   cd lambda-forge
   ```
3. **Create a Branch**:
   ```sh
   git checkout -b feature-or-bugfix-name
   ```
4. **Install Dependencies**:
   ```sh
   pip install -r requirements.txt
   ```
5. **Run Tests**:
   ```sh
   pytest
   ```

## Contribution Guidelines

### Reporting Issues
- Before opening a new issue, check the [existing issues](https://github.com/lambda-forge/lambda-forge/issues).
- Provide clear steps to reproduce the issue.
- If applicable, include error messages and logs.

### Adding a New Feature
- Open an issue first to discuss the idea.
- Follow the project’s existing architecture and conventions.
- Write unit tests for new functionality.
- Update the documentation if needed.

### Submitting a Pull Request
1. **Ensure your code is formatted**:
   ```sh
   black .
   isort .
   ```
2. **Run all tests before submitting**:
   ```sh
   pytest
   ```
3. **Push your branch**:
   ```sh
   git push origin feature-or-bugfix-name
   ```
4. **Open a Pull Request**:  
   - Go to the repository and create a new Pull Request (PR).
   - Describe the changes and reference any related issues.
   - Ensure all checks pass before requesting a review.

## Code Style
- Follow [PEP 8](https://peps.python.org/pep-0008/) for Python code.
- Use `black` and `isort` for consistent formatting.

