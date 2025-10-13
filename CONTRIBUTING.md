# Contributing to MorningBrief

Thank you for your interest in contributing to MorningBrief! This document provides guidelines for contributing to the project.

## 🚀 Getting Started

### Prerequisites
- Python 3.13+
- Git
- OpenAI API key
- News API key (from NewsAPI.org)
- Telegram Bot Token (from @BotFather)

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/mlchelCar/brifing.git
   cd brifing
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. **Run Tests**
   ```bash
   python test_personalized_briefings.py
   python test_scheduled_delivery.py
   ```

## 🛠️ Development Guidelines

### Code Style
- Follow PEP 8 Python style guidelines
- Use type hints where appropriate
- Write descriptive commit messages
- Add docstrings to functions and classes

### Project Structure
```
brifing/
├── app/
│   ├── config.py          # Configuration settings
│   ├── database.py        # Database connection
│   ├── main.py           # FastAPI application
│   ├── models.py         # Database models
│   ├── routes/           # API routes
│   └── services/         # Business logic
├── tests/                # Test files
├── requirements.txt      # Dependencies
└── README.md            # Project documentation
```

## 🐛 Reporting Issues

### Bug Reports
Please include:
- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error messages/logs

### Feature Requests
Please include:
- Clear description of the feature
- Use case and benefits
- Possible implementation approach

## 🔄 Pull Request Process

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Write clean, documented code
   - Add tests for new functionality
   - Update documentation if needed

3. **Test Your Changes**
   ```bash
   python test_personalized_briefings.py
   python test_scheduled_delivery.py
   ```

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

5. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

## 📄 License

By contributing to MorningBrief, you agree that your contributions will be licensed under the MIT License.

## 🙋‍♂️ Getting Help

- **Documentation**: Check README.md and docs/
- **Issues**: Search existing GitHub issues
- **Questions**: Use GitHub Discussions
- **Contact**: Open an issue for project-related questions

Thank you for contributing to MorningBrief! 🎉
