# 汇文世界 · Literary Universe

**跨作品、跨时空的文学人物宇宙**

四大名著（《红楼梦》《水浒传》《三国演义》《西游记》）的角色在此共存——林黛玉可以在赤壁遇见诸葛亮，鲁智深可以和武松一起喝酒。

## 功能特色

- **🎭 5位经典角色** — 林黛玉、诸葛亮、宋江、武松、孙悟空
- **📜 文格系统** — 半定制用户身份，找到属于你的角色类型
- **💬 双模式体验** — 日常聊天 + 剧本沉浸，随意切换
- **🤝 角色关系** — 三层关系系统（陌生→熟悉→知己）
- **📖 名场面记录** — 记录你的高光时刻
- **🏆 文名系统** — 积累你的名声标签

## 快速开始

### 1. 安装依赖

```bash
pip install flask
```

### 2. 运行服务

```bash
cd huiwen-world
python -m src.app
```

服务启动于 `http://localhost:5001`

### 3. API 文档

| 接口 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 主页 |
| `/api/wen_ge_types` | GET | 获取文格类型 |
| `/api/wen_ge/init` | POST | 初始化文格 |
| `/api/characters` | GET | 获取所有角色 |
| `/api/character/<id>` | GET | 获取单个角色 |
| `/api/chat` | POST | 聊天接口 |
| `/api/script/start` | POST | 启动剧本 |
| `/api/script/exit` | POST | 退出剧本 |
| `/api/user/<user_id>` | GET | 用户状态 |
| `/api/scenes/<user_id>` | GET | 名场面记录 |

### 4. 初始化数据库

```bash
cd huiwen-world
python -m src.database
```

## 项目结构

```
huiwen-world/
├── characters/           # 角色设定（Markdown）
├── wen_ge/              # 文格系统
├── src/                 # 核心代码
│   ├── database.py    # SQLite 数据库
│   ├── character.py   # 角色加载器
│   ├── game_master.py # 游戏引擎
│   └── app.py         # Flask API
├── data/               # 数据文件
├── templates/          # 前端模板
├── system_prompt.md    # AI System Prompt
└── SPEC.md            # 技术规格
```

## 技术栈

- **语言**: Python 3
- **框架**: Flask
- **数据库**: SQLite
- **AI**: GLM / MiniMax（通过 OpenClaw 模型）

## 接入平台

- [ ] 飞书（开发中）
- [ ] 微信
- [ ] Telegram

---

*「愿你在汇文世界里，找到属于自己的文学知己。」*
