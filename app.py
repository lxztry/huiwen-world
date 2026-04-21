"""
汇文世界 · Flask 主入口
提供 HTTP API + 飞书 WebSocket 接入
"""

import os
import json
import re
from flask import Flask, request, jsonify
from game_master import GameMaster
from database import init_db

app = Flask(__name__)
gm = GameMaster()

# ==================== 健康检查 ====================

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "world": "汇文世界"})


# ==================== 角色相关 ====================

@app.route("/api/characters", methods=["GET"])
def get_characters():
    """获取所有可用角色"""
    chars = gm.list_characters()
    return jsonify({"characters": chars})


# ==================== 用户注册 ====================

@app.route("/api/users/<user_id>/wenge", methods=["POST"])
def setup_wenge(user_id):
    """开始文格设置"""
    data = request.get_json()
    wenge_type = data.get("wenge_type")
    if not wenge_type:
        return jsonify({"error": "缺少 wenge_type"}), 400

    result = gm.start_wen_ge_setup(user_id, wenge_type)
    return jsonify(result)


@app.route("/api/users/<user_id>/wenge/answers", methods=["POST"])
def apply_wenge_answers(user_id):
    """提交文格回答，生成文格卡"""
    data = request.get_json()
    answers = data.get("answers", [])
    result = gm.apply_wen_ge_answers(user_id, answers)
    return jsonify(result)


# ==================== 日常对话 ====================

@app.route("/api/chat", methods=["POST"])
def chat():
    """日常模式对话"""
    data = request.get_json()
    user_id = data.get("user_id")
    character_id = data.get("character_id")
    message = data.get("message")
    history = data.get("history", [])

    if not all([user_id, character_id, message]):
        return jsonify({"error": "缺少必要参数"}), 400

    reply = gm.chat(user_id, character_id, message, history)
    return jsonify({"reply": reply})


# ==================== 剧本模式 ====================

@app.route("/api/script/start", methods=["POST"])
def start_script():
    """开始剧本"""
    data = request.get_json()
    user_id = data.get("user_id")
    character_id = data.get("character_id")
    scene_prompt = data.get("scene_prompt")

    if not all([user_id, character_id]):
        return jsonify({"error": "缺少必要参数"}), 400

    result = gm.start_script(user_id, character_id, scene_prompt)
    return jsonify(result)


@app.route("/api/script/end", methods=["POST"])
def end_script():
    """结束剧本"""
    data = request.get_json()
    user_id = data.get("user_id")
    memorable_quote = data.get("memorable_quote")
    user_action = data.get("user_action")
    relationship_effect = data.get("relationship_effect")

    result = gm.end_script(user_id, memorable_quote, user_action, relationship_effect)
    return jsonify(result)


# ==================== 文名 ====================

@app.route("/api/users/<user_id>/wenming", methods=["GET"])
def get_wenming(user_id):
    """获取文名"""
    return jsonify(gm.get_wenming(user_id))


# ==================== 名场面 ====================

@app.route("/api/users/<user_id>/scenes", methods=["GET"])
def get_scenes(user_id):
    """获取名场面记录"""
    limit = request.args.get("limit", 10, type=int)
    scenes = gm.get_memorable_scenes(user_id, limit)
    return jsonify({"scenes": scenes})


# ==================== 飞书接入 ====================

@app.route("/feishu/webhook", methods=["POST"])
def feishu_webhook():
    """
    飞书 WebSocket 模式的 webhook（用于接收消息）
    实际通过 WebSocket 长连接接收，参考 feishu_app_scopes 确认权限
    """
    data = request.get_json()
    # 飞书消息格式处理
    return jsonify({"status": "received"})


# ==================== 入口界面 ====================

@app.route("/", methods=["GET"])
def index():
    return """
    <html>
    <head><meta charset="utf-8"><title>汇文世界</title></head>
    <body>
    <h1>📚 汇文世界</h1>
    <p>一个跨作品、跨时空的文学人物宇宙。</p>
    <h2>可用角色</h2>
    <ul>
    {% for c in characters %}
    <li><b>{{ c.name }}</b>（《{{ c.work }}》）- {{ c.identity }}</li>
    {% endfor %}
    </ul>
    <h2>API 文档</h2>
    <ul>
    <li>GET /api/characters - 获取所有角色</li>
    <li>POST /api/chat - 日常对话</li>
    <li>POST /api/script/start - 开始剧本</li>
    <li>POST /api/script/end - 结束剧本</li>
    </ul>
    </body>
    </html>
    """, 200, {"Content-Type": "text/html; charset=utf-8"}


if __name__ == "__main__":
    init_db()
    print("🚀 汇文世界 启动中...")
    app.run(host="0.0.0.0", port=5000, debug=False)
