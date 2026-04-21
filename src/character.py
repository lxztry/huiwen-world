"""
汇文世界 · 角色加载器
Loads and manages character definitions from Markdown files.
"""

import os
import re
from typing import Dict, Optional, List


CHARACTERS_DIR = os.path.join(os.path.dirname(__file__), "..", "characters")


def load_character_file(filepath: str) -> Optional[Dict[str, str]]:
    """Parse a character markdown file and extract metadata."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract frontmatter fields
    data = {}
    lines = content.split("\n")
    in_frontmatter = False
    frontmatter_lines = []

    for line in lines:
        if line.strip() == "---":
            if not in_frontmatter:
                in_frontmatter = True
            else:
                in_frontmatter = False
            continue
        if in_frontmatter:
            frontmatter_lines.append(line)
        elif "## " in line or "# " in line:
            break

    for fm_line in frontmatter_lines:
        if ":" in fm_line:
            key = fm_line.split(":", 1)[0].strip()
            value = fm_line.split(":", 1)[1].strip()
            data[key] = value

    data["content"] = content
    return data


def load_all_characters() -> List[Dict[str, str]]:
    """Load all character files from the characters directory."""
    if not os.path.exists(CHARACTERS_DIR):
        return []

    characters = []
    for fname in os.listdir(CHARACTERS_DIR):
        if fname.endswith(".md"):
            fpath = os.path.join(CHARACTERS_DIR, fname)
            char = load_character_file(fpath)
            if char:
                characters.append(char)
    return characters


def get_character_by_id(char_id: str) -> Optional[Dict[str, str]]:
    """Get a single character by ID."""
    chars = load_all_characters()
    for char in chars:
        if char.get("id") == char_id:
            return char
    return None


def build_character_prompt(char: Dict[str, str]) -> str:
    """Build a system prompt snippet for a single character."""
    return f"""
### {char.get('name', char['id'])}

**角色ID**: {char['id']}
**作品**: {char.get('source', '未知')}
**身份**: {char.get('identity', '')}

**性格**: {char.get('personality', '')}
**说话风格**: {char.get('speech_style', '')}

{char.get('content', '')}
"""


def get_all_character_ids() -> List[str]:
    """Get list of all character IDs."""
    chars = load_all_characters()
    return [c["id"] for c in chars]


if __name__ == "__main__":
    chars = load_all_characters()
    for c in chars:
        print(f"- {c.get('name', c['id'])} ({c['id']}) from {c.get('source', 'unknown')}")
