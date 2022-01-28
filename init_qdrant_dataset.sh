curl -X POST 'http://localhost:6333/collections' \
  -H 'Content-Type: application/json' \
  --data-raw '{
      "create_collection": {
          "name": "test_collection",
          "vector_size": 512,
          "distance": "Dot"
      }
  }'