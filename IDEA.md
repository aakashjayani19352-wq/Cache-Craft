Cache-Craft is an Autonomous Semantic RAG Router and caching middleware designed to reduce Large Language Model (LLM) API costs and latency. 

It intercepts user queries before they reach expensive cloud LLMs (like Gemini/ChatGPT). Using local sentence transformers (all-MiniLM-L6-v2) and a PostgreSQL pgvector database, it converts queries into dense vector embeddings and performs Approximate Nearest Neighbor (ANN) search. If the semantic intent of a new query matches a previously answered query above a configured cosine similarity threshold (e.g., 85%), it instantly serves the cached response. 

Tech Stack:
- Backend: Python, FastAPI
- Database: PostgreSQL (with pgvector), Redis
- AI: SentenceTransformers, Google Gemini API
- Frontend: Next.js, Tailwind CSS
- DevOps: Docker Compose
