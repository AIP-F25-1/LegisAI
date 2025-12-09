# Contributing to LegisAI

Thank you for your interest in contributing to LegisAI!

## Development Setup

### Prerequisites
- Docker Desktop
- Git
- Code editor (VS Code recommended)

### Getting Started

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd LegisAI
   ```

2. **Start with Docker (Recommended)**
   ```bash
   # Windows
   .\docker-start.ps1
   
   # Linux/Mac
   ./docker-start.sh
   ```

3. **Or run locally**
   ```bash
   # Backend
   cd backend
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   uvicorn main:app --reload
   
   # Frontend
   cd frontend
   npm install
   npm run dev
   ```

## Code Style

- **Python**: Follow PEP 8, use type hints
- **TypeScript/React**: Use ESLint, follow React best practices
- **Commits**: Use clear, descriptive commit messages

## Testing

- Test your changes locally before submitting
- Ensure Docker builds succeed
- Test all affected endpoints

## Pull Request Process

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a PR with a clear description

## Questions?

Open an issue for questions or discussions.

