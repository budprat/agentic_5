# Sankhya Database Rules and Best Practices

## Database Overview
The `sankhya` table contains 2,402 records from "Secret Of Sankhya: Acme Of Scientific Unification" - a philosophical text about Sankhya philosophy and scientific unification. Each record represents a text chunk with high-dimensional vector embeddings.

## Table Structure
```sql
-- Column specifications
id: bigint (primary key, auto-increment)
content: text (text excerpts from the PDF)
metadata: jsonb (PDF metadata, page locations, timestamps)
embedding: vector(3072) (high-dimensional embeddings)
```

## Vector Specifications
- **Dimensions**: 3072 (likely OpenAI text-embedding-3-large model)
- **Total Records**: 2,402 (all have embeddings)
- **Table Size**: 36 MB
- **Index Limitations**: Cannot use HNSW or IVFFlat indexes (2000-dimension limit)

## Search Rules and Best Practices

### 1. Distance Metric Selection
```sql
-- RECOMMENDED: Use cosine distance for semantic similarity
-- Cosine distance range: 0 (identical) to 2 (opposite)
SELECT * FROM sankhya 
ORDER BY embedding <=> query_embedding;

-- Alternative metrics (use case dependent):
-- Euclidean: embedding <-> query_embedding
-- Inner Product: embedding <#> query_embedding (if normalized)
```

### 2. Similarity Threshold Guidelines
Based on empirical analysis:
- **>0.9**: Nearly identical content
- **0.7-0.9**: Highly related content
- **0.6-0.7**: Moderately related content
- **0.5-0.6**: Loosely related content
- **<0.5**: Unrelated content

### 3. Optimal Search Function
```sql
-- Use this function for all semantic searches
SELECT * FROM search_sankhya(
    query_embedding,
    0.6,  -- Recommended threshold for relevant results
    10    -- Top N results
);
```

### 4. Content Categories for Filtering
Pre-filter by content type to improve search relevance:
- **Philosophy**: `content LIKE '%Kapila%' OR content LIKE '%Maharishi%'` (65 records)
- **Physics/Science**: `content LIKE '%quantum%' OR content LIKE '%physics%'` (161 records)
- **Vedic Content**: `content LIKE '%Vedas%'` (43 records)
- **Appendices**: `content LIKE '%Appendix%'` (13 records)

### 5. Performance Optimization Strategies

#### Without Indexes (Current State)
```sql
-- Combine semantic search with text filtering for better performance
WITH filtered AS (
    SELECT * FROM sankhya 
    WHERE content ILIKE '%your_keyword%'  -- Pre-filter
)
SELECT 
    id, 
    content,
    1 - (embedding <=> query_embedding) as similarity
FROM filtered
ORDER BY embedding <=> query_embedding
LIMIT 10;
```

#### Batch Processing
```sql
-- For multiple queries, batch them together
WITH query_batch AS (
    SELECT unnest(ARRAY[embedding1, embedding2, embedding3]) as query_emb
)
SELECT DISTINCT ON (s.id)
    s.id,
    s.content,
    MIN(s.embedding <=> q.query_emb) as best_similarity
FROM sankhya s, query_batch q
GROUP BY s.id, s.content
ORDER BY s.id, best_similarity;
```

### 6. Metadata Utilization
```sql
-- Use metadata for advanced filtering
SELECT * FROM sankhya
WHERE metadata->'pdf'->'info'->>'Title' LIKE '%Part 2%'
AND metadata->'loc'->'lines'->>'from' :: int < 1000;
```

### 7. Multi-Concept Search Pattern
```sql
-- Search for documents matching multiple concepts
WITH search_concepts AS (
    SELECT embedding FROM sankhya 
    WHERE content LIKE '%concept1%'
    UNION
    SELECT embedding FROM sankhya 
    WHERE content LIKE '%concept2%'
)
SELECT DISTINCT
    s.id,
    s.content,
    MIN(s.embedding <=> sc.embedding) as relevance_score
FROM sankhya s
CROSS JOIN search_concepts sc
GROUP BY s.id, s.content
HAVING MIN(s.embedding <=> sc.embedding) < 0.4  -- Cosine distance < 0.4
ORDER BY relevance_score
LIMIT 20;
```

