#!/usr/bin/env python3
"""feedback_server.py -- serve the walkable map viewer with live feedback.

Serves the generated viewer site (build_map_viewer.py --out DIR) and a small
JSON API that lets whoever is walking a map pin notes to world positions, and
lets agents read and answer them while the walk goes on.

Storage (an append-only event log, replayed at start-up):
  <notes-dir>/events.jsonl   one JSON event per line: note, reply, status.
                             `tail -f` it to follow a walk as it happens.
  <notes-dir>/OPEN.md        regenerated on every change: the open notes,
                             newest first, with the items under each pin.
  <site>/feedback-shots/     the view snapshot attached to a note. These
                             contain Origin art, so they stay out of git.

API (paths are relative, so the site can sit behind a path prefix):
  GET  api/state                      {"fixed": sha, "notes": [...]}
  GET  api/events                     Server-Sent Events, one per change
  POST api/notes                      {map, x, y, z, zoom, kind, text, who,
                                       shot: data URL (optional)}
  POST api/notes/<id>/reply           {who, text}
  POST api/notes/<id>/status          {who, status: open|fixed|wontfix}

Agents answer from a shell, for example:
  curl -s localhost:8460/api/notes/7/reply -d '{"who":"agent:codex","text":"moved the wall"}'
  curl -s localhost:8460/api/notes/7/status -d '{"who":"agent:codex","status":"fixed"}'

Usage:
  python3 tools/map_viewer/feedback_server.py \\
      --site ~/projects/lost-vale-maps/site [--port 8460]
"""

import argparse
import base64
import hashlib
import http.server
import json
import os
import queue
import re
import sys
import threading
import time
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
MP_SRC = os.path.join(REPO, 'agents', 'map-populator', 'src')
sys.path.insert(0, MP_SRC)

KINDS = ('bug', 'visual', 'walk', 'idea', 'good')
STATUSES = ('open', 'fixed', 'wontfix')
NEAR_XY = 96          # world units around the pin searched for items
NEAR_MAX = 15
MAX_BODY = 12 << 20   # a 2x-DPI view snapshot fits comfortably


def now():
    return time.strftime('%Y-%m-%dT%H:%M:%S%z')


class Items:
    """Expanded FIXED.DAT items per map, reloaded when FIXED.DAT changes."""

    def __init__(self, data_root):
        self.build = os.path.join(data_root, 'shared', 'build')
        self.static = os.path.join(data_root, 'shared', 'data', 'u8-install',
                                   'STATIC')
        self.lock = threading.Lock()
        self.key = None
        self.maps = {}
        self.sha = None

    def _fixed(self):
        return os.path.join(self.build, 'FIXED.DAT')

    def _refresh(self):
        st = os.stat(self._fixed())
        glob_path = os.path.join(self.build, 'GLOB.FLX')
        if not os.path.exists(glob_path):
            glob_path = os.path.join(self.static, 'GLOB.FLX')
        gs = os.stat(glob_path)
        key = (st.st_mtime_ns, st.st_size, gs.st_mtime_ns, gs.st_size)
        if key == self.key:
            return
        from u8_map import MapArchive
        from glob_catalog import GlobReader
        import item_sorter as isort
        h = hashlib.sha256()
        with open(self._fixed(), 'rb') as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b''):
                h.update(chunk)
        self.sha = h.hexdigest()[:8]
        self.arch = MapArchive(self._fixed())
        self.globs = GlobReader(glob_path)
        self.sorter = isort.ItemSorter(
            typeflag=os.path.join(self.build, 'TYPEFLAG.DAT'),
            shapes=os.path.join(self.build, 'U8SHAPES.FLX'))
        try:
            from shape_names import all_names
            self.names = all_names()
        except Exception:                  # names are a convenience only
            self.names = {}
        self.maps = {}
        self.isort = isort
        self.key = key

    def fixed_sha(self):
        with self.lock:
            try:
                self._refresh()
            except OSError:
                return None
            return self.sha

    def near(self, mapnum, x, y, z):
        """Items whose footpad lies within NEAR_XY of (x, y) and whose
        height range meets an Avatar standing at z, nearest first."""
        with self.lock:
            self._refresh()
            if mapnum not in self.maps:
                from map_preview import expand_globs
                self.maps[mapnum] = expand_globs(
                    self.arch.get_map_items(mapnum), self.globs)
            items = self.maps[mapnum]
            out = []
            for it in items:
                if it.flags & 0x0008:                     # FLG_CONTAINED
                    continue
                inf = self.sorter.info(it.shape)
                xd, yd = inf['xd'], inf['yd']
                if it.flags & self.isort.FLG_FLIPPED:
                    xd, yd = yd, xd
                # U8 items sit at their max corner: footpad x-xd..x, y-yd..y
                dx = max(it.x - xd - x, 0, x - it.x)
                dy = max(it.y - yd - y, 0, y - it.y)
                d = max(dx, dy)
                if d > NEAR_XY:
                    continue
                if it.z > z + 56 or it.z + inf['zd'] < z - 16:
                    continue
                out.append((d, -it.z, dict(
                    shape=it.shape, frame=it.frame, x=it.x, y=it.y, z=it.z,
                    q=it.quality, npc=it.npcnum, d=d,
                    dims=[xd, yd, inf['zd']],
                    name=self.names.get(it.shape),
                    editor=inf['editor'])))
            out.sort(key=lambda t: (t[0], t[1]))
            return [o for _, _, o in out[:NEAR_MAX]]


