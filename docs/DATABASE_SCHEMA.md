# Database Schema Documentation

This document describes all the tables created and used by the Nimbus application.

## 📊 Database Tables Overview

### 1. **Static Tables** (Created by SQL scripts)

#### `users` table
- **Source**: `01_init.sql`
- **Purpose**: User authentication and authorization
```sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  username TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  role TEXT DEFAULT 'user'
);
```

#### `chat_sessions` table  
- **Source**: `02_chat_tables.sql`
- **Purpose**: Chat conversation organization
```sql
CREATE TABLE chat_sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username TEXT NOT NULL,
    title TEXT DEFAULT 'New Chat',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    message_count INTEGER DEFAULT 0
);
```

#### `chat_messages` table
- **Source**: `02_chat_tables.sql`  
- **Purpose**: Individual chat messages storage
```sql
CREATE TABLE chat_messages (
    id SERIAL PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES chat_sessions(session_id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    model TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);
```

### 2. **Dynamic Tables** (Auto-created by application)

#### `documents` table
- **Source**: `apps/documents/db_store.py` - `ensure_table()`
- **Purpose**: Document metadata and processing status
```sql
CREATE TABLE documents (
    id TEXT PRIMARY KEY,
    filename TEXT NOT NULL,
    uploader TEXT,
    created_at TIMESTAMP,
    enabled BOOLEAN DEFAULT FALSE,
    parsing_status TEXT,
    size INTEGER,
    file_path TEXT,
    parser_name TEXT,
    parsed_text TEXT,
    splitter_name TEXT,
    splits JSON,
    embeddings_model TEXT,
    embeddings BOOLEAN DEFAULT FALSE
);
```

#### Embedding Tables (Per Model)
- **Source**: `apps/documents/routes.py` - `embeddings_document()`
- **Purpose**: Vector embeddings for semantic search
- **Naming**: `document_embeddings_{model_name}`

Examples:
```sql
CREATE TABLE document_embeddings_nomic_embed_text (
    id SERIAL PRIMARY KEY,
    filename TEXT,
    text TEXT,
    embedding VECTOR
);

CREATE TABLE document_embeddings_mxbai_embed_large (
    id SERIAL PRIMARY KEY,
    filename TEXT,
    text TEXT,
    embedding VECTOR
);
```

## 🔄 Table Creation Flow

### On Database Initialization (Docker Compose)
1. `01_init.sql` - Creates `users` table and pgvector extension
2. `02_chat_tables.sql` - Creates chat-related tables
3. Default admin user is inserted

### During Application Runtime
1. **Documents table**: Created on first document upload via `ensure_table()`
2. **Embedding tables**: Created when generating embeddings for specific models
3. **Automatic cleanup**: Embedding tables are discovered and cleaned up dynamically

## 🎯 Key Features

### Performance Optimizations
- **Indexes** on frequently queried columns
- **Foreign key constraints** ensure data integrity
- **Triggers** automatically update session statistics

### Data Integrity
- **CASCADE DELETE** - Deleting sessions removes associated messages
- **CHECK constraints** - Ensure valid role values
- **UNIQUE constraints** - Prevent duplicate users

### Scalability
- **Dynamic table creation** - Support for unlimited embedding models
- **JSON columns** for flexible metadata storage
- **UUID primary keys** for distributed systems compatibility

## 🚀 Migration Notes

If upgrading from an older version:

1. **Run database initialization**: `docker compose down && docker compose up -d`
2. **Existing data**: Tables use `IF NOT EXISTS` for safe creation
3. **New features**: Chat functionality requires the new chat tables

## 🔍 Troubleshooting

### Common Issues

**Chat not working?**
- Ensure `02_chat_tables.sql` has been executed
- Check if `chat_sessions` and `chat_messages` tables exist

**Embeddings not found?**
- Embedding tables are created dynamically per model
- Use `\dt document_embeddings*` in psql to list tables

**Performance issues?**
- Ensure indexes are created (included in table creation scripts)
- Consider adding vector indexes for large embedding tables

### Useful Queries

```sql
-- List all tables
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- Check embedding tables
SELECT table_name FROM information_schema.tables 
WHERE table_name LIKE 'document_embeddings_%';

-- View session statistics
SELECT username, COUNT(*) as session_count 
FROM chat_sessions 
GROUP BY username;
```