### 8. Clustering and Analysis Queries
```sql
-- Find semantically similar document clusters
WITH document_pairs AS (
    SELECT 
        s1.id as doc1_id,
        s2.id as doc2_id,
        s1.embedding <=> s2.embedding as distance
    FROM sankhya s1
    CROSS JOIN sankhya s2
    WHERE s1.id < s2.id
    AND s1.embedding <=> s2.embedding < 0.3  -- Very similar
)
SELECT * FROM document_pairs
ORDER BY distance
LIMIT 100;
```

### 9. Quality Control Rules
- **Always check for NULL embeddings** before similarity calculations
- **Validate similarity scores** are within expected ranges (0-2 for cosine)
- **Use LIMIT** to prevent overwhelming result sets
- **Monitor query execution time** - queries >1s may need optimization

### 10. Special Considerations
1. **No Vector Indexes**: All searches perform full table scans
2. **Memory Usage**: Large result sets can consume significant memory
3. **Concurrent Access**: Use connection pooling for multiple simultaneous searches
4. **Embedding Consistency**: All embeddings must be from the same model (text-embedding-3-large)

## Common Query Templates

### Basic Semantic Search
```sql
-- Find similar content to a specific record
WITH target AS (
    SELECT embedding FROM sankhya WHERE id = :target_id
)
SELECT 
    s.id,
    LEFT(s.content, 200) as preview,
    1 - (s.embedding <=> t.embedding) as similarity
FROM sankhya s, target t
WHERE s.id != :target_id
ORDER BY similarity DESC
LIMIT 10;
```

### Keyword + Semantic Hybrid Search
```sql
-- Combine keyword and semantic search
WITH keyword_matches AS (
    SELECT id, embedding 
    FROM sankhya 
    WHERE to_tsvector('english', content) @@ plainto_tsquery('english', :search_term)
)
SELECT 
    s.id,
    s.content,
    CASE 
        WHEN k.id IS NOT NULL THEN 0.3  -- Keyword match bonus
        ELSE 0
    END + (1 - (s.embedding <=> :query_embedding)) as combined_score
FROM sankhya s
LEFT JOIN keyword_matches k ON s.id = k.id
ORDER BY combined_score DESC
LIMIT 20;
```

### Exploratory Semantic Analysis
```sql
-- Find thematic clusters in the dataset
WITH random_samples AS (
    SELECT id, embedding, content
    FROM sankhya
    ORDER BY RANDOM()
    LIMIT 10
)
SELECT 
    rs.id as sample_id,
    LEFT(rs.content, 50) as sample_preview,
    COUNT(*) as cluster_size,
    AVG(1 - (s.embedding <=> rs.embedding)) as avg_similarity
FROM random_samples rs
CROSS JOIN sankhya s
WHERE s.embedding <=> rs.embedding < 0.4
GROUP BY rs.id, rs.content
ORDER BY cluster_size DESC;
```

## Maintenance and Monitoring

### Regular Health Checks
```sql
-- Check embedding completeness
SELECT 
    COUNT(*) as total_records,
    COUNT(embedding) as records_with_embeddings,
    COUNT(*) FILTER (WHERE embedding IS NULL) as missing_embeddings
FROM sankhya;

-- Monitor table size growth
SELECT 
    pg_size_pretty(pg_total_relation_size('sankhya')) as total_size,
    pg_size_pretty(avg(pg_column_size(embedding))) as avg_embedding_size
FROM sankhya;
```

## Future Optimization Paths
1. **Dimension Reduction**: Implement PCA to reduce to <2000 dimensions for indexing
2. **Materialized Views**: Pre-compute common similarity calculations
3. **Partitioning**: Partition by content type or date ranges
4. **Caching Layer**: Implement Redis for frequently accessed embeddings
5. **Approximate Methods**: Use LSH or other approximate nearest neighbor techniques

## Important Warnings
- ⚠️ **No RLS enabled** - Enable Row Level Security for production use
- ⚠️ **Full table scans** - Each query scans all 2,402 records
- ⚠️ **Memory intensive** - Large similarity matrices can exhaust memory
- ⚠️ **Model consistency** - Never mix embeddings from different models

## Version History
- Created: 2024-01-07
- Last Updated: 2024-01-07
- Database: PostgreSQL 17.4 with pgvector extension
- Embedding Model: text-embedding-3-large (3072 dimensions)