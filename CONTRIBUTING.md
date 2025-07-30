# Contributing to Donkey Quoter 🫏

Thank you for your interest in contributing!

## How to Contribute

### 🐛 Report a Bug
- Check if already reported in [Issues](https://github.com/fdayde/donkey-quoter/issues)
- Create a new issue with clear reproduction steps

### 💡 Suggest a Feature
- Open an [Issue](https://github.com/fdayde/donkey-quoter/issues/new) with your idea
- Explain the use case and why it would be valuable

### 📝 Submit Code

1. **Fork** the repository
2. **Clone** your fork: `git clone https://github.com/YOUR-USERNAME/donkey-quoter.git`
3. **Create** a feature branch: `git checkout -b feature/your-feature-name`
4. **Make** your changes following our guidelines
5. **Commit** with clear messages: `git commit -m "Add: clear description"`
6. **Push** to your fork: `git push origin feature/your-feature-name`
7. **Open** a Pull Request

### 🎯 Code Guidelines

- **KISS**: Keep it simple - prefer clarity over cleverness
- **DRY**: Don't repeat yourself - extract common logic
- **Modular**: One function = one responsibility
- **PEP8**: Follow Python style guide
- **Documentation**: Add docstrings to new functions

### ✅ Before Submitting

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Setup pre-commit hooks (required)
pre-commit install

# Run all checks
pre-commit run --all-files

# Ensure your code is properly formatted
black src/
isort src/
```

### 📋 Pull Request Checklist

- [ ] Code follows project style (Black, isort, PEP8)
- [ ] Functions have clear docstrings
- [ ] No code duplication (DRY principle)
- [ ] Changes are focused and minimal (KISS principle)
- [ ] Pre-commit checks pass
- [ ] Manual testing completed

### 🚀 Quick Fixes Welcome

- Typos in documentation
- Bug fixes with clear explanations
- Performance improvements
- Translation updates
- Add quotes via [Quote Submission Form](https://github.com/fdayde/donkey-quoter/issues/new?template=quote_submission.yml)

### 💬 Questions?
Open an issue and we'll help!

Remember: Simple, clean, and functional code is always preferred over complex solutions.
