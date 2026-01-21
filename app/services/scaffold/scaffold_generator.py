from __future__ import annotations

import re

from app.core.schemas.agent_plan import AgentArchitecturePlan
from app.services.scaffold import templates

_SLUG_RE = re.compile(r"[^a-zA-Z0-9_]+")


def _normalize_slug(slug: str) -> str:
    """
    Normalizes a repo slug to: letters/numbers/underscore only.
    Also blocks path separators to prevent traversal.
    """
    slug = (slug or "generated_project").strip()

    # Hard block path separators first
    slug = slug.replace("/", "_").replace("\\", "_")

    slug = _SLUG_RE.sub("_", slug)
    slug = slug.strip("_")
    return slug or "generated_project"


def _add(files: dict[str, str], path: str, content: str) -> None:
    files[path] = content


def _folders_from_paths(paths: list[str]) -> list[str]:
    """
    Produce folder entries so the returned tree looks like a real repo.
    Example:
      myproj/
      myproj/app/
      myproj/app/api/
    """
    folders = set()
    for p in paths:
        # Normalize separators just in case
        p = p.replace("\\", "/").strip("/")
        if not p:
            continue

        parts = [x for x in p.split("/") if x]
        for i in range(1, len(parts)):
            folders.add("/".join(parts[:i]) + "/")
    return sorted(folders)


def generate_repo_scaffold(
    plan: AgentArchitecturePlan,
    project_slug: str,
    include_docker: bool = True,
    include_github_actions: bool = False,
) -> tuple[list[str], dict[str, str]]:
    """
    Returns:
      tree: list of paths (folders + files)
      files: dict path -> content
    """
    slug = _normalize_slug(project_slug)
    files: dict[str, str] = {}

    def p(rel: str) -> str:
        rel = (rel or "").replace("\\", "/").lstrip("/")
        return f"{slug}/{rel}"

    # Core files
    _add(files, p("README.md"), templates.render_readme(plan, project_slug=slug))
    _add(files, p("requirements.txt"), templates.render_requirements_txt())
    _add(files, p(".gitignore"), templates.render_gitignore())
    _add(files, p(".env.example"), templates.render_env_example())

    # App skeleton
    _add(files, p("app/__init__.py"), "")
    _add(files, p("app/main.py"), templates.render_main_py())

    _add(files, p("app/api/__init__.py"), "")
    _add(files, p("app/services/__init__.py"), "")
    _add(files, p("app/models/__init__.py"), "")

    # Docker (optional)
    if include_docker:
        _add(files, p("Dockerfile"), templates.render_dockerfile())
        _add(files, p("docker-compose.yml"), templates.render_docker_compose())

    # GitHub Actions (optional)
    if include_github_actions:
        _add(
            files,
            p(".github/workflows/ci.yml"),
            "\n".join(
                [
                    "name: CI",
                    "on: [push]",
                    "jobs:",
                    "  build:",
                    "    runs-on: ubuntu-latest",
                    "    steps:",
                    "      - uses: actions/checkout@v4",
                    "      - uses: actions/setup-python@v5",
                    "        with:",
                    "          python-version: '3.12'",
                    "      - run: pip install -r requirements.txt",
                    "",
                ]
            ),
        )

    file_paths = sorted(files.keys())
    folder_paths = _folders_from_paths(file_paths)

    tree = folder_paths + file_paths
    return tree, files
