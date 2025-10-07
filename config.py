"""
Centralized configuration module for Nimbus application.
All environment variables and static configurations are defined here.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.absolute()
UPLOADS_DIR = BASE_DIR / 'uploads'

# Flask Configuration
SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-change-for-production')
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'true').lower() == 'true'
APP_HOST = os.getenv('APP_HOST', '0.0.0.0')
APP_PORT = int(os.getenv('APP_PORT', '8000'))

# Database Configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/nimbus')

# Ollama Configuration
OLLAMA_URL = os.getenv('OLLAMA_URL', 'http://localhost:11434')

# Document Processing Configuration
ALLOWED_EXTENSIONS = os.getenv(
    'ALLOWED_EXTENSIONS', 
    '.pdf,.md,.txt,.docx,.pptx'
).split(',')

# RAG Configuration - Strict Document Instruction
STRICT_DOCS_INSTRUCTION = os.getenv(
    'STRICT_DOCS_INSTRUCTION',
    "You are given a set of retrieved document snippets which are the only allowed source "
    "of truth for this conversation. If user greets you, You can welcome him...and You MUST NOT use outside knowledge or hallucinate. "
    "Answer only from the provided documents. If the answer cannot be found in the documents, "
    "respond exactly: 'I don't know'. Be concise."
)

# Embedding Models - Models to exclude from chat interface
EMBEDDING_MODELS = set(
    os.getenv(
        'EMBEDDING_MODELS',
        'mxbai-embed-large,nomic-embed-text,all-minilm,snowflake-arctic-embed,bge-m3,bge-large,paraphrase-multilingual'
    ).split(',')
)

# Model to Embedding Table Mapping
# Format: model_name:table1:embedding_model1|table2:embedding_model2
MODEL_EMBEDDING_TABLE_MAP_STR = os.getenv(
    'MODEL_EMBEDDING_TABLE_MAP',
    'llama3:latest=document_embeddings_nomic_embed_text:nomic-embed-text|document_embeddings_mxbai_embed_large:mxbai-embed-large|document_embeddings_all_minilm:all-minilm'
)

# Parse the mapping string into a dictionary
MODEL_EMBEDDING_TABLE_MAP = {}
for entry in MODEL_EMBEDDING_TABLE_MAP_STR.split(';'):
    if '=' in entry:
        model, tables_str = entry.split('=', 1)
        tables = []
        for table_entry in tables_str.split('|'):
            if ':' in table_entry:
                table, emb_model = table_entry.split(':', 1)
                tables.append({
                    'table': table.strip(),
                    'embedding_model': emb_model.strip()
                })
        MODEL_EMBEDDING_TABLE_MAP[model.strip()] = tables

# RAG Retrieval Configuration
RAG_TOP_K_PER_MODEL = int(os.getenv('RAG_TOP_K_PER_MODEL', '5'))  # Top chunks per embedding model
RAG_TOP_K_OVERALL = int(os.getenv('RAG_TOP_K_OVERALL', '10'))  # Top chunks overall
RAG_SNIPPET_MAX_CHARS = int(os.getenv('RAG_SNIPPET_MAX_CHARS', '800'))  # Max chars per snippet

# Default Splitter Configuration
DEFAULT_CHUNK_SIZE = int(os.getenv('DEFAULT_CHUNK_SIZE', '1000'))
DEFAULT_CHUNK_OVERLAP = int(os.getenv('DEFAULT_CHUNK_OVERLAP', '200'))

# Default Embedding Model
DEFAULT_EMBEDDING_MODEL = os.getenv('DEFAULT_EMBEDDING_MODEL', 'nomic-embed-text')

# Session Configuration
SESSION_TIMEOUT = int(os.getenv('SESSION_TIMEOUT', '3600'))
SESSION_PERMANENT = os.getenv('SESSION_PERMANENT', 'true').lower() == 'true'

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Chat Configuration
CHAT_MAX_HISTORY = int(os.getenv('CHAT_MAX_HISTORY', '50'))  # Max chat sessions to retrieve
CHAT_REQUEST_TIMEOUT = int(os.getenv('CHAT_REQUEST_TIMEOUT', '60'))  # Ollama request timeout

# Embedding Request Configuration
EMBEDDING_REQUEST_TIMEOUT = int(os.getenv('EMBEDDING_REQUEST_TIMEOUT', '20'))

# Model Request Configuration
MODELS_REQUEST_TIMEOUT = int(os.getenv('MODELS_REQUEST_TIMEOUT', '5'))


def get_config_summary():
    """Return a summary of current configuration (for debugging)."""
    return {
        'FLASK_ENV': FLASK_ENV,
        'FLASK_DEBUG': FLASK_DEBUG,
        'DATABASE_URL': DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else 'configured',
        'OLLAMA_URL': OLLAMA_URL,
        'ALLOWED_EXTENSIONS': ALLOWED_EXTENSIONS,
        'EMBEDDING_MODELS_COUNT': len(EMBEDDING_MODELS),
        'DEFAULT_EMBEDDING_MODEL': DEFAULT_EMBEDDING_MODEL,
        'RAG_TOP_K_OVERALL': RAG_TOP_K_OVERALL,
        'UPLOADS_DIR': str(UPLOADS_DIR),
    }