class Store:
    def __init__(self, notes_dir, site, items):
        self.dir = notes_dir
        self.site = site
        self.items = items
        self.log = os.path.join(notes_dir, 'events.jsonl')
        self.lock = threading.Lock()
        self.notes = {}
        self.subs = set()
        os.makedirs(notes_dir, exist_ok=True)
        os.makedirs(os.path.join(site, 'feedback-shots'), exist_ok=True)
        if os.path.exists(self.log):
            with open(self.log, encoding='utf-8') as fh:
                for line in fh:
                    line = line.strip()
                    if line:
                        self._apply(json.loads(line))

    def _apply(self, ev):
        if ev['ev'] == 'note':
            n = dict(ev['note'])
            n.setdefault('thread', [])
            n.setdefault('status', 'open')
            self.notes[n['id']] = n
        elif ev['id'] in self.notes:
            n = self.notes[ev['id']]
            if ev['ev'] == 'reply':
                n['thread'].append(dict(who=ev['who'], text=ev['text'],
                                        ts=ev['ts']))
            elif ev['ev'] == 'status':
                n['status'] = ev['status']
                n['thread'].append(dict(who=ev['who'], ts=ev['ts'],
                                        text=f"status: {ev['status']}"))

    def _emit(self, ev):
        """Caller holds the lock."""
        with open(self.log, 'a', encoding='utf-8') as fh:
            fh.write(json.dumps(ev, separators=(',', ':')) + '\n')
        self._apply(ev)
        self._write_open()
        msg = json.dumps(ev)
        for q in list(self.subs):
            q.put(msg)

    def _write_open(self):
        open_notes = sorted((n for n in self.notes.values()
                             if n['status'] == 'open'),
                            key=lambda n: n['id'], reverse=True)
        lines = ['# Open map feedback', '',
                 'Generated by tools/map_viewer/feedback_server.py from '
                 'events.jsonl; do not edit. Answer through the API (see the '
                 'server docstring).', '']
        if not open_notes:
            lines.append('Nothing open.')
        for n in open_notes:
            lines.append(f"## #{n['id']} Map {n['map']} ({n['x']}, {n['y']}, "
                         f"{n['z']}) {n['kind']}, {n['who']}, {n['ts']}")
            lines.append('')
            lines.append(n['text'])
            lines.append('')
            lines.append(f"FIXED.DAT {n.get('fixed') or '?'}; view "
                         f"map{n['map']:02d}.html#{n['x']},{n['y']},{n['z']},"
                         f"{n.get('zoom', 1)}"
                         + (f"; snapshot {n['shot']}" if n.get('shot') else ''))
            if n.get('near'):
                lines.append('')
                lines.append('| shape:frame | name | x, y, z | footpad | dist |')
                lines.append('|---|---|---|---|---|')
                for it in n['near']:
                    lines.append(
                        f"| {it['shape']}:{it['frame']} | {it['name'] or ''}"
                        f"{' (editor)' if it['editor'] else ''} | "
                        f"{it['x']}, {it['y']}, {it['z']} | "
                        f"{it['dims'][0]}x{it['dims'][1]}x{it['dims'][2]} | "
                        f"{it['d']} |")
            for t in n['thread']:
                lines.append('')
                lines.append(f"> {t['who']} ({t['ts']}): {t['text']}")
            lines.append('')
        tmp = os.path.join(self.dir, 'OPEN.md.tmp')
        with open(tmp, 'w', encoding='utf-8') as fh:
            fh.write('\n'.join(lines) + '\n')
        os.replace(tmp, os.path.join(self.dir, 'OPEN.md'))

    def add_note(self, body):
        mapnum = int(body['map'])
        x, y, z = int(body['x']), int(body['y']), int(body['z'])
        text = str(body.get('text', '')).strip()
        if not text:
            raise ValueError('text is empty')
        kind = body.get('kind') if body.get('kind') in KINDS else 'bug'
        try:
            near = self.items.near(mapnum, x, y, z)
            fixed = self.items.fixed_sha()
        except Exception as e:             # the note matters more than this
            near, fixed = [], None
            print(f'near-item lookup failed: {e}', file=sys.stderr)
        with self.lock:
            nid = max(self.notes, default=0) + 1
            shot = None
            m = re.match(r'data:image/(png|webp|jpeg);base64,(.*)$',
                         body.get('shot') or '', re.S)
            if m:
                ext = 'jpg' if m.group(1) == 'jpeg' else m.group(1)
                shot = f'feedback-shots/{nid:04d}.{ext}'
                with open(os.path.join(self.site, shot), 'wb') as fh:
                    fh.write(base64.b64decode(m.group(2)))
            note = dict(id=nid, map=mapnum, x=x, y=y, z=z,
                        zoom=body.get('zoom', 1), kind=kind, text=text,
                        who=str(body.get('who') or 'Douglas')[:40],
                        ts=now(), fixed=fixed, shot=shot, near=near,
                        status='open', thread=[])
            self._emit(dict(ev='note', note=note))
            return self.notes[nid]

    def reply(self, nid, body):
        text = str(body.get('text', '')).strip()
        if not text:
            raise ValueError('text is empty')
        with self.lock:
            if nid not in self.notes:
                raise KeyError(nid)
            self._emit(dict(ev='reply', id=nid, ts=now(), text=text,
                            who=str(body.get('who') or 'agent')[:40]))
            return self.notes[nid]

    def status(self, nid, body):
        st = body.get('status')
        if st not in STATUSES:
            raise ValueError(f'status must be one of {STATUSES}')
        with self.lock:
            if nid not in self.notes:
                raise KeyError(nid)
            self._emit(dict(ev='status', id=nid, ts=now(), status=st,
                            who=str(body.get('who') or 'agent')[:40]))
            return self.notes[nid]

    def state(self):
        with self.lock:
            return dict(fixed=self.items.fixed_sha(),
                        notes=sorted(self.notes.values(),
                                     key=lambda n: n['id']))


