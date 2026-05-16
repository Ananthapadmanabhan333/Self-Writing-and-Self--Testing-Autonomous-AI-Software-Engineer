-- NEXUS OS PostgreSQL Schema Initialization
-- Enables pgvector extension for semantic search

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_tasks_project ON engineering_tasks(project_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON engineering_tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_type ON engineering_tasks(type);
CREATE INDEX IF NOT EXISTS idx_executions_task ON agent_executions(task_id);
CREATE INDEX IF NOT EXISTS idx_deployments_project ON deployments(project_id);
CREATE INDEX IF NOT EXISTS idx_deployments_status ON deployments(status);
CREATE INDEX IF NOT EXISTS idx_memory_org ON engineering_memory(organization_id);
CREATE INDEX IF NOT EXISTS idx_memory_type ON engineering_memory(memory_type);
CREATE INDEX IF NOT EXISTS idx_incidents_status ON incidents(status);
CREATE INDEX IF NOT EXISTS idx_incidents_severity ON incidents(severity);

-- Full text search index for repositories
CREATE INDEX IF NOT EXISTS idx_repos_name_trgm ON repositories USING gin(name gin_trgm_ops);

-- Insert default organization and admin user for local dev
INSERT INTO organizations (id, name, slug, plan)
VALUES (
  '00000000-0000-0000-0000-000000000001',
  'NEXUS Demo Org',
  'nexus-demo',
  'enterprise'
) ON CONFLICT DO NOTHING;
