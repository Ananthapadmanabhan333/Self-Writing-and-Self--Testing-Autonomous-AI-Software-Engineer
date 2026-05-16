"""
NEXUS OS — Application Configuration
Pydantic settings with full environment variable support.
"""

from functools import lru_cache
from typing import List, Optional

from pydantic import Field, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ---- Application ----
    APP_NAME: str = "nexus-os"
    APP_ENV: str = "development"
    APP_VERSION: str = "1.0.0"
    APP_SECRET_KEY: str = "change-me-in-production"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]

    # ---- AI / LLM ----
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-large"
    ANTHROPIC_API_KEY: Optional[str] = None
    LANGCHAIN_API_KEY: Optional[str] = None
    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_PROJECT: str = "nexus-os"

    # ---- Database ----
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "nexus_os"
    POSTGRES_USER: str = "nexus"
    POSTGRES_PASSWORD: str = "nexus_secure_password"

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def DATABASE_URL_SYNC(self) -> str:
        return f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # ---- Redis ----
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_URL: str = "redis://localhost:6379/1"
    CELERY_BROKER_URL: str = "redis://localhost:6379/2"

    # ---- Vector Database ----
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: Optional[str] = None
    QDRANT_COLLECTION_CODE: str = "nexus_code_embeddings"
    QDRANT_COLLECTION_MEMORY: str = "nexus_engineering_memory"

    # ---- Elasticsearch ----
    ELASTICSEARCH_URL: str = "http://localhost:9200"
    ELASTICSEARCH_USERNAME: str = "elastic"
    ELASTICSEARCH_PASSWORD: str = "elastic_password"

    # ---- Kafka ----
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_TOPIC_TASKS: str = "nexus.engineering.tasks"
    KAFKA_TOPIC_EVENTS: str = "nexus.engineering.events"
    KAFKA_TOPIC_TELEMETRY: str = "nexus.telemetry"

    # ---- GitHub ----
    GITHUB_TOKEN: Optional[str] = None
    GITHUB_WEBHOOK_SECRET: Optional[str] = None

    # ---- Cloud Deployments ----
    VERCEL_TOKEN: Optional[str] = None
    RAILWAY_TOKEN: Optional[str] = None
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"

    # ---- Kubernetes ----
    KUBECONFIG_PATH: Optional[str] = None
    ARGOCD_URL: Optional[str] = None
    ARGOCD_TOKEN: Optional[str] = None

    # ---- Monitoring ----
    PROMETHEUS_URL: str = "http://localhost:9090"
    GRAFANA_URL: str = "http://localhost:3001"
    GRAFANA_API_KEY: Optional[str] = None
    JAEGER_ENDPOINT: str = "http://localhost:4317"
    OTEL_EXPORTER_OTLP_ENDPOINT: str = "http://localhost:4317"

    # ---- Sandbox ----
    DOCKER_HOST: str = "unix:///var/run/docker.sock"
    SANDBOX_NETWORK: str = "nexus_sandbox"
    SANDBOX_MAX_CPU: str = "0.5"
    SANDBOX_MAX_MEMORY: str = "512m"
    SANDBOX_MAX_TIMEOUT: int = 300

    # ---- Security ----
    JWT_SECRET: str = "change-me-jwt-secret"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60

    # ---- Feature Flags ----
    ENABLE_AUTONOMOUS_MODE: bool = True
    ENABLE_SELF_HEALING: bool = True
    ENABLE_AUTO_DEPLOY: bool = False
    ENABLE_KNOWLEDGE_GRAPH: bool = True
    ENABLE_MULTI_AGENT: bool = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
