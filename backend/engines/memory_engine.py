"""NEXUS OS — Engineering Memory System (Vector + Relational)"""

from typing import Any, Dict, List, Optional
import uuid
import structlog
from langchain_openai import OpenAIEmbeddings
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams, Filter, FieldCondition, MatchValue
from core.config import settings

logger = structlog.get_logger()

embeddings = OpenAIEmbeddings(
    model=settings.OPENAI_EMBEDDING_MODEL,
    api_key=settings.OPENAI_API_KEY,
)

qdrant = AsyncQdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)

MEMORY_COLLECTION = settings.QDRANT_COLLECTION_MEMORY
CODE_COLLECTION = settings.QDRANT_COLLECTION_CODE
EMBEDDING_DIM = 3072  # text-embedding-3-large


class EngineeringMemorySystem:
    """Long-term semantic memory for engineering knowledge, decisions, and patterns."""

    async def initialize(self):
        """Initialize Qdrant collections."""
        try:
            collections = await qdrant.get_collections()
            existing = [c.name for c in collections.collections]
            for name in [MEMORY_COLLECTION, CODE_COLLECTION]:
                if name not in existing:
                    await qdrant.create_collection(
                        collection_name=name,
                        vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE),
                    )
            logger.info("✅ Qdrant collections initialized")
        except Exception as e:
            logger.warning("⚠️ Qdrant init failed", error=str(e))

    async def store_memory(
        self,
        content: str,
        memory_type: str,
        title: str,
        organization_id: str,
        project_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        source: str = "system",
    ) -> str:
        """Embed and store an engineering memory."""
        try:
            vector = await embeddings.aembed_query(content)
            memory_id = str(uuid.uuid4())
            await qdrant.upsert(
                collection_name=MEMORY_COLLECTION,
                points=[
                    PointStruct(
                        id=memory_id,
                        vector=vector,
                        payload={
                            "title": title,
                            "content": content,
                            "memory_type": memory_type,
                            "organization_id": organization_id,
                            "project_id": project_id,
                            "tags": tags or [],
                            "source": source,
                        },
                    )
                ],
            )
            logger.info("💾 Memory stored", memory_type=memory_type, title=title[:50])
            return memory_id
        except Exception as e:
            logger.error("❌ Memory store failed", error=str(e))
            return ""

    async def recall(
        self,
        query: str,
        organization_id: str,
        memory_type: Optional[str] = None,
        top_k: int = 5,
        score_threshold: float = 0.6,
    ) -> List[Dict[str, Any]]:
        """Semantic similarity search over engineering memory."""
        try:
            vector = await embeddings.aembed_query(query)
            filters = [FieldCondition(key="organization_id", match=MatchValue(value=organization_id))]
            if memory_type:
                filters.append(FieldCondition(key="memory_type", match=MatchValue(value=memory_type)))

            results = await qdrant.search(
                collection_name=MEMORY_COLLECTION,
                query_vector=vector,
                limit=top_k,
                score_threshold=score_threshold,
                query_filter=Filter(must=filters),
                with_payload=True,
            )
            return [
                {
                    "id": r.id,
                    "score": r.score,
                    "title": r.payload.get("title"),
                    "content": r.payload.get("content"),
                    "memory_type": r.payload.get("memory_type"),
                    "tags": r.payload.get("tags", []),
                    "source": r.payload.get("source"),
                }
                for r in results
            ]
        except Exception as e:
            logger.error("❌ Memory recall failed", error=str(e))
            return []

    async def index_code_file(
        self,
        file_path: str,
        code: str,
        language: str,
        repository_id: str,
        organization_id: str,
    ) -> str:
        """Embed and index a source code file for semantic search."""
        try:
            # Chunk large files
            chunks = self._chunk_code(code, chunk_size=1500)
            chunk_ids = []
            for i, chunk in enumerate(chunks):
                vector = await embeddings.aembed_query(chunk)
                chunk_id = str(uuid.uuid4())
                await qdrant.upsert(
                    collection_name=CODE_COLLECTION,
                    points=[
                        PointStruct(
                            id=chunk_id,
                            vector=vector,
                            payload={
                                "file_path": file_path,
                                "chunk_index": i,
                                "language": language,
                                "repository_id": repository_id,
                                "organization_id": organization_id,
                                "content": chunk,
                            },
                        )
                    ],
                )
                chunk_ids.append(chunk_id)
            logger.info("📁 Code indexed", file=file_path, chunks=len(chunk_ids))
            return chunk_ids[0] if chunk_ids else ""
        except Exception as e:
            logger.error("❌ Code indexing failed", error=str(e))
            return ""

    async def search_code(
        self,
        query: str,
        repository_id: Optional[str] = None,
        language: Optional[str] = None,
        top_k: int = 10,
    ) -> List[Dict[str, Any]]:
        """Semantic code search across repositories."""
        try:
            vector = await embeddings.aembed_query(query)
            filters = []
            if repository_id:
                filters.append(FieldCondition(key="repository_id", match=MatchValue(value=repository_id)))
            if language:
                filters.append(FieldCondition(key="language", match=MatchValue(value=language)))

            qfilter = Filter(must=filters) if filters else None
            results = await qdrant.search(
                collection_name=CODE_COLLECTION,
                query_vector=vector,
                limit=top_k,
                score_threshold=0.5,
                query_filter=qfilter,
                with_payload=True,
            )
            return [
                {
                    "score": r.score,
                    "file_path": r.payload.get("file_path"),
                    "content": r.payload.get("content"),
                    "language": r.payload.get("language"),
                }
                for r in results
            ]
        except Exception as e:
            logger.error("❌ Code search failed", error=str(e))
            return []

    def _chunk_code(self, code: str, chunk_size: int = 1500) -> List[str]:
        """Split code into semantic chunks by line boundaries."""
        lines = code.split("\n")
        chunks, current, count = [], [], 0
        for line in lines:
            current.append(line)
            count += len(line)
            if count >= chunk_size:
                chunks.append("\n".join(current))
                current, count = [], 0
        if current:
            chunks.append("\n".join(current))
        return chunks or [code]


memory_system = EngineeringMemorySystem()
