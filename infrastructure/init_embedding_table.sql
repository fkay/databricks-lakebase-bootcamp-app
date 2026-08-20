-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create the embeddings table
-- IMPORTANT: Replace {{EMBEDDING_DIM}} below with the correct dimension for your model:
--   - sentence-transformers/all-MiniLM-L6-v2: 384
--   - sentence-transformers/all-mpnet-base-v2: 768
--   - BAAI/bge-small-en-v1.5: 384
--   - BAAI/bge-base-en-v1.5: 768
--   - BAAI/bge-large-en-v1.5: 1024
CREATE TABLE IF NOT EXISTS tickets_app.weather_embeddings (
    id TEXT PRIMARY KEY,
    weather_doc_id TEXT NOT NULL,
    chunk_index TEXT NOT NULL,
    chunk_text TEXT NOT NULL,
    embedding VECTOR({{EMBEDDING_DIM}}) NOT NULL,
    model_name TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);