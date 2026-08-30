<h1 align="center">⚔️ 三省六部 · Edict</h1>

<p align="center">
  <strong>我用 1300 年前的帝国制度，重新设计了 AI 多 Agent 协作架构。<br>结果发现，古人比现代 AI 框架更懂分权制衡。</strong>
</p>

<p align="center">
  <sub>三省六部 = 8 个通用技能（角色 prompt 内嵌，任何 agent 平台可用）：太子分拣、中书省规划、门下省审核封驳、尚书省派发、六部并行执行、回奏。<br>比 CrewAI 多一层<b>制度性审核</b>，比 AutoGen 多一个<b>看板</b>。</sub>
</p>

<p align="center">
  <a href="#-demo">🎬 看 Demo</a> ·
  <a href="#-30-秒快速体验">🚀 30 秒体验</a> ·
  <a href="#-架构">🏛️ 架构</a> ·
  <a href="#-功能全景">📋 看板功能</a> ·
  <a href="docs/task-dispatch-architecture.md">📚 架构文档</a> ·
  <a href="README_EN.md">English</a> ·
  <a href="CONTRIBUTING.md">参与贡献</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Harness-Agnostic-8B5CF6?style=flat-square" alt="Any Harness">
  <img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Skills-8-8B5CF6?style=flat-square" alt="Agents">
  <img src="https://img.shields.io/badge/Dashboard-Real--time-F59E0B?style=flat-square" alt="Dashboard">
  <img src="https://img.shields.io/badge/License-MIT-22C55E?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/Frontend-React_18-61DAFB?style=flat-square&logo=react&logoColor=white" alt="React">
  <img src="https://img.shields.io/badge/Backend-stdlib_only-EC4899?style=flat-square" alt="Zero Backend Dependencies">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/公众号-cft0808-07C160?style=for-the-badge&logo=wechat&logoColor=white" alt="WeChat">
</p>

---

## 🎬 Demo

<p align="center">
  <video src="docs/Agent_video_Pippit_20260225121727.mp4" width="100%" autoplay muted loop playsinline controls>
    您的浏览器不支持视频播放，请查看下方 GIF 或 <a href="docs/Agent_video_Pippit_20260225121727.mp4">下载视频</a>。
  </video>
  <br>
  <sub>🎥 三省六部 AI 多 Agent 协作全流程演示</sub>
</p>

<details>
<summary>📸 GIF 预览（加载更快）</summary>
<p align="center">
  <img src="docs/demo.gif" alt="三省六部 Demo" width="100%">
  <br>
  <sub>一句话下旨 → 太子分拣 → 中书省规划 → 门下省审议 → 六部并行执行 → 奏折回报（30 秒）</sub>
</p>
</details>

---

## 🤔 为什么是三省六部？

大多数 Multi-Agent 框架的套路是：

> *"来，你们几个 AI 自己聊，聊完把结果给我。"*

然后你拿到一坨不知道经过了什么处理的结果，无法复现，无法审计，无法干预。

**三省六部的思路完全不同** —— 我们用了一个在中国存在 1400 年的制度架构：

```
你 (皇上) → 太子 (分拣) → 中书省 (规划) → 门下省 (审议) → 尚书省 (派发) → 六部 (执行) → 回奏
```

这不是花哨的 metaphor，这是**真正的分权制衡**：

| | CrewAI | MetaGPT | AutoGen | **三省六部** |
|---|:---:|:---:|:---:|:---:|
| **审核机制** | ❌ 无 | ⚠️ 可选 | ⚠️ Human-in-loop | **✅ 门下省专职审核 · 可封驳** |
| **实时看板** | ❌ | ❌ | ❌ | **✅ 军机处 Kanban + 时间线** |
| **流转审计** | ⚠️ | ⚠️ | ❌ | **✅ 完整奏折存档** |
| **部署难度** | 中 | 高 | 中 | **低 · 技能目录约定 / 一键安装器** |

