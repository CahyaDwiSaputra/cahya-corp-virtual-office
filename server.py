import os
import sys
import re
import json
import time
import socket
import sqlite3
import shutil
import threading
import subprocess
from pathlib import Path
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

PORT = 8090
DIR = Path.home() / "virtual-office"
STATUS_FILE = DIR / "status.json"
LOG_FILE = DIR / "server.log"
STATE_DB_PATH = Path(os.environ.get("LOCALAPPDATA", "")) / "hermes" / "state.db"

PROFILES = ["pm", "uiux", "frontend", "backend", "database", "devops", "qa", "security"]

PROFILE_SPECS = {
    "pm": {
        "name": "Tech Lead",
        "role": "Product Manager",
        "spec": "Menyusun PRD, batasan scope, user stories, dan acceptance criteria"
    },
    "uiux": {
        "name": "UI/UX Lead",
        "role": "Design Systems",
        "spec": "Merancang wireframe, user flow, visual design tokens, layout antarmuka, dan aksesibilitas"
    },
    "frontend": {
        "name": "Frontend Dev",
        "role": "Client & Web UI",
        "spec": "Membangun komponen UI web, client state management, styling responsive, dan integrasi API"
    },
    "backend": {
        "name": "Backend Dev",
        "role": "API & Microservices",
        "spec": "Membangun REST API endpoint, controller, middleware validasi, autentikasi, dan logika bisnis"
    },
    "database": {
        "name": "DB Architect",
        "role": "Data & Storage",
        "spec": "Merancang skema relasional tabel, model data ORM, migrasi database, dan optimasi query"
    },
    "devops": {
        "name": "DevOps Eng",
        "role": "Cloud & Infrastructure",
        "spec": "Mengonfigurasi Docker container, pipeline CI/CD GitHub Actions, Nginx proxy, dan deployment"
    },
    "qa": {
        "name": "QA Specialist",
        "role": "Test Automation",
        "spec": "Menulis skenario test otomatis E2E Playwright, unit test, dan verifikasi alur kerja"
    },
    "security": {
        "name": "AppSec Lead",
        "role": "Security & OWASP",
        "spec": "Audit celah keamanan OWASP, sanitasi input, proteksi celah injeksi/auth, dan dependensi"
    }
}

status_lock = threading.Lock()
active_tasks = {}
recent_logs = []
execution_semaphore = threading.Semaphore(2)  # Max 2 concurrent CLI runs to prevent CPU/API throttling

def log_debug(msg):
    ts = time.strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{ts}] {msg}"
    recent_logs.append({"time": ts, "message": msg})
    if len(recent_logs) > 100:
        recent_logs.pop(0)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass
    print(line)

def get_status_data_locked():
    data = {}
    if STATUS_FILE.exists():
        try:
            data = json.loads(STATUS_FILE.read_text(encoding="utf-8"))
        except Exception:
            data = {}

    changed = False
    for pid in PROFILES:
        if pid not in data:
            spec = PROFILE_SPECS[pid]
            data[pid] = {
                "name": spec["name"],
                "role": spec["role"],
                "status": "idle",
                "task": f"Standby - {spec['spec']}",
                "last_output": f"Siap menjalankan tugas {spec['role']}.",
                "active_pid": None,
                "last_updated": time.time()
            }
            changed = True

    if changed:
        save_status_data_locked(data)

    return data

def save_status_data_locked(data):
    try:
        STATUS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception as e:
        log_debug(f"Error saving status: {e}")

def get_status_data():
    with status_lock:
        return get_status_data_locked()

def update_profile_status(profile, status=None, task=None, output=None, pid=None):
    with status_lock:
        data = get_status_data_locked()
        if profile in data:
            if status is not None:
                data[profile]["status"] = status
            if task is not None:
                data[profile]["task"] = task
            if output is not None:
                data[profile]["last_output"] = output
            if pid is not None:
                data[profile]["active_pid"] = pid
            data[profile]["last_updated"] = time.time()
            save_status_data_locked(data)

