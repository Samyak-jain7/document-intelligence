# Document Intelligence Pipeline

A full-stack RAG (Retrieval-Augmented Generation) platform for uploading PDF documents, extracting text, and chatting with them using AI-powered semantic search.

![Document Intelligence](https://img.shields.io/badge/AI-RAG-blue) ![Python](https://img.shields.io/badge/Python-3.11-green) ![Next.js](https://img.shields.io/badge/Next.js-14-black) ![FastAPI](https://img.shields.io/badge/FastAPI-0.109-orange)

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
│  │   Upload     │  │   Chat       │  │   Search     │    │
│  │   Endpoint   │  │   Endpoint   │  │   Endpoint   │    │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘    │
│         │                 │                  │             │
│  ┌──────┴─────────────────┴──────────────────┴───────┐   │
│  │                   Services Layer                    │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐│   │
│  │  │   PDF     │ │  Text    │ │ Embedding│ │  LLM   ││   │
│  │  │ Processor │ │ Chunker  │ │ Service  │ │Service ││   │
│  │  └──────────┘ └──────────┘ └──────────┘ └────────┘│   │
│  └─────────────────────────┬───────────────────────────┘   │
│                              │                              │
│  ┌──────────────────────────┴───────────────────────────┐  │
│  │                   Vector Store (ChromaDB)             │  │
│  │         + Document Store (JSON Persistence)            │  │
│  └───────────────────────────────────────────────────────┘  │
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
│   │   ├── api/           # API routes
│   │   │   ├── documents.py
│   │   │   ├── chat.py
│   │   │   └── health.py
│   │   ├── core/          # Configuration
│   │   │   └── config.py
│   │   ├── models/        # Pydantic schemas
│   │   │   └── schemas.py
│   │   ├── services/      # Business logic
│   │   │   ├── pdf_processor.py
│   │   │   ├── text_chunker.py
│   │   │   ├── embedding_service.py
│   │   │   ├── vector_store.py
│   │   │   ├── llm_service.py
│   │   │   ├── document_store.py
│   │   │   └── processing_service.py
│   │   └── main.py         # FastAPI app
│   ├── uploads/            # Uploaded files
│   ├── chromadb/           # ChromaDB data
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── app/
│   │   ├── page.tsx        # Main page
│   │   └── layout.tsx      # Root layout
│   ├── components/
│   │   ├── ui/             # UI components
│   │   ├── chat-interface.tsx
│   │   ├── document-list.tsx
│   │   ├── header.tsx
│   │   └── upload-zone.tsx
│   ├── lib/
│   │   ├── api.ts          # API client
│   │   ├── store.ts        # Zustand store
│   │   └── utils.ts        # Utilities
│   ├── package.json
│   ├── tailwind.config.js
│   ├── Dockerfile
│   └── .env.example
├── docker-compose.yml
├── .env.example
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- OpenAI API Key

### 1. Clone the Repository

```bash
git clone https://github.com/Samyak-jain7/document-intelligence.git
cd document-intelligence
```

### 2. Set Environment Variables

Create a `.env` file in the root directory:

```bash
# Get your key from https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

### 3. Start with Docker Compose

```bash
docker-compose up --build
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
uvicorn app.main:app --reload
```

#### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

## 📖 API Documentation

### Health Check

```bash
GET /health
```

Returns the health status of the API and its dependencies.

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
  "message": "Document uploaded successfully",
  "file_size": 1024000
}
```

### Get Document Status

```bash
GET /documents/status/{document_id}
```

### List Documents

```bash
GET /documents/
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

### Backend Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `OPENAI_MODEL` | GPT model for chat | `gpt-4o-mini` |
| `OPENAI_EMBEDDING_MODEL` | Embedding model | `text-embedding-3-small` |
| `ENVIRONMENT` | Environment mode | `development` |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `CHROMA_DB_PATH` | ChromaDB data path | `/app/chromadb` |
| `UPLOAD_DIR` | Upload storage path | `/app/uploads` |
| `MAX_FILE_SIZE_MB` | Max upload size (MB) | `50` |

## 🔌 Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **ChromaDB**: Vector database for embeddings
- **LangChain**: LLM orchestration
- **pdfplumber**: PDF text extraction
- **PyPDF2**: PDF processing fallback
- **OpenAI**: Embeddings and chat

### Frontend
- **Next.js 14**: React framework
- **Tailwind CSS**: Styling
- **Zustand**: State management
- **Radix UI**: UI primitives
- **React Dropzone**: File uploads

## 🐛 Troubleshooting

### ChromaDB Connection Issues

If you see "ChromaDB not connected", ensure:
1. The ChromaDB volume is properly mounted
2. There's no permission issue with the data directory

```bash
# Fix permissions
sudo chown -R 1001:1001 backend/chromadb backend/uploads
```

### OpenAI API Errors

If you get API errors:
1. Verify your API key is correct
2. Check your OpenAI account has available credits
3. Ensure the API key has the right permissions

### PDF Processing Fails

- Ensure the PDF is not password-protected
- Try a different PDF if extraction fails
- Check the server logs for specific errors

## 📝 License

MIT License - feel free to use this project for personal or commercial purposes.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Contact

For questions or support, please open an issue on GitHub.
