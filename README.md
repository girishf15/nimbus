<div align="center">
  <img src="static/nimbus-logo.png" alt="Nimbus - A Document Mind" width="400"/>
</div>

# Nimbus - A Document Mind 🧠

> **Intelligent Document Processing with RAG-Powered Conversations**

Nimbus is your Document Mind - a sophisticated AI system that reads, understands, and converses about your documents using advanced RAG (Retrieval-Augmented Generation) technology. Transform any collection of documents into an intelligent knowledge base that you can chat with naturally. Built with Flask, PostgreSQL with pgvector, and Ollama for local LLM inference.

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-green.svg)](https://flask.palletsprojects.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🌟 Why Choose Nimbus?

**Nimbus acts as your Document Mind** - it doesn't just store your documents, it truly understands them. Ask questions in natural language and get intelligent answers backed by your actual content, with full source citations.

## 🚀 Features

### 🤖 **Advanced RAG System**
- **Multi-Model Embeddings**: Support for multiple embedding models simultaneously (nomic-embed-text, mxbai-embed-large, all-minilm)
- **Intelligent Retrieval**: Query multiple embedding models and merge results with deduplication
- **Context-Aware Responses**: LLM only answers from your documents, preventing hallucinations
- **Source Citations**: Track which documents were used to generate each answer

### 📄 **Powerful Document Processing**
- **Multiple Parsers**: 
  - PyMuPDF (fast, standard PDFs)
  - PDFPlumber (tables and structured data)
  - Unstructured (advanced layout detection)
  - **OCR Parser** (scanned documents, images)
  - **OCR + Vision** (AI-powered image description using LLaVA)
  
- **Smart Text Splitting**:
  - Recursive Character Splitter (balanced chunks)
  - Token-based Splitter (LLM-optimized)
  - **Semantic Splitter** (embedding-based, natural boundaries)

### 💬 **Rich Chat Interface**
- **Session Management**: Organize conversations by topic
- **Persistent History**: All chats saved to database
- **Multi-Model Support**: Switch between different LLMs
- **Conversation History**: Maintains context across messages
- **Sidebar Navigation**: Quick access to all chat sessions

### 👥 **User Management**
- Role-based access control (Admin/User)
- Secure password hashing with bcrypt
- User creation, deletion, and password management
- Per-user document isolation

### 🎨 **Modern UI/UX**
- Custom Nimbus branding with professional logos
- Responsive Bootstrap 5 design
- Dark/light theme support
- Real-time status updates
- Drag-and-drop file upload
- Document preview functionality

---

## 🧠 How Nimbus Works as Your Document Mind

Nimbus transforms your documents into an intelligent, searchable knowledge base:

1. **📄 Ingestion**: Upload documents in various formats (PDF, DOCX, TXT, etc.)
2. **🔍 Understanding**: Advanced parsers extract text, including OCR for scanned documents
3. **✂️ Chunking**: Smart text splitting creates semantically meaningful pieces
4. **🧭 Vectorization**: Multiple embedding models create rich vector representations
5. **💬 Conversation**: Chat naturally - Nimbus retrieves relevant information and responds intelligently
6. **📋 Citation**: Every answer includes source references to maintain trust and accuracy

## 🏗️ Architecture

```
                    🧠 Nimbus Document Mind
                          ┌─────────────────┐
                          │   Web Browser   │
                          └────────┬────────┘
                                   │
                          ┌────────▼────────────────────────────────────┐
                          │         Flask Application (Document Mind)    │
                          │  ┌──────────┬──────────┬──────────────┐    │
                          │  │   Chat   │Documents │    Users     │    │
                          │  │ Blueprint│Blueprint │  Blueprint   │    │
                          │  └──────────┴──────────┴──────────────┘    │
                          └────────┬────────────────────────────────────┘
                                   │
                              ┌────┴────┐
                              │         │
                          ┌───▼──┐  ┌──▼──────────┐
                          │Ollama│  │ PostgreSQL  │
                          │ LLMs │  │  + pgvector │
                          └──────┘  └─────────────┘
                         💭 AI Mind   🧠 Memory Bank
```

**Tech Stack:**
- **Backend**: Flask (Python)
- **Database**: PostgreSQL 16 + pgvector extension
- **LLM/Embeddings**: Ollama (local inference)
- **Document Processing**: PyMuPDF, PDFPlumber, Tesseract OCR, Pillow
- **Text Splitting**: LangChain, custom implementations
- **Frontend**: Bootstrap 5, vanilla JavaScript
- **Containerization**: Docker & Docker Compose

---

## 🚀 Quick Start

### Prerequisites

- **Docker** and **Docker Compose** installed
- **Python 3.12+** (if running without Docker)
- **Ollama** installed and running with desired models

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd nimbus
```

2. **Choose your deployment method**

**Option A: Full Docker Deployment (Recommended for Production)**
```bash
# Starts Nimbus app + PostgreSQL + Ollama
docker compose up -d
```

**Option B: Development Setup (Local Python + Docker Services)**
```bash
# Only starts PostgreSQL + Ollama, run Nimbus locally
docker compose -f docker-compose.dev.yml up -d
```

3. **If using Option B (Development), set up Python environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

5. **Configure environment variables** (Optional)

Create a `.env` file in the project root:
```env
# Flask Configuration
FLASK_SECRET_KEY=your-secure-secret-key-here
FLASK_ENV=development
FLASK_DEBUG=true
APP_HOST=0.0.0.0
APP_PORT=8000

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/nimbus

# Ollama
OLLAMA_URL=http://localhost:11434

# Default Models
DEFAULT_EMBEDDING_MODEL=nomic-embed-text
```

6. **Run the application (Development mode only)**
```bash
# Only needed for Option B
python app.py
```

7. **Access the application**

Open your browser and navigate to:
```
http://localhost:8000
```

**Default credentials:**
- Username: `admin`
- Password: `admin123`

> ⚠️ **Security Note**: Change the default password immediately after first login!

---

## 📖 Usage Guide

### 1. **Upload Documents**

Navigate to **Documents** page:
- Click "Upload Document" or drag & drop files
- Supported formats: PDF, TXT, MD, DOCX, PPTX
- Files are associated with your user account

### 2. **Parse Documents**

Choose a parser based on your document type:
- **PyMuPDF**: Best for standard PDFs with selectable text
- **PDFPlumber**: Excellent for tables and structured data
- **Unstructured**: Advanced layout analysis
- **OCR**: For scanned documents or images
- **OCR + Vision**: Combines text extraction with AI image description

### 3. **Split Text**

Select a splitting strategy:
- **Recursive**: Balanced chunks with configurable size/overlap
- **Token-based**: Optimized for LLM token limits
- **Semantic**: Uses embeddings to find natural breakpoints

### 4. **Generate Embeddings**

Choose embedding models to create:
- `nomic-embed-text`: Fast, efficient
- `mxbai-embed-large`: High accuracy
- `all-minilm`: Compact, good for large datasets

> 💡 **Tip**: Generate multiple embedding models for better retrieval!

### 5. **Enable Documents**

Toggle documents "enabled" to include them in RAG context

### 6. **Chat with Your Documents**

Go to **Chat** page:
1. Select a chat model (e.g., `llama3.2`, `qwen2.5`)
2. Start asking questions about your documents
3. The AI will retrieve relevant chunks and cite sources
4. Create multiple sessions to organize conversations

---

## ⚙️ Configuration

All configuration is centralized in `config.py`. Key settings:

### RAG Configuration
```python
RAG_TOP_K_PER_MODEL = 5      # Top chunks per embedding model
RAG_TOP_K_OVERALL = 10       # Total chunks to include in context
RAG_SNIPPET_MAX_CHARS = 800  # Max characters per snippet
```

### Document Processing
```python
DEFAULT_CHUNK_SIZE = 1000     # Characters per chunk
DEFAULT_CHUNK_OVERLAP = 200   # Overlap between chunks
```

### Model Mapping
Define which embedding tables to query for each chat model:
```python
MODEL_EMBEDDING_TABLE_MAP = {
    'llama3:latest': [
        {'table': 'document_embeddings_nomic_embed_text', 'embedding_model': 'nomic-embed-text'},
        {'table': 'document_embeddings_mxbai_embed_large', 'embedding_model': 'mxbai-embed-large'}
    ]
}
```

---

## 🐳 Docker Deployment

**Full Stack Deployment:**
```bash
# Complete deployment with all services
docker compose up -d
```

**Development Setup:**
```bash
# Only database and Ollama (run Nimbus locally)
docker compose -f docker-compose.dev.yml up -d
python app.py
```

**What's Included:**
- 🐘 **PostgreSQL with pgvector** - Vector database for embeddings
- 🤖 **Ollama** - Local LLM inference server
- 🧠 **Nimbus App** - Document Mind application (full deployment only)
- 🗄️ **Persistent volumes** - Data survives container restarts
- 🌐 **Internal networking** - Services communicate securely

**Database initialization scripts in `db/init/`:**
- `01_init.sql`: Creates users table, pgvector extension, and default admin user
- `02_chat_tables.sql`: Creates chat sessions and messages tables with triggers

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed deployment options and production setup.

---

## 🔧 Advanced Features

### Multi-Model RAG
Nimbus queries multiple embedding models simultaneously and intelligently merges results:
1. Computes embeddings for user query with each configured model
2. Retrieves top-K chunks from each embedding table
3. Deduplicates based on content
4. Ranks by similarity score
5. Sends top results to LLM as context

### OCR + Vision Pipeline
For image-heavy or scanned documents:
1. Converts PDF pages to images (300 DPI for OCR)
2. Extracts text using Tesseract OCR
3. Optionally uses LLaVA vision model to describe images
4. Combines textual and visual information

### Semantic Text Splitting
Uses embeddings to find natural boundaries:
- Calculates similarity between consecutive sentences
- Splits at points where similarity drops (semantic shift)
- Creates more coherent chunks than arbitrary character counts

---

## 📁 Project Structure

```
nimbus/
├── app.py                      # Main Flask application
├── config.py                   # Centralized configuration
├── requirements.txt            # Python dependencies
├── docker-compose.yml          # Docker setup
│
├── apps/                       # Modular blueprints
│   ├── chat/                   # Chat interface & RAG logic
│   ├── documents/              # Document management
│   │   ├── parsers/           # PDF/OCR parsers
│   │   └── splitters/         # Text splitting strategies
│   └── users/                  # User management
│
├── db/                         # Database
│   ├── init/                  # SQL initialization scripts
│   └── chat.db                # SQLite (if using)
│
├── templates/                  # HTML templates
├── static/                     # CSS, JS, images
└── uploads/                    # User-uploaded files
```

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit your changes** (`git commit -m 'Add amazing feature'`)
4. **Push to the branch** (`git push origin feature/amazing-feature`)
5. **Open a Pull Request**

Please ensure your code follows the existing style and includes appropriate documentation.

---

## 🛣️ Roadmap

- [ ] API endpoints for programmatic access
- [ ] Support for more document types (Excel, CSV, HTML)
- [ ] Vector index optimization (IVFFlat, HNSW)
- [ ] Batch document processing
- [ ] Multi-language support
- [ ] Export chat conversations
- [ ] Advanced analytics dashboard
- [ ] Docker image for full application

---

## � Security

**⚠️ Important Security Notice**: This application includes default credentials for development. **Change all default passwords immediately** before production deployment!

- Default admin login: `admin` / `admin123`
- See [SECURITY.md](SECURITY.md) for complete security guidelines
- Follow the security checklist before going live

For security issues, please report responsibly to maintainers directly.

---

## �📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Ollama** for local LLM inference
- **pgvector** for PostgreSQL vector extension
- **LangChain** for semantic splitting utilities
- **Bootstrap** for UI components
- **Tesseract OCR** for text extraction

---

## 📧 Support

For questions, issues, or feature requests:
- Open an issue on GitLab
- Check existing documentation in the `/docs` folder
- Review the configuration guide in `CONFIGURATION_GUIDE.md`

---

**Built with ❤️ to be your intelligent Document Mind - transforming how you interact with knowledge** 🧠📄