def batch_update_status(profile_updates):
    with status_lock:
        data = get_status_data_locked()
        for prof, fields in profile_updates.items():
            if prof in data:
                data[prof].update(fields)
                data[prof]["last_updated"] = time.time()
        save_status_data_locked(data)

def decompose_prompt(user_prompt):
    p = user_prompt.lower()

    # Domain indicators with regex word boundaries
    has_db = bool(re.search(r'\b(db|database|sql|postgres|postgresql|mysql|mongodb|prisma|drizzle|skema|schema|tabel|table|query|migrasi|migration|redis)\b', p))
    has_fe = bool(re.search(r'\b(frontend|react|next|nextjs|tailwind|css|html|komponen|component|button|modal|navbar|form|halaman|page|slicing|responsive|tampilan|antarmuka|ui|menu|header|footer)\b', p))
    has_be = bool(re.search(r'\b(backend|api|rest|endpoint|controller|service|middleware|express|fastapi|jwt|auth|login|register|token|crud|upload)\b', p))
    has_devops = bool(re.search(r'\b(docker|container|ci\/cd|pipeline|deploy|deployment|github actions|hosting|nginx|ssl|cloud|aws|k8s|kubernetes)\b', p))
    has_sec = bool(re.search(r'\b(security|keamanan|audit|owasp|vulnerability|celah|xss|sql injection|csrf|enkripsi|sanitize|proteksi)\b', p))
    has_qa = bool(re.search(r'\b(test|testing|uji|pengujian|e2e|unit test|playwright|vitest|bug|verifikasi)\b', p))
    has_design = bool(re.search(r'\b(desain|design|figma|wireframe|mockup|warna|kontras|layout|ux|user flow|interaksi)\b', p))
    has_pm = bool(re.search(r'\b(prd|roadmap|sprint|backlog|user story|scope|requirement|jadwal|rencana)\b', p))

    # Project / System / App / SRS triggers
    is_project_or_feature = bool(re.search(r'\b(project|proyek|develop|sistem|website|aplikasi|platform|toko|hosting|domain|vps|srs|figma|fitur|buatkan|bikin|mengerjakan)\b', p))
    is_broad = bool(re.search(r'\b(full stack|fullstack|keseluruhan|lengkap|seluruh tim|semua)\b', p))

    active_tasks_map = {}

    # If it is a whole project or broad feature development (e.g. CV Buana Logika Utama Hosting & VPS)
    if is_broad or (is_project_or_feature and any(k in p for k in ["project", "proyek", "srs", "sistem", "hosting", "website", "develop", "mengerjakan"])):
        active_tasks_map["pm"] = f"Menyusun PRD, WBS, dan arsitektur modul sistem untuk: {user_prompt}"
        active_tasks_map["uiux"] = f"Merancang design tokens, wireframe antarmuka, dan komponen Figma untuk: {user_prompt}"
        active_tasks_map["frontend"] = f"Membangun antarmuka web responsif, katalog layanan, dan checkout untuk: {user_prompt}"
        active_tasks_map["backend"] = f"Membangun REST API endpoint, controller pesanan, dan integrasi payment untuk: {user_prompt}"
        active_tasks_map["database"] = f"Merancang skema relasional tabel, model data ORM, dan migrasi untuk: {user_prompt}"
        active_tasks_map["devops"] = f"Menyiapkan container Docker, Nginx reverse proxy, dan deployment environment untuk: {user_prompt}"
        active_tasks_map["qa"] = f"Menulis skenario pengujian otomatis E2E dan verifikasi alur pemesanan untuk: {user_prompt}"
        active_tasks_map["security"] = f"Audit celah keamanan OWASP, validasi input domain, dan proteksi otentikasi untuk: {user_prompt}"
        return active_tasks_map, "Dekomposisi Menyeluruh Seluruh Tim Multi-Agent (8 Spesialis Berkolaborasi)"

    # Targeted tasks
    if has_db: active_tasks_map["database"] = f"Merancang skema database, model data, dan migrasi tabel untuk: {user_prompt}"
    if has_fe: active_tasks_map["frontend"] = f"Mengimplementasikan komponen UI, state management, dan styling web untuk: {user_prompt}"
    if has_be: active_tasks_map["backend"] = f"Membangun endpoint API, controller, dan middleware logika bisnis untuk: {user_prompt}"
    if has_devops: active_tasks_map["devops"] = f"Menyiapkan konfigurasi infrastruktur, container Docker, dan pipeline deployment untuk: {user_prompt}"
    if has_sec: active_tasks_map["security"] = f"Melakukan audit keamanan OWASP, sanitasi input, dan proteksi celah untuk: {user_prompt}"
    if has_qa: active_tasks_map["qa"] = f"Menulis skenario pengujian otomatis dan memverifikasi fungsionalitas untuk: {user_prompt}"
    if has_design: active_tasks_map["uiux"] = f"Merancang wireframe, user flow, dan desain visual antarmuka untuk: {user_prompt}"
    if has_pm: active_tasks_map["pm"] = f"Menyusun PRD, batasan scope, user stories, dan acceptance criteria untuk: {user_prompt}"

    if not active_tasks_map:
        active_tasks_map["pm"] = f"Menganalisis kebutuhan dan mendekomposisi tugas teknis untuk: {user_prompt}"

    names = [PROFILE_SPECS[p]["name"] for p in active_tasks_map.keys()]
    return active_tasks_map, f"Didelegasikan ke {len(active_tasks_map)} spesialis: {', '.join(names)}"

