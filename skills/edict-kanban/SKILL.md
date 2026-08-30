---
name: edict-kanban
description: "Use for ANY 军机处看板(kanban) operation — 建卡/流转/进展/子任务/记忆/审计查询. Documents the canonical state machine, the per-role command permissions matrix, and the sanitation rules. 任何看板操作场景触发本技能（所有看板操作必须走本技能，不要直接读写 JSON 文件）。"
---

本技能是看板操作的权威参考：状态机、权限矩阵、命令手册。**任何角色的看板操作都以本技能为准绳。**

## 数据位置

- 任务卡：`data/tasks_source.json`（仓库根 `data/` 目录；看板根目录可用 `EDICT_HOME` 环境变量覆盖，默认仓库根）
- 审计日志：`data/audit_log.json`
- 看板 CLI：`scripts/kanban_update.py`（所有操作必须经由它，**严禁直接读写 JSON**——自行操作文件会因路径问题静默失败，看板卡住不动）

## 状态机（权威定义）

规范流程：`Pending → Taizi → Zhongshu → Menxia → Assigned → Doing → Review → Done`
终态：`Done | Cancelled`

| 当前状态 | 允许流转到 | 说明 |
|----------|-----------|------|
| Pending | Taizi, Cancelled | 待分拣 |
| Taizi | Zhongshu, Cancelled | 太子转中书省 |
| Zhongshu | Menxia, Cancelled, Blocked | 方案提交审议 |
| Menxia | Assigned, Zhongshu, Cancelled | 准奏→派发；封驳→退回中书省 |
| Assigned | Doing, Next, Blocked, Cancelled | 尚书省已派发 |
| Next | Doing, Blocked, Cancelled | 排队 |
| Doing | Review, Done, Blocked, Cancelled | 执行中 |
| Review | Done, Menxia, Doing, Cancelled, PendingConfirm | 产出复核（Review→Menxia 是产出回炉循环） |
| PendingConfirm | Done, Review, Cancelled | 高风险操作待确认 |
| Blocked | (恢复时回到被阻塞前的合法状态), Cancelled | 阻塞 |

**高风险转换（需要对应角色 confirm 才能 Done）**：Review→Done 需门下省确认；Doing→Cancelled 需尚书省确认；Menxia→Cancelled 需中书省确认。

## 命令手册

```bash
# 新建任务（收旨时，仅太子）
python3 scripts/kanban_update.py create JJC-20260223-012 "任务标题" Zhongshu 中书省 中书令

# 更新状态
python3 scripts/kanban_update.py state JJC-20260223-012 Menxia "规划方案已提交门下省"

# 添加流转记录（审计链）
python3 scripts/kanban_update.py flow JJC-20260223-012 "中书省" "门下省" "规划方案提交审核"

# 完成任务（三省内与六部均会用到）
python3 scripts/kanban_update.py done JJC-20260223-012 "/path/to/output" "任务完成摘要"

# 标记阻塞
python3 scripts/kanban_update.py block JJC-20260223-012 "依赖未就绪：xxx"

# 子任务列表（--detail 记录产出详情）
python3 scripts/kanban_update.py todo JJC-20260223-012 1 "实现API接口" in-progress
python3 scripts/kanban_update.py todo JJC-20260223-012 1 "" completed
python3 scripts/kanban_update.py todo JJC-20260223-012 1 "实现API接口" completed --detail "产出：\n- 端点A\n- 端点B\n验证：pytest 通过"

# 实时进展汇报（不改状态，只更新"当前动态"+"计划清单"）
python3 scripts/kanban_update.py progress JJC-20260223-012 "正在分析需求，拟定3个子方案" "调研选型🔄|设计文档|实现原型"

# 记忆操作（角色记忆/任务记忆/共享记忆）
python3 scripts/kanban_update.py memory <agent> <key> <value>
python3 scripts/kanban_update.py task-memo <id> <key> <value>
python3 scripts/kanban_update.py shared-memo <key> <value>

# 高风险确认（Review→Done 等，对应确认方）
python3 scripts/kanban_update.py confirm <id> <approve|reject> "确认理由"

# 委派（中书省/尚书省）
python3 scripts/kanban_update.py delegate <id> <target_agent> <message> <mode>
python3 scripts/kanban_update.py delegate-result <id> <result>
```

`progress` 可选 `--tokens/--cost/--elapsed` 上报成本。

## 权限矩阵（AGENT_POLICY——角色能执行哪些命令）

| 角色 | 允许的命令 |
|------|-----------|
| 太子 taizi | create, state, flow, progress, todo, memory, task-memo |
| 中书省 zhongshu | state, flow, progress, todo, memory, task-memo, delegate |
| 门下省 menxia | state, flow, progress, todo, confirm, memory, task-memo |
| 尚书省 shangshu | state, flow, progress, todo, confirm, delegate, memory, task-memo, shared-memo |
| 六部（户礼兵刑工吏） | progress, todo, done, block, memory, task-memo, delegate-result |

> 身份识别：执行命令时通过环境变量 `OPENCLAW_AGENT_ID` / `OPENCLAW_AGENT` / `EDICT_AGENT_ID` / `AGENT_ID`（或工作目录含 `workspace-<id>`）推断。未知身份不拦截（向前兼容）。**子代理应在看板命令前以 `AGENT_ID=<角色id>` 前缀声明身份**，使越权检测生效。

## 消毒规则（标题/备注/说明）

1. 标题必须是中文概括的一句话（10-30 字），**严禁**文件路径、URL、代码片段
2. **严禁** `Conversation`、`session`、`message_id` 等系统元数据
3. **严禁**「传旨/下旨」前缀（流程词不是任务描述）
4. 全部字符串参数只允许自己概括的中文描述，严禁粘贴原始消息
5. 命令本身会二次消毒（剥离路径/URL/元数据/代码块），但**不要依赖它**——源头就要干净

## 审计

- 所有关键操作写入 `data/audit_log.json`（原子追加，上限 5000 条）：谁、何时、对哪个任务、做了什么、原因
- 越权操作会被拒绝（`权限拒绝` 并退出），并留下审计记录
- 回奏/复盘时通过审计查询完整链路：`flow_log` + `progress_log` + `audit_log`

## 看板界面

- 本地看板 UI：`http://127.0.0.1:7891`（`python3 dashboard/server.py` 启动，读取仓库 `data/`）

## 降级

- 无 shell / 无法运行 CLI → 维护 `data/kanban-offline-log.md`（追加式记录：时间/角色/动作/参数），向皇上声明"看板离线"，恢复后补录。
- 无看板服务（dashboard 未启动）→ 任务卡文件本身仍是权威数据，CLI 操作不受影响；仅实时 UI 不可见。