> **核心差异：制度性审核 + 完全可观测 + 实时可干预**

<details>
<summary><b>🔍 为什么「门下省审核」是杀手锏？（点击展开）</b></summary>

<br>

CrewAI 和 AutoGen 的 Agent 协作模式是 **"做完就交"**——没有人检查产出质量。就像一个公司没有 QA 部门，工程师写完代码直接上线。

三省六部的 **门下省** 专门干这件事：

- 📋 **审查方案质量** —— 中书省的规划是否完备？子任务拆解是否合理？
- 🚫 **封驳不合格的产出** —— 不是 warning，是直接打回重做
- 🔄 **强制返工循环** —— 直到方案达标才放行

这不是可选的插件——**它是架构的一部分**。每一个旨意都必须经过门下省，没有例外。

这就是为什么三省六部能处理复杂任务而结果可靠：因为在送到执行层之前，有一个强制的质量关卡。1300 年前唐太宗就想明白了——**不受制约的权力必然会出错**。

</details>

---

## ✨ 能力全景

### 🏛️ 制度流程（分权制衡，不是建议而是流程）

- **太子分拣** —— 闲聊直接回，旨意才建任务（≥10 字 + 动作词 + 目标；含「传旨/下旨」前缀必走流程）
- **中书省规划** —— 起草方案（≤500 字）：谁来做 / 做什么 / 怎么做 / 交付物
- **门下省审核** —— 四维对抗审议（可行性/完整性/风险/资源），**❌ 封驳打回重做**（≤3 轮，第 3 轮强制准奏+附建议）；审核由全新上下文的子代理执行，与起草方零共享上下
- **尚书省派发** —— 按职责矩阵并行调度六部（代码任务必含 工部实现 + 刑部测试）
- **六部执行** —— 专项执行，先验证再报完成
- **回奏** —— 基于看板事实链（流转/进度/审计）的奏折，先 done 后呈报

### 🛡️ 制度性审核 + 完全可观测

- 状态机校验：`kanban_update.py` 内置 `_VALID_TRANSITIONS`，非法跳转（Doing→Taizi）被拒绝并记日志
- 权限矩阵：每个角色的看板命令白名单（AGENT_POLICY），越权即拒
- 审计日志：每次建卡/流转/确认落 `data/audit_log.json`（原子写、上限 5000 条）
- 旨意数据清洗：标题/备注自动剥离文件路径、URL、系统元数据、传旨前缀

### 🧩 通用技能包（任何 harness）

- 技能正文只写动作不写平台工具名（工具映射在 `skills/using-edict/references/<harness>-tools.md`）
- 拷走 `skills/` 一个目录即可在任何平台跑全流程；无子代理/无 shell 能力时按技能内降级文案继续
- 根目录 `install-skills.sh` / `install-skills.ps1` 一键装到当前平台

### 📋 军机处看板（本地 · 零依赖）

- 状态分列（待分拣 → 执行中 → 已完成）+ 每 5 秒自动刷新
- 点卡片看完整流转时间线（含封驳记录）+ 审计追溯
- 深浅色自适应；点空白处自动关闭详情侧边栏
- 纯读：agent 用 CLI 写卡，看板只做"眼睛"（`python board/server.py` → http://127.0.0.1:7891）

### 📦 任务产物约定

- 每个旨意的产物（代码/文档/报告）统一落盘 `output/<任务ID>/`（如 `output/JJC-20260830-001/`），运行产物带时间戳
- `output/` 整体 gitignore —— 本地产物不入库

---

## 🚀 30 秒快速体验

### 三步跑通（本地，零依赖）

```powershell
cd F:\edict
.\install-skills.ps1     # 1. 把 8 个技能装进当前 agent（Claude Code/Codex/dsh 自动检测）
.\start.ps1              # 2. 启动军机处看板 → http://127.0.0.1:7891
```
然后对 agent 说：「朕要一个 React 待办应用，六部协同办理」——太子分拣建卡 → 中书省规划 → 门下省审核（故意提模糊需求可触发封驳）→ 尚书省派发 → 六部执行 → 回奏，看板实时可见。

