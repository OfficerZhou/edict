"""技能元数据与中性词汇 lint：确保 skills/ 是 harness 无关的规范内容。

铁律：技能正文只写动作，不写平台工具名（工具映射在 references/ 里）。
"""
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / 'skills'

# 平台上具名工具的拒绝清单（技能正文与 frontmatter 均不得出现）
NEUTRAL_DENY = re.compile(
    r'\b(Task|Bash|Read|Write|Edit|Grep|Glob|TodoWrite|AskUserQuestion|'
    r'spawn_agent|apply_patch|sessions_send|WebFetch|WebSearch)\b'
)

EXPECTED_SKILLS = {
    'using-edict', 'edict-triaging', 'edict-planning', 'edict-review',
    'edict-dispatch', 'edict-ministries', 'edict-report', 'edict-kanban',
}


def _skill_files():
    return sorted(SKILLS_DIR.glob('*/SKILL.md'))


def _frontmatter(text: str) -> dict | None:
    if not text.startswith('---\n'):
        return None
    m = re.match(r'^---\n([\s\S]*?)\n---\n', text)
    if not m:
        return None
    meta = {}
    for line in m.group(1).split('\n'):
        if ':' in line:
            k, v = line.split(':', 1)
            meta[k.strip()] = v.strip().strip('"').strip("'")
    return meta


def test_all_expected_skills_present():
    names = {p.parent.name for p in _skill_files()}
    assert EXPECTED_SKILLS <= names, f'缺失技能: {EXPECTED_SKILLS - names}'


def test_frontmatter_valid():
    for f in _skill_files():
        text = f.read_text(encoding='utf-8')
        meta = _frontmatter(text)
        assert meta is not None, f'{f} 缺少 YAML frontmatter'
        assert meta.get('name'), f'{f} frontmatter 缺 name'
        assert meta.get('description'), f'{f} frontmatter 缺 description'
        assert meta['name'] == f.parent.name, f'{f} name 与目录名不一致'


def test_description_length_bounded():
    # dsh 技能描述上限 1024 字符；过长会截断丢失触发语
    for f in _skill_files():
        meta = _frontmatter(f.read_text(encoding='utf-8'))
        assert len(meta['description']) <= 1024, f'{f} description 超过 1024 字符'


def test_description_has_trigger_force():
    # 触发性描述（强触发语或明确触发时机），保证自动触发可靠性
    for f in _skill_files():
        meta = _frontmatter(f.read_text(encoding='utf-8'))
        desc = meta['description']
        assert ('MUST' in desc or 'Use when' in desc or '触发' in desc), \
            f'{f} description 缺少强触发语（MUST / Use when / 触发）'


def test_neutral_vocabulary():
    """技能正文禁止出现平台工具名；references/ 目录豁免（那里就是翻译表）。"""
    for f in _skill_files():
        if 'references' in f.parts:
            continue
        text = f.read_text(encoding='utf-8')
        m = NEUTRAL_DENY.search(text)
        assert m is None, f'{f} 出现平台工具名 "{m.group(1)}" —— 技能只写动作，工具映射放 references/'


def test_no_placeholder_substitution_left():
    # OpenClaw 安装器的 __REPO_DIR__ 占位符不应泄漏进中立技能
    for f in _skill_files():
        assert '__REPO_DIR__' not in f.read_text(encoding='utf-8'), f'{f} 残留 __REPO_DIR__ 占位符'


if __name__ == '__main__':
    raise SystemExit(pytest.main([__file__, '-v']))
