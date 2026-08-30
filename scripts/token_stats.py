#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
token_stats.py — 统计本机(WSL/Claude Code/Codex)各 agent 会话的 token 用量与成本

数据来源（三个域，尽力而为）：
  1. 本机 Claude Code 会话: C:\\Users\\Administrator\\.claude\\projects\\**\\*.jsonl
     （全目录扫描，不排除 --wsl-localhost-* 镜像目录，靠会话 UUID 全局去重防双计）
  2. WSL 各发行版: 用 `wsl -l -v`（按 utf-16le 解码）枚举发行版；
     - 优先经 \\wsl$\\<distro>\\home\\*\\ .claude\\projects 直读（UNC/fs 路径）
     - 失败降级: `wsl -d <distro> <shell>` 在发行版内部打包读取（tar 流）
  3. 本机 Codex: C:\\Users\\Administrator\\.codex\\sessions\\**\\*.jsonl（尽力采集，目录缺失则跳过）

解析：逐行 json.loads；只统计带 usage 的 assistant 记录，取四个字段：
      input_tokens(输入) / cache_creation_input_tokens(缓存写) /
      cache_read_input_tokens(缓存读) / output_tokens(输出)
      （缺失字段按 0 处理；坏行 / orphaned-*.jsonl 容错并记入未解析清单）

成本：按内置单价表（PRICE_TABLE，来源见 PRICE_SOURCE），未匹配模型记入"未计价"清单。
依赖：纯 Python 标准库，零第三方依赖。

用法示例：
  python scripts\\token_stats.py                    # 三域全扫 + 终端摘要，并保存产出到 output/
  python scripts\\token_stats.py --days 7           # 只看最近 7 天
  python scripts\\token_stats.py --no-wsl           # 跳过 WSL 采集
  python scripts\\token_stats.py --distros Ubuntu2404
  python scripts\\token_stats.py --csv              # CSV 输出到标准输出（同时保存文件）
  python scripts\\token_stats.py --json             # JSON 输出到标准输出（同时保存文件）
  python scripts\\token_stats.py --out-dir reports  # 指定产出目录（默认 output/）
  python scripts\\token_stats.py --no-save          # 只打印终端摘要
