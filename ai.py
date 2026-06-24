
from pathlib import Path

STRUCTURE = {
    "README.md": "",
    ".env": "",
    ".env.example": "",
    ".gitignore": "",
    "requirements.txt": "",
    "Dockerfile": "",
    "docker-compose.yml": "",

    "app/main.py": "# Hermes AI OS Entry Point\n",

    "app/api/auth.py": "",
    "app/api/chat.py": "",
    "app/api/goals.py": "",
    "app/api/tasks.py": "",
    "app/api/memories.py": "",
    "app/api/documents.py": "",
    "app/api/knowledge.py": "",

    "app/core/config.py": "",
    "app/core/security.py": "",
    "app/core/logger.py": "",
    "app/core/tracing.py": "",
    "app/core/telemetry.py": "",
    "app/core/constants.py": "",
    "app/core/dependencies.py": "",
    "app/core/exceptions.py": "",

    "app/common/enums.py": "",
    "app/common/interfaces.py": "",
    "app/common/types.py": "",
    "app/common/constants.py": "",

    "app/clients/base_client.py": "",
    "app/clients/llm_client.py": "",
    "app/clients/embedding_client.py": "",
    "app/clients/vector_client.py": "",
    "app/clients/search_client.py": "",

    "app/prompts/system_prompt.py": "",
    "app/prompts/loader.py": "",
    "app/prompts/memory_agent.py": "",
    "app/prompts/planner_agent.py": "",
    "app/prompts/research_agent.py": "",
    "app/prompts/review_agent.py": "",
    "app/prompts/knowledge_agent.py": "",

    "app/models/user.py": "",
    "app/models/conversation.py": "",
    "app/models/message.py": "",
    "app/models/goal.py": "",
    "app/models/task.py": "",
    "app/models/memory.py": "",
    "app/models/document.py": "",
    "app/models/review.py": "",
    "app/models/agent_run.py": "",

    "app/schemas/base.py": "",
    "app/schemas/user.py": "",
    "app/schemas/chat.py": "",
    "app/schemas/goal.py": "",
    "app/schemas/task.py": "",
    "app/schemas/memory.py": "",
    "app/schemas/document.py": "",
    "app/schemas/review.py": "",

    "app/repositories/base_repo.py": "",
    "app/repositories/user_repo.py": "",
    "app/repositories/goal_repo.py": "",
    "app/repositories/task_repo.py": "",
    "app/repositories/memory_repo.py": "",
    "app/repositories/document_repo.py": "",
    "app/repositories/review_repo.py": "",

    "app/services/auth_service.py": "",
    "app/services/user_service.py": "",
    "app/services/assistant_service.py": "",
    "app/services/memory_service.py": "",
    "app/services/rag_service.py": "",
    "app/services/planner_service.py": "",
    "app/services/review_service.py": "",

    "app/memory/store.py": "",
    "app/memory/retrieve.py": "",
    "app/memory/summarize.py": "",
    "app/memory/rank.py": "",

    "app/rag/ingest.py": "",
    "app/rag/chunker.py": "",
    "app/rag/embedder.py": "",
    "app/rag/retrieve.py": "",
    "app/rag/rerank.py": "",
    "app/rag/pipeline.py": "",

    "app/agents/orchestrator.py": "",
    "app/agents/memory_agent.py": "",
    "app/agents/planner_agent.py": "",
    "app/agents/research_agent.py": "",
    "app/agents/review_agent.py": "",
    "app/agents/knowledge_agent.py": "",

    "app/tools/memory_tool.py": "",
    "app/tools/goal_tool.py": "",
    "app/tools/task_tool.py": "",
    "app/tools/rag_tool.py": "",
    "app/tools/search_tool.py": "",

    "app/cache/redis_client.py": "",
    "app/cache/llm_cache.py": "",

    "app/workers/celery_app.py": "",
    "app/workers/document_worker.py": "",
    "app/workers/memory_worker.py": "",
    "app/workers/review_worker.py": "",

    "app/db/base.py": "",
    "app/db/session.py": "",

    "app/utils/helpers.py": "",
    "app/utils/validators.py": "",
    "app/utils/datetime_utils.py": "",

    "tests/conftest.py": "",
    "tests/unit/test_repositories.py": "",
    "tests/unit/test_services.py": "",
    "tests/unit/test_agents.py": "",
    "tests/unit/test_tools.py": "",
    "tests/integration/test_api_routes.py": "",
    "tests/integration/test_rag_pipeline.py": "",
    "tests/integration/test_workers.py": "",
    "tests/e2e/test_conversation_flow.py": "",

    "docs/vision.md": "",
    "docs/architecture.md": "",
    "docs/folder-structure.md": "",
    "docs/database-design.md": "",
    "docs/api-design.md": "",
    "docs/request-flow.md": "",
    "docs/roadmap.md": "",

    "scripts/seed_data.py": "",
    "scripts/create_admin.py": "",
    "scripts/reset_db.py": "",
}

PACKAGE_DIRS = [
    "app","app/api","app/core","app/common","app/clients","app/prompts",
    "app/models","app/schemas","app/repositories","app/services","app/memory",
    "app/rag","app/agents","app/tools","app/cache","app/workers","app/db",
    "app/utils","tests","tests/unit","tests/integration","tests/e2e"
]

def main():
    root = Path("hermes-ai-os")
    root.mkdir(exist_ok=True)

    for rel_path, content in STRUCTURE.items():
        file_path = root / rel_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")

    for pkg in PACKAGE_DIRS:
        init_file = root / pkg / "__init__.py"
        init_file.parent.mkdir(parents=True, exist_ok=True)
        init_file.touch(exist_ok=True)

    (root / "app/db/migrations").mkdir(parents=True, exist_ok=True)
    (root / "tests/fixtures").mkdir(parents=True, exist_ok=True)
    (root / "infra/docker").mkdir(parents=True, exist_ok=True)
    (root / "infra/nginx").mkdir(parents=True, exist_ok=True)
    (root / "infra/monitoring").mkdir(parents=True, exist_ok=True)

    print("Hermes AI OS scaffold created successfully!")

if __name__ == "__main__":
    main()