> 历史演示镜像 `docker run cft0808/sansheng-demo` 仍可运行（旧版看板，仅供怀旧；Docker 相关源码已随通用化移除）。


### 🧩 通用技能包（Harness 无关）

三省六部不做任何 agent 平台的私生子：**`skills/` 是自足的通用技能包**（Agent Skills 标准，`SKILL.md` + 动作语言——技能正文不写平台工具名），每个角色的完整 prompt 与人格增强都内嵌在技能内；拷走 `skills/` 一个目录，任何支持技能目录约定的 agent 都能跑完整流程（分拣→规划→审核→派发→执行→回奏），无任何平台/仓库硬依赖。

#### 🧰 一键安装到当前 agent（推荐）

任意 agent 克隆本仓库后，运行根目录安装器即可自动把 8 个技能装到它所在平台的技能目录（自动检测 Claude Code / Codex CLI / DeepSeek Harness，也可 `--target` 指定）：

```bash
git clone git@github.com:OfficerZhou/edict.git && cd edict
./install-skills.sh              # 复制安装（新会话立即生效）
./install-skills.sh --link      # 符号链接安装，仓库更新自动跟随
./install-skills.sh --dry-run   # 只看计划不写入
```

Windows PowerShell：

```powershell
.\install-skills.ps1            # 复制安装
.\install-skills.ps1 -Link      # 目录联接（免管理员），跟随仓库更新
```

装好后开新会话，说「朕要一个 React 待办应用，六部协同办理」验证触发。各平台技能目录的手工位置见 `docs/porting-edict-to-a-harness.md` Part 1。

通用层的三件事（详见 `docs/porting-edict-to-a-harness.md`）：

1. **技能内容**：`skills/*/SKILL.md` 全平台共用，正文只写动作（"派一个全新上下文的子代理"、"更新任务卡"），可降级能力（无子代理/无 shell）的兜底文案内嵌
2. **工具映射**：`skills/using-edict/references/<harness>-tools.md` 把动作翻译成该平台真实工具
3. **bootstrap**：会话启动时把 `skills/using-edict/SKILL.md` 注入上下文（平台自己的机制：钩子/上下文文件/插件）——没有它技能"躺着没被调用"，所以各平台打包时补这一层即可

> 本仓库**不含任何平台接入文件**（曾有的 `.claude-plugin/`、`hooks/`、`.codex-plugin/`、`dsh-plugin/`、`AGENTS.md` 等平台层与 OpenClaw 部署件均已移除，按需恢复或按移植指南重打包——备份：`claude` 会话记录中的 `edict-deleted-20260830.tar.gz`）。
>
> 验收标准（任何平台）：干净会话中说「朕要一个 React 待办应用，六部协同办理」，agent 必须先触发 `edict-triaging`（建任务卡、转中书省），之后才许写代码。

#### 军机处看板（可选配套）

`board/`（单文件网页 + 零依赖 stdlib API）+ `scripts/kanban_update.py` 是看板配套服务：agent 用 CLI 写卡，看板直接读 `data/` 实时渲染，无数据库、无刷新循环：

```bash
python board/server.py   # 看板 UI → http://127.0.0.1:7891
```

#### 启动

```powershell
# Windows（推荐）：一键启动军机处看板
.\start.ps1                  # Ctrl+C 关闭；-Port 8080 指定端口

# 或直接启动（任何平台）
python board/server.py       # 看板 UI → http://127.0.0.1:7891
```

> 💡 **看板即开即用**：`board/board.html` 单文件前端（深浅色自适应），读取 `data/` 下任务卡实时渲染，点卡片看完整流转时间线 + 审计

---

## 🏛️ 架构

