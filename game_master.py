"""
汇文世界 · 游戏引擎
核心逻辑：AI 对话生成、剧本模式、模式切换、名场面记录
"""

import json
import uuid
import re
from datetime import datetime
from typing import Optional
from character import build_character_prompt, get_character_info, get_wen_ge_system, list_characters
from database import UserDB, RelationshipDB, ScriptDB, MemorableSceneDB

# LLM API 调用（使用 SiliconFlow / GLM / OpenAI 兼容接口）
LLM_API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
LLM_API_KEY = "your-api-key"  # TODO: 从配置文件读取

FAMILIARITY_LABELS = {
    0: "陌生",
    1: "熟悉",
    2: "知己"
}


def call_llm(system_prompt: str, user_message: str, history: list = None) -> str:
    """调用 LLM 生成回复"""
    import requests

    messages = [{"role": "system", "content": system_prompt}]
    if history:
        for h in history[-10:]:  # 限制历史长度
            messages.append({"role": h['role'], "content": h['content']})
    messages.append({"role": "user", "content": user_message})

    try:
        resp = requests.post(
            LLM_API_URL,
            headers={
                "Authorization": f"Bearer {LLM_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "glm-4",
                "messages": messages,
                "temperature": 0.8,
                "max_tokens": 800
            },
            timeout=30
        )
        data = resp.json()
        return data['choices'][0]['message']['content']
    except Exception as e:
        return f"[系统] LLM 调用出错：{e}。请稍后再试。"


