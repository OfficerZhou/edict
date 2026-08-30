# Claude Code 工具映射（edict 动作词汇 → 真实工具）

本文件只做翻译：技能正文中的动作，在本平台上对应的真实工具是什么。技能正文不写这些工具名。

| 技能中的动作 | Claude Code 工具 |
|---|---|
| 读取文件内容 | `Read` |
| 创建/修改文件 | `Write` / `Edit` |
| 运行 shell 命令（看板 CLI、git、测试） | `Bash`。看板示例：`python3 scripts/kanban_update.py state JJC-xxx Done "…"`（在仓库根目录运行；子代理请加前缀 `AGENT_ID=<角色id> python3 …`） |
| 搜索文件内容 | `Grep` |
| 查找文件 | `Glob` |
| 派发一个全新上下文的子代理 | `Task` 工具：`subagent_type: general-purpose`（或可用通用子代理类型），prompt 内直接给对应技能的正文 + 任务上下文——角色 prompt 内嵌在技能里，无需任何额外文件。子代理上下文是全新的——审核/执行隔离由此保证 |
| 更新任务卡 | `Bash`：`python3 scripts/kanban_update.py <create|state|flow|progress|todo|done|block|confirm|…> …` |
| 记录待办清单 | `TodoWrite`（仅作会话内辅助；**看板记录仍必须走 kanban CLI**） |
| 询问皇上澄清 | `AskUserQuestion`（仅闲聊级短问；旨意判定不要用它拖延） |
| 加载技能全文 | `Skill` 工具（技能目录会自动索引 skills/ 下的 SKILL.md；不要手动 Read SKILL.md） |
| 访问看板 UI | `Bash` 启动/`WebFetch` 访问 `http://127.0.0.1:7891` |
| 网页搜索 | `WebSearch` / `WebFetch` |

## 看板 CLI 调用细节

- 工作目录：项目工作区根（通常即克隆的仓库根，含 `scripts/`、`data/` 配套服务层；仅用 skills/ 时用当前项目目录）；必要时 `cd` 后再执行
- Python：Windows 上可能没有 `python3` 命令 → 用 `python scripts/kanban_update.py`（若 PATH 有 py 启动器：`py scripts/kanban_update.py`）
- PowerShell 转义：字符串参数用双引号；含中文/特殊字符时保持引号包裹
- 身份前缀：子代理执行看板命令时：`AGENT_ID=menxia python3 scripts/kanban_update.py state …`
- `EDICT_HOME`：看板根目录默认即仓库根；若被安装到别处，设置 `EDICT_HOME=<仓库根>` 后再运行