def make_handler(store, site, prefix):
    class H(http.server.SimpleHTTPRequestHandler):
        protocol_version = 'HTTP/1.1'

        def __init__(self, *a, **kw):
            super().__init__(*a, directory=site, **kw)

        def log_message(self, fmt, *args):
            if '/api/' in self.path and not self.path.endswith('/api/events'):
                sys.stderr.write('%s %s\n' % (self.log_date_time_string(),
                                              fmt % args))

        def _route(self):
            p = urllib.parse.urlsplit(self.path).path
            if prefix and p.startswith(prefix):
                p = p[len(prefix):] or '/'
            return p

        def translate_path(self, path):
            return super().translate_path(self._route())

        def _json(self, code, obj):
            data = json.dumps(obj).encode()
            self.send_response(code)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(data)))
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            self.wfile.write(data)

        def end_headers(self):
            if self._route().endswith('.html') or self._route().endswith('/'):
                self.send_header('Cache-Control', 'no-cache')
            super().end_headers()

        def do_GET(self):
            p = self._route()
            if p == '/api/state':
                return self._json(200, store.state())
            if p == '/api/events':
                return self._events()
            return super().do_GET()

        def _events(self):
            q = queue.Queue()
            self.send_response(200)
            self.send_header('Content-Type', 'text/event-stream')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Accel-Buffering', 'no')
            self.end_headers()
            self.close_connection = True
            with store.lock:
                store.subs.add(q)
            try:
                self.wfile.write(b': hello\n\n')
                self.wfile.flush()
                while True:
                    try:
                        msg = q.get(timeout=15)
                        self.wfile.write(f'data: {msg}\n\n'.encode())
                    except queue.Empty:
                        self.wfile.write(b': ping\n\n')
                    self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError, OSError):
                pass
            finally:
                with store.lock:
                    store.subs.discard(q)

        def do_POST(self):
            p = self._route()
            n = int(self.headers.get('Content-Length') or 0)
            if n > MAX_BODY:
                return self._json(413, dict(error='body too large'))
            try:
                body = json.loads(self.rfile.read(n) or b'{}')
                if p == '/api/notes':
                    return self._json(200, store.add_note(body))
                m = re.match(r'^/api/notes/(\d+)/(reply|status)$', p)
                if m:
                    fn = store.reply if m.group(2) == 'reply' else store.status
                    return self._json(200, fn(int(m.group(1)), body))
                return self._json(404, dict(error='no such endpoint'))
            except KeyError as e:
                return self._json(404, dict(error=f'no note {e}'))
            except (ValueError, TypeError) as e:
                return self._json(400, dict(error=str(e)))

    return H


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[1])
    ap.add_argument('--site', required=True,
                    help='build_map_viewer.py --out directory')
    ap.add_argument('--notes', default=os.path.join(REPO, 'docs',
                                                    'map-feedback'),
                    help='where events.jsonl and OPEN.md live')
    ap.add_argument('--data-root', default=REPO,
                    help='checkout holding shared/build (for the item lookup)')
    ap.add_argument('--host', default='127.0.0.1')
    ap.add_argument('--port', type=int, default=8460)
    ap.add_argument('--prefix', default='/lostvale-maps',
                    help='path prefix to strip if the proxy keeps it')
    args = ap.parse_args()
    site = os.path.abspath(os.path.expanduser(args.site))
    store = Store(os.path.abspath(args.notes), site, Items(args.data_root))
    with store.lock:
        store._write_open()
    srv = http.server.ThreadingHTTPServer(
        (args.host, args.port), make_handler(store, site, args.prefix))
    srv.daemon_threads = True
    print(f'serving {site} on http://{args.host}:{args.port}/ '
          f'({len(store.notes)} notes loaded)', flush=True)
    srv.serve_forever()


if __name__ == '__main__':
    main()
