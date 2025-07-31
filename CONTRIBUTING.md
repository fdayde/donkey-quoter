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
- **Style**: Code formatting and linting handled by Ruff
- **Documentation**: Add docstrings to new functions

### ✅ Before Submitting

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Setup pre-commit hooks (required)
pre-commit install

# Run all checks
pre-commit run --all-files

# Format and lint your code
ruff check src/ --fix
ruff format src/
```

### 🎨 Generate Haikus

To regenerate haikus using Claude API:

```bash
# Test with dry run (no API calls)
python scripts/regenerate_haikus.py --dry-run

# Generate missing haikus only
python scripts/regenerate_haikus.py

# Regenerate ALL haikus
python scripts/regenerate_haikus.py --regenerate-all

# Test with limited quotes
python scripts/regenerate_haikus.py --limit 5
```

**Note**: Requires `ANTHROPIC_API_KEY` in `.env` file.

### 📋 Pull Request Checklist

- [ ] Code follows project style (Ruff for formatting and linting)
- [ ] Functions have clear docstrings
- [ ] No code duplication (DRY principle)
- [ ] Changes are focused and minimal (KISS principle)
- [ ] Pre-commit checks pass
- [ ] Manual testing completed

### 📖 Contributing Quotes

We welcome quote suggestions to enrich our collection!

**🎯 Quote Submission Guidelines**:
- Provide both French and English translations
- Choose appropriate category (classic, personal, humorous)
- Ensure quotes are inspiring, meaningful, or thought-provoking
- Verify author attribution when possible

**📝 How to Submit**:
1. Use our [Quote Submission Template](https://github.com/fdayde/donkey-quoter/issues/new?template=quote_submission.yml)
2. Fill in all required fields (text, author, category)
3. Wait for maintainer review and approval

**✅ What Makes a Good Quote**:
- Universal wisdom or insight
- Clear, concise language
- Appropriate for all audiences
- Original or properly attributed

### 🚀 Quick Fixes Welcome

- Typos in documentation
- Bug fixes with clear explanations
- Performance improvements
- Translation updates
- Quote suggestions via [Quote Submission Form](https://github.com/fdayde/donkey-quoter/issues/new?template=quote_submission.yml)

### 💬 Questions?
Open an issue and we'll help!

Remember: Simple, clean, and functional code is always preferred over complex solutions.
