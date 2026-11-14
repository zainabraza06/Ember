"""M1: fetch PSI Combustion Science investigation metadata and small experiment-table files.

Idempotent: existing files are skipped; failures are appended to data/raw/_errors.log.
Only files listed as `experimentalTable` in the PSI investigation record are downloaded,
and only if they are under MAX_BYTES. No media. Standard library only.

Usage: python -I scripts/fetch_psi_tables.py
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from datetime import date

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW = os.path.join(ROOT, "data", "raw", "psi")
ERR = os.path.join(ROOT, "data", "raw", "_errors.log")
BASE = "https://psi.nasa.gov/geode-py/ws"
UA = {"User-Agent": "Mozilla/5.0 (ember-m1-research)"}
MAX_BYTES = 50 * 1024 * 1024


def log_error(msg):
    os.makedirs(os.path.dirname(ERR), exist_ok=True)
    with open(ERR, "a", encoding="utf-8") as f:
        f.write(f"{date.today().isoformat()} {msg}\n")


def get(url, timeout=60):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=timeout).read()


def main():
    search = json.loads(get(f"{BASE}/repo/search?q=&data_source=psi&data_type=investigation&size=500"))
    ids = sorted(
        (h["_source"]["Accession"] for h in search["hits"]["hits"]
         if h["_source"].get("Research Area") == "Combustion Science"),
        key=lambda a: int(a.split("-")[1]),
    )
    print(len(ids), "combustion investigations")
    for acc in ids:
        out_dir = os.path.join(RAW, acc)
        os.makedirs(out_dir, exist_ok=True)
        meta_path = os.path.join(out_dir, f"{acc}_record.json")
        try:
            if os.path.exists(meta_path):
                rec = json.load(open(meta_path, encoding="utf-8"))
            else:
                rec = json.loads(get(f"{BASE}/repo/investigations/{acc}"))
                with open(meta_path, "w", encoding="utf-8") as f:
                    json.dump(rec, f, indent=1, ensure_ascii=False)
        except Exception as e:  # keep going
            log_error(f"{acc} record: {e}")
            continue
        for t in rec.get("experimentalTable", []):
            name = t["file_name"]
            dest = os.path.join(out_dir, name)
            if os.path.exists(dest):
                continue
            if t.get("restricted") or t.get("file_size", 0) > MAX_BYTES:
                log_error(f"{acc} {name}: skipped (restricted or over size limit)")
                continue
            try:
                q = urllib.parse.urlencode({"file": name, "redirect": "false"})
                presigned = get(f"{BASE}/studies/{acc}/download?{q}").decode().strip()
                data = get(presigned)
                with open(dest, "wb") as f:
                    f.write(data)
                print("ok", acc, name, len(data))
            except Exception as e:
                log_error(f"{acc} {name}: {e}")
            time.sleep(0.3)


if __name__ == "__main__":
    sys.exit(main())
