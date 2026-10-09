# Contributing to AIAS

Thanks for your interest in contributing! Here's how to help.

## Getting Started

1. **Fork the repository**
2. **Clone your fork:** `git clone https://github.com/YOUR_USERNAME/ai-as.git`
3. **Create a branch:** `git checkout -b feature/your-feature-name`
4. **Make your changes**
5. **Push to your fork:** `git push origin feature/your-feature-name`
6. **Create a Pull Request**

---

## Code Style

- **Python:** Follow PEP 8
- **Indentation:** 4 spaces
- **Line length:** 100 characters (soft limit, 120 hard limit)
- **Imports:** Group in order: standard library → third-party → local

---

## Commit Messages

Use clear, descriptive commit messages:

```
feat: Add multi-target tracking
fix: Resolve Arduino connection timeout
refactor: Simplify vision loop logic
docs: Update README with Phase 7 info
test: Add unit tests for config module
```

---

## Pull Request Process

1. Update `CHANGELOG.md` with your changes
2. Ensure all tests pass
3. Update documentation if needed
4. Provide a clear PR description with:
   - What problem does this solve?
   - How does it work?
   - Any breaking changes?

---

## Reporting Bugs

Use the [Bug Report template](.github/ISSUE_TEMPLATE/bug_report.md):
- Clear description
- Steps to reproduce
- Expected vs. actual behavior
- Environment details

---

## Suggesting Features

Use the [Feature Request template](.github/ISSUE_TEMPLATE/feature_request.md):
- Clear description
- Use case / motivation
- Implementation ideas (optional)

---

## Development Setup

```bash
# Clone and setup
git clone https://github.com/YOUR_USERNAME/ai-as.git
cd ai-as
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
pip install -e .  # If packaging

# Run tests
python -m pytest  # (if tests exist)

# Format code
flake8 .
```

---

## Questions?

Open a discussion or issue. We're here to help!

---

**Thank you for contributing!** 🙏
