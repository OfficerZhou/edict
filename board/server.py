#!/usr/bin/env python3
"""
军机处 · 极简本地看板服务（零依赖，stdlib only）

读取 data/tasks_source.json + data/audit_log.json，为浏览器提供看板数据。
与旧 dashboard 无任何依赖关系；agent 通过 scripts/kanban_update.py 写卡，本服务只是"眼睛"。

用法:
  python board/server.py            # 默认 127.0.0.1:7891
  python board/server.py --port 8080
"""
import argparse
import json
import pathlib
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / 'data'
HTML = pathlib.Path(__file__).resolve().parent / 'board.html'

sys.path.insert(0, str(ROOT / 'scripts'))
from file_lock import atomic_json_read  # noqa: E402  （与 kanban_update.py 同一套原子读）


def read_json(path, default):
    return atomic_json_read(path, default)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        if self.path in ('/', '/index.html'):
            self._send_file(HTML, 'text/html; charset=utf-8')
        elif self.path == '/api/board':
            self._send_json({
                'tasks': read_json(DATA / 'tasks_source.json', []),
                'audit': read_json(DATA / 'audit_log.json', []),
                'generatedAt': __import__('datetime').datetime.now().isoformat(timespec='seconds'),
            })
        else:
            self.send_error(404)

    def _send_file(self, path, ctype):
        try:
            body = path.read_bytes()
        except Exception:
            self.send_error(500)
            return
        self.send_response(200)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, obj):
        body = json.dumps(obj, ensure_ascii=False, indent=1).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):  # 静默访问日志
        pass


def main():
    try:
        # Windows GBK 控制台对 emoji 无解，重配置成 UTF-8 避免打印即崩溃
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument('--port', type=int, default=7891)
    ap.add_argument('--host', default='127.0.0.1')
    args = ap.parse_args()

    httpd = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f'🏛️  军机处看板: http://{args.host}:{args.port}  (Ctrl+C 停止)')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
