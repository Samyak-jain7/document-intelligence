# Document Intelligence Pipeline

A full-stack RAG (Retrieval-Augmented Generation) platform for uploading PDF documents, extracting text, and chatting with them using AI-powered semantic search.

![Document Intelligence](https://img.shields.io/badge/AI-RAG-blue) ![Python](https://img.shields.io/badge/Python-3.11-green) ![Next.js](https://img.shields.io/badge/Next.js-14-black) ![FastAPI](https://img.shields.io/badge/FastAPI-0.109-orange) ![CI](https://github.com/Samyak-jain7/document-intelligence/actions/workflows/ci.yml/badge.svg)

## 🌟 Features

- **PDF Upload & Processing**: Drag-and-drop interface for uploading PDF documents
- **Text Extraction**: Extracts text and tables from PDFs using pdfplumber and PyPDF2
- **Semantic Chunking**: Intelligently splits documents into overlapping chunks for better retrieval
- **Vector Embeddings**: Generates OpenAI embeddings for semantic search
- **RAG Chat**: Ask questions in natural language and get answers with citations
- **Source Tracking**: See which documents and pages were used to generate answers
- **Document Management**: View, search, and manage your uploaded documents

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend                              │
│                     (Next.js 14)                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  Upload UI  │  │  Chat UI    │  │  Document   │         │
│  │             │  │             │  │  List       │         │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘         │
└─────────┼────────────────┼────────────────┼─────────────────┘
          │                │                │
          └────────────────┴────────────────┘
                           │
                    REST API (8000)
                           │
┌──────────────────────────┼──────────────────────────────────┐
│                     Backend (FastAPI)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   Upload      │  │   Chat       │  │   Search     │    │
│  │   Endpoint    │  │   Endpoint   │  │   Endpoint   │    │
│  └──────┬────────┘  └──────┬────────┘  └──────┬────────┘    │
│         │                   │                   │             │
│  ┌──────┴──────────────────┴───────────────────┴────────┐   │
│  │                   Services Layer                      │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐│   │
│  │  │   PDF     │ │  Text    │ │ Embedding│ │  LLM   ││   │
│  │  │ Processor │ │ Chunker  │ │ Service  │ │Service ││   │
│  │  └──────────┘ └──────────┘ └──────────┘ └────────┘│   │
│  └─────────────────────────┬───────────────────────────┘   │
│                             │                               │
│  ┌─────────────────────────┴───────────────────────────┐   │
│  │                   Vector Store (ChromaDB)          │   │
│  │         + Document Store (JSON Persistence)         │   │
│  └────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
             ┌────────────────────────┐
             │     OpenAI API         │
             │  (Embeddings + GPT-4)   │
             └────────────────────────┘
```

## 📁 Project Structure

```
document-intelligence/
├── backend/
│   ├── app/
│   │   ├── api/           # API route handlers
│   │   │   ├── documents.py
│   │   │   ├── chat.py
│   │   │   └── health.py
│   │   ├── core/          # Configuration management
│   │   │   └── config.py
│   │   ├── models/        # Pydantic request/response schemas
│   │   │   └── schemas.py
│   │   ├── services/      # Business logic layer
│   │   │   ├── pdf_processor.py
│   │   │   ├── text_chunker.py
│   │   │   ├── embedding_service.py
│   │   │   ├── vector_store.py
│   │   │   ├── llm_service.py
│   │   │   ├── document_store.py
│   │   │   └── processing_service.py
│   │   └── main.py         # FastAPI application entry
│   ├── uploads/            # Uploaded PDF files
│   ├── chromadb/          # ChromaDB persistent data
│   ├── requirements.txt   # Python dependencies
│   ├── Dockerfile         # Multi-stage production build
│   └── .env.example       # Environment variable template
├── frontend/
│   ├── app/               # Next.js 14 app directory
│   │   ├── page.tsx       # Main page
│   │   └── layout.tsx     # Root layout
│   ├── components/       # React components
│   │   ├── ui/            # Radix UI primitives
│   │   ├── chat-interface.tsx
│   │   ├── document-list.tsx
│   │   ├── header.tsx
│   │   └── upload-zone.tsx
│   ├── lib/               # Utilities and API client
│   │   ├── api.ts         # TypeScript API client
│   │   ├── store.ts       # Zustand state store
│   │   └── utils.ts       # Helper functions
│   ├── package.json
│   ├── next.config.js
│   ├── Dockerfile         # Multi-stage production build
│   └── .env.example
├── .github/
│   └── workflows/
│       └── ci.yml          # GitHub Actions CI/CD
├── docker-compose.yml      # Full stack orchestration
├── .env.example            # Root env vars template
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose v2+
- OpenAI API Key ([Get one here](https://platform.openai.com/api-keys))

### 1. Clone the Repository

```bash
git clone https://github.com/Samyak-jain7/document-intelligence.git
cd document-intelligence
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Required
OPENAI_API_KEY=sk-your-api-key-here

# Optional - with defaults
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
MAX_FILE_SIZE_MB=50
ENVIRONMENT=production
BACKEND_PORT=8000
FRONTEND_PORT=3000
```

### 3. Start with Docker Compose

```bash
# Build and start all services
docker-compose up --build

# Run in detached mode
docker-compose up --build -d
```

The application will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### 4. Local Development

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
uvicorn app.main:app --reload --port 8000
```

#### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
# Set NEXT_PUBLIC_API_URL=http://localhost:8000 in .env.local
npm run dev
```

## 📖 API Documentation

### Health Check

```bash
GET /health
```

Response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "chroma_connected": true,
  "openai_configured": true
}
```

### Upload Document

```bash
POST /documents/upload
Content-Type: multipart/form-data

file: <PDF file>
```

Response:
```json
{
  "document_id": "uuid",
  "filename": "document.pdf",
  "status": "pending",
  "message": "Document uploaded successfully. Processing started.",
  "file_size": 1024000
}
```

### Get Document Status

```bash
GET /documents/status/{document_id}
```

### List Documents

```bash
GET /documents/?limit=100&offset=0
```

### Delete Document

```bash
DELETE /documents/{document_id}
```

### Chat (RAG)

```bash
POST /chat/
Content-Type: application/json

{
  "query": "What is the main topic of the document?",
  "document_ids": ["optional", "filter", "by", "ids"],
  "top_k": 5
}
```

Response:
```json
{
  "answer": "Based on the documents...",
  "sources": [
    {
      "chunk_id": "...",
      "content": "...",
      "document_id": "...",
      "filename": "doc.pdf",
      "page_number": 1
    }
  ],
  "conversation_id": "uuid"
}
```

### Semantic Search

```bash
POST /chat/search
Content-Type: application/json

{
  "query": "search term",
  "document_ids": null,
  "top_k": 10
}
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OPENAI_API_KEY` | OpenAI API key for embeddings and chat | - | **Yes** |
| `OPENAI_MODEL` | GPT model for chat responses | `gpt-4o-mini` | No |
| `OPENAI_EMBEDDING_MODEL` | Model for generating embeddings | `text-embedding-3-small` | No |
| `CHUNK_SIZE` | Target size for text chunks (characters) | `1000` | No |
| `CHUNK_OVERLAP` | Overlap between chunks (characters) | `200` | No |
| `MAX_FILE_SIZE_MB` | Maximum upload size in MB | `50` | No |
| `ENVIRONMENT` | Runtime environment | `development` | No |
| `DEBUG` | Enable debug mode | `false` | No |
| `HOST` | Backend server host | `0.0.0.0` | No |
| `PORT` | Backend server port | `8000` | No |
| `BACKEND_PORT` | Host port for backend | `8000` | No |
| `FRONTEND_PORT` | Host port for frontend | `3000` | No |
| `FRONTEND_URL` | Frontend URL for CORS | `http://localhost:3000` | No |
| `CHROMA_DB_PATH` | ChromaDB data directory | `/app/chromadb` | No |
| `UPLOAD_DIR` | File upload directory | `/app/uploads` | No |
| `APP_API_KEY` | Optional API key for endpoint authentication | - | No |

### Chunking Configuration

The text chunking behavior can be tuned via environment variables:

- `CHUNK_SIZE`: Target number of characters per chunk (100-4000)
- `CHUNK_OVERLAP`: Number of overlapping characters between chunks (0-1000)

Larger chunks capture more context but may reduce retrieval precision. Overlap helps maintain context across chunk boundaries.

## 🐛 Troubleshooting

### ChromaDB Connection Issues

If you see "ChromaDB not connected", ensure:
1. The ChromaDB volume is properly mounted in docker-compose
2. There's no permission issue with the data directory

```bash
# Fix permissions
sudo chown -R 1001:1001 backend/chromadb backend/uploads
```

### OpenAI API Errors

If you get API errors:
1. Verify your API key is correct and has available credits
2. Check your OpenAI account has not hit rate limits
3. Ensure the API key has the right permissions

### PDF Processing Fails

- Ensure the PDF is not password-protected
- Try a different PDF if extraction fails
- Check the server logs for specific errors
- Large PDFs may take longer to process

### Docker Build Fails

If the Docker build fails, ensure you have:
- Docker Engine 20.10+
- Docker Compose v2+
- At least 4GB of available RAM

## 🐳 Deployment

### Docker Compose (Production)

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose up --build -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Environment-Specific Configuration

For production, use environment variables or a `.env` file:

```bash
# Production environment
 ENVIRONMENT=production
 DEBUG=false
 OPENAI_API_KEY=sk-prod-key-here
```

## 🔌 Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **ChromaDB**: Vector database for embeddings
- **LangChain**: LLM orchestration
- **pdfplumber**: PDF text extraction
- **PyPDF2**: PDF processing fallback
- **OpenAI**: Embeddings and chat

### Frontend
- **Next.js 14**: React framework with App Router
- **Tailwind CSS**: Utility-first styling
- **Zustand**: State management
- **Radix UI**: UI component primitives
- **React Dropzone**: File uploads

## 📝 License

MIT License - feel free to use this project for personal or commercial purposes.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📧 Contact

For questions or support, please open an issue on GitHub.