def is_pid_running(pid):
    if not pid:
        return False
    try:
        os.kill(pid, 0)
        return True
    except (OSError, ProcessLookupError):
        return False

def monitor_active_pids():
    while True:
        try:
            with status_lock:
                data = get_status_data_locked()
                changed = False
                for p_name in PROFILES:
                    info = data.get(p_name, {})
                    if p_name in active_tasks:
                        if info.get("status") != "working":
                            info["status"] = "working"
                            changed = True
                        continue

                    pid = info.get("active_pid")
                    if pid:
                        if is_pid_running(pid):
                            if info.get("status") != "working":
                                info["status"] = "working"
                                changed = True
                        else:
                            info["status"] = "idle"
                            info["active_pid"] = None
                            info["last_updated"] = time.time()
                            changed = True

                if changed:
                    save_status_data_locked(data)
        except Exception:
            pass
        time.sleep(1.5)

def execute_hermes_task(profile, prompt):
    active_tasks[profile] = True
    update_profile_status(profile, status="working", task=prompt)
    log_debug(f"[*] Starting task for [{profile}]: {prompt[:60]}")

    proc = None
    output = ""

    with execution_semaphore:
        try:
            hermes_bin = shutil.which("hermes") or "hermes"
            cmd = [hermes_bin, "-p", profile, "-z", prompt]

            creationflags = 0
            startupinfo = None
            if sys.platform == "win32":
                creationflags = subprocess.CREATE_NO_WINDOW
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = 0

            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                creationflags=creationflags,
                startupinfo=startupinfo
            )

            update_profile_status(profile, pid=proc.pid)
            stdout, stderr = proc.communicate(timeout=300)
            output = stdout.strip() if stdout else stderr.strip()

        except subprocess.TimeoutExpired:
            if proc:
                try:
                    proc.kill()
                    proc.communicate()
                except Exception:
                    pass
            output = "Error: Timeout setelah 300 detik"
        except Exception as e:
            if proc:
                try:
                    proc.kill()
                    proc.communicate()
                except Exception:
                    pass
            output = f"Error: {e}"

    if profile in active_tasks:
        del active_tasks[profile]

    update_profile_status(
        profile,
        status="idle",
        task=f"Selesai: {prompt[:35]}...",
        output=output,
        pid=None
    )
    log_debug(f"[+] Task finished for [{profile}]. Output: {output[:50]}")

