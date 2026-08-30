# DeepSeek Harness (dsh) 工具映射（edict 动作词汇 → 真实工具）

> ⚠️ **本表部分行为 live 实测后填充。** dsh 为 pre-release（`dsh ≥ 0.1.0-rc.6`，API 可能漂移）。
> 填充方法（porting 指南）：在 live 会话中要求模型"枚举你每一个工具的准确机器名"，并用 unique-marker 测试验证每个假设。标注 `TBD` 的条目在实测前不要信任。

| 技能中的动作 | dsh 工具/机制 |
|---|---|
| 读取文件内容 | 文件读取工具（工具名 TBD — 实测填充） |
| 创建/修改文件 | 文件写入/编辑工具（TBD） |
| 运行 shell 命令（看板 CLI、git、测试） | shell 工具（TBD）。看板示例：`python3 scripts/kanban_update.py state JJC-xxx Done "…"`（仓库根运行；子代理加前缀 `AGENT_ID=<角色id>`） |
| 搜索文件内容 / 查找文件 | 搜索工具（TBD） |
| 派发一个全新上下文的子代理 | dsh 子代理能力（`@deepseek-ai/dsh-agent-teams` 等生态插件：可延续子代理、mailbox DM、`attempt_id` 语义；工具名与配置 TBD — 实测填充）。不可用时按技能内降级文案角色扮演 |
| 更新任务卡 | shell：`python3 scripts/kanban_update.py <create|state|flow|progress|todo|done|block|confirm|…> …` |
| 加载技能全文 | `skill` 工具（`dsh-tool-skill` 消费技能注册表，模型可见 name+description 目录并可按需加载全文；我们的插件把 `skills/` 注册为 custom 源，rank 300） |
| 会话启动注入（bootstrap） | `@deepseek-ai/dsh-agent-instructions` 自动加载 `AGENTS.md` 链（项目根 → 当前目录；本仓库根的 `AGENTS.md` 即注入源，内联全文，dsh 无 @include 语法） |
| 询问皇上澄清 | 对话回复 |
| 访问看板 UI | shell 启动 / 请求 `http://127.0.0.1:7891` |
| 网页搜索 | 平台搜索工具（TBD / 或降级） |

## dsh 安装与验证要点

- 技能注册：`dsh` bundle 插件（`dsh-plugin/`）通过 `ctx.skills.registerProvider` 把仓库 `skills/` 注册为 `custom` 源；或零代码路径：项目放 `.dsh/skills/`（dsh 原生扫描用户级 `~/.dsh/skills/` 与项目级 `.dsh/skills/`）
- 安装：`dsh plugin --profile web add <仓库路径>` → `dsh --profile web --dump-config` 验证 bundle 行 → 重启
- 验证：Skill Center / headless 会话中应列出 8 个 edict 技能；用中文触发句实测

## 看板 CLI 调用细节

- 工作目录：仓库根；Python：`python3`（dsh 环境一般具备）
- 身份前缀：`AGENT_ID=<角色id> python3 scripts/kanban_update.py …`
- `EDICT_HOME`：默认仓库根；安装到别处时设置该变量
