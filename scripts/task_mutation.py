#!/usr/bin/env python3
"""
看板任务的原子读改写助手（TOCTOU 安全）。

并发写者（多个 agent / 定时任务 / HTTP 处理器）同时改 tasks_source.json 时，
"先读后写"模式必然丢更新。本模块把 读-改-写 全程放进文件锁（file_lock.atomic_json_update），
与 dashboard 时代 server.py 的 modify_tasks/modify_task 行为一致，作为中立核心保留。

用法:
  from task_mutation import modify_task
  modify_task('JJC-xxx', lambda t: t.update(now='新动态'))
"""
import os
import pathlib

BASE = pathlib.Path(os.environ['EDICT_HOME']) if 'EDICT_HOME' in os.environ else pathlib.Path(__file__).resolve().parent.parent
DATA = BASE / 'data'

from file_lock import atomic_json_update  # noqa: E402
from utils import now_iso  # noqa: E402


def modify_tasks(modifier, data_dir=None):
    """原子读改写整个任务列表（锁内执行 modifier(tasks) 并落盘）。"""
    path = (data_dir or DATA) / 'tasks_source.json'
    atomic_json_update(path, modifier, default=[])


def modify_task(task_id, updater, data_dir=None):
    """原子更新单个任务；updater(task) 在锁内原地修改。返回是否找到该任务。"""
    found = [False]

    def _modifier(tasks):
        task = next((t for t in tasks if t.get('id') == task_id), None)
        if task is None:
            return tasks
        updater(task)
        task['updatedAt'] = now_iso()
        found[0] = True
        return tasks

    modify_tasks(_modifier, data_dir)
    return found[0]
