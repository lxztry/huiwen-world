# 汇文世界 · 技术规格文档

**版本**：v0.1  
**日期**：2026-04-21  
**状态**：开发中

---

## 一、技术栈

- **语言**：Python 3
- **框架**：Flask（轻量 Web 服务）
- **数据库**：SQLite
- **AI 接口**：GLM/MiniMax（通过 OpenClaw 模型）
- **接入平台**：飞书（作为首个接入平台）

---

## 二、项目结构

```
huiwen-world/
├── characters/               # 角色设定文件（Markdown）
│   ├── lin_daiyu.md        # 林黛玉
│   ├── zhuge_liang.md      # 诸葛亮
│   ├── song_jiang.md       # 宋江
│   ├── wu_song.md          # 武松
│   └── sun_wukong.md       # 孙悟空
├── wen_ge/                  # 文格系统
│   └── wen_ge_system.md    # 文格半定制流程
├── src/                     # 核心代码
│   ├── database.py         # SQLite 数据库层
│   ├── character.py        # 角色加载器
│   ├── game_master.py      # 游戏引擎框架
│   └── app.py             # Flask API 入口
├── data/                    # 数据文件
│   └── wen_ge_presets.json # 文格预设数据
├── templates/               # 前端模板
│   └── index.html          # 主页
├── system_prompt.md         # AI System Prompt
├── README.md
└── SPEC.md                 # 本规格文档
```

---

## 三、核心模块

### 3.1 database.py

SQLite 数据库表：

```sql
-- 用户身份卡
CREATE TABLE users (
    user_id TEXT PRIMARY KEY,
    wen_ge_type TEXT,          -- 文格类型
    name TEXT,                 -- 角色名
    background TEXT,            -- 身世
    personality TEXT,          -- 性格标签
    relationships TEXT,         -- JSON: {character_id: {level, tags}}
    wenming TEXT DEFAULT '',   -- 文名
    created_at TIMESTAMP
);

-- 剧本存档
CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY,
    user_id TEXT,
    mode TEXT,                 -- 'daily' | 'script'
    scene TEXT,
    characters TEXT,           -- JSON: 同屏角色列表
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- 名场面记录
CREATE TABLE memorable_scenes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    user_id TEXT,
    scene_type TEXT,
    description TEXT,
    participants TEXT,         -- JSON: 参与者
    tags TEXT,                  -- JSON: 标签
    created_at TIMESTAMP
);
```

### 3.2 character.py

- 加载 `characters/` 目录下所有 `.md` 文件
- 解析角色设定，生成角色对象
- 支持按 ID 查询角色

### 3.3 game_master.py

- **双模式管理**：日常模式 / 剧本模式
- **场景激活语**：剧本启动时的专属描述
- **名场面记录**：关键时刻自动存档
- **文名更新**：根据用户行为更新文名

### 3.4 app.py

Flask 路由：

```
GET  /                  -- 主页
GET  /api/wen_ge_types  -- 获取文格类型列表
POST /api/wen_ge/init  -- 初始化文格
GET  /api/character/<id> -- 获取角色信息
POST /api/chat         -- 聊天接口
POST /api/script/start -- 启动剧本
POST /api/script/exit  -- 退出剧本
GET  /api/user/<user_id> -- 获取用户状态
```

---

## 四、AI System Prompt

见 `system_prompt.md`，包含：
- 世界观设定
- 角色人设指南
- 双模式切换规则
- 沉浸感设计要点

---

## 五、待完成事项

- [x] 项目结构初始化
- [ ] characters/ 目录：5个角色设定文件
- [ ] wen_ge/ 目录：文格半定制流程
- [ ] src/database.py：SQLite 库
- [ ] src/character.py：角色加载器
- [ ] src/game_master.py：游戏引擎
- [ ] src/app.py：Flask API
- [ ] data/wen_ge_presets.json：文格预设
- [ ] templates/index.html：主页
- [ ] system_prompt.md：AI System Prompt
- [ ] GitHub 初始化 + Pages 部署
