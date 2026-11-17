#!/usr/bin/env python3
"""K2 Vizag YouTube auto-uploader.

Reads youtube_uploader/queue.yaml, uploads the next pending videos to the
channel (title, description, tags, category, privacy / scheduled publish),
and records each upload in youtube_uploader/uploaded.json.

Runs in GitHub Actions (.github/workflows/youtube-upload.yml) with these repo
secrets: YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN.

Local check without uploading:  python3 youtube_uploader/upload.py --dry-run
"""
import argparse, datetime as dt, json, os, sys
from zoneinfo import ZoneInfo

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
QUEUE = os.path.join(HERE, "queue.yaml")
DONE = os.path.join(HERE, "uploaded.json")


def load_queue():
    with open(QUEUE, encoding="utf-8") as f:
        q = yaml.safe_load(f) or {}
    s = q.get("settings", {}) or {}
    defaults = q.get("defaults", {}) or {}
    items = []
    for v in q.get("videos", []) or []:
        it = {**defaults, **v}
        # description: defaults.description is appended under the per-video text
        if v.get("description") and defaults.get("description"):
            it["description"] = v["description"].rstrip() + "\n\n" + defaults["description"]
        # tags: defaults + per-video, no duplicates
        tags = list(defaults.get("tags", []) or []) + list(v.get("tags", []) or [])
        it["tags"] = list(dict.fromkeys(t.strip() for t in tags if t and t.strip()))
        items.append(it)
    return s, items


def load_done():
    if os.path.exists(DONE):
        with open(DONE, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_done(done):
    with open(DONE, "w", encoding="utf-8") as f:
        json.dump(done, f, ensure_ascii=False, indent=1)
        f.write("\n")


def check(it):
    errs = []
    path = os.path.join(ROOT, it.get("file", ""))
    if not it.get("file") or not os.path.isfile(path):
        errs.append(f"file not found: {it.get('file')}")
    t = it.get("title", "")
    if not t:
        errs.append("title missing")
    if len(t) > 100:
        errs.append(f"title is {len(t)} chars (max 100)")
    if any(c in t for c in "<>"):
        errs.append("title has < or >")
    if len(it.get("description", "")) > 5000:
        errs.append("description over 5000 chars")
    if sum(len(x) + 2 for x in it.get("tags", [])) > 500:
        errs.append("tags over 500 chars in total")
    return errs


def next_slots(settings, done, n):
    """Daily publish times after the latest one already used."""
    tz = ZoneInfo(settings.get("timezone", "Asia/Kolkata"))
    hh, mm = map(int, str(settings.get("publish_time", "18:00")).split(":"))
    now = dt.datetime.now(tz)
    used = [dt.datetime.fromisoformat(d["publish_at"]) for d in done.values() if d.get("publish_at")]
    day = max([now.date()] + [u.astimezone(tz).date() for u in used])
    start = dt.datetime.combine(day, dt.time(hh, mm), tz)
    if used and start <= max(used):
        start += dt.timedelta(days=1)
    if start < now + dt.timedelta(minutes=30):
        start += dt.timedelta(days=1)
    per = max(1, int(settings.get("publish_per_day", 1)))
    return [start + dt.timedelta(days=i // per, hours=3 * (i % per)) for i in range(n)]


def youtube_client():
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    creds = Credentials(None, refresh_token=os.environ["YT_REFRESH_TOKEN"], client_id=os.environ["YT_CLIENT_ID"],
                        client_secret=os.environ["YT_CLIENT_SECRET"], token_uri="https://oauth2.googleapis.com/token",
                        scopes=["https://www.googleapis.com/auth/youtube.upload"])
    return build("youtube", "v3", credentials=creds, cache_discovery=False)


def upload(yt, it, publish_at):
    from googleapiclient.http import MediaFileUpload
    status = {"privacyStatus": it.get("privacy", "public"), "selfDeclaredMadeForKids": bool(it.get("made_for_kids", False))}
    if publish_at:
        status = {**status, "privacyStatus": "private", "publishAt": publish_at.astimezone(dt.timezone.utc).isoformat().replace("+00:00", "Z")}
    body = {"snippet": {"title": it["title"], "description": it.get("description", ""), "tags": it.get("tags", []),
                        "categoryId": str(it.get("category", 10)), "defaultLanguage": it.get("language", "te"),
                        "defaultAudioLanguage": it.get("language", "te")}, "status": status}
    media = MediaFileUpload(os.path.join(ROOT, it["file"]), mimetype="video/mp4", chunksize=8 * 1024 * 1024, resumable=True)
    req = yt.videos().insert(part="snippet,status", body=body, media_body=media)
    resp = None
    while resp is None:
        st, resp = req.next_chunk()
        if st:
            print(f"   {int(st.progress() * 100)}%", flush=True)
    return resp


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="check the queue, upload nothing")
    ap.add_argument("--max", type=int, help="override settings.uploads_per_run")
    a = ap.parse_args()

    settings, items = load_queue()
    done = load_done()
    pending = [it for it in items if it.get("file") not in done and not it.get("skip")]
    bad = {it.get("file"): check(it) for it in pending}
    bad = {k: v for k, v in bad.items() if v}
    for k, v in bad.items():
        print(f"!! {k}: {'; '.join(v)}")
    pending = [it for it in pending if it.get("file") not in bad]
    n = a.max if a.max is not None else int(settings.get("uploads_per_run", 6))
    batch = pending[:n]
    sched = settings.get("mode", "schedule") == "schedule"
    slots = next_slots(settings, done, len(batch)) if sched else [None] * len(batch)

    print(f"{len(items)} in queue, {len(done)} already uploaded, {len(pending)} pending, uploading {len(batch)} now"
          + (" (scheduled daily)" if sched else ""))
    for it, when in zip(batch, slots):
        print(f"-> {it['file']}\n   title: {it['title']}\n   tags: {', '.join(it['tags'])}"
              + (f"\n   publish: {when.isoformat()}" if when else f"\n   privacy: {it.get('privacy', 'public')}"))
    if a.dry_run or not batch:
        return 1 if bad else 0

    if not all(os.environ.get(k) for k in ("YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN")):
        print("::warning::YouTube secrets not set yet (YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN) – nothing uploaded. See youtube_uploader/README.md")
        return 0
    yt = youtube_client()
    for it, when in zip(batch, slots):
        print(f"uploading {it['file']} ...", flush=True)
        r = upload(yt, it, when)
        done[it["file"]] = {"video_id": r["id"], "url": f"https://youtube.com/shorts/{r['id']}", "title": it["title"],
                            "uploaded_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                            "publish_at": when.isoformat() if when else None,
                            "privacy": r.get("status", {}).get("privacyStatus")}
        save_done(done)  # after every video, so a failure later keeps earlier results
        print(f"   done: {done[it['file']]['url']}", flush=True)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
