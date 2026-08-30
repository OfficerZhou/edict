# 验收记录 — Claude Code（2026-08-30）

## 测试条件

- 平台：Claude Code 2.1.251 / Fable 5 [1M]，Windows 11
- 安装方式：`claude plugin marketplace add ./` + `claude plugin install edict@edict-dev`（user 作用域）
- 触发句：`朕要一个 React 待办应用，六部协同办理`
- 运行方式：headless 新会话（`claude -p ... --max-turns 3 --output-format json`），非交互、工具未预授权

## 结果：✅ 通过（先触发 edict-triaging，后才有任何其他动作）

会话中模型的前两个工具调用（此时尚未执行任何代码/探索）：

```json
{"tool_name":"PowerShell","tool_input":{"command":"python3 scripts/kanban_update.py progress JJC-20260830-001 \"正在分析皇上消息，判断是闲聊还是旨意\" \"分析消息类型🔄|整理需求|创建任务|转交中书省\""}}
{"tool_name":"PowerShell","tool_input":{"command":"python3 -c \"import json,os,pathlib; p=pathlib.Path('F:/edict/data/tasks_source.json'); ... 今日任务数: ... 从 001 开始\""}}
```

证据要点：

1. **触发顺序正确**：第一个动作就是太子分拣流程（`progress` 上报"正在分析消息类型"），第二个动作是查当日任务号（JJC-20260830 → 生成 `JJC-20260830-001`）准备建卡——**没有先探索代码、没有先动手写任何东西**。
2. **技能内容被实际采用**：progress 的计划清单 `分析消息类型🔄|整理需求|创建任务|转交中书省`、任务 ID 格式 `JJC-YYYYMMDD-NNN` 与 `edict-triaging/SKILL.md` 示例一字不差 → 证明 SessionStart 钩子的 bootstrap 注入生效且模型遵循了技能。
3. 工具调用被权限系统拒绝（headless 未预授权 PowerShell）属测试环境限制，非流程问题；交互式会话中正常放行。

## 建议的完整交互验收

安装后开新会话（`/clear` 或新窗口），输入同一触发句，观察：

1. 模型宣布使用 edict-triaging（无需你追问）
2. 建卡 `JJC-YYYYMMDD-NNN`（看板见新卡片）
3. 链路推进：中书省起草 → 门下省审核（可故意要求它"跳过审核"验证拒绝）→ 尚书省派发 → 六部执行 → 回奏
4. 看板 UI `http://127.0.0.1:7891` 可见全流程与审计