def auto_detect_chat_tasks():
    """
    Continuous daemon thread that watches Hermes state.db in read-only mode.
    When any chat turn contains an actionable project or feature instruction,
    it automatically decomposes the prompt and sets the matching profiles to working!
    """
    if not STATE_DB_PATH.exists():
        log_debug(f"state.db not found at {STATE_DB_PATH}, skipping chat watcher")
        return

    last_seen_id = 0
    try:
        conn = sqlite3.connect(f"file:{STATE_DB_PATH}?mode=ro", uri=True)
        c = conn.cursor()
        c.execute("SELECT MAX(id) FROM messages WHERE role='user'")
        row = c.fetchone()
        if row and row[0]:
            last_seen_id = row[0]
        conn.close()
        log_debug(f"Hermes Chat Watcher initialized at message ID {last_seen_id}")
    except Exception as e:
        log_debug(f"Error initializing chat watcher: {e}")

    ACTION_KEYWORDS = [
        "buatkan", "bikin", "develop", "kerjakan", "mengerjakan", "bantu aku mengerjakan",
        "tolong buat", "fitur", "project", "proyek", "sistem", "website", "web",
        "api", "endpoint", "backend", "frontend", "database", "skema", "schema",
        "tabel", "table", "prisma", "drizzle", "sql", "ui", "ux", "desain", "design",
        "figma", "wireframe", "docker", "ci/cd", "pipeline", "deploy", "nginx",
        "test", "testing", "playwright", "vitest", "security", "audit", "owasp",
        "perbaiki", "fix", "optimasi", "srs", "hosting", "vps", "domain", "auth", "login"
    ]

    IGNORE_PATTERNS = [
        r"^jalankan$", r"^jalan$", r"^run$", r"^start$", r"^stop$", r"^tes$", r"^test$",
        r"^bukan itu$", r"^oke$", r"^siap$", r"^terima kasih$", r"^makasih$",
        r"aku ingin logikanya itu otomatis"
    ]

    while True:
        try:
            time.sleep(1.2)
            if not STATE_DB_PATH.exists():
                continue

            conn = sqlite3.connect(f"file:{STATE_DB_PATH}?mode=ro", uri=True)
            c = conn.cursor()
            c.execute(
                "SELECT id, content FROM messages WHERE role='user' AND id > ? ORDER BY id ASC LIMIT 5",
                (last_seen_id,)
            )
            new_msgs = c.fetchall()
            conn.close()

            for msg_id, content in new_msgs:
                last_seen_id = max(last_seen_id, msg_id)
                if not content:
                    continue

                clean_text = content.strip()
                if clean_text.startswith("[System:"):
                    continue

                clean_lower = clean_text.lower()
                if any(re.search(pat, clean_lower) for pat in IGNORE_PATTERNS):
                    continue

                text_to_check = re.sub(r'@(image|file|url):[^\s]+', '', clean_lower).strip()

                has_work_intent = any(kw in text_to_check for kw in ACTION_KEYWORDS)

                if has_work_intent and len(text_to_check) >= 5:
                    log_debug(f"[AUTO-DETECT] New task in chat (ID {msg_id}): {text_to_check[:60]}...")
                    task_map, explanation = decompose_prompt(clean_text)
                    targets = list(task_map.keys())

                    if targets:
                        log_debug(f"[AUTO-DETECT] Dispatched to {len(targets)} profiles: {targets}")
                        # Instantly update all matched profiles to working in 3D office
                        batch_updates = {}
                        for prof in targets:
                            batch_updates[prof] = {
                                "status": "working",
                                "task": task_map.get(prof, clean_text)
                            }
                        batch_update_status(batch_updates)

                        # Launch background task workers
                        for prof in targets:
                            prof_task = task_map.get(prof, clean_text)
                            t = threading.Thread(target=execute_hermes_task, args=(prof, prof_task), daemon=True)
                            t.start()

        except Exception as e:
            pass

