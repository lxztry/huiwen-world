# 汇文世界 · 数据库设计

## 概述

使用 SQLite 存储所有用户数据和关系。数据库文件：`data/huiwen_world.db`

---

## 表结构

### users（用户表）

| 字段 | 类型 | 说明 |
|------|------|------|
| user_id | TEXT PRIMARY KEY | 用户唯一标识（飞书 open_id / 微信 openid） |
| wenge_type | TEXT | 文格类型（书香门第/江湖游侠/谋士策士/热血将军/世家闺秀） |
| wenge_name | TEXT | 用户在世界中的人物名称 |
| wenge_background | TEXT | 用户身世描述（JSON格式） |
| personality_tags | TEXT | 性格标签，逗号分隔 |
| interpersonal_tendency | TEXT | 人际倾向描述 |
| catchphrase | TEXT | 口头禅 |
| wenming_score | TEXT | 文名分数（JSON格式：义薄云天/足智多谋/冷酷无情/多情种子的数值） |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 最后更新时间 |

### relationships（用户与角色关系表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PRIMARY KEY AUTOINCREMENT | 自增ID |
| user_id | TEXT | 用户ID |
| character_id | TEXT | 角色ID（如 lin_daiyu, zhuge_liang） |
| familiarity | INTEGER | 熟悉度 0-100（0=陌生，1=熟悉，2=知己） |
| tags | TEXT | 角色对用户的评价标签（如 侠义、谋略、仁厚），逗号分隔 |
| total_chats | INTEGER | 总对话次数 |
| script_count | INTEGER | 共同经历剧本次数 |
| last_chat_at | TIMESTAMP | 最后对话时间 |
| created_at | TIMESTAMP | 首次互动时间 |

UNIQUE(user_id, character_id)

### scripts（剧本存档表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PRIMARY KEY AUTOINCREMENT | 自增ID |
| user_id | TEXT | 用户ID |
| script_id | TEXT | 剧本唯一ID（UUID） |
| script_name | TEXT | 剧本名称（如 赤壁之战） |
| characters | TEXT | 参与角色列表（JSON格式） |
| user_action | TEXT | 用户关键行动描述 |
| memorable_quote | TEXT | 名场面关键台词 |
| scene_summary | TEXT | 场景总结描述 |
| relationship_changes | TEXT | 关系变化（JSON格式） |
| status | TEXT | 状态（active/completed） |
| started_at | TIMESTAMP | 开始时间 |
| ended_at | TIMESTAMP | 结束时间 |

### memorable_scenes（名场面记录表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PRIMARY KEY AUTOINCREMENT | 自增ID |
| user_id | TEXT | 用户ID |
| scene_id | TEXT | 名场面ID |
| scene_name | TEXT | 名场面名称 |
| characters | TEXT | 参与角色（JSON格式） |
| key_quote | TEXT | 关键台词 |
| user_action | TEXT | 用户的关键行动 |
| relationship_effect | TEXT | 对关系的影响描述 |
| scene_description | TEXT | 场景亮点描述 |
| scene_type | TEXT | 场景类型（日常/剧本） |
| created_at | TIMESTAMP | 创建时间 |

---

## 索引

```sql
CREATE INDEX idx_relationships_user ON relationships(user_id);
CREATE INDEX idx_scripts_user ON scripts(user_id);
CREATE INDEX idx_memorable_user ON memorable_scenes(user_id);
CREATE INDEX idx_scripts_status ON scripts(status);
```

---

## 数据初始化

首次运行时，自动创建以下角色记录：

characters/ 目录下的每个角色文件对应一个 character_id：
- `lin_daiyu` → 林黛玉
- `zhuge_liang` → 诸葛亮
- `song_jiang` → 宋江
- `wu_song` → 武松
- `sun_wukong` → 孙悟空

后续可通过添加新的角色文件扩展角色库。
