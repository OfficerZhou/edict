# 移植 Edict 到新的 Agent 平台（harness）

本指南说明如何为新的平台（IDE/CLI/agent runner）添加支持，让三省六部技能在那里
像在 Claude Code / Codex CLI / dsh 一样自动触发。方法论与参考实现来自
[obra/superpowers](https://github.com/obra/superpowers) 的
`docs/porting-to-a-new-harness.md`（MIT），以下为缩编并适配 Edict 的版本。

## Part 1 — 跨平台工作原理（三组件，内容不变）

| 组件 | 说明 |
|------|------|
| **技能（所有平台共用）** | `skills/*/SKILL.md` 是唯一内容源。正文只描述**动作**（"派一个全新上下文的子代理"、"更新任务卡"），**永不写平台工具名**。每个角色的完整 prompt 内嵌在对应技能正文；语气/案例等人格增强放在技能目录的 `references/` 下（随技能分发，如 `persona-full.md`）。 |
| **工具映射（每平台）** | `skills/using-edict/references/<harness>-tools.md`：动作词汇 → 该平台真实工具名。 |
| **bootstrap（每平台）** | 会话启动时把 `skills/using-edict/SKILL.md` 全文注入模型上下文（`<EXTREMELY_IMPORTANT>` 包裹 + 工具映射附后）。**bootstrap 就是整个集成**——没有它，技能文件躺在磁盘上永远不会被调用。 |

两条铁律：
1. 技能只写动作，不写工具名——**不要**为了适配平台改写 `skills/*/SKILL.md` 正文
2. 一切经平台**自己的**安装机制分发（插件/扩展/市场/上下文文件），**不得**改动用户配置文件

## Part 2 — 平台能否支持（先检查）

硬性要求：平台必须能在**每次会话启动时自动注入文本**（无需用户每次手动开启）。形态任选其一：

- **Shape A**：shell 钩子（会话启动执行命令，读其 stdout）——Claude Code ✓（`hooks/session-start`）
- **Shape B**：进程内插件（会话生命周期回调可改消息数组）——OpenCode/pi
- **Shape C**：上下文文件约定（平台加载你随扩展声明的指令文件）——Codex ✓ 与 dsh ✓（都读项目根 `AGENTS.md`）

能力清单：文件读写/写、shell、子代理派发（可降级）、待办（可降级）、搜索（可降级）。
**可降级能力**的兜底文案已写在技能体内（见 `using-edict` 的降级规则表），映射层只需
"有真工具就用真工具，没有就用兜底"。

**先查能否白拿**：有些"新平台"其实是已有集成的不同安装器（如 Factory Droid 直接消费
Claude Code 插件）。能在 README 加一段话就交付，就是完美的交付。

## Part 3 — 完成标准（Definition of Done）

1. bootstrap 每次会话自动加载（无需用户 opt-in）
2. 存在该平台的工具映射（`references/<harness>-tools.md`）
3. 技能可被实际调用（原生技能机制，或按官方兜底读 `SKILL.md`）
4. **验收测试通过**：干净会话 + 用户消息 `朕要一个 React 待办应用，六部协同办理`
   ——必须先触发 `edict-triaging`（宣布使用技能、建卡），之后才许探索/写代码。
   转录存档 `docs/acceptance/<harness>-<date>.md`
5. 测试覆盖集成（本仓库 `tests/` 下加对应 manifest 测试）
6. 用户可通过平台自己的机制安装（非手拷文件）

快速冒烟：新会话中问模型"描述你的三省六部技能"——bootstrap 注入了它就说得出来。

## Part 4 — 参考实现（照抄最近的）

本仓库**不含平台接入文件**（曾有的 `.claude-plugin/`、`hooks/`、`.codex-plugin/`、`dsh-plugin/`、`AGENTS.md` 与 OpenClaw 部署件已按用户要求移除；备份在会话记录里的 `edict-deleted-20260830.tar.gz`）。接入层参考实现直接取 superpowers 仓库（obra/superpowers，MIT），平台形态与关键文件：

| 平台 | 形态 | 参考文件（均在 obra/superpowers 仓库） | Edict 侧要点 |
|------|------|----------------------------------------|--------------|
| Claude Code | A（shell 钩子） | `.claude-plugin/plugin.json`、`hooks/hooks.json`、`hooks/run-hook.cmd`、`hooks/session-start` | 注入 `skills/using-edict/SKILL.md`；映射用 `skills/using-edict/references/claude-code-tools.md`；无角色子代理文件——subagent 用通用类型 + 内嵌技能 prompt |
| Codex CLI | C（上下文文件） | `.codex-plugin/plugin.json`（`"skills": "./skills/"` + **`"hooks": {}` 必须精确空对象**，否则回退自动发现会重注册 Claude 钩子）、`.agents/plugins/marketplace.json` | 根 `AGENTS.md` 内联 using-edict 全文（Codex 原生加载，无 @include）；映射 `references/codex-tools.md` |
| dsh | C + bundle 插件 | `dsh-plugin/`（Cordis bundle）形态见本仓库备份 | `ctx.skills.registerProvider` 注册 `skills/`；或零代码 `.dsh/skills/` 目录约定；根 `AGENTS.md` 注入；契约以实测为准（`references/dsh-tools.md` 有 TBD 标记） |

## Part 5 — 方法与坑

- **发现机制要实证**：先搜平台文档；找一个该平台的真实第三方插件作样本（比文档可靠，
  能看到实际清单形状）；不要凭训练知识假设。dsh 这类 pre-release 项目尤其如此。
- **让运行中的模型自述工具名**："列出你每个工具的准确机器名"——这是不臆造工具名的权威来源。
- **unique-marker 测试**：往你以为有效的通道注入一个无意义 token，开新会话确认它真的到达了模型。
- **Windows 钩子**：`run-hook.cmd` 用 cmd/bash 双栖 polyglot（无 bash 时静默退出 0，插件仍可加载，
  只是无注入）；git 符号链接需要开发者模式。
- **AGENTS.md 与 SKILL.md 漂移**（Shape C 平台）：生成器内联 using-edict 全文，改动后重生成并做
  CI 漂移比对（Codex/dsh 都不支持 @include）。
- **双发注入**：Claude Code 同时读 `additional_context` 与 `hookSpecificOutput.additionalContext`
  且不去重——钩子只能发射当前平台消费的那一个形状。

## Part 6 — 后续平台（计划中）

- **OpenClaw 作第四平台**：OpenClaw 原生支持 SKILL.md 技能目录约定
  （workspace/skills/<名>/SKILL.md → 第一档目录安装零成本）；
  `OPENCLAW_AGENT_ID` 身份变量已被 `kanban_update.py` 识别。补 `references/openclaw-tools.md`
  与 workspace 注入点即可。
