# ══════════════════════════════════════════════════════════
# 三省六部(Edict) 技能安装器 (Windows/PowerShell) —— harness 无关
# 任何 agent 克隆本仓库后，运行本脚本即可把 8 个技能安装到
# 当前平台的技能目录。技能内容零改动、零 platform 依赖。
#
# 用法:
#   .\install-skills.ps1               # 自动检测 Claude Code/Codex/DSH 技能目录并安装
#   .\install-skills.ps1 -Link         # 用目录联接安装（免管理员，跟随仓库更新）
#   .\install-skills.ps1 -Target DIR   # 指定技能目录
#   .\install-skills.ps1 -DryRun       # 只显示计划，不写入
#   .\install-skills.ps1 -Force        # 已存在的技能目录允许覆盖
# ══════════════════════════════════════════════════════════
param(
    [switch]$Link,
    [switch]$Force,
    [switch]$DryRun,
    [string]$Target = ""
)

$ErrorActionPreference = 'Stop'
$Root = $PSScriptRoot
$Src  = Join-Path $Root 'skills'
$Names = @('using-edict','edict-triaging','edict-planning','edict-review',
           'edict-dispatch','edict-ministries','edict-report','edict-kanban')

# ── 定位目标技能目录（优先级: -Target > EDICT_SKILLS_DIR > 检测常见路径 > 默认）──
function Get-Dest {
    if ($Target) { return $Target }
    if ($env:EDICT_SKILLS_DIR) { return $env:EDICT_SKILLS_DIR }
    $userHome = $env:USERPROFILE
    foreach ($cand in @((Join-Path $userHome '.claude\skills'),
                        (Join-Path $userHome '.codex\skills'),
                        (Join-Path $userHome '.dsh\skills'))) {
        if (Test-Path $cand) { return $cand }
    }
    return (Join-Path $userHome '.claude\skills')
}

$Dest = Get-Dest
$note = ""
if (-not $Target -and -not $env:EDICT_SKILLS_DIR -and $Dest -eq (Join-Path $env:USERPROFILE '.claude\skills') -and -not (Test-Path $Dest)) {
    $note = "（未检测到已知平台技能目录，使用默认位置；可用 -Target 指定）"
}

Write-Host "═══ 三省六部 · 通用技能安装器 ═══"
Write-Host "技能源: $Src"
Write-Host "安装到: $Dest $note"
if ($DryRun) { Write-Host "(dry-run：以下仅计划，不写入)" }

# ── 校验源 ──
$missing = $false
foreach ($n in $Names) {
    if (-not (Test-Path (Join-Path $Src "$n\SKILL.md"))) {
        Write-Error "❌ 技能缺失: $Src\$n\SKILL.md"
        $missing = $true
    }
}
if ($missing) { exit 1 }

New-Item -ItemType Directory -Force -Path $Dest | Out-Null

# ── 安装每个技能 ──
foreach ($n in $Names) {
    $dst = Join-Path $Dest $n
    if (Test-Path $dst) {
        if ($Force) {
            if (-not $DryRun) { Remove-Item -Recurse -Force $dst }
        } else {
            Write-Host "⏭️  $n 已存在，跳过（-Force 覆盖）"
            continue
        }
    }
    if ($DryRun) {
        $how = if ($Link) { '目录联接' } else { '复制' }
        Write-Host "计划: $n -> $dst ($how)"
        continue
    }
    if ($Link) {
        # 目录联接（junction）无需管理员权限；跟随仓库更新
        New-Item -ItemType Junction -Path $dst -Target (Join-Path $Src $n) | Out-Null
        Write-Host "🔗  $n -> 目录联接"
    } else {
        Copy-Item -Recurse -Force (Join-Path $Src $n) $dst
        Write-Host "✅  $n -> 复制完成"
    }
}

Write-Host "── 完成 ──"
Write-Host "新开一个会话让 agent 索引技能；测试触发句:「朕要一个 React 待办应用，六部协同办理」"
Write-Host "Unix/macOS 可用 ./install-skills.sh"
