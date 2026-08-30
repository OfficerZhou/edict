#!/usr/bin/env bash
# ══════════════════════════════════════════════════════════
# 三省六部(Edict) 技能安装器 —— harness 无关
# 任何 agent 克隆本仓库后，运行本脚本即可把 8 个技能安装到
# 当前平台的技能目录。技能内容零改动、零 platform 依赖。
#
# 用法:
#   ./install-skills.sh               # 自动检测 Claude Code/Codex/DSH 技能目录并安装
#   ./install-skills.sh --link       # 用符号链接安装（跟随仓库更新）
#   ./install-skills.sh --target DIR # 指定技能目录
#   ./install-skills.sh --dry-run    # 只显示计划，不写入
#   ./install-skills.sh --force      # 已存在的技能目录允许覆盖
# ══════════════════════════════════════════════════════════
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$ROOT/skills"
SKILL_NAMES=(using-edict edict-triaging edict-planning edict-review edict-dispatch edict-ministries edict-report edict-kanban)

LINK=0; FORCE=0; DRY=0; TARGET=""

while [ $# -gt 0 ]; do
  case "$1" in
    --link) LINK=1; shift ;;
    --force) FORCE=1; shift ;;
    --dry-run) DRY=1; shift ;;
    --target) TARGET="$2"; shift 2 ;;
    --target=*) TARGET="${1#--target=}"; shift ;;
    *) echo "未知参数: $1" >&2; exit 1 ;;
  esac
done

# ── 定位目标技能目录（优先级: --target > EDICT_SKILLS_DIR > 检测常见路径 > 默认）──
detect_target() {
  if [ -n "$TARGET" ]; then echo "$TARGET"; return; fi
  if [ -n "${EDICT_SKILLS_DIR:-}" ]; then echo "$EDICT_SKILLS_DIR"; return; fi
  if [ -d "$HOME/.claude/skills" ]; then echo "$HOME/.claude/skills"; return; fi
  if [ -d "$HOME/.codex/skills" ]; then echo "$HOME/.codex/skills"; return; fi
  if [ -d "$HOME/.dsh/skills" ]; then echo "$HOME/.dsh/skills"; return; fi
  # 都没检测到：给一个可预期的默认值，并在输出中说明
  echo "$HOME/.claude/skills"
}

DEST="$(detect_target)"
DETECTED_NOTE=""
if [ -z "$TARGET" ] && [ -z "${EDICT_SKILLS_DIR:-}" ] && [ "$DEST" = "$HOME/.claude/skills" ] && [ ! -d "$HOME/.claude/skills" ]; then
  DETECTED_NOTE="（未检测到已知平台技能目录，使用默认位置；可用 --target 指定）"
fi

echo "╔══════════════════════════════════════════╗"
echo "║  🏛️  三省六部 · 通用技能安装器           ║"
echo "╚══════════════════════════════════════════╝"
echo "技能源: $SRC"
echo "安装到: $DEST $DETECTED_NOTE"
[ "$DRY" = 1 ] && echo "(dry-run：以下仅计划，不写入)"

# ── 校验源 ──
missing=0
for n in "${SKILL_NAMES[@]}"; do
  [ -f "$SRC/$n/SKILL.md" ] || { echo "❌ 技能缺失: $SRC/$n/SKILL.md" >&2; missing=1; }
done
[ "$missing" = 1 ] && exit 1

mkdir -p "$DEST"

# ── 安装每个技能 ──
for n in "${SKILL_NAMES[@]}"; do
  dst="$DEST/$n"
  if [ -e "$dst" ]; then
    if [ "$FORCE" = 1 ]; then
      [ "$DRY" = 1 ] || rm -rf "$dst"
    else
      echo "⏭️  $n 已存在，跳过（--force 覆盖）"
      continue
    fi
  fi

  if [ "$DRY" = 1 ]; then
    echo "计划: $n -> $dst $([ "$LINK" = 1 ] && echo '(符号链接)' || echo '(复制)')"
    continue
  fi

  if [ "$LINK" = 1 ]; then
    ln -s "$SRC/$n" "$dst"
    echo "🔗  $n -> 符号链接"
  else
    cp -r "$SRC/$n" "$dst"
    echo "✅  $n -> 复制完成"
  fi
done

echo "── 完成 ──"
echo "新开一个会话让 agent 索引技能；测试触发句:「朕要一个 React 待办应用，六部协同办理」"
echo "Windows 可用 .\\install-skills.ps1（--link 用目录联接，免管理员）"
