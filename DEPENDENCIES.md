# AI Recipe Generator - Dependencies Documentation

## Backend Dependencies (Python)

### Core Framework
- **fastapi**: Modern, fast web framework for building APIs with Python
- **uvicorn**: Lightning-fast ASGI server implementation
- **python-multipart**: Support for form data parsing

### Database
- **sqlalchemy**: SQL toolkit and Object-Relational Mapping (ORM) library
- **psycopg2-binary**: PostgreSQL adapter for Python
- **alembic**: Database migration tool for SQLAlchemy

### Data Validation
- **pydantic**: Data validation and settings management using Python type annotations

### AI/ML Integration
- **google-generativeai**: Google's Generative AI Python SDK for recipe generation

### Configuration & Environment
- **python-dotenv**: Load environment variables from .env file

### HTTP & Network
- **requests**: HTTP library for Python
- **certifi**: Collection of Root Certificates for SSL/TLS verification
- **urllib3**: HTTP library with thread-safe connection pooling

### Development & Testing (Optional)
- **pytest**: Testing framework
- **pytest-asyncio**: Pytest plugin for asyncio support
- **httpx**: HTTP client for testing FastAPI applications

## Frontend Dependencies (Node.js/React)

### Core Framework
- **react**: JavaScript library for building user interfaces
- **react-dom**: React package for working with the DOM
- **react-scripts**: Configuration and scripts for Create React App

### HTTP Client
- **axios**: Promise-based HTTP client for the browser and Node.js

### PDF Export
- **jspdf**: JavaScript PDF generation library
- **html2canvas**: Screenshot library for converting HTML to canvas

### Styling
- **styled-components**: CSS-in-JS library for styling React components

### Testing
- **@testing-library/jest-dom**: Custom Jest matchers for testing DOM elements
- **@testing-library/react**: Testing utilities for React components
- **@testing-library/user-event**: User interaction simulation for testing

### Performance
- **web-vitals**: Library for measuring web performance metrics

## Installation Instructions

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
```

### Frontend Setup
```bash
cd frontend
npm install
```

### Docker Setup (Recommended)
```bash
docker-compose up -d
```

This will automatically install all dependencies in their respective containers.

## Environment Variables Required

### Backend (.env file)
- `DATABASE_URL`: PostgreSQL connection string
- `GEMINI_API_KEY`: Google Gemini API key for recipe generation

### Frontend
- Proxy configuration is handled in package.json
- No additional environment variables required for basic functionality

## Notes

- All dependencies are pinned to specific versions for stability
- The application supports both SQLite (development) and PostgreSQL (production)
- Frontend build process handles all bundling and optimization
- Docker containers include all necessary dependencies and runtime environments
