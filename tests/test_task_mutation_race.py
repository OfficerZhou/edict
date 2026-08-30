"""Tests for task mutation atomicity — verifying that concurrent writers
cannot clobber each other's changes on the tasks JSON blackboard.

The classic race: ``load_tasks()`` + modify + ``save_tasks()`` allows two
concurrent writers to both read the same snapshot, each modify a different
field, and the second save overwrites the first's changes (TOCTOU).

``scripts/task_mutation.py`` provides ``modify_tasks()`` / ``modify_task()``
wrappers around ``file_lock.atomic_json_update()`` which hold the file lock
for the entire read-modify-write cycle. These tests verify that contract.

（本文件前身覆盖旧 dashboard 的调度器 scan/retry/rollback 路径；那些功能已随旧看板
栈移除，相关测试类同时下线——只剩原子性契约本身的验证。）
"""
import json
import pathlib
import sys
import threading

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))

import task_mutation as srv  # noqa: E402


def _setup_server(monkeypatch, tmp_path, tasks=None):
    """Bootstrap task_mutation with an isolated data directory."""
    data_dir = tmp_path / 'data'
    data_dir.mkdir()
    tasks_path = data_dir / 'tasks_source.json'
    tasks_path.write_text(json.dumps(tasks or [], ensure_ascii=False), encoding='utf-8')

    monkeypatch.setattr(srv, 'DATA', data_dir)
    return srv, data_dir, tasks_path


class TestModifyTasksAtomicity:
    """Verify modify_tasks/modify_task use atomic_json_update and behave."""

    def test_modify_tasks_exists_and_callable(self, monkeypatch, tmp_path):
        srv, _, _ = _setup_server(monkeypatch, tmp_path)
        assert callable(getattr(srv, 'modify_tasks', None)), \
            'modify_tasks must be a callable function on task_mutation module'

    def test_modify_task_exists_and_callable(self, monkeypatch, tmp_path):
        srv, _, _ = _setup_server(monkeypatch, tmp_path)
        assert callable(getattr(srv, 'modify_task', None)), \
            'modify_task must be a callable function on task_mutation module'

    def test_modify_task_updates_single_task(self, monkeypatch, tmp_path):
        task = {
            'id': 'T-001', 'title': '测试', 'state': 'Doing',
            'org': '兵部', 'updatedAt': '2026-04-22T00:00:00Z',
        }
        srv, _, tasks_path = _setup_server(monkeypatch, tmp_path, [task])

        found = srv.modify_task('T-001', lambda t: t.update({'state': 'Review'}))
        assert found is True

        data = json.loads(tasks_path.read_text(encoding='utf-8'))
        assert data[0]['state'] == 'Review'
        assert 'updatedAt' in data[0]  # auto-stamped

    def test_modify_task_returns_false_for_missing(self, monkeypatch, tmp_path):
        srv, _, _ = _setup_server(monkeypatch, tmp_path, [])
        found = srv.modify_task('NONEXISTENT', lambda t: t.update({'state': 'Done'}))
        assert found is False

    def test_modify_tasks_bulk_update(self, monkeypatch, tmp_path):
        tasks = [
            {'id': 'T-A', 'title': 'A', 'state': 'Doing', 'org': '', 'updatedAt': ''},
            {'id': 'T-B', 'title': 'B', 'state': 'Doing', 'org': '', 'updatedAt': ''},
        ]
        srv, _, tasks_path = _setup_server(monkeypatch, tmp_path, tasks)

        def _mark_all_done(tasks):
            for t in tasks:
                t['state'] = 'Done'
            return tasks

        srv.modify_tasks(_mark_all_done)

        data = json.loads(tasks_path.read_text(encoding='utf-8'))
        assert all(t['state'] == 'Done' for t in data)


class TestConcurrentModifyTask:
    """Simulate the race that existed before the fix: two threads
    concurrently modifying different fields of the same task."""

    def test_concurrent_writes_both_persist(self, monkeypatch, tmp_path):
        """Two threads updating different fields should both be visible
        in the final state (no lost updates)."""
        task = {
            'id': 'T-RACE', 'title': '竞争测试', 'state': 'Doing',
            'org': '兵部', 'updatedAt': '2026-04-22T02:00:00Z',
            '_scheduler': {
                'field_a': 'initial_a', 'field_b': 'initial_b',
            },
        }
        srv, _, tasks_path = _setup_server(monkeypatch, tmp_path, [task])

        barrier = threading.Barrier(2, timeout=5)
        errors = []

        def update_field_a():
            try:
                barrier.wait()
                srv.modify_task('T-RACE', lambda t: t.setdefault('_scheduler', {}).update({'field_a': 'updated_a'}))
            except Exception as e:
                errors.append(e)

        def update_field_b():
            try:
                barrier.wait()
                srv.modify_task('T-RACE', lambda t: t.setdefault('_scheduler', {}).update({'field_b': 'updated_b'}))
            except Exception as e:
                errors.append(e)

        t1 = threading.Thread(target=update_field_a)
        t2 = threading.Thread(target=update_field_b)
        t1.start()
        t2.start()
        t1.join(timeout=10)
        t2.join(timeout=10)

        assert not errors, f'Thread errors: {errors}'

        data = json.loads(tasks_path.read_text(encoding='utf-8'))
        sched = data[0].get('_scheduler', {})

        # With atomic modify_task, BOTH updates must be visible.
        # The old load_tasks/save_tasks pattern would lose one.
        assert sched['field_a'] == 'updated_a', \
            f'field_a lost: {sched.get("field_a")}'
        assert sched['field_b'] == 'updated_b', \
            f'field_b lost: {sched.get("field_b")}'


class TestSourceAudit:
    """Verify the helpers really delegate to the locking primitive —
    enforced by source inspection, like the original test."""

    def test_modify_tasks_uses_atomic_json_update(self):
        import inspect

        source = inspect.getsource(srv.modify_tasks)
        assert 'atomic_json_update' in source, \
            'modify_tasks must use atomic_json_update for file-level locking'

    def test_modify_task_delegates_to_modify_tasks(self):
        import inspect

        source = inspect.getsource(srv.modify_task)
        assert 'modify_tasks' in source or 'atomic_json_update' in source, \
            'modify_task should delegate to modify_tasks or atomic_json_update'
