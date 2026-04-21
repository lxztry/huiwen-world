"""
汇文世界 · 角色管理器
加载角色设定文件，提供角色信息
"""

import re
import yaml
from pathlib import Path
from typing import Optional

CHARACTERS_DIR = Path(__file__).parent / "prompts" / "characters"
SYSTEM_PROMPT_PATH = Path(__file__).parent / "prompts" / "system_prompt.md"
WEN_GE_PATH = Path(__file__).parent / "prompts" / "wen_ge_system.md"


def load_character_file(character_id: str) -> Optional[dict]:
    """加载角色设定文件"""
    file_path = CHARACTERS_DIR / f"{character_id}.md"
    if not file_path.exists():
        return None

    content = file_path.read_text(encoding='utf-8')

    # 解析 YAML frontmatter
    match = re.match(r'^---\n(.*?)\n---\n(.*)', content, re.DOTALL)
    if not match:
        return None

    meta_yaml = match.group(1)
    body = match.group(2)

    meta = yaml.safe_load(meta_yaml)
    return {
        'character_id': character_id,
        'name': meta.get('name', character_id),
        'work': meta.get('work', ''),
        'identity': meta.get('identity', ''),
        'core_conflict': meta.get('core_conflict', ''),
        'body': body.strip()
    }


def get_all_character_ids() -> list:
    """获取所有可用角色ID"""
    if not CHARACTERS_DIR.exists():
        return []
    return [p.stem for p in CHARACTERS_DIR.glob("*.md")]


def get_character_info(character_id: str) -> Optional[dict]:
    """获取角色信息"""
    return load_character_file(character_id)


def build_character_prompt(character_id: str, user_wenge: dict = None,
                           familiarity: int = 0) -> str:
    """
    构建角色的完整 system prompt
    familiarity: 0=陌生, 1=熟悉, 2=知己
    """
    char = load_character_file(character_id)
    if not char:
        return None

    # 读取系统基础 prompt
    system_base = SYSTEM_PROMPT_PATH.read_text(encoding='utf-8')

    # 添加角色专属信息
    role_section = f"""
## 当前角色：{char['name']}

### 基本信息
- **作品**：《{char['work']}》
- **身份**：{char['identity']}
- **核心冲突**：{char['core_conflict']}

### 角色设定
{char['body']}

### 与用户的熟悉度层级：{"陌生" if familiarity == 0 else "熟悉" if familiarity == 1 else "知己"}
"""

    # 添加用户文格信息（如果有）
    wenge_section = ""
    if user_wenge:
        wenge_section = f"""
### 用户文格
用户在这个世界里的身份是「{user_wenge.get('wenge_type', '未知')}」。
用户角色名：{user_wenge.get('wenge_name', '未知访客')}
口头禅：{user_wenge.get('catchphrase', '暂无')}
"""

    return system_base + role_section + wenge_section


def get_wen_ge_system() -> str:
    """获取文格系统 prompt"""
    return WEN_GE_PATH.read_text(encoding='utf-8')


def list_characters() -> list:
    """列出所有可用角色"""
    chars = []
    for cid in get_all_character_ids():
        info = get_character_info(cid)
        if info:
            chars.append({
                'character_id': cid,
                'name': info['name'],
                'work': info['work'],
                'identity': info['identity']
            })
    return chars


if __name__ == "__main__":
    # 测试
    print("可用角色：")
    for c in list_characters():
        print(f"  {c['character_id']}: {c['name']}（《{c['work']}》）")
