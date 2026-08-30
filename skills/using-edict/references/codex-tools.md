# Codex CLI 工具映射（edict 动作词汇 → 真实工具）

本文件只做翻译：技能正文中的动作，在 Codex CLI 上对应的真实工具。**Codex 不运行会话启动钩子**——bootstrap 由根目录 `AGENTS.md` 提供（Codex 原生加载，内容与本文件配套）。

| 技能中的动作 | Codex CLI 工具/机制 |
|---|---|
| 读取文件内容 | `Read` |
| 创建/修改文件 | `Write` / `apply_patch`（编辑器工具） |
| 运行 shell 命令（看板 CLI、git、测试） | shell 命令。看板示例：`python3 scripts/kanban_update.py state JJC-xxx Done "…"`（仓库根运行；子代理加前缀 `AGENT_ID=<角色id>`） |
| 搜索文件内容 / 查找文件 | `Grep` / `Glob`（如其实际工具名不同，以 live 会话自述为准） |
| 派发一个全新上下文的子代理 | `spawn_agent` 配 `{fork_turns: "none"}`（新上下文不继承对话），辅以 `wait_agent`（事件订阅等待）、`list_agents`、`followup_task`。需要用户配置 `[features] multi_agent = true`——**未开启时按技能内降级文案**（在会话内角色扮演），并提示用户开启 |
| 更新任务卡 | shell：`python3 scripts/kanban_update.py <create|state|flow|progress|todo|done|block|confirm|…> …` |
| 记录待办清单 | 会话内待办工具（如有）；**看板记录仍必须走 kanban CLI** |
| 加载技能全文 | Codex 插件技能面（`skills/` 目录由插件清单挂载，模型可见技能索引）；若未呈现 → 直接读 `skills/<技能名>/SKILL.md` |
| 询问皇上澄清 | 对话回复（无专门工具时用普通回复） |
| 访问看板 UI | shell 启动 / 请求 `http://127.0.0.1:7891` |
| 网页搜索 | 平台搜索工具（如有）；无则降级（任务内注明资料搜索受限于平台能力） |

## 看板 CLI 调用细节

- 工作目录：项目工作区根（通常即克隆的仓库根，含 `scripts/`、`data/` 配套服务层；仅用 skills/ 时用当前项目目录）
- Python：`python3 scripts/kanban_update.py …`；无 python3 时用 `python`
- 身份前缀：`AGENT_ID=menxia python3 scripts/kanban_update.py state …`
- `EDICT_HOME`：默认仓库根；安装到别处时设置该变量后再运行

## multi_agent 开启（用户侧，可选但推荐）

Codex CLI 配置 `[features] multi_agent = true`（或对应 CLI flag），三省六部才能派发真实独立子代理。未开启时全流程降级为会话内角色扮演——流程与看板纪律不变，只是审核/执行由同一上下文逐个扮演。
