#!/usr/bin/env python3
"""Run any fal model (image, video, music, speech, avatar) via the queue API and download its outputs.
Reads FAL_KEY from the environment and never prints it.

Usage:
  fal_run.py <endpoint> --out DIR [--name STEM] [--in key=value ...] [--timeout 900]
      Values: plain text; JSON (numbers, true/false, {...}, [...]);
      @file.txt / @file.md  -> the file's text (for long prompts);
      @image.png / @clip.mp4 / @audio.mp3 -> sent as a data URI (local media as input);
      key=@a.png,@b.png     -> a list of data URIs.
      Every media URL in the result is downloaded into DIR as STEM[-N].ext.
      Prints a JSON summary (files + hosted URLs, reusable as inputs) on stdout.
  fal_run.py check [endpoint ...]   Verify FAL_KEY and print prices (free).
  fal_run.py models <query>         Search fal's model catalog.
  fal_run.py schema <endpoint>      Print the model's input fields.

Examples:
  fal_run.py openai/gpt-image-2.5/flare/text-to-image --out work/art --name hero \\
      --in prompt=@prompts/hero.txt 'image_size={"width":1024,"height":1536}' quality=high
  fal_run.py openai/gpt-image-2.5/flare/edit --out work/art --name after \\
      --in prompt=@prompts/after.txt image_urls=@work/art/before.png
"""
import argparse, base64, json, mimetypes, os, re, sys, time, urllib.error, urllib.parse, urllib.request

MEDIA_EXT = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".mp4", ".mov", ".webm", ".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac"}
TEXT_EXT = {".txt", ".md", ".json"}
DEFAULT_PRICED = ["openai/gpt-image-2.5/flare/text-to-image", "openai/gpt-image-2.5/flare/edit"]


def key():
    k = os.environ.get("FAL_KEY")
    if not k:
        sys.exit("FAL_KEY is not set. Add it to your shell profile and restart the session.")
    return k


def call(url, body=None, auth=True):
    headers = {"Content-Type": "application/json", "User-Agent": "promo-skill"}
    if auth:
        headers["Authorization"] = f"Key {key()}"
    req = urllib.request.Request(url, data=json.dumps(body).encode() if body is not None else None,
                                 headers=headers, method="POST" if body is not None else "GET")
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code in (429, 502, 503, 504) and attempt < 2:
                time.sleep(5 * (attempt + 1))
                continue
            sys.exit(f"HTTP {e.code} from {url.split('?')[0]}: {e.read().decode(errors='replace')[:800]}")
        except urllib.error.URLError as e:
            if attempt < 2:
                time.sleep(5)
                continue
            sys.exit(f"network error: {e}")


def data_uri(path):
    mime = mimetypes.guess_type(path)[0] or "application/octet-stream"
    return f"data:{mime};base64," + base64.b64encode(open(path, "rb").read()).decode()


def parse_value(v):
    if v.startswith("@"):
        parts = [p[1:] if p.startswith("@") else p for p in v[1:].split(",@")]
        if len(parts) == 1 and os.path.splitext(parts[0])[1].lower() in TEXT_EXT:
            return open(parts[0]).read().strip()
        uris = [data_uri(p) for p in parts]
        return uris if len(uris) > 1 or "," in v else uris[0]
    try:
        return json.loads(v)
    except json.JSONDecodeError:
        return v


def media_urls(obj):
    """Yield every URL in the result that looks like a media file."""
    if isinstance(obj, dict):
        for v in obj.values():
            yield from media_urls(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from media_urls(v)
    elif isinstance(obj, str) and obj.startswith("http"):
        ext = os.path.splitext(urllib.parse.urlparse(obj).path)[1].lower()
        if ext in MEDIA_EXT:
            yield obj


def run(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("endpoint")
    ap.add_argument("--out", required=True)
    ap.add_argument("--name", default="out")
    ap.add_argument("--in", dest="inputs", nargs="*", default=[], metavar="key=value")
    ap.add_argument("--timeout", type=int, default=900, help="seconds")
    a = ap.parse_args(argv)

    body = {}
    for kv in a.inputs:
        k, _, v = kv.partition("=")
        body[k] = parse_value(v)
    list_keys = {"image_urls", "video_urls", "audio_urls", "reference_image_urls"}
    for k in list_keys & body.keys():
        if isinstance(body[k], str):
            body[k] = [body[k]]

    job = call(f"https://queue.fal.run/{a.endpoint}", body)
    t0 = time.time()
    while (s := call(job["status_url"]))["status"] != "COMPLETED":
        if s["status"] not in ("IN_QUEUE", "IN_PROGRESS"):
            sys.exit(f"job failed: {json.dumps(s)[:800]}")
        if time.time() - t0 > a.timeout:
            sys.exit(f"timed out after {a.timeout}s (request {job.get('request_id')}); the job may still finish on fal")
        time.sleep(3)
    res = call(job["response_url"])

    os.makedirs(a.out, exist_ok=True)
    files, urls = [], list(dict.fromkeys(media_urls(res)))
    for i, url in enumerate(urls):
        ext = os.path.splitext(urllib.parse.urlparse(url).path)[1].lower()
        path = os.path.join(a.out, f"{a.name}{'' if len(urls) == 1 else f'-{i + 1}'}{ext}")
        urllib.request.urlretrieve(url, path)
        files.append(path)
    json.dump(res, open(os.path.join(a.out, f"{a.name}.result.json"), "w"), indent=2)
    print(json.dumps({"endpoint": a.endpoint, "seconds": round(time.time() - t0), "files": files, "urls": urls}, indent=2))
    if not files:
        print("warning: no media URLs in the result; see the .result.json file", file=sys.stderr)


def check(endpoints):
    q = "&".join("endpoint_id=" + urllib.parse.quote(e, safe="") for e in endpoints or DEFAULT_PRICED)
    res = call(f"https://api.fal.ai/v1/models/pricing?{q}")
    print("FAL_KEY works.")
    for p in res.get("prices", []):
        print(f"  {p['endpoint_id']}: {p['unit_price']} {p['currency']} per {p['unit']}")


def models(query):
    res = call(f"https://api.fal.ai/v1/models?q={urllib.parse.quote(query)}&limit=40", auth=False)
    for m in res.get("models", []):
        print(f"{m['endpoint_id']:<60} {m.get('metadata', {}).get('display_name', '')}")


def schema(endpoint):
    url = f"https://fal.ai/api/openapi/queue/openapi.json?endpoint_id={urllib.parse.quote(endpoint, safe='')}"
    d = call(url, auth=False)
    for name, s in d.get("components", {}).get("schemas", {}).items():
        if not re.search(r"Input$", name):
            continue
        req = set(s.get("required", []))
        for p, q in s.get("properties", {}).items():
            kind = q.get("type") or ("enum" if "enum" in q else "") or "/".join(x.get("type", "?") for x in q.get("anyOf", []))
            extra = f" {q['enum']}" if "enum" in q else (f" default={q['default']}" if "default" in q else "")
            print(f"  {'*' if p in req else ' '} {p:<28} {kind:<10}{extra}  {q.get('description', '')[:90]}")


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        sys.exit(__doc__)
    cmd = sys.argv[1]
    if cmd == "check":
        check(sys.argv[2:])
    elif cmd == "models":
        models(" ".join(sys.argv[2:]) or "video")
    elif cmd == "schema":
        schema(sys.argv[2])
    else:
        run(sys.argv[1:])