class GameMaster:
    """
    汇文世界游戏引擎
    负责：对话生成、剧本模式、双模式切换、名场面记录
    """

    def __init__(self):
        self.user_db = UserDB()
        self.rel_db = RelationshipDB()
        self.script_db = ScriptDB()
        self.scene_db = MemorableSceneDB()

    # ==================== 用户状态 ====================

    def get_user(self, user_id: str) -> dict:
        return self.user_db.get_user(user_id)

    def register_user(self, user_id: str, wenge_type: str) -> dict:
        """创建新用户"""
        return self.user_db.create_user(user_id, wenge_type)

    def is_registered(self, user_id: str) -> bool:
        return self.user_db.get_user(user_id) is not None

    # ==================== 文格半定制 ====================

    def start_wen_ge_setup(self, user_id: str, wenge_type: str) -> dict:
        """开始文格设置，返回第一组问题"""
        user = self.user_db.get_user(user_id)
        if not user:
            user = self.register_user(user_id, wenge_type)

        wen_ge_prompt = get_wen_ge_system()

        # 返回对应文格的问题组
        question_map = {
            '书香门第': 'A',
            '江湖游侠': 'B',
            '谋士策士': 'C',
            '热血将军': 'D',
            '世家闺秀': 'E'
        }
        group = question_map.get(wenge_type, 'A')

        questions = {
            'A': [
                "🌿 你出身世家，但这个世家现在处境如何？\n\nA. 祖上是名门，如今家道中落，但诗书传家的风气还在\nB. 家族正处鼎盛，父亲在朝中为官\nC. 家族表面风光，内里已经危机四伏\nD. 家族早已败落，靠变卖旧物和亲友接济生活"
            ],
            'B': [
                "⚔️ 你为什么成为游侠？\n\nA. 看不惯权贵欺压百姓，动手打了人，被迫离开家乡\nB. 从小被师父收养，学了一身武艺，下山历练\nC. 家门被奸人陷害，死里逃生，浪迹天涯寻复仇机会\nD. 天生不喜欢被束缚，向往自由"
            ],
            'C': [
                "🎓 你为什么选择做谋士？\n\nA. 觉得凭脑子比凭拳头更有价值\nB. 家学渊源，从小读兵法，有济世志向\nC. 想找一个能施展抱负的主公\nD. 被迫入局——家族利益绑着你，没有选择"
            ],
            'D': [
                "🔥 你是怎么成为将军的？\n\nA. 从小兵一步步打上来，全凭战功\nB. 将门虎子，父亲是名将，继承衣钵\nC. 被逼无奈——边关告急，临时从军\nD. 被人赏识提拔，一步步走到今天"
            ],
            'E': [
                "🌸 你对自己"世家女子"的身份是什么态度？\n\nA. 自豪——出身名门是荣耀，也是责任\nB. 厌倦——这个身份是枷锁，我想挣脱\nC. 矛盾——有骄傲也有无奈\nD. 无感——这个身份是别人给的，不是我选的"
            ]
        }

        return {
            'wenge_type': wenge_type,
            'questions': questions.get(group, questions['A']),
            'step': 1
        }

    def apply_wen_ge_answers(self, user_id: str, answers: list) -> dict:
        """根据用户回答生成文格卡"""
        wenge_type = self.user_db.get_user(user_id)['wenge_type']

        # 根据答案生成文格信息（实际由 LLM 生成，这里用模板）
        templates = {
            '书香门第': {
                'name': '待定（书香门第）',
                'background': '家道中落的世家子弟，靠祖传诗书在世间行走',
                'tags': '内敛、傲气、重情',
                'tendency': '慢热，但一旦交心就极重情义',
                'catchphrase': '唉，说来话长……'
            },
            '江湖游侠': {
                'name': '待定（江湖游侠）',
                'background': '为仗义得罪权贵，被迫流落江湖，以武会友',
                'tags': '洒脱、热血、正义',
                'tendency': '重义气，轻生死',
                'catchphrase': '路见不平，拔刀相助！'
            },
            '谋士策士': {
                'name': '待定（谋士策士）',
                'background': '熟读兵法，胸有韬略，正在寻找明主',
                'tags': '冷静、洞察、持重',
                'tendency': '谋定而后动，不打无把握之仗',
                'catchphrase': '此事还需从长计议……'
            },
            '热血将军': {
                'name': '待定（热血将军）',
                'background': '边关将士出身，历经百战，战功赫赫',
                'tags': '刚烈、忠义、护短',
                'tendency': '护兄弟，也护百姓',
                'catchphrase': '跟我上！'
            },
            '世家闺秀': {
                'name': '待定（世家闺秀）',
                'background': '名门之女，见惯了人情世故，内心向往自由',
                'tags': '聪慧、敏感、外柔内刚',
                'tendency': '话不多但看人极准',
                'catchphrase': '唉……'
            }
        }

        tpl = templates.get(wenge_type, templates['书香门第'])

        self.user_db.update_user(user_id,
            wenge_name=tpl['name'],
            wenge_background=tpl['background'],
            personality_tags=tpl['tags'],
            interpersonal_tendency=tpl['tendency'],
            catchphrase=tpl['catchphrase']
        )

        return {
            'status': 'ok',
            'wenge_card': {
                '文格': wenge_type,
                '姓名': tpl['name'],
                '身世': tpl['background'],
                '性格标签': tpl['tags'],
                '人际倾向': tpl['tendency'],
                '口头禅': tpl['catchphrase']
            }
        }

    # ==================== 日常模式 ====================

    def chat(self, user_id: str, character_id: str, message: str,
             history: list = None) -> str:
        """日常模式对话"""
        user = self.user_db.get_user(user_id)
        if not user:
            return "你还没有设定自己的文格，请先选择文格类型。"

        familiarity = self.rel_db.get_familiarity_level(user_id, character_id)
        system_prompt = build_character_prompt(character_id, user, familiarity)

        reply = call_llm(system_prompt, message, history)

        # 更新关系
        self.rel_db.update_relationship(user_id, character_id)

        return reply

    # ==================== 剧本模式 ====================

    def start_script(self, user_id: str, character_id: str, scene_prompt: str = None) -> dict:
        """开始一个剧本"""
        user = self.user_db.get_user(user_id)
        if not user:
            return {'error': '请先设定文格'}

        # 检查是否有正在进行的剧本
        active = self.script_db.get_active_script(user_id)
        if active:
            return {
                'error': f"你还有一个剧本正在进行：{active['script_name']}，说「出来了」结束后再开始新剧本"
            }

        # 获取角色信息
        char_info = get_character_info(character_id)
        if not char_info:
            return {'error': f'角色 {character_id} 不存在'}

        script_id = str(uuid.uuid4())[:8]

        # 生成场景（如果用户没有指定）
        if not scene_prompt:
            scene_prompt = self._generate_scene(user_id, character_id, char_info)

        # 保存剧本记录
        self.script_db.create_script(user_id, script_id, scene_prompt[:20], [character_id])

        # 更新关系（剧本模式加成）
        self.rel_db.update_relationship(user_id, character_id, familiarity_delta=15, is_script=True)

        return {
            'status': 'script_started',
            'script_id': script_id,
            'activation_text': scene_prompt,
            'character_name': char_info['name']
        }

    def _generate_scene(self, user_id: str, character_id: str, char_info: dict) -> str:
        """生成剧本场景"""
        user = self.user_db.get_user(user_id)
        wenge = user.get('wenge_type', '') if user else ''

        scene_prompts = {
            'lin-daiyu': f"""🌙 「剧本启动」

你走进潇湘馆，满目皆是竹影摇曳，清幽异常。
远处传来低低的咳嗽声，案上的诗稿被风吹动，纸页翻飞。

一个纤弱的少女坐在窗前，手执诗稿，似乎在想着什么心事。
她抬起头，看到了你，眼中闪过一丝讶异，又很快恢复了惯有的忧愁。

「你来了。」她轻声道，「我正想着，前日写的诗……你且帮我看看。」

——林黛玉在等你。""",

            'zhuge-liang': f"""🌙 「剧本启动」

你被引入一间简朴的草庐，四周悬挂着地图与书卷。
一盏油灯微微摇曳，映照着案上的兵书。

一个青衫文士正负手而立，望着墙上的地图，神情专注。
他似乎在思索什么国家大事，连你的到来都未曾察觉。

片刻后，他转过身来，目光深邃而平静。

「久等了。」他淡淡道，「今有一事，想与君相商。」

——诸葛亮在等你。""",

            'song-jiang': f"""🌙 「剧本启动」

你踏上忠义堂的石阶，堂中灯火通明。
一百零八把交椅整齐排列，气势非凡。

一个黑矮的汉子坐在主位上，正看着一封密信，眉头紧锁。
见你进来，他放下信，起身相迎，脸上挤出一丝笑意。

「兄弟来了！」他抱拳道，「正有一件为难事，想听听兄弟的意见。」

——宋江在等你。""",

            'wu-song': f"""🌙 「剧本启动」

你走进一间喧闹的酒馆，酒香四溢，人声鼎沸。
一个身形魁梧的汉子独坐一桌，面前摆着两坛酒。

他抬头看你，目光如炬。
「坐下，喝一碗！」他拍着板凳，声音洪亮。

——武松在等你。""",

            'sun-wukong': f"""🌙 「剧本启动」

你发现自己站在一片云海之上，四周仙气缭绕。
一座仙山若隐若现，山顶有一块巨石，迸发出耀眼的金光。

一个毛脸雷公嘴的猴子坐在石台上，手里拿着一根金光闪闪的棍子。
他对你咧嘴一笑，露出獠牙。

「来得好！」他跳下石台，「俺老孙正无聊得紧！」

——孙悟空在等你。"""
        }

        return scene_prompts.get(character_id,
            f"""🌙 「剧本启动」

你和{char_info['name']}相遇了。

——{char_info['name']}在等你。""")

    def end_script(self, user_id: str, memorable_quote: str = None,
                   user_action: str = None, relationship_effect: str = None) -> dict:
        """结束当前剧本，生成名场面回顾"""
        active = self.script_db.get_active_script(user_id)
        if not active:
            return {'error': '当前没有正在进行的剧本'}

        # 更新剧本状态
        self.script_db.update_script(active['script_id'],
            memorable_quote=memorable_quote or '（无）',
            user_action=user_action or '（无）',
            scene_summary=relationship_effect or '（无）',
            status='completed'
        )

        # 保存名场面
        scene_id = str(uuid.uuid4())[:8]
        characters = json.loads(active['characters']) if active['characters'] else []

        self.scene_db.save_scene(
            user_id, scene_id,
            scene_name=active['script_name'],
            characters=characters,
            key_quote=memorable_quote or '',
            user_action=user_action or '',
            relationship_effect=relationship_effect or '',
            scene_description=f"完成了剧本：{active['script_name']}",
            scene_type='script'
        )

        # 生成名场面回顾
        memorable_review = f"""
✨ 「本场名场面」

📍 剧本：{active['script_name']}
👤 参与角色：{', '.join([get_character_info(c)['name'] for c in characters]) if characters else '未知'}
💬 关键台词：{memorable_quote or '（无）'}
🎭 你的行动：{user_action or '（无）'}
❤️ 关系变化：{relationship_effect or '关系有所进展'}

这是一段难忘的经历。
"""

        return {
            'status': 'script_ended',
            'review': memorable_review,
            'scene_id': scene_id
        }

    def get_active_script_info(self, user_id: str) -> Optional[dict]:
        """获取当前剧本信息"""
        return self.script_db.get_active_script(user_id)

    # ==================== 文名系统 ====================

    def update_wenming(self, user_id: str, **scores) -> dict:
        """更新文名"""
        return self.user_db.update_wenming(user_id, **scores)

    def get_wenming(self, user_id: str) -> dict:
        """获取文名"""
        user = self.user_db.get_user(user_id)
        if not user:
            return {}
        return json.loads(user.get('wenming_score', '{}'))

    # ==================== 角色列表 ====================

    def list_characters(self) -> list:
        return list_characters()

    # ==================== 名场面记录 ====================

    def get_memorable_scenes(self, user_id: str, limit: int = 10) -> list:
        return self.scene_db.get_recent_scenes(user_id, limit)


if __name__ == "__main__":
    gm = GameMaster()
    print("角色列表：")
    for c in gm.list_characters():
        print(f"  {c['character_id']}: {c['name']}（《{c['work']}》）")
