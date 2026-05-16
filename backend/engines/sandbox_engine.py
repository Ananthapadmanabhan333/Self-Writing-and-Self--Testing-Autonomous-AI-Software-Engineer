"""NEXUS OS — Sandboxed Execution Engine (Docker-based)"""

import asyncio
import json
import tempfile
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional
import docker
import structlog
from core.config import settings

logger = structlog.get_logger()


class SandboxedExecutionEngine:
    """Secure ephemeral sandboxes for code execution and validation."""

    SUPPORTED_IMAGES = {
        "python": "python:3.12-slim",
        "node": "node:20-alpine",
        "go": "golang:1.23-alpine",
        "rust": "rust:1.82-slim",
        "java": "openjdk:21-slim",
        "bash": "alpine:latest",
    }

    def __init__(self):
        try:
            self.client = docker.from_env()
            logger.info("✅ Docker client connected")
        except Exception as e:
            logger.warning("⚠️ Docker unavailable, sandbox disabled", error=str(e))
            self.client = None

    async def execute(
        self,
        code: str,
        language: str = "python",
        timeout: int = 30,
        environment: Optional[Dict[str, str]] = None,
        files: Optional[Dict[str, str]] = None,
        install_packages: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Execute code in an isolated Docker container."""
        if not self.client:
            return {"success": False, "error": "Docker not available", "stdout": "", "stderr": ""}

        execution_id = str(uuid.uuid4())[:8]
        logger.info("🔒 Starting sandbox", execution_id=execution_id, language=language)

        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)

            # Write main code file
            ext_map = {"python": "py", "node": "js", "go": "go", "rust": "rs", "bash": "sh"}
            ext = ext_map.get(language, "txt")
            main_file = workspace / f"main.{ext}"
            main_file.write_text(code)

            # Write additional files
            if files:
                for fname, content in files.items():
                    fpath = workspace / fname
                    fpath.parent.mkdir(parents=True, exist_ok=True)
                    fpath.write_text(content)

            # Build command
            cmd = self._build_command(language, f"main.{ext}", install_packages)
            image = self.SUPPORTED_IMAGES.get(language, "python:3.12-slim")

            start_time = time.time()
            try:
                container = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.client.containers.run(
                        image=image,
                        command=cmd,
                        volumes={str(workspace): {"bind": "/workspace", "mode": "ro"}},
                        working_dir="/workspace",
                        mem_limit=settings.SANDBOX_MAX_MEMORY,
                        nano_cpus=int(float(settings.SANDBOX_MAX_CPU) * 1e9),
                        network_mode="none",
                        read_only=True,
                        tmpfs={"/tmp": "size=64m"},
                        environment=environment or {},
                        timeout=timeout,
                        remove=True,
                        detach=False,
                    ),
                )
                stdout = container.decode("utf-8") if isinstance(container, bytes) else str(container)
                duration = time.time() - start_time
                logger.info("✅ Sandbox complete", execution_id=execution_id, duration_s=round(duration, 2))
                return {
                    "success": True,
                    "stdout": stdout,
                    "stderr": "",
                    "exit_code": 0,
                    "duration_seconds": duration,
                    "execution_id": execution_id,
                }
            except docker.errors.ContainerError as e:
                duration = time.time() - start_time
                return {
                    "success": False,
                    "stdout": e.container.logs().decode("utf-8") if e.container else "",
                    "stderr": str(e),
                    "exit_code": e.exit_status,
                    "duration_seconds": duration,
                    "execution_id": execution_id,
                }
            except Exception as e:
                return {
                    "success": False,
                    "stdout": "",
                    "stderr": str(e),
                    "exit_code": -1,
                    "duration_seconds": time.time() - start_time,
                    "execution_id": execution_id,
                }

    def _build_command(self, language: str, filename: str, packages: Optional[List[str]]) -> str:
        pkg_install = ""
        if packages:
            if language == "python":
                pkg_install = f"pip install -q {' '.join(packages)} && "
            elif language == "node":
                pkg_install = f"npm install -q {' '.join(packages)} && "
        cmds = {
            "python": f"{pkg_install}python {filename}",
            "node": f"{pkg_install}node {filename}",
            "go": f"go run {filename}",
            "rust": f"rustc {filename} -o /tmp/output && /tmp/output",
            "bash": f"sh {filename}",
        }
        return cmds.get(language, f"python {filename}")

    async def run_tests(
        self, code_files: Dict[str, str], language: str = "python"
    ) -> Dict[str, Any]:
        """Run test suite inside sandbox and return structured results."""
        if language == "python":
            test_runner = "python -m pytest /workspace -v --tb=short --json-report --json-report-file=/tmp/results.json 2>&1 || true"
            # Combine all files into a single execution context
            return await self.execute(
                code=test_runner,
                language="bash",
                files=code_files,
                timeout=120,
            )
        elif language == "node":
            return await self.execute(
                code="npx jest --json 2>&1 || true",
                language="bash",
                files=code_files,
                timeout=120,
            )
        return {"success": False, "error": f"Unsupported test language: {language}"}

    async def validate_dockerfile(self, dockerfile_content: str) -> Dict[str, Any]:
        """Validate a Dockerfile without actually building."""
        response = {"valid": True, "warnings": [], "errors": []}
        required = ["FROM"]
        for req in required:
            if req not in dockerfile_content:
                response["errors"].append(f"Missing required instruction: {req}")
                response["valid"] = False
        if "latest" in dockerfile_content:
            response["warnings"].append("Using 'latest' tag is not recommended for production")
        return response


sandbox_engine = SandboxedExecutionEngine()
