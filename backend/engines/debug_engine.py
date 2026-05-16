"""NEXUS OS — Self-Debugging & Failure Recovery Engine"""

import asyncio
import re
from typing import Any, Dict, List, Optional
import structlog
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from core.config import settings

logger = structlog.get_logger()
llm = ChatOpenAI(model=settings.OPENAI_MODEL, temperature=0, api_key=settings.OPENAI_API_KEY)

SYSTEM_DEBUG_PROMPT = """You are an elite Software Debugging Expert with 20 years of experience.
Perform deep root-cause analysis. Given an error, stack trace, and code context:
1. Identify the exact root cause
2. Generate a minimal, correct patch
3. Explain why the error occurred
4. Suggest prevention strategies
Return ONLY valid JSON matching this schema:
{
  "root_cause": "string",
  "error_category": "syntax|runtime|logic|dependency|configuration|network|database",
  "severity": "critical|high|medium|low",
  "patches": {"filepath": "patched_code"},
  "explanation": "string",
  "prevention": "string",
  "confidence": 0.0-1.0,
  "resolved": true|false
}"""


class SelfDebuggingEngine:
    """Recursive failure analysis and autonomous patch generation."""

    MAX_ITERATIONS = 5

    async def analyze_and_fix(
        self,
        error_message: str,
        stack_trace: Optional[str] = None,
        code_context: Optional[Dict[str, str]] = None,
        task_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Run recursive debugging loop until error is resolved or max iterations reached."""
        history: List[Dict] = []
        current_error = error_message
        current_code = code_context or {}

        for iteration in range(self.MAX_ITERATIONS):
            logger.info("🐛 Debug iteration", iteration=iteration + 1, task_id=task_id)
            result = await self._run_debug_pass(current_error, stack_trace, current_code)
            history.append({"iteration": iteration + 1, "result": result})

            if result.get("resolved") or result.get("confidence", 0) >= 0.9:
                logger.info("✅ Debug resolved", iterations=iteration + 1, task_id=task_id)
                return {
                    "resolved": True,
                    "iterations": iteration + 1,
                    "final_fix": result,
                    "history": history,
                }

            # Apply patches and retry
            if result.get("patches"):
                current_code.update(result["patches"])

        logger.warning("⚠️ Debug max iterations reached", task_id=task_id)
        return {"resolved": False, "iterations": self.MAX_ITERATIONS, "history": history}

    async def _run_debug_pass(
        self,
        error: str,
        stack_trace: Optional[str],
        code_context: Dict[str, str],
    ) -> Dict[str, Any]:
        """Single debugging pass using LLM."""
        context_snippet = ""
        for path, code in list(code_context.items())[:3]:
            context_snippet += f"\n--- {path} ---\n{code[:2000]}\n"

        prompt = f"""Error: {error}
Stack Trace: {stack_trace or 'Not available'}
Code Context: {context_snippet}"""

        response = await llm.ainvoke([
            SystemMessage(content=SYSTEM_DEBUG_PROMPT),
            HumanMessage(content=prompt),
        ])
        import json
        try:
            return json.loads(response.content)
        except Exception:
            return {
                "root_cause": "Unable to parse AI response",
                "resolved": False,
                "raw_response": response.content,
                "confidence": 0.3,
            }

    async def analyze_ci_failure(self, ci_logs: str, workflow_name: str) -> Dict[str, Any]:
        """Analyze CI/CD pipeline failures and generate fix recommendations."""
        response = await llm.ainvoke([
            SystemMessage(content="""Analyze CI/CD failure logs. Return JSON:
{
  "failed_step": "string",
  "root_cause": "string",
  "category": "build|test|lint|deploy|network|dependency",
  "fix_commands": ["command1", "command2"],
  "config_fixes": {"filename": "fixed_content"},
  "prevention": "string"
}"""),
            HumanMessage(content=f"Workflow: {workflow_name}\nLogs:\n{ci_logs[-3000:]}"),
        ])
        import json
        try:
            return json.loads(response.content)
        except Exception:
            return {"root_cause": response.content, "category": "unknown"}

    async def detect_memory_leak(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Detect memory leaks from runtime metrics."""
        response = await llm.ainvoke([
            SystemMessage(content="""Analyze runtime metrics for memory leaks. Return JSON:
{
  "leak_detected": bool,
  "leak_location": "string or null",
  "growth_rate_mb_per_hour": float,
  "likely_cause": "string",
  "remediation": "string"
}"""),
            HumanMessage(content=f"Metrics: {metrics}"),
        ])
        import json
        try:
            return json.loads(response.content)
        except Exception:
            return {"leak_detected": False, "error": "analysis_failed"}

    async def analyze_flaky_test(self, test_name: str, failure_history: List[Dict]) -> Dict[str, Any]:
        """Identify and fix flaky tests."""
        response = await llm.ainvoke([
            SystemMessage(content="""Analyze flaky test patterns. Return JSON:
{
  "flakiness_cause": "timing|race_condition|external_dependency|data_pollution|random",
  "confidence": float,
  "fix_strategy": "string",
  "patched_test": "string or null"
}"""),
            HumanMessage(content=f"Test: {test_name}\nFailure history: {failure_history}"),
        ])
        import json
        try:
            return json.loads(response.content)
        except Exception:
            return {"flakiness_cause": "unknown", "confidence": 0.0}


debug_engine = SelfDebuggingEngine()
