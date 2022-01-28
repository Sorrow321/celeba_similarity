docker run -p 6333:6333 \
    -v $(pwd)/qdrant_data:/qdrant/storage \
    generall/qdrant