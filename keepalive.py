import os
import time
import logging
import threading
from datetime import datetime, timezone

import http
from flask import Flask, jsonify

log = logging.getLogger("keepalive")

# Silencia los logs de cada request de Flask para no llenar la consola
logging.getLogger("werkzeug").setLevel(logging.ERROR)

app = flask.Flask(__name__)

SUPABASE_URL = (os.getenv("SUPABASE_URL") or "").rstrip("/")
SUPABASE_KEY = (
    os.getenv("SUPABASE_KEY")
    or os.getenv("SUPABASE_SERVICE_KEY")
    or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    or os.getenv("SUPABASE_ANON_KEY")
)
DB_PING_HOURS = float(os.getenv("KEEPALIVE_DB_HOURS", 12))

# Estado del último ping a Supabase (se muestra en /health)
_status = {"last_db_ping": None, "db_ok": None}


@app.route("/")
def home():
    return "The bot is alive and running ✅", 200


@app.route("/health")
def health():
    return flask.jsonify(status="ok", **_status), 200


def ping_supabase() -> bool:
    """Consulta mínima a la tabla guild_config (existe en tu schema)."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        log.warning("Supabase keepalive skipped: SUPABASE_URL / SUPABASE_KEY missing")
        return False
    try:
        r = http.get(
            f"{SUPABASE_URL}/rest/v1/guild_config",
            params={"select": "guild_id", "limit": 1},
            headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"},
            timeout=15,
        )
        ok = r.status_code < 400
        if ok:
            log.info("Supabase keepalive OK")
        else:
            log.warning(f"Supabase keepalive failed: HTTP {r.status_code}")
        return ok
    except Exception as e:
        log.warning(f"Supabase keepalive error: {e}")
        return False


def _db_loop():
    while True:
        _status["db_ok"] = ping_supabase()
        _status["last_db_ping"] = datetime.now(timezone.utc).isoformat()
        time.sleep(DB_PING_HOURS * 3600)


def _run_web():
    port = int(os.getenv("KEEPALIVE_PORT", 8080))
    app.run(host="0.0.0.0", port=port)


def keep_alive():
    threading.Thread(target=_run_web, daemon=True).start()
    threading.Thread(target=_db_loop, daemon=True).start()
