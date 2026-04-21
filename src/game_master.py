"""
汇文世界 · 游戏引擎
Core game engine handling dual-mode (daily/script), scene activation, and memorable scenes.
"""

import os
import json
import uuid
from typing import Dict, Optional, List, Any
from . import database
from . import character


# === Scene Activation Templates ===

SCENE_ACTIVATION_TEMPLATES = {
    "red_cliff": {
        "atmosphere": "肃杀江风",
        "activation": """🌙 「剧本启动」

你睁开眼，发现自己站在一艘摇晃的楼船上。江风灌入，吹动你的衣袍。
远处火光映天——曹军的连营灯火通明，仿佛一条火龙盘踞在对岸。
身旁，一个青年文士正负手而立，望着那火光，神情平静。
他似乎察觉到了你，转过身来。
"你来了。"他说，"今夜过后，天下大势将定。"
——诸葛亮在等你。"""
    },
    "riverside": {
        "atmosphere": "酒香四溢",
        "activation": """🌙 「剧本启动」

夜深了，梁山泊的聚义厅里灯火通明。
你踏入门槛，一股酒香扑面而来。
正中虎皮交椅上，一条黑脸大汉正捧着酒碗，见你进来，哈哈大笑。
"兄弟，来得正好！"宋江起身相迎，"今日众好汉齐聚，正要议一件大事。"
——宋江在等你。"""
    },
    "damian": {
        "atmosphere": "红烛摇曳",
        "activation": """🌙 「剧本启动」

大观园的深夜，怡红院里烛光摇曳。
你穿过回廊，远远听见有琴声传来，凄婉清冷。
门半掩着，烛影里，一个纤细的身影正在窗前独自抚琴。
她似乎察觉到了你的脚步声，琴声骤止。
"谁？"她回过头，烛光映照下，是一张带着忧愁的脸庞。
——林黛玉在等你。"""
    },
    "mountain": {
        "atmosphere": "云雾缭绕",
        "activation": """🌙 「剧本启动」

你跌跌撞撞穿过一片密林，忽然眼前豁然开朗。
一座高山耸立云端，山顶似有金光闪烁。
一只毛脸雷公嘴的猴子从岩石后跳了出来，金箍棒往地上一杵。
"俺老孙等你好久了！"他咧嘴一笑，火眼金睛闪烁。
"想在这天地间闯荡，先过俺老孙这一关！"
——孙悟空在等你。"""
    },
    "jingxing": {
        "atmosphere": "酒旗飘飘",
        "activation": """🌙 「剧本启动」

阳谷县的街道上人来人往，你正走间，忽见一群人围在一家酒店门前。
门内传出一声暴喝："再来十碗！"
你挤进人群，只见一条大汉正坐在角落，酒碗堆成小山，面不改色。
他抬头看见你，眼中精光一闪。
"好汉，过来喝一杯！"他洪声喊道。
——武松在等你。"""
    },
}


class GameMaster:
    """Core game engine for 汇文世界."""

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.session_id = str(uuid.uuid4())[:8]
        database.init_db()

        # Load user or create default
        user = database.get_user(user_id)
        if user:
            self.mode = user.get("mode", "daily")
        else:
            self.mode = "daily"

    # === WenGe (文格) Management ===

    def get_wen_ge_types(self) -> List[Dict[str, str]]:
        """Return available WenGe preset types."""
        path = os.path.join(os.path.dirname(__file__), "..", "data", "wen_ge_presets.json")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data["presets"]

    def init_wen_ge(self, wen_ge_type: str, name: str, background: str, personality: str) -> bool:
        """Initialize user's WenGe profile."""
        self.mode = "daily"
        ok = database.create_user(self.user_id, wen_ge_type, name, background, personality)
        if ok:
            database.update_user_mode(self.user_id, "daily")
        return ok

    # === Character Interaction ===

    def get_character(self, char_id: str) -> Optional[Dict[str, str]]:
        """Get character data."""
        return character.get_character_by_id(char_id)

    def get_all_characters(self) -> List[Dict[str, str]]:
        """Get all available characters."""
        return character.load_all_characters()

    # === Mode Management ===

    def switch_to_script(self, scene_key: str = "red_cliff") -> str:
        """Switch to script mode and return activation text."""
        self.mode = "script"
        database.update_user_mode(self.user_id, "script")

        scene_data = SCENE_ACTIVATION_TEMPLATES.get(scene_key, SCENE_ACTIVATION_TEMPLATES["red_cliff"])
        database.update_session_scene(self.session_id, scene_key, [])

        return scene_data["activation"]

    def switch_to_daily(self) -> str:
        """Switch back to daily mode."""
        self.mode = "daily"
        database.update_user_mode(self.user_id, "daily")
        return "你已经回到了日常模式。随时可以与任何角色聊天，或说「进入剧本」再次开始沉浸体验。"

    # === Relationship & WenMing ===

    def update_relationship(self, char_id: str, level: str, tag: str) -> bool:
        """Update user's relationship with a character."""
        return database.update_user_relationship(self.user_id, char_id, level, tag)

    def update_wenming(self, wenming: str) -> bool:
        """Update user's wenming."""
        return database.update_user_wenming(self.user_id, wenming)

    def get_wenming(self) -> str:
        """Get user's current wenming."""
        user = database.get_user(self.user_id)
        if user:
            return user.get("wenming", "")
        return ""

    # === Memorable Scenes ===

    def record_scene(self, scene_type: str, description: str,
                     participants: List[str], tags: List[str]) -> bool:
        """Record a memorable scene."""
        return database.add_memorable_scene(
            self.session_id, self.user_id, scene_type, description, participants, tags
        )

    def get_scenes(self) -> List[Dict[str, Any]]:
        """Get user's memorable scenes."""
        return database.get_memorable_scenes(self.user_id)

    # === User Info ===

    def get_user_info(self) -> Optional[Dict[str, Any]]:
        """Get full user info."""
        return database.get_user(self.user_id)

    def get_system_prompt(self) -> str:
        """Build full system prompt for AI."""
        prompt_path = os.path.join(os.path.dirname(__file__), "..", "system_prompt.md")
        with open(prompt_path, "r", encoding="utf-8") as f:
            base_prompt = f.read()

        chars = self.get_all_characters()
        char_section = "\n\n## 可用角色\n\n"
        for c in chars:
            char_section += character.build_character_prompt(c)

        user = self.get_user_info()
        user_section = ""
        if user:
            user_section = f"\n\n## 当前用户\n"
            user_section += f"文格类型: {user['wen_ge_type']}\n"
            user_section += f"姓名: {user['name']}\n"
            user_section += f"背景: {user['background']}\n"
            user_section += f"性格: {user['personality']}\n"
            user_section += f"文名: {user.get('wenming', '')}\n"

        mode_note = ""
        if self.mode == "script":
            mode_note = "\n\n**【剧本模式】** 用户当前在剧本模式。请根据场景激活语推进剧情。"
        else:
            mode_note = "\n\n**【日常模式】** 用户在日常模式，自由聊天。"

        return base_prompt + char_section + user_section + mode_note