class CahyaBridgeHandler(SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIR), **kwargs)

    def log_message(self, format, *args):
        pass

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Access-Control-Allow-Private-Network', 'true')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Connection', 'close')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_GET(self):
        path_clean = self.path.split('?')[0].rstrip('/')
        if path_clean == "/api/status":
            data = get_status_data()
            body = json.dumps(data, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        elif path_clean == "/api/logs":
            body = json.dumps(recent_logs, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()

    def do_POST(self):
        content_len = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_len).decode('utf-8', errors='ignore') if content_len > 0 else "{}"
        try:
            payload = json.loads(body)
        except Exception:
            payload = {}

        path_clean = self.path.split('?')[0].rstrip('/')

        # 1. API AUTO-ROUTE
        if path_clean == "/api/auto-route":
            prompt = payload.get("prompt", "").strip()
            task_map, explanation = decompose_prompt(prompt)
            resp = json.dumps({
                "matched_profiles": list(task_map.keys()),
                "tasks": task_map,
                "explanation": explanation
            }, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(resp)))
            self.end_headers()
            self.wfile.write(resp)
            return

        # 2. API SMART DISPATCH
        elif path_clean == "/api/smart-dispatch":
            prompt = payload.get("prompt", "").strip()
            specified_profiles = payload.get("profiles", [])

            if not prompt:
                self.send_response(400)
                self.send_header("Content-Length", "0")
                self.end_headers()
                return

            task_map, explanation = decompose_prompt(prompt)
            if specified_profiles:
                targets = [p for p in specified_profiles if p in PROFILES]
            else:
                targets = list(task_map.keys())

            batch_updates = {}
            for prof in targets:
                batch_updates[prof] = {
                    "status": "working",
                    "task": task_map.get(prof, prompt)
                }
            batch_update_status(batch_updates)

            for prof in targets:
                prof_task = task_map.get(prof, prompt)
                t = threading.Thread(target=execute_hermes_task, args=(prof, prof_task), daemon=True)
                t.start()

            resp = json.dumps({
                "success": True,
                "targets": targets,
                "tasks": task_map,
                "explanation": explanation
            }, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(resp)))
            self.end_headers()
            self.wfile.write(resp)
            return

        # 3. API RUN: Direct profile execution
        elif path_clean == "/api/run":
            profile = payload.get("profile")
            prompt = payload.get("prompt", "").strip()

            if not profile or profile not in PROFILES or not prompt:
                self.send_response(400)
                self.send_header("Content-Length", "0")
                self.end_headers()
                return

            t = threading.Thread(target=execute_hermes_task, args=(profile, prompt), daemon=True)
            t.start()

            resp = json.dumps({"success": True, "profile": profile, "status": "working"}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(resp)))
            self.end_headers()
            self.wfile.write(resp)
            return

        # 4. API SET STATUS: Manual status toggle
        elif path_clean == "/api/set-status":
            profile = payload.get("profile")
            status = payload.get("status")
            task = payload.get("task")

            if profile in PROFILES and status in ["working", "idle"]:
                update_profile_status(profile, status=status, task=task)

            resp = b'{"success": true}'
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(resp)))
            self.end_headers()
            self.wfile.write(resp)
            return

        self.send_response(404)
        self.send_header("Content-Length", "0")
        self.end_headers()

def run():
    monitor_thread = threading.Thread(target=monitor_active_pids, daemon=True)
    monitor_thread.start()

    chat_watcher_thread = threading.Thread(target=auto_detect_chat_tasks, daemon=True)
    chat_watcher_thread.start()

    server = ThreadingHTTPServer(("127.0.0.1", PORT), CahyaBridgeHandler)
    log_debug(f"Server listening on http://127.0.0.1:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    run()
