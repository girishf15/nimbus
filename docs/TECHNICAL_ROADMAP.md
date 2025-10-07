# Nimbus Technical Roadmap & Future Improvements

This document outlines the technical enhancements and features planned for future versions of Nimbus.

## 🎯 Implementation Priority

### **Phase 1: Core Performance & Reliability**
**Timeline: Next 3-6 months**

#### 1. Hybrid Retrieval + Re-ranker
**Priority: High**
- **Current Limitation**: Single-stage retrieval may miss relevant context
- **Solution**: 
  - Implement dense + sparse retrieval (embedding + BM25)
  - Add cross-encoder re-ranking for final result ordering
  - Configurable fusion algorithms (RRF, linear combination)
- **Technologies**: `rank-bm25`, `sentence-transformers` cross-encoders
- **Impact**: 15-30% improvement in retrieval accuracy

#### 2. ANN Indexing for pgvector
**Priority: High**
- **Current Limitation**: Linear search doesn't scale beyond 100K+ documents
- **Solution**:
  - Implement HNSW indexing for approximate nearest neighbor search
  - Add IVFFlat for memory-efficient large datasets
  - Dynamic index selection based on dataset size
- **Configuration**: 
  ```sql
  CREATE INDEX ON embeddings USING hnsw (embedding vector_cosine_ops);
  ```
- **Impact**: 10-100x faster search for large document collections

#### 3. Security Hardening
**Priority: Medium-High**
- **Current Limitation**: Development-grade security only
- **Enhancements**:
  - OAuth 2.0 / OIDC integration (Google, Microsoft, GitHub)
  - Role-based access control (RBAC) with granular permissions
  - API key management for programmatic access
  - Rate limiting and request throttling
  - Audit logging for all user actions
  - Session management improvements
- **Standards**: OWASP security guidelines compliance

### **Phase 2: Advanced Features**
**Timeline: 6-12 months**

#### 4. Async Ingestion Pipeline
**Priority: Medium**
- **Current Limitation**: Synchronous processing blocks UI
- **Solution**:
  - Redis/RabbitMQ job queue for background processing
  - Progress tracking and notifications
  - Batch processing capabilities
  - Error handling and retry mechanisms
- **Architecture**:
  ```
  Upload → Queue → Worker Pool → Progress Updates → Completion
  ```

#### 5. Enhanced Document Processing
**Priority: Medium**
- **File Type Extensions**:
  - Excel/CSV: Advanced table extraction with pandas
  - HTML: Content extraction with Beautiful Soup
  - PowerPoint: Slide content and image analysis
  - Images: Direct image embedding with CLIP
- **Table Extraction**:
  - Structure-aware parsing
  - Table-specific embeddings
  - Relationship preservation between table elements

#### 6. Semantic Caching & Query Expansion
**Priority: Medium-Low**
- **Semantic Caching**:
  - Cache similar queries using embedding similarity
  - Reduce LLM API calls and response times
  - Configurable cache hit thresholds
- **Query Expansion**:
  - Automatic query enhancement with synonyms
  - Context-aware query reformulation
  - Multi-turn conversation context integration

### **Phase 3: Enterprise & Integration**
**Timeline: 12+ months**

#### 7. API & Integration Layer
- RESTful API with OpenAPI/Swagger documentation
- Webhook support for real-time notifications
- Third-party integrations (Slack, Teams, etc.)
- SDK development for popular languages

#### 8. Enterprise Features
- Multi-tenant architecture
- Advanced analytics and reporting
- Custom model deployment support
- Compliance features (GDPR, HIPAA, SOC2)

## 🔧 Technical Implementation Details

### Database Optimizations
```sql
-- Future index strategies
CREATE INDEX CONCURRENTLY idx_doc_embeddings_hnsw 
ON document_embeddings USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- Partitioning for large datasets
CREATE TABLE document_embeddings_partitioned (
    LIKE document_embeddings INCLUDING ALL
) PARTITION BY RANGE (created_at);
```

### Configuration Enhancements
```python
# Future config structure
class AdvancedRAGConfig:
    # Hybrid retrieval
    dense_weight: float = 0.7
    sparse_weight: float = 0.3
    rerank_top_k: int = 100
    final_top_k: int = 10
    
    # Index configuration
    use_hnsw: bool = True
    hnsw_m: int = 16
    hnsw_ef_construction: int = 64
    
    # Caching
    enable_semantic_cache: bool = True
    cache_similarity_threshold: float = 0.85
```

### Architecture Evolution
```
Current: Flask → PostgreSQL → Ollama

Future: 
┌─────────────────┐
│   Load Balancer │
└─────────┬───────┘
          │
┌─────────▼───────┐
│  Flask App Pool │
└─────────┬───────┘
          │
┌─────────▼───────┐    ┌──────────────┐
│   Redis Queue   │◄──►│ Worker Pool  │
└─────────┬───────┘    └──────────────┘
          │
┌─────────▼───────┐    ┌──────────────┐
│ PostgreSQL +    │◄──►│   Ollama     │
│ Vector Index    │    │  + Re-ranker │
└─────────────────┘    └──────────────┘
```

## 📊 Expected Impact

| Feature | Performance Gain | User Experience | Development Effort |
|---------|------------------|----------------|-------------------|
| Hybrid Retrieval | +25% accuracy | Better answers | Medium |
| ANN Indexing | +50x speed | Faster search | Medium |
| Security Hardening | N/A | Enterprise-ready | High |
| Async Processing | No UI blocking | Smoother UX | Medium |
| More File Types | +3x supported formats | Broader utility | Medium |
| Semantic Caching | +40% response time | Faster responses | Low |

## 🚀 Getting Started with Contributions

Interested in implementing any of these features? Here's how to get started:

1. **Review the codebase**: Understand current architecture
2. **Pick a feature**: Start with Medium/Low effort items
3. **Create an issue**: Discuss approach before implementation
4. **Fork & develop**: Follow coding standards and tests
5. **Submit PR**: Include documentation and examples

## 📝 Notes

- All future features will maintain backward compatibility
- Performance benchmarks will be established before major changes
- User feedback will influence priority ordering
- Enterprise features may require separate licensing tiers

---

*This roadmap is living document and will be updated based on community feedback and technical discoveries.*