```
👑 皇上（你，任何 agent 对话里一句话下旨）
        │
   ┌────▼────────────────────────────────────────────┐
   │  三省六部技能链（skills/ · 角色 prompt 内嵌）       │
   │  太子分拣 → 中书省规划 → 门下省审核(可封驳)          │
   │        → 尚书省派发 → 六部并行 → 回奏             │
   │   每个角色 = 一个技能；子代理能力可用时交由          │
   │   全新上下文子代理执行（审核隔离），否则角色扮演      │
   └────┬────────────────────────────────────────────┘
        │ 看板 CLI（scripts/kanban_update.py）
   ┌────▼────────────────────────────────────────────┐
   │  军机处黑板（data/tasks_source.json + audit_log） │
   │  军机处看板 board/（只读绘制：状态列/时间线/审计）   │
   │  任务产物 output/<任务ID>/（本地产物，不入库）      │
   └─────────────────────────────────────────────────┘
```

### 角色 × 技能映射

| 角色 | 技能 | 职责 | 看板命令权限（AGENT_POLICY） |
|------|------|------|------|
| 太子 | `edict-triaging` | 分拣、建卡、转交、回奏 | create/state/flow/progress/todo |
| 中书省 | `edict-planning` | 规划（≤500 字）、驱动审核与执行 | state/flow/progress/todo/delegate |
| 门下省 | `edict-review` | 四维对抗审议、封驳 | state/flow/progress/todo/confirm |
| 尚书省 | `edict-dispatch` | 派发矩阵、并行调度、汇总 | state/flow/progress/todo/confirm/delegate |
| 六部 | `edict-ministries` | 专项执行（工/兵/户/礼/刑/吏） | progress/todo/done/block |
| 回奏 | `edict-report` | 基于事实链的奏折 | —（流程末环） |
| 看板 | `edict-kanban` | 状态机/权限/命令权威手册 | —（只读） |

> 完整权限矩阵（谁能执行哪些命令）与状态机定义见 `skills/edict-kanban/SKILL.md`——技能即文档。


### 任务状态流转

```
皇上 → 太子分拣 → 中书规划 → 门下审议 → 已派发 → 执行中 → 待审查 → ✅ 已完成
                      ↑          │                              │
                      └──── 封驳 ─┘                    阻塞 Blocked
```

> ⚡ **状态转换受保护**：`kanban_update.py` 内置 `_VALID_TRANSITIONS` 状态机校验，
> 非法跳转（如 Doing→Taizi）会被拒绝并记录日志，确保流程不可绕过。
>
> 🔄 **异步事件驱动**：服务间通过 Redis Streams EventBus 解耦通信，Outbox Relay 保障事件可靠投递。
> 所有状态变更自动写入审计日志（`audit.py`），支持完整追溯。

---

## 📁 项目结构