"""

import argparse
import csv
import datetime as dt
import io
import json
import os
import pathlib
import re
import subprocess
import sys
import tarfile

# ---------------------------------------------------------------------------
# 数据源（按当前机器布局硬编码）
# ---------------------------------------------------------------------------
LOCAL_CLAUDE_ROOT = r"C:\Users\Administrator\.claude\projects"
CODEX_ROOT = r"C:\Users\Administrator\.codex\sessions"

UUID_RE = re.compile(
    r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
)
TS_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?$"
)

FIELD_INPUT = "input_tokens"
FIELD_WRITE = "cache_creation_input_tokens"
FIELD_READ = "cache_read_input_tokens"
FIELD_OUTPUT = "output_tokens"
SPECIAL_SKIP_DIR_NAMES = {"memory", ".git"}


# ---------------------------------------------------------------------------
# 单价表（美元 / 每 100 万 tokens）—— 来源与日期见 PRICE_SOURCE
# 字段: (input, output, cache_read, cache_write)
# 注: Anthropic 缓存折扣为 读=输入价×0.1、写=输入价×1.25
# ---------------------------------------------------------------------------
PRICE_SOURCE_DATE = "2026-08-30"
PRICE_SOURCE = (
    "单价表来源说明（整理日期 2026-08-30）："
    "① Anthropic 官方价目——取自本机 claude-api 技能内嵌官方文档 "
    "(shared/models.md / shared/model-migration.md："
    "Fable 5 = $10/$50 per MTok；Sonnet 5 标价 $3/$15、促销价 $2/$10 至 2026-08-31"
    "（本表按 2026-08-30 生效中的促销价计入，标价见注）；Haiku 4.5 = $1/$5；"
    "Opus 5 于 2026-07-24 发布、公开报道称价格为 Fable 5 的一半即 $5/$25)。"
    "② DeepSeek——2026-08-17 官方调价公告（新浪财经/腾讯科技等报道）："
    "Flash 平时价 输入缓存未命中 1.5 元/M、缓存命中 0.05 元/M、输出 4.5 元/M；"
    "峰谷计费高峰期翻倍，本表取平时价，人民币按 1 USD = 7.20 CNY 折算（2026-08-30 假设汇率）。"
    "vision/0731 快照均属 V4 Flash 系列，公告未单列价格，按 Flash 同价；"
    "V4 百万上下文版为标配，[1M] 变体亦按 Flash 同价（估算）。"
    "③ GLM——VentureBeat 等公开报道：GLM-5.3 API 上市价 $1.4/$4.4 per MTok（2026-08）。"
    "④ Qwen——公开报道：Qwen3.8-Max API 价约为 Opus 5 的 24%，折算 $1.2/$6（估算）。"
    "⑤ OpenAI——官方公开价目（GPT-4o/GPT-4.1/o1/o3 等；本机数据暂未出现 GPT 模型，仅兜底）。"
    "未收录模型（glm-5.2、glm-5.3-flash、裸名 sonnet/opus、<synthetic> 内部标记等）"
    "统一计入『未计价』清单：token 照实计数、成本缺省，请核对模型名后更新单价表。"
)

PRICE_TABLE = {
    # ---------------- DeepSeek（2026-08-17 调价公告，元->美元 @7.2） ----------------
    "deepseek-v4-flash":             (0.2083, 0.6250, 0.0069, 0.2083),
    "deepseek-v4-flash-vision-exp":  (0.2083, 0.6250, 0.0069, 0.2083),
    "deepseek-v4-flash-0731":        (0.2083, 0.6250, 0.0069, 0.2083),
    "deepseek-v4-flash[1m]":         (0.2083, 0.6250, 0.0069, 0.2083),
    # ---------------- Anthropic Claude ----------------
    "claude-opus-5":                 (5.00, 25.00, 0.50, 6.25),
    "claude-sonnet-5":               (2.00, 10.00, 0.20, 2.50),   # 促销价(至2026-08-31)；标价 $3/$15
    "claude-haiku-4-5":              (1.00, 5.00, 0.10, 1.25),
    "claude-opus-4-5":               (15.00, 75.00, 1.50, 18.75),  # legacy
    "claude-opus-4-1":               (15.00, 75.00, 1.50, 18.75),
    "claude-sonnet-4-6":             (3.00, 15.00, 0.30, 3.75),
    "claude-sonnet-4-5":             (3.00, 15.00, 0.30, 3.75),
    "claude-3-7-sonnet":             (3.00, 15.00, 0.30, 3.75),
    "claude-3-5-sonnet":             (3.00, 15.00, 0.30, 3.75),
    "claude-haiku-3-5":              (0.80, 4.00, 0.08, 1.00),
    # ---------------- GLM / Qwen ----------------
    "glm-5.3":                       (1.40, 4.40, 0.14, 1.75),
    "qwen3.8-max-preview":           (1.20, 6.00, 0.12, 1.50),
    "qwen3.8-max":                   (1.20, 6.00, 0.12, 1.50),
    # ---------------- OpenAI（官方公开价；本机暂无用例，仅兜底） ----------------
    "gpt-4o":                        (2.50, 10.00, 0.25, 3.13),
    "gpt-4o-mini":                   (0.15, 0.60, 0.02, 0.19),
    "gpt-4-1":                       (2.00, 8.00, 0.50, 2.50),
    "o1":                            (15.00, 60.00, 1.50, 18.75),
    "o3":                            (2.00, 8.00, 0.20, 2.50),
}

# 别名映射：模型名 -> 表内 key；None 表示"裸名无对应，不计价"
PRICE_ALIASES = {
    "claude-haiku-4-5-20251001": "claude-haiku-4-5",
    "sonnet": None,
    "opus": None,
}


def _norm(m):
    return re.sub(r"\s+", "", (m or "").lower())


def _lookup_price(model_name):
    """返回 (input, output, cache_read, cache_write) 或 None（未计价）"""
    if not model_name:
        return None
    key = _norm(model_name)
    if key in PRICE_TABLE:
        return PRICE_TABLE[key]
    if key in PRICE_ALIASES:
        tgt = PRICE_ALIASES[key]
        return PRICE_TABLE.get(tgt) if tgt else None
    # 供应商前缀（如 accounts/fireworks/models/deepseek-v4-flash-0731）只取末段匹配
    if "/" in key:
        base = key.rsplit("/", 1)[-1]
        if base in PRICE_TABLE:
            return PRICE_TABLE[base]
        if base in PRICE_ALIASES and PRICE_ALIASES[base]:
            return PRICE_TABLE[PRICE_ALIASES[base]]
        key = base
    # 长 id 前缀匹配（如 claude-haiku-4-5-20251001、deepseek-v4-flash-0928 之类快照名）
    for k in sorted(PRICE_TABLE, key=len, reverse=True):
        if len(k) >= 8 and (key.startswith(k) or key.startswith(k + "-")):
            return PRICE_TABLE[k]
    return None


# ---------------------------------------------------------------------------
# 文件收集
# ---------------------------------------------------------------------------
def iter_jsonl_files(root):
    """递归列出 root 下所有 *.jsonl，返回 [(项目目录名, 文件名, 绝对路径)]"""
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SPECIAL_SKIP_DIR_NAMES]
        rel = os.path.relpath(dirpath, root)
        rel = "" if rel == "." else rel
        for fn in filenames:
            if fn.endswith(".jsonl"):
                out.append((rel, fn, os.path.join(dirpath, fn)))
    return out


def session_uuid(filename):
    """会话去重键：文件名中的 UUID；无 UUID 时退回文件全名(小写)。"""
    m = UUID_RE.search(filename)
    if m:
        return m.group(0).lower()
    return os.path.splitext(filename)[0].lower()


# ---------------------------------------------------------------------------
# WSL
# ---------------------------------------------------------------------------
def wsl_list_distros():
    """`wsl -l -v` 输出为 UTF-16LE；返回 [(distro, state)] 或 []"""
    try:
        p = subprocess.run(["wsl.exe", "-l", "-v"], capture_output=True, timeout=90)
        raw = p.stdout or p.stderr
        text = None
        for enc in ("utf-16-le", "utf-16"):
            try:
                if b"\x00" not in raw:
                    raise UnicodeError
                text = raw.decode(enc)
                break
            except UnicodeError:
                continue
        if text is None:
            text = raw.decode("utf-8", errors="replace")
        distros = []
        for line in text.splitlines():
            line = line.strip().strip("*").strip()
            if not line:
                continue
            parts = re.split(r"\s{2,}|\t+", line)
            if not parts:
                continue
            name = parts[0].strip()
            if re.match(r"^(name|wsl|发行版|windows)", name, re.I):
                continue
            if "windows" in name.lower():
                continue
            state = parts[1].strip() if len(parts) > 1 else "?"
            distros.append((name, state))
        return distros
    except Exception as e:
        sys.stderr.write("[wsl] 枚举失败: %s\n" % e)
        return []


def wsl_collect_direct(distro):
    r"""
    优先：UNC 直读 \\wsl$\<distro>\home\<user>\.claude\projects
    返回 (entries, err) —— entries: [(agent_dir, filename, abspath)]；err 为不可达原因(否则 None)
    """
    base = r"\\wsl$\%s\home" % distro
    if not os.path.exists(base):
        return None, "UNC 根不可达"
    try:
        homes = [d for d in os.listdir(base) if os.path.isdir(os.path.join(base, d))]
    except OSError as e:
        return None, "UNC 枚举失败: %s" % e
    got = []
    for user in homes:
        proj = os.path.join(base, user, ".claude", "projects")
        try:
            if os.path.isdir(proj):
                got.extend(iter_jsonl_files(proj))
        except OSError:
            continue
    return got, None


def wsl_tar_stream(distro, root_path):
    """
    降级：在发行版内 tar 打包单项 <root_path> 到 stdout，返回 [(agent_dir, filename, text)]
    root_path: 发行版内的 .claude/projects 目录绝对路径(引号转义)
    """
    out = []
    try:
        script = "tar -C %s -cf - ." % _bash_quote(root_path)
        p = subprocess.Popen(
            ["wsl.exe", "-d", distro, "--", "bash", "-lc", script],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
        )
        tf = tarfile.open(fileobj=p.stdout, mode="r|*")
        for member in tf:
            nm = member.name.lstrip("./")
            if not nm.endswith(".jsonl"):
                continue
            raw = tf.extractfile(member)
            try:
                text = raw.read().decode("utf-8", errors="replace")
            except Exception:
                continue
            parts = nm.split("/")
            agent_dir = parts[0] if len(parts) > 1 else "."
            out.append((agent_dir, parts[-1], text))
        p.stdout.close()
        try:
            p.wait(timeout=600)
        except Exception:
            p.kill()
    except Exception:
        pass
    return out


def _bash_quote(s):
    return "'" + s.replace("'", "'\\''") + "'"


def wsl_collect(distro):
    """采一个发行版: 返回 (entries, mode)。entries: [(agent_dir, filename, abspath_or_text)]
    mode: 'direct'(UNC) / 'fallback'(tar) / 'skip'"""
    got, err = wsl_collect_direct(distro)
    if got is not None:
        return got, "direct"
    # 降级：找发行版内 /home/*/.claude/projects
    try:
        p = subprocess.run(
            ["wsl.exe", "-d", distro, "--", "bash", "-lc",
             "ls -d /home/*/.claude/projects 2>/dev/null; ls -d /root/.claude/projects 2>/dev/null"],
            capture_output=True, timeout=90,
        )
        if p.returncode != 0:
            return [], "skip"
    except Exception:
        return [], "skip"
    roots = [l.strip() for l in p.stdout.decode("utf-8", errors="replace").splitlines() if l.strip()]
    if not roots:
        return [], "skip"
    entries = []
    for root in roots:
        entries.extend(wsl_tar_stream(distro, root))
    return [(agent, fn, text) for (agent, fn, text) in entries], "fallback"


# ---------------------------------------------------------------------------
# 解析
# ---------------------------------------------------------------------------
def parse_timestamp(value):
    """解析时间戳为本地时区日期；无法解析返回 None"""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        try:
            return dt.datetime.fromtimestamp(float(value)).date()
        except (OSError, ValueError, OverflowError):
            return None
    if isinstance(value, str):
        s = value.strip()
        if not TS_RE.match(s):
            return None
        s = s.replace("Z", "+00:00")
        try:
            d = dt.datetime.fromisoformat(s)
        except ValueError:
            return None
        if d.tzinfo is None:
            d = d.replace(tzinfo=dt.timezone.utc)
        try:
            return d.astimezone().date()
        except (ValueError, OverflowError):
            return None
    return None


def extract_usage(obj):
    """从一行对象中提取 (model, usage_dict)；找不到返回 None"""
    if not isinstance(obj, dict):
        return None
    msg = obj.get("message")
    if isinstance(msg, dict) and isinstance(msg.get("usage"), dict):
        return msg.get("model") or obj.get("model"), msg["usage"]
    payload = obj.get("payload")
    if isinstance(payload, dict) and isinstance(payload.get("usage"), dict):
        return payload.get("model"), payload["usage"]
    return None


def usage_to_counts(usage):
    """提取四字段，缺失/非数字按 0"""
    def n(key):
        v = usage.get(key)
        try:
            return int(v) if v is not None else 0
        except (TypeError, ValueError):
            return 0
    return n(FIELD_INPUT), n(FIELD_OUTPUT), n(FIELD_READ), n(FIELD_WRITE)


def parse_lines(lines_iter, is_codex=False):
    """
    解析行迭代器，返回 (rows, bad_lines, reason)
      rows: [{model, in, out, rd, wr, day}]
    is_codex=True: 采用 Codex 的 token_count 事件语义 —— 每个文件只取最后一次
    token_count 事件的 total_token_usage（累计值）作为整个会话一行，避免重复累计。
    """
    rows = []
    bad = 0
    codex_last = None   # (model, in, out, rd, wr, day)
    for line in lines_iter:
        line = line.rstrip("\n").rstrip("\r")
        if not line:
            continue
        if '"usage"' not in line and '"type":"assistant"' not in line and '"token_count"' not in line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            bad += 1
            continue
        if not isinstance(obj, dict):
            bad += 1
            continue
        payload = obj.get("payload") if isinstance(obj.get("payload"), dict) else {}
        if is_codex and obj.get("type") == "event_msg" and payload.get("type") == "token_count":
            info = payload.get("info") or {}
            usage = info.get("total_token_usage") or info.get("last_token_usage")
            if not isinstance(usage, dict):
                continue
            codex_last = (
                "codex(model未记录)",
                _field(usage, "input_tokens"),
                _field(usage, "output_tokens") + _field(usage, "reasoning_output_tokens"),
                _field(usage, "cached_input_tokens"),
                _field(usage, "cache_write_input_tokens"),
                parse_timestamp(obj.get("timestamp")),
            )
            continue
        found = extract_usage(obj)
        if not found:
            continue
        model, usage = found
        inp, out, rd, wr = usage_to_counts(usage)
        if inp == out == rd == wr == 0:
            continue
        day = parse_timestamp(obj.get("timestamp"))
        if day is None:
            msg = obj.get("message")
            day = parse_timestamp((msg or {}).get("timestamp")) if isinstance(msg, dict) else None
        rows.append({"model": model, "in": inp, "out": out, "rd": rd, "wr": wr, "day": day})
    if is_codex and codex_last is not None:
        m, inp, out, rd, wr, day = codex_last
        if inp or out or rd or wr:
            rows.append({"model": m, "in": inp, "out": out, "rd": rd, "wr": wr, "day": day})
    return rows, bad, None


def _field(usage, key):
    try:
        return int(usage.get(key) or 0)
    except (TypeError, ValueError):
        return 0


def parse_file(abspath, is_codex=False):
    """解析一个 jsonl 文件; 返回 (rows, bad_lines, reason)"""
    try:
        with open(abspath, "r", encoding="utf-8", errors="replace") as f:
            return parse_lines(f, is_codex=is_codex)
    except Exception as e:
        return [], 0, "%s: %s" % (type(e).__name__, e)


def parse_text(text, name, is_codex=False):
    """解析内存内容（WSL 降级 tar 流场景）"""
    return parse_lines(io.StringIO(text), is_codex=is_codex)


# ---------------------------------------------------------------------------
# 聚合
# ---------------------------------------------------------------------------
def aggregate(rows):
    """
    rows: [{uuid, agent, model, in, out, rd, wr, day, src_file}]
    返回 (by_agent, by_date, unpriced, total)
    """
    ag = {}
    dtm = {}
    unpriced = {}
    total = {"in": 0, "out": 0, "rd": 0, "wr": 0, "cost": 0.0}
    sess_keys = set()

    for r in rows:
        aid = r["agent"]
        a = ag.setdefault(aid, {"sessions": set(), "in": 0, "out": 0, "rd": 0, "wr": 0, "cost": 0.0})
        a["sessions"].add(r["uuid"])
        sess_keys.add((aid, r["uuid"]))
        if r["day"] is not None:
            d = dtm.setdefault(r["day"], {"sessions": set(), "in": 0, "out": 0, "rd": 0, "wr": 0, "cost": 0.0})
            d["sessions"].add(r["uuid"])
        a["in"] += r["in"]; a["out"] += r["out"]; a["rd"] += r["rd"]; a["wr"] += r["wr"]
        if r["day"] is not None:
            d["in"] += r["in"]; d["out"] += r["out"]; d["rd"] += r["rd"]; d["wr"] += r["wr"]

        price = _lookup_price(r["model"])
        if price is None:
            mname = str(r["model"]) or "(无模型名)"
            u = unpriced.setdefault(mname, {"files": set(), "sessions": set(),
                                            "in": 0, "out": 0, "rd": 0, "wr": 0})
            u["files"].add(r["src_file"])
            u["sessions"].add(r["uuid"])
            u["in"] += r["in"]; u["out"] += r["out"]; u["rd"] += r["rd"]; u["wr"] += r["wr"]
        else:
            pin, pout, prd, pwr = price
            cost = (r["in"] * pin + r["out"] * pout + r["rd"] * prd + r["wr"] * pwr) / 1_000_000.0
            a["cost"] += cost
            if r["day"] is not None:
                d["cost"] += cost
            total["cost"] += cost

        total["in"] += r["in"]; total["out"] += r["out"]
        total["rd"] += r["rd"]; total["wr"] += r["wr"]

    def finalize(m):
        return {k: {"sessions": len(v["sessions"]), "in": v["in"], "out": v["out"],
                    "rd": v["rd"], "wr": v["wr"], "cost": round(v["cost"], 4)}
                for k, v in m.items()}

    total = {"sessions": len(sess_keys), "in": total["in"], "out": total["out"],
             "rd": total["rd"], "wr": total["wr"], "cost": round(total["cost"], 4)}
    return finalize(ag), finalize(dtm), unpriced, total


# ---------------------------------------------------------------------------
# 输出
# ---------------------------------------------------------------------------
def human(n):
    return "{:,}".format(n)


def fmt_cost(c):
    return "${:,.2f}".format(c)


def fmt_row(label, v, w=46):
    return "  {:<46} {:>8} {:>14} {:>14} {:>14} {:>14} {:>12}".format(
        label, v["sessions"], human(v["in"]), human(v["out"]),
        human(v["rd"]), human(v["wr"]), fmt_cost(v["cost"]))


def emit_terminal(meta, by_agent, by_date, unpriced, unparsed, bad_total, mode_notes):
    print("=" * 74)
    print("Token 用量统计  %s" % meta["now"])
    print("=" * 74)
    print("扫描范围: %s" % meta["scope"])
    print("单价表: %s" % meta["price_source_line"])
    print("去重策略: 全部会话按文件名/UUID 全局去重，一个会话只计一次")
    for n in mode_notes:
        print("  · %s" % n)

    print("\n[按 agent(会话来源) 分组]")
    print("  {:<46} {:>8} {:>14} {:>14} {:>14} {:>14} {:>12}".format(
        "agent", "会话数", "输入", "输出", "缓存读", "缓存写", "成本$"))
    print("  " + "-" * 118)
    for aid in sorted(by_agent):
        print(fmt_row(aid, by_agent[aid]))
    print("  " + "-" * 118)
    print(fmt_row("合计", meta["total"]))

    print("\n[按日期 分组]")
    print("  {:<14} {:>8} {:>14} {:>14} {:>14} {:>14} {:>12}".format(
        "日期", "会话数", "输入", "输出", "缓存读", "缓存写", "成本$"))
    print("  " + "-" * 86)
    for day in sorted(by_date):
        v = by_date[day]
        print("  {:<14} {:>7} {:>14} {:>14} {:>14} {:>14} {:>12}".format(
            str(day), v["sessions"], human(v["in"]), human(v["out"]),
            human(v["rd"]), human(v["wr"]), fmt_cost(v["cost"])))

    print("\n[数据质量]")
    print("  扫描 jsonl 文件: 总计 %d (本机 %d / WSL %d / Codex %d)，去重跳过 %d，"
          "未解析 %d，坏行 %d"
          % (meta["files_scanned"], meta["files_local"], meta["files_wsl"],
             meta["files_codex"], meta["dup_files_skipped"], len(unparsed), bad_total))
    if unparsed:
        print("  未解析文件(至多 20 条):")
        for name, reason in list(unparsed.items())[:20]:
            print("    - %s  (%s)" % (name, reason))
    print("  去重后有效会话: %d 个(计 %d 条 assistant 用量记录)"
          % (meta["total"]["sessions"], meta["rows_count"]))
    if unpriced:
        print("\n[未计价模型] —— token 已计数、成本未折算:")
        for m, u in sorted(unpriced.items(), key=lambda kv: -(kv[1]["in"] + kv[1]["out"])):
            print("  %-44s 文件 %d | 会话 %d | 输入 %s | 输出 %s | 缓存读 %s | 缓存写 %s"
                  % (m, len(u["files"]), len(u["sessions"]), human(u["in"]),
                     human(u["out"]), human(u["rd"]), human(u["wr"])))
    else:
        print("\n[未计价模型] 无")
    print("\n货币: 美元；单价表来源/日期见 --help 中文文档说明。")


def emit_csv(by_agent, by_date, total):
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(["group", "name", "date", "sessions", "input_tokens", "output_tokens",
                "cache_read_tokens", "cache_write_tokens", "cost_usd"])
    for aid in sorted(by_agent):
        v = by_agent[aid]
        w.writerow(["agent", aid, "", v["sessions"], v["in"], v["out"],
                    v["rd"], v["wr"], v["cost"]])
    for day in sorted(by_date):
        v = by_date[day]
        w.writerow(["date", "", str(day), v["sessions"], v["in"], v["out"],
                    v["rd"], v["wr"], v["cost"]])
    w.writerow(["total", "", "", total["sessions"], total["in"], total["out"],
                total["rd"], total["wr"], total["cost"]])
    return out.getvalue()


def emit_json(meta, by_agent, by_date, unpriced, unparsed, bad_total):
    doc = {
        "generated_at": meta["now"],
        "price_source": PRICE_SOURCE,
        "config": meta["config"],
        "scope": meta["scope"],
        "stats": {
            "files_scanned": meta["files_scanned"],
            "files_local": meta["files_local"],
            "files_wsl": meta["files_wsl"],
            "files_codex": meta["files_codex"],
            "files_ok": meta["files_ok"],
            "files_unparsed": len(unparsed),
            "dup_files_skipped": meta["dup_files_skipped"],
            "bad_lines": bad_total,
            "usage_rows": meta["rows_count"],
        },
        "total": meta["total"],
        "by_agent": by_agent,
        "by_date": {str(k): v for k, v in by_date.items()},
        "unpriced_models": {m: {"files": len(u["files"]), "sessions": len(u["sessions"]),
                                "in": u["in"], "out": u["out"], "rd": u["rd"], "wr": u["wr"]}
                            for m, u in unpriced.items()},
        "unparsed_files": [{"file": k, "reason": v} for k, v in list(unparsed.items())[:500]],
    }
    return json.dumps(doc, ensure_ascii=False, indent=2) + "\n"


def _md_report(meta, by_agent, by_date, unpriced, unparsed, bad_total, mode_notes):
    """组装 Markdown 摘要报告（与终端摘要同源数据）。"""
    lines = [
        "# Token 用量统计报告",
        "",
        "- 生成时间: %s" % meta["now"],
        "- 扫描范围: %s" % meta["scope"],
        "- 单价表: %s" % meta["price_source_line"],
        "- 去重策略: 全部会话按文件名/UUID 全局去重，一个会话只计一次",
    ]
    for n in mode_notes:
        lines.append("- %s" % n)
    lines += ["", "## 按 agent 分组", "",
              "| agent | 会话数 | 输入 | 输出 | 缓存读 | 缓存写 | 成本$ |",
              "|---|---|---|---|---|---|---|"]
    for aid in sorted(by_agent):
        v = by_agent[aid]
        lines.append("| %s | %d | %s | %s | %s | %s | %s |" % (
            aid, v["sessions"], human(v["in"]), human(v["out"]),
            human(v["rd"]), human(v["wr"]), fmt_cost(v["cost"])))
    t = meta["total"]
    lines.append("| **合计** | %d | %s | %s | %s | %s | %s |" % (
        t["sessions"], human(t["in"]), human(t["out"]),
        human(t["rd"]), human(t["wr"]), fmt_cost(t["cost"])))
    lines += ["", "## 按日期分组", "",
              "| 日期 | 会话数 | 输入 | 输出 | 缓存读 | 缓存写 | 成本$ |",
              "|---|---|---|---|---|---|---|"]
    for day in sorted(by_date):
        v = by_date[day]
        lines.append("| %s | %d | %s | %s | %s | %s | %s |" % (
            str(day), v["sessions"], human(v["in"]), human(v["out"]),
            human(v["rd"]), human(v["wr"]), fmt_cost(v["cost"])))
    lines += ["", "## 数据质量", "",
              "扫描 jsonl: %d 个（本机 %d / WSL %d / Codex %d），去重跳过 %d，未解析 %d，坏行 %d；"
              "去重后有效会话 %d（计 %d 条 assistant 用量记录）" % (
                  meta["files_scanned"], meta["files_local"], meta["files_wsl"],
                  meta["files_codex"], meta["dup_files_skipped"],
                  len(unparsed), bad_total, t["sessions"], meta["rows_count"])]
    if unpriced:
        lines += ["", "## 未计价模型", ""]
        for m, u in sorted(unpriced.items(), key=lambda kv: -(kv[1]["in"] + kv[1]["out"])):
            lines.append("- %s：输入 %s / 输出 %s 未折算成本" % (
                m, human(u["in"]), human(u["out"])))
    return "\n".join(lines) + "\n"


def write_outputs(meta, by_agent, by_date, unpriced, unparsed, bad_total, mode_notes, out_dir):
    """把 JSON / CSV / Markdown 报告写入指定目录（默认 output/），返回写入的文件路径。"""
    out_dir = pathlib.Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    base = "token-stats-%s" % stamp
    paths = []
    for suffix, content in (
        (".json", emit_json(meta, by_agent, by_date, unpriced, unparsed, bad_total)),
        (".csv", emit_csv(by_agent, by_date, meta["total"])),
        (".md", _md_report(meta, by_agent, by_date, unpriced, unparsed, bad_total, mode_notes)),
    ):
        p = out_dir / (base + suffix)
        p.write_text(content, encoding="utf-8")
        paths.append(p)
    return paths


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser(
        description=(
            "统计本机 Claude Code / WSL 发行版 / Codex 三域 agent 会话的 token 用量与成本。\n"
            "纯 Python 标准库实现。三域采集均为尽力而为：WSL 失败自动降级或跳过；"
            "Codex 目录缺失自动跳过，不影响本机统计。"),
        epilog=PRICE_SOURCE,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--days", type=int, default=0,
                    help="只统计最近 N 天(会话事件本地日期)；默认 0=全部")
    ap.add_argument("--no-wsl", action="store_true", help="跳过 WSL 各发行版采集")
    ap.add_argument("--distros", default="", metavar="D1,D2",
                    help="只采集指定 WSL 发行版(逗号分隔)，其余跳过")
    ap.add_argument("--csv", action="store_true", help="以 CSV 输出到标准输出")
    ap.add_argument("--json", action="store_true", help="以 JSON 输出到标准输出")
    ap.add_argument("--out-dir", default="", metavar="DIR",
                    help="可选：产出目录（写出 .json/.csv/.md 三份报告）；不指定则不写文件，仅终端/标准输出")
    ap.add_argument("--no-save", action="store_true", help="不写产出文件（默认即不写；兼容参数）")
    ap.add_argument("--debug", action="store_true", help="输出详细执行提示")
    args = ap.parse_args(argv)

    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    mode_notes = []
    selected = [d.strip() for d in args.distros.split(",") if d.strip()]

    # ---------- 1. 本机 Claude ----------
    local_files = iter_jsonl_files(LOCAL_CLAUDE_ROOT)
    local_n = len(local_files)
    if args.debug:
        print("[debug] 本机 jsonl 文件数: %d" % local_n)

    # ---------- 2. WSL ----------
    wsl_entries = []
    distro_names = []
    codex_note = None
    if not args.no_wsl:
        distro_list = wsl_list_distros()
        distro_names = [d for d, _ in distro_list]
        if selected:
            distro_names = [d for d in distro_names if d in selected]
            for s in set(selected) - set(distro_names):
                mode_notes.append("WSL 发行版 %s 未在 wsl -l -v 中发现，跳过" % s)
        for d in distro_names:
            entries, mode = wsl_collect(d)
            if mode == "skip":
                mode_notes.append("WSL 发行版 %s 不可达(UNC 直读与降级均失败)，已跳过" % d)
            elif mode == "fallback":
                mode_notes.append("WSL 发行版 %s: UNC 直读不可达，已降级为发行版内 tar 打包读取" % d)
            else:
                mode_notes.append("WSL 发行版 %s: UNC 直读成功" % d)
            if mode == "direct":
                for rel, fn, abspath in entries:
                    wsl_entries.append((d, rel, fn, abspath, "file"))
            elif mode == "fallback":
                for agent_dir, fn, text in entries:
                    wsl_entries.append((d, agent_dir, fn, text, "text"))
    else:
        mode_notes.append("WSL: 按 --no-wsl 跳过")

    # ---------- 3. Codex（尽力而为） ----------
    codex_files = []
    codex_n = 0
    try:
        if os.path.isdir(CODEX_ROOT):
            codex_files = iter_jsonl_files(CODEX_ROOT)
            codex_n = len(codex_files)
        else:
            codex_note = "目录不存在(%s)，已跳过" % CODEX_ROOT
            mode_notes.append("Codex: %s" % codex_note)
    except OSError as e:
        codex_note = str(e)
        mode_notes.append("Codex: 访问失败(%s)，已跳过" % e)

    # ---------- 4. 解析 ----------
    seen = set()
    rows = []
    unparsed = {}
    bad_total = 0
    files_ok = 0
    dup_files = 0

    day_cut = None
    if args.days and args.days > 0:
        day_cut = (dt.datetime.now() - dt.timedelta(days=args.days - 1)).date()

    def feed_rows(agent, pairs):
        """pairs: [(filename, payload, kind)] —— kind: 'file'(磁盘路径) | 'text'(内容)"""
        nonlocal bad_total, files_ok, dup_files
        for fn, payload, kind in pairs:
            uid = session_uuid(fn)
            src_label = "%s/%s" % (agent, fn)
            is_codex = (agent == "codex")
            if kind == "text":
                res, bad, reason = parse_text(payload, fn, is_codex=is_codex)
            else:
                res, bad, reason = parse_file(payload, is_codex=is_codex)
            if reason is not None:
                unparsed[src_label] = reason
                continue
            files_ok += 1
            bad_total += bad
            if uid in seen:
                dup_files += 1
                continue
            seen.add(uid)
            for rr in res:
                if day_cut is not None and rr["day"] is not None and rr["day"] < day_cut:
                    continue
                rows.append({"uuid": uid, "agent": agent, "model": rr["model"],
                             "in": rr["in"], "out": rr["out"], "rd": rr["rd"],
                             "wr": rr["wr"], "day": rr["day"], "src_file": src_label})

    # 本机
    for rel, fn, abspath in local_files:
        feed_rows(rel if rel else "?", [(fn, abspath, "file")])
    # WSL
    for distro, agent_dir, fn, payload, kind in wsl_entries:
        agent = "%s::%s" % (distro, agent_dir) if agent_dir != "." else distro
        feed_rows(agent, [(fn, payload, kind)])
    # Codex
    for rel, fn, abspath in codex_files:
        feed_rows("codex", [(fn, abspath, "file")])

    by_agent, by_date, unpriced, total = aggregate(rows)

    meta = {
        "now": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "scope": "本机 Claude Code + WSL(%s) + Codex%s" % (
            ",".join(distro_names) if distro_names else ("已跳过" if args.no_wsl else "无可用发行版"),
            "(已跳过)" if codex_note else "",
        ),
        "price_source_line": "来源见 --help 中文说明(整理日期 %s)；汇率/估算假设均已注明" % PRICE_SOURCE_DATE,
        "config": {"days": args.days, "no_wsl": args.no_wsl,
                   "distros": args.distros, "csv": args.csv, "json": args.json},
        "total": total,
        "files_scanned": local_n + len(wsl_entries) + codex_n,
        "files_local": local_n,
        "files_wsl": len(wsl_entries),
        "files_codex": codex_n,
        "files_ok": files_ok,
        "dup_files_skipped": dup_files,
        "rows_count": len(rows),
    }

    if args.csv:
        sys.stdout.write(emit_csv(by_agent, by_date, total))
    elif args.json:
        sys.stdout.write(emit_json(meta, by_agent, by_date, unpriced, unparsed, bad_total))
    else:
        emit_terminal(meta, by_agent, by_date, unpriced, unparsed, bad_total, mode_notes)

    if args.out_dir and not args.no_save:
        saved = write_outputs(meta, by_agent, by_date, unpriced, unparsed, bad_total,
                              mode_notes, args.out_dir)
        print("\n📁 产出已保存:")
        for p in saved:
            print("   %s" % p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
