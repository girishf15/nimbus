# Nimbus Deployment Guide

This guide covers different deployment options for Nimbus - A Document Mind.

## 🚀 Deployment Options

### 1. **Full Docker Deployment (Recommended)**

**Best for:** Production deployments, easy setup, complete isolation

```bash
# Clone the repository
git clone https://github.com/yourusername/nimbus.git
cd nimbus

# Start all services
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f nimbus
```

**What this includes:**
- ✅ Nimbus application (containerized)
- ✅ PostgreSQL with pgvector
- ✅ Ollama for local LLMs
- ✅ Automatic networking between services
- ✅ Data persistence with volumes

### 2. **Development Setup**

**Best for:** Local development, debugging, customization

```bash
# Start only supporting services
docker compose -f docker-compose.dev.yml up -d

# Set up Python environment
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run Nimbus locally
python app.py
```

### 3. **Production Deployment with Custom Configurations**

#### Step 1: Prepare Environment

```bash
# Create production environment file
cp .env.example .env.production

# Edit configuration for production
nano .env.production
```

**Key production settings:**
```env
FLASK_ENV=production
FLASK_DEBUG=false
FLASK_SECRET_KEY=your-super-secure-secret-key-here
DATABASE_URL=postgresql://user:password@host:5432/nimbus
OLLAMA_URL=http://ollama:11434
```

#### Step 2: Deploy with Production Config

```bash
# Use production environment
docker compose --env-file .env.production up -d

# Or with docker swarm for high availability
docker stack deploy -c docker-compose.yml nimbus-stack
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `FLASK_SECRET_KEY` | Flask session encryption key | ⚠️ Change in production | Yes |
| `DATABASE_URL` | PostgreSQL connection string | Auto-configured in Docker | Yes |
| `OLLAMA_URL` | Ollama API endpoint | `http://ollama:11434` | Yes |
| `DEFAULT_EMBEDDING_MODEL` | Default model for embeddings | `nomic-embed-text` | No |
| `RAG_TOP_K_OVERALL` | Max chunks in RAG context | `10` | No |

### Volume Mounts

```yaml
volumes:
  - ./uploads:/app/uploads          # User uploaded files
  - postgres_data:/var/lib/postgresql/data  # Database persistence
  - ollama_data:/root/.ollama       # Ollama models cache
```

## 🌐 Reverse Proxy Setup (Production)

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Traefik Configuration (Docker)

```yaml
# Add to docker-compose.yml
services:
  nimbus:
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.nimbus.rule=Host(`your-domain.com`)"
      - "traefik.http.routers.nimbus.tls.certresolver=letsencrypt"
```

## 📊 Monitoring & Logs

### View Application Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f nimbus
docker compose logs -f db
docker compose logs -f ollama
```

### Health Checks
```bash
# Check if services are running
curl http://localhost:8000/api/session-check
curl http://localhost:11434/api/tags
```

### Database Backup
```bash
# Backup
docker compose exec db pg_dump -U postgres nimbus > backup.sql

# Restore
docker compose exec -T db psql -U postgres nimbus < backup.sql
```

## 🔐 Security Considerations

### Production Security Checklist

- [ ] **Change default passwords** in environment files
- [ ] **Use strong SECRET_KEY** (32+ random characters)
- [ ] **Enable HTTPS** with SSL certificates
- [ ] **Restrict database access** to application only
- [ ] **Regular backups** of database and uploads
- [ ] **Update dependencies** regularly
- [ ] **Monitor logs** for suspicious activity

### Firewall Rules
```bash
# Only allow necessary ports
ufw allow 80   # HTTP
ufw allow 443  # HTTPS
ufw allow 22   # SSH
ufw deny 5432  # Block direct database access
ufw deny 11434 # Block direct Ollama access
```

## 🚨 Troubleshooting

### Common Issues

**Database connection failed:**
```bash
# Check if PostgreSQL is running
docker compose ps db

# View database logs
docker compose logs db

# Test connection
docker compose exec db psql -U postgres -d nimbus -c "SELECT 1;"
```

**Ollama not responding:**
```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# Download a model
docker compose exec ollama ollama pull llama3.2
```

**Application errors:**
```bash
# Check application logs
docker compose logs nimbus

# Restart application
docker compose restart nimbus
```

### Performance Tuning

**For large document processing:**
```env
# Increase timeouts
CHAT_REQUEST_TIMEOUT=120
EMBEDDING_REQUEST_TIMEOUT=60

# Optimize chunk sizes
DEFAULT_CHUNK_SIZE=1500
RAG_TOP_K_OVERALL=15
```

**For high traffic:**
```yaml
# Add to docker-compose.yml
deploy:
  replicas: 3
  resources:
    limits:
      cpus: '1.0'
      memory: 2G
```

## 📈 Scaling

### Horizontal Scaling
- Use Docker Swarm or Kubernetes
- Load balance between multiple app instances
- Separate database to dedicated server
- Use Redis for session storage

### Vertical Scaling
- Increase container memory/CPU limits
- Optimize PostgreSQL configuration
- Use faster storage (SSD)
- Increase Ollama model cache

---

For more help, check the [GitHub Issues](https://github.com/yourusername/nimbus/issues) or [Contributing Guide](CONTRIBUTING.md).