```
edict/
├── skills/                     # 通用技能包（harness 无关，核心）
│   ├── using-edict/            # 总纲：技能目录/铁律/降级 + 平台工具映射
│   ├── edict-triaging/         # 太子 · 分拣（角色 prompt 内嵌）
│   ├── edict-planning/         # 中书省 · 规划
│   ├── edict-review/           # 门下省 · 审核封驳
│   ├── edict-dispatch/         # 尚书省 · 派发
│   ├── edict-ministries/       # 六部 · 执行（references/depts 含各部人格）
│   ├── edict-report/           # 回奏
│   └── edict-kanban/           # 看板操作手册（状态机/权限矩阵）
├── board/
│   ├── board.html              # 军机处看板（单文件 · 零依赖）
│   └── server.py               # 看板 API（Python 标准库 · 零依赖）
├── scripts/
│   ├── kanban_update.py        # 看板 CLI（状态机校验/权限/审计 — agent 写卡唯一入口）
│   ├── file_lock.py            # 文件锁（防多 Agent 并发写入）
│   └── utils.py                # 公共工具
├── edict/backend/              # 事件驱动后端（SQLAlchemy + Redis）
│   ├── app/models/             #   task.py 状态机 / audit / outbox
│   ├── app/services/           #   event_bus / task_service
│   └── app/workers/            #   dispatch / orchestrator / outbox_relay
├── tests/
│   ├── test_kanban.py          # 看板 CLI 单元测试
│   ├── test_e2e_kanban.py      # 端到端测试（17 个断言）
│   ├── test_state_machine_consistency.py  # 状态机一致性测试
│   └── test_skills_metadata.py # 技能元数据/中性词汇 lint
├── data/                       # 运行时数据（gitignored）
├── docs/
│   ├── porting-edict-to-a-harness.md    # 📚 移植指南：接入任何 agent 平台
│   ├── task-dispatch-architecture.md    # 架构文档：任务分发、流转、调度的完整设计
│   ├── wechat-article.md                # 微信文章
│   └── screenshots/                     # 功能截图
├── install-skills.sh / .ps1    # 一键安装器（把 skills/ 装进当前平台的技能目录）
├── start.ps1                   # 一键启动军机处看板（Windows）
├── CONTRIBUTING.md             # 贡献指南
└── LICENSE                     # MIT License
```
```

---

## 🎯 使用方法

### 向 AI 下旨

在装了三省六部技能的 agent 对话里，直接对皇上口吻的用户下旨：

```
给我设计一个用户注册系统，要求：
1. RESTful API（FastAPI）
2. PostgreSQL 数据库
3. JWT 鉴权
4. 完整测试用例
5. 部署文档
```

**然后坐好，看戏：**

1. 📜 中书省接旨，规划子任务分配方案
2. 🔍 门下省审议，通过 / 封驳打回重规划
3. 📮 尚书省准奏，派发给兵部 + 工部 + 礼部
4. ⚔️ 各部并行执行，进度实时可见
5. 📮 尚书省汇总结果，回奏给你

全程可在**军机处看板**实时监控，随时可以**叫停、取消、恢复**。

### 看产物

每个旨意的产物统一在 `output/<任务ID>/`（代码/文档/报告，本地产物不入库）：
```
output/JJC-20260830-001/    # 工具 + 使用指南 + 时间戳运行报告
```

### 干预任务

看板只读，干预走 CLI（含状态机校验与高风险二次确认）：
```bash
python scripts/kanban_update.py state JJC-xxx Blocked "依赖未就绪"   # 挂起
python scripts/kanban_update.py state JJC-xxx Cancelled "取消"       # 取消（高风险需确认）
python scripts/kanban_update.py confirm JJC-xxx approve "确认"       # 高风险转换确认
```

### 角色人格在哪

角色完整 prompt 内嵌在对应技能正文；语气/案例等人格增强在 `skills/edict-*/references/` 下（随技能分发）。

---

## 🔧 技术亮点

| 特点 | 说明 |
|------|------|
| **React 18 前端** | TypeScript + Vite + Zustand 状态管理，13 个功能组件 |
| **纯 stdlib 后端** | `server.py` 基于 `http.server`，零依赖，同时提供 API + 静态文件服务 |
| **EventBus 事件总线** | Redis Streams 发布/订阅，服务间解耦通信 |
| **Outbox Relay** | 事务性 Outbox 模式，保障事件可靠投递（至少一次语义） |
| **状态机审计** | 严格生命周期状态转换 + 完整审计日志（`audit.py`） |
| **并行调度引擎** | Dispatch Worker 支持并行执行、指数退避重试、资源锁 |
| **DAG 编排器** | Orchestrator 基于 DAG 的任务分解与依赖解析 |
| **Agent 思考可视** | 实时展示 Agent 的 thinking 过程、工具调用、返回结果 |
| **通用技能包** | `skills/` 拷到任何 agent 技能目录即可用（无平台/仓库硬依赖） |
| **看板启动** | `.\start.ps1`（Windows 一键）/ `python board/server.py` |
| **实时刷新** | 看板每 5 秒自动拉取任务卡（页面内开关可关） |

---

## � 深入了解

### 核心文档

- **[📖 任务分发流转完整架构](docs/task-dispatch-architecture.md)** — **必读文档**
  - 详细讲解三省六部如何处理复杂任务的业务设计和技术实现
  - 涵盖：9大任务状态机 / 权限矩阵 / 4阶段调度（重试→升级→回滚）/ Session JSONL数据融合
  - 包含完整的使用案例、API端点说明、CLI工具文档
  - 对标 CrewAI/AutoGen：为什么制度化>自由协作
  - 故障场景与恢复机制
  - **读这个文档会理解为什么三省六部这么强大**（9500+ 字，30 分钟完整理解）

- **[🤝 贡献指南](CONTRIBUTING.md)** — 想参与贡献？从这里开始

---
## 🔧 常见问题排查

<details>
<summary><b>❌ 命令后看板没变化 / 服务没启动</b></summary>

**排查**：
```bash
python board/server.py            # 直接启动看板（127.0.0.1:7891）
python scripts/kanban_update.py flow JJC-xxx "太子" "机关" "测试"   # 验证 CLI 可写
```

**常见原因**：
- 看板进程未启动（`\start.ps1` 或 `python board/server.py`）；端口被占（`-Port 8080` 换端口）
- 任务卡文件损坏：清 `data/tasks_source.json` 为 `[]` 后重来（仅测试环境）
- 命令字符串含未引号中文 → 加引号

<details>
> （历史演示镜像 `cft0808/sansheng-demo` 与已移除的 Docker 部署文档仅存于 git 历史，当前版本无 Docker 相关源码）

<details>
<summary><b>❌ agent 没触发三省六部流程</b></summary>

**排查**：
1. 确认技能已装：`ls ~/.claude/skills/` 下有 `edict-triaging` 等 8 个目录
2. 开新会话（技能索引在会话启动时加载）；`/clear` 后再试
3. 触发句要有动作词+目标（≥10 字）：`「朕要一个 React 待办应用，六部协同办理」`；加前缀「传旨：」强制走流程
4. 模型偶尔漏触发时，在项目说明文件（AGENTS.md/CLAUDE.md）里加一句"任务消息先用 edict-triaging"兜底

---
## �🗺️ Roadmap

> 完整路线图及参与方式：[ROADMAP.md](ROADMAP.md)

### Phase 1 — 核心架构 ✅
- [x] 通用技能包（harness 无关）：8 个 SKILL.md 技能，角色 prompt 内嵌，可降级
- [x] 制度性审核（门下省四维对抗审议 + 封驳闭环 ≤3 轮 + 全新上下文隔离）
- [x] 军机处看板 v2（零依赖：状态分列 / 流转时间线 / 审计追溯 / 5s 刷新）
- [x] 任务流转状态机 + 权限矩阵 + 审计日志（kanban_update.py CLI 强制）
- [x] 任务产物约定（output/<任务ID>/，本地产物不入库）
- [x] 一键安装器（install-skills.sh / .ps1：自动检测 Claude Code/Codex/dsh 技能目录）
- [x] 移植指南（docs/porting-edict-to-a-harness.md：任何平台自建薄层接入）
- [x] 旨意数据清洗（路径/元数据/前缀自动剥离）
- [x] 重复任务防护 + 已完成任务保护
- [x] 端到端测试覆盖（17 个断言）
- [x] React 18 前端重构（TypeScript + Vite + Zustand · 13 组件）
- [x] Agent 思考过程可视化（实时 thinking / 工具调用 / 返回结果）
- [x] 前后端一体化部署（server.py 同时提供 API + 静态文件服务）

### Phase 2 — 制度深化 🚧
- [ ] 御批模式（人工审批 + 一键准奏/封驳）
- [x] 功过簿（Agent 绩效评分 + 模型推荐 + 成本优化）
- [x] EventBus 事件总线（Redis Streams 解耦通信）
- [x] Outbox Relay（事务性事件投递）
- [x] 状态机审计（严格生命周期 + 审计日志）
- [x] 并行调度引擎（指数退避重试 + 资源锁）
- [x] DAG 编排器（任务分解 + 依赖解析）
- [x] Dashboard 鉴权（登录认证）
- [x] 一键启动 / systemd 生产部署
- [ ] 急递铺（Agent 间实时消息流可视化）
- [ ] 国史馆（知识库检索 + 引用溯源）

### Phase 3 — 生态扩展
- [ ] Notion / Linear 适配器
- [ ] 年度大考（Agent 年度绩效报告）
- [ ] 移动端适配 + PWA
- [ ] ClawHub 上架

---

## 🤝 参与贡献

欢迎任何形式的贡献！详见 [CONTRIBUTING.md](CONTRIBUTING.md)

特别欢迎的方向：
- 🎨 **UI 增强**：深色/浅色主题、响应式、动画优化
- 🤖 **新 Agent**：适合特定场景的专职 Agent 角色
- 📦 **Skills 生态**：各部门专用技能包
- 🔗 **集成扩展**：Notion · Jira · Linear · GitHub Issues
- 🌐 **国际化**：日文 · 韩文 · 西班牙文
- 📱 **移动端**：响应式适配、PWA

---

## 📂 案例

`examples/` 目录收录了真实的端到端使用案例：

| 案例 | 旨意 | 涉及部门 |
|------|------|----------|
| [竞品分析](examples/competitive-analysis.md) | "分析 CrewAI vs AutoGen vs LangGraph" | 中书→门下→户部+兵部+礼部 |
| [代码审查](examples/code-review.md) | "审查这段 FastAPI 代码的安全性" | 中书→门下→兵部+刑部 |
| [周报生成](examples/weekly-report.md) | "生成本周工程团队周报" | 中书→门下→户部+礼部 |

每个案例包含：完整旨意 → 中书省规划 → 门下省审核意见 → 各部执行结果 → 最终奏折。

---

## ⭐ Star History

如果这个项目让你会心一笑，请给个 Star ⚔️

[![Star History Chart](https://api.star-history.com/svg?repos=cft0808/edict&type=Date)](https://star-history.com/#cft0808/edict&Date)

---

## 📮 朕的邸报——公众号

> 古有邸报传天下政令，今有公众号聊 AI 架构。

<p align="center">
  <img src="docs/assets/wechat-qrcode.jpg" width="220" alt="公众号二维码 · cft0808">
  <br><br>
  <b>👆 扫码关注「cft0808」—— 朕的技术邸报</b>
</p>

你会看到：

- 🏛️ **架构拆解** —— 三省六部到底怎么分权制衡的？8 个技能 各司何职？
- 🔥 **踩坑复盘** —— Agent 吵架了怎么办？Token 烧光了怎么省？门下省为什么总封驳？
- 🛠️ **Issue 修复实录** —— 每个 bug 都是一道奏折，看朕如何批红
- 💡 **Token 省钱术** —— 用 1/10 的 token 跑出门下省审核效果的秘密
- 🎭 **Agent 人设彩蛋** —— 六部的 SOUL.md 是怎么写出来的？

> *"朕让 AI 上朝，结果 AI 比朕还卷。"* —— 关注后你会懂的。

---

## 📄 License

[MIT](LICENSE) · 源自 OpenClaw 社区

---

<p align="center">
  <strong>⚔️ 以古制御新技，以智慧驾驭 AI</strong><br>
  <sub>Governing AI with the wisdom of ancient empires</sub><br><br>
  <a href="#-朕的邸报公众号"><img src="https://img.shields.io/badge/公众号_cft0808-关注获取更新-07C160?style=for-the-badge&logo=wechat&logoColor=white" alt="WeChat"></a>
</p>
