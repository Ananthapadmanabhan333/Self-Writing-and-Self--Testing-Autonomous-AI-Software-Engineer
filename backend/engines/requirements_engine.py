"""NEXUS OS — Requirements Understanding Engine"""

from typing import Any, Dict, List, Optional
import structlog
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from core.config import settings

logger = structlog.get_logger()
llm = ChatOpenAI(model=settings.OPENAI_MODEL, temperature=0.1, api_key=settings.OPENAI_API_KEY)

REQUIREMENTS_SYSTEM = """You are a Principal Product & Engineering Requirements Analyst.
Transform any input (natural language, GitHub issues, Jira tickets, voice notes, API specs) 
into a fully structured engineering specification. 

Return ONLY valid JSON:
{
  "project_name": "string",
  "summary": "string",
  "problem_statement": "string",
  "target_users": ["string"],
  "core_features": [
    {
      "id": "F001",
      "name": "string",
      "description": "string",
      "priority": "critical|high|medium|low",
      "complexity": "xs|s|m|l|xl",
      "story_points": int,
      "acceptance_criteria": ["string"],
      "dependencies": ["F00X"]
    }
  ],
  "non_functional_requirements": {
    "performance": "string",
    "scalability": "string",
    "security": "string",
    "availability": "string"
  },
  "tech_stack_recommendations": {
    "frontend": ["string"],
    "backend": ["string"],
    "database": ["string"],
    "infrastructure": ["string"]
  },
  "architecture_type": "monolith|microservices|serverless|hybrid",
  "estimated_timeline_weeks": int,
  "implementation_phases": [
    {
      "phase": int,
      "name": "string",
      "features": ["F00X"],
      "duration_weeks": int,
      "deliverables": ["string"]
    }
  ],
  "risks": [
    {"risk": "string", "probability": "high|medium|low", "mitigation": "string"}
  ],
  "success_metrics": ["string"]
}"""


class RequirementsEngine:
    """Semantic requirement parsing and engineering specification generation."""

    async def parse(self, raw_input: str, input_type: str = "text") -> Dict[str, Any]:
        """Parse any requirement input into structured engineering spec."""
        logger.info("📋 Parsing requirements", input_type=input_type, length=len(raw_input))
        response = await llm.ainvoke([
            SystemMessage(content=REQUIREMENTS_SYSTEM),
            HumanMessage(content=f"Input Type: {input_type}\n\nRequirements:\n{raw_input}"),
        ])
        import json
        try:
            spec = json.loads(response.content)
            logger.info("✅ Requirements parsed", features=len(spec.get("core_features", [])))
            return spec
        except Exception:
            return {"raw": response.content, "error": "parse_failed"}

    async def generate_prd(self, spec: Dict[str, Any]) -> str:
        """Generate a full Product Requirements Document from a parsed spec."""
        response = await llm.ainvoke([
            SystemMessage(content="Generate a comprehensive, professional PRD document in Markdown format."),
            HumanMessage(content=f"Spec: {spec}"),
        ])
        return response.content

    async def generate_technical_spec(self, spec: Dict[str, Any]) -> str:
        """Generate a detailed technical specification document."""
        response = await llm.ainvoke([
            SystemMessage(content="""Generate a detailed technical specification including:
- System architecture decisions
- API contract definitions  
- Database schema design
- Security considerations
- Performance targets
- Deployment strategy
Format as professional Markdown."""),
            HumanMessage(content=f"Product Spec: {spec}"),
        ])
        return response.content

    async def decompose_to_tasks(self, spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Break features into atomic engineering tasks."""
        response = await llm.ainvoke([
            SystemMessage(content="""Decompose features into atomic engineering tasks. Return JSON array:
[{
  "title": "string",
  "type": "feature|bug|refactor|test|infra",
  "description": "string",
  "agent": "backend|frontend|devops|qa|security",
  "story_points": int,
  "priority": "critical|high|medium|low",
  "acceptance_criteria": ["string"],
  "dependencies": ["task_title"]
}]"""),
            HumanMessage(content=f"Features: {spec.get('core_features', [])}"),
        ])
        import json
        try:
            return json.loads(response.content)
        except Exception:
            return []

    async def infer_architecture(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Infer optimal system architecture from requirements."""
        response = await llm.ainvoke([
            SystemMessage(content="""Design optimal system architecture. Return JSON:
{
  "pattern": "string",
  "services": [{"name": str, "responsibility": str, "tech": str}],
  "data_stores": [{"type": str, "purpose": str}],
  "communication": {"sync": ["REST|gRPC"], "async": ["Kafka|RabbitMQ"]},
  "scalability_strategy": "string",
  "deployment_topology": "string"
}"""),
            HumanMessage(content=f"Requirements spec: {spec}"),
        ])
        import json
        try:
            return json.loads(response.content)
        except Exception:
            return {"error": "architecture_inference_failed"}


requirements_engine = RequirementsEngine()
