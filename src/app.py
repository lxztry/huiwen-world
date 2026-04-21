"""
汇文世界 · Flask API 入口
REST API for 汇文世界 game engine.
"""

import os
import json
import uuid
from flask import Flask, request, jsonify, render_template
from .game_master import GameMaster


app = Flask(__name__, template_folder="../templates")

# Simple in-memory session store (replace with proper session management in production)
_sessions = {}


def get_gm(user_id: str) -> GameMaster:
    """Get or create a GameMaster instance for a user."""
    if user_id not in _sessions:
        _sessions[user_id] = GameMaster(user_id)
    return _sessions[user_id]


@app.route("/")
def index():
    """Home page."""
    return render_template("index.html")


@app.route("/api/wen_ge_types")
def api_wen_ge_types():
    """Get list of available WenGe types."""
    user_id = request.args.get("user_id", "default")
    gm = get_gm(user_id)
    return jsonify(gm.get_wen_ge_types())


@app.route("/api/wen_ge/init", methods=["POST"])
def api_wen_ge_init():
    """Initialize user's WenGe profile."""
    data = request.get_json()
    user_id = data.get("user_id", "default")
    wen_ge_type = data.get("wen_ge_type", "")
    name = data.get("name", "")
    background = data.get("background", "")
    personality = data.get("personality", "")

    gm = get_gm(user_id)
    ok = gm.init_wen_ge(wen_ge_type, name, background, personality)
    return jsonify({"ok": ok, "message": "文格已确立，欢迎来到汇文世界！" if ok else "创建失败"})


@app.route("/api/character/<char_id>")
def api_character(char_id):
    """Get character info."""
    user_id = request.args.get("user_id", "default")
    gm = get_gm(user_id)
    char = gm.get_character(char_id)
    if char:
        return jsonify(char)
    return jsonify({"error": "角色不存在"}), 404


@app.route("/api/characters")
def api_characters():
    """Get all available characters."""
    user_id = request.args.get("user_id", "default")
    gm = get_gm(user_id)
    chars = gm.get_all_characters()
    return jsonify(chars)


@app.route("/api/chat", methods=["POST"])
def api_chat():
    """Main chat endpoint."""
    data = request.get_json()
    user_id = data.get("user_id", "default")
    message = data.get("message", "")
    char_id = data.get("character_id", "")

    gm = get_gm(user_id)

    # Handle mode switch commands
    if "进入剧本" in message:
        scene_key = data.get("scene_key", "red_cliff")
        activation = gm.switch_to_script(scene_key)
        return jsonify({"mode": "script", "response": activation, "scene_key": scene_key})

    if "出来了" in message or "退出剧本" in message:
        exit_msg = gm.switch_to_daily()
        return jsonify({"mode": "daily", "response": exit_msg})

    if "我的文名" in message:
        wm = gm.get_wenming()
        return jsonify({"response": f"你的文名是：{wm if wm else '暂无（继续积累）'}"})

    # Normal chat - in production this would call the AI model
    # For now, return a placeholder response
    char = gm.get_character(char_id) if char_id else None
    char_name = char.get("name", "未知角色") if char else "角色"

    response = f"【{char_name}】：收到你的消息了。"{message}""

    return jsonify({
        "response": response,
        "mode": gm.mode,
        "character_id": char_id
    })


@app.route("/api/script/start", methods=["POST"])
def api_script_start():
    """Start a script (剧本模式)."""
    data = request.get_json()
    user_id = data.get("user_id", "default")
    scene_key = data.get("scene_key", "red_cliff")

    gm = get_gm(user_id)
    activation = gm.switch_to_script(scene_key)
    return jsonify({"mode": "script", "activation": activation, "scene_key": scene_key})


@app.route("/api/script/exit", methods=["POST"])
def api_script_exit():
    """Exit script mode."""
    data = request.get_json()
    user_id = data.get("user_id", "default")

    gm = get_gm(user_id)
    exit_msg = gm.switch_to_daily()
    return jsonify({"mode": "daily", "response": exit_msg})


@app.route("/api/user/<user_id>")
def api_user(user_id):
    """Get user status."""
    gm = get_gm(user_id)
    info = gm.get_user_info()
    if info:
        return jsonify(info)
    return jsonify({"error": "用户不存在"}), 404


@app.route("/api/scenes/<user_id>")
def api_scenes(user_id):
    """Get user's memorable scenes."""
    gm = get_gm(user_id)
    scenes = gm.get_scenes()
    return jsonify(scenes)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=True)
