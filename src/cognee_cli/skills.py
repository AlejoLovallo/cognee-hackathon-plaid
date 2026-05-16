"""Browse and install agent skill instructions."""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict


class Skill(TypedDict):
    """Skill metadata."""

    name: str
    description: str


def detect_agent_dir() -> Path | None:
    """Auto-detect .claude/skills or .agents/skills directory."""
    cwd = Path.cwd()
    candidates = [
        cwd / ".claude" / "skills",
        cwd / ".agents" / "skills",
    ]
    for path in candidates:
        if path.is_dir():
            return path
    return None


def skill_names() -> list[str]:
    """Return available skill names."""
    skills_dir = Path(__file__).parent / "skills"
    if not skills_dir.is_dir():
        return []
    return sorted(
        d.name
        for d in skills_dir.iterdir()
        if d.is_dir() and (d / "SKILL.md").is_file()
    )


def list_skills() -> list[Skill]:
    """Return available skills with metadata."""
    skills_dir = Path(__file__).parent / "skills"
    if not skills_dir.is_dir():
        return []

    skills: list[Skill] = []
    for skill_dir in sorted(skills_dir.iterdir()):
        if not skill_dir.is_dir():
            continue
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.is_file():
            continue

        # Parse frontmatter for description
        description = ""
        content = skill_file.read_text()
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                for line in frontmatter.splitlines():
                    if line.startswith("description:"):
                        description = line.split(":", 1)[1].strip()
                        break

        skills.append({"name": skill_dir.name, "description": description})

    return skills


def get_skill_content(skill_name: str) -> str:
    """Return the SKILL.md content for a skill."""
    skills_dir = Path(__file__).parent / "skills"
    skill_file = skills_dir / skill_name / "SKILL.md"
    if not skill_file.is_file():
        raise FileNotFoundError(f"Skill not found: {skill_name}")
    return skill_file.read_text()


def install_skill(skill_name: str, target_dir: Path) -> str:
    """
    Install a skill to the target directory.

    Returns: "installed" or "updated"
    """
    import shutil

    skills_dir = Path(__file__).parent / "skills"
    source = skills_dir / skill_name
    if not source.is_dir():
        raise FileNotFoundError(f"Skill not found: {skill_name}")

    dest = target_dir / skill_name
    status = "updated" if dest.exists() else "installed"

    # Remove existing and copy fresh
    if dest.exists():
        shutil.rmtree(dest)

    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, dest)

    return status
