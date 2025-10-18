# Zaman AI Assistant

An intelligent AI assistant specializing in Islamic finance and personal financial management.

## Features

- 🤖 Multi-agent system for specialized financial advice
- 🎯 Goal setting and tracking
- 📊 Spending analytics and insights
- 🔍 Product recommendations
- 🗣️ Voice interface
- 📝 Islamic finance knowledge base
- 📈 Peer comparison
- 🔒 Secure and privacy-focused

## Tech Stack

### Backend
- FastAPI
- PostgreSQL
- MongoDB
- Redis
- OpenAI GPT-4
- Pinecone/ChromaDB
- PyTorch
- Scikit-learn

### Frontend
- Next.js 14
- React
- TailwindCSS
- TypeScript
- Zustand
- React Query

## Getting Started

1. Clone the repository
2. Copy `.env.example` to `.env` and fill in your credentials
3. Install dependencies:
   ```bash
   # Backend
   pip install -r requirements.txt
   
   # Frontend
   cd frontend && npm install
   ```

4. Run the development servers:
   ```bash
   # Backend
   uvicorn backend.main:app --reload
   
   # Frontend
   cd frontend && npm run dev
   ```

## Docker Deployment

```bash
docker-compose up -d
```

## Documentation

- [API Documentation](docs/API.md)
- [Architecture Overview](docs/ARCHITECTURE.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Agent System](docs/AGENTS.md)

## Contributing

Please read our [Contributing Guidelines](CONTRIBUTING.md) before submitting a Pull Request.

## License

MIT License - see the [LICENSE](LICENSE) file for details.