#!/usr/bin/env python3
"""Generate or edit an image on fal via the queue API. Reads FAL_KEY from the environment and never prints it.

Usage:
  fal_gen.py <endpoint> <out.png> <prompt-file> [--size WxH] [--ref URL_OR_PATH ...] [--bg opaque|transparent] [--quality high]
      Prints the hosted URL of the result on stdout (pass it as --ref to edit the result).
      --ref accepts URLs or local image paths (sent as data URIs).
  fal_gen.py check [endpoint ...]
      Verifies FAL_KEY and prints prices. Costs nothing.
  fal_gen.py models <query>
      Searches fal's model catalog, e.g. `models gpt-image`.
"""
import argparse, base64, json, mimetypes, os, sys, time, urllib.error, urllib.parse, urllib.request

DEFAULTS = ["openai/gpt-image-2.5/flare/text-to-image", "openai/gpt-image-2.5/flare/edit"]


def key():
    k = os.environ.get("FAL_KEY")
    if not k:
        sys.exit("FAL_KEY is not set. Add it to your shell profile and restart the session.")
    return k


def call(url, body=None, auth=True):
    headers = {"Content-Type": "application/json"}
    if auth:
        headers["Authorization"] = f"Key {key()}"
    req = urllib.request.Request(url, data=json.dumps(body).encode() if body is not None else None,
                                 headers=headers, method="POST" if body is not None else "GET")
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code} from {url.split('?')[0]}: {e.read().decode(errors='replace')[:500]}")


def as_ref(ref):
    if ref.startswith(("http://", "https://", "data:")):
        return ref
    mime = mimetypes.guess_type(ref)[0] or "image/png"
    return f"data:{mime};base64," + base64.b64encode(open(ref, "rb").read()).decode()


def check(endpoints):
    q = "&".join("endpoint_id=" + urllib.parse.quote(e, safe="") for e in endpoints or DEFAULTS)
    res = call(f"https://api.fal.ai/v1/models/pricing?{q}")
    print("FAL_KEY works.")
    for p in res.get("prices", []):
        print(f"  {p['endpoint_id']}: {p['unit_price']} {p['currency']} per {p['unit']}")


def models(query):
    res = call(f"https://api.fal.ai/v1/models?q={urllib.parse.quote(query)}&limit=30", auth=False)
    for m in res.get("models", []):
        print(f"{m['endpoint_id']:<55} {m.get('metadata', {}).get('display_name', '')}")


def generate(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("endpoint"); ap.add_argument("out"); ap.add_argument("prompt_file")
    ap.add_argument("--size", default="1024x1536")
    ap.add_argument("--ref", nargs="*", default=[])
    ap.add_argument("--bg", default="opaque", choices=["opaque", "transparent", "auto"])
    ap.add_argument("--quality", default="high")
    a = ap.parse_args(argv)

    w, h = map(int, a.size.split("x"))
    body = {"prompt": open(a.prompt_file).read().strip(), "image_size": {"width": w, "height": h},
            "quality": a.quality, "background": a.bg, "output_format": "png", "num_images": 1}
    if a.ref:
        body["image_urls"] = [as_ref(r) for r in a.ref]

    job = call(f"https://queue.fal.run/{a.endpoint}", body)
    t0 = time.time()
    while (s := call(job["status_url"]))["status"] != "COMPLETED":
        if s["status"] not in ("IN_QUEUE", "IN_PROGRESS"):
            sys.exit(f"job failed: {s}")
        if time.time() - t0 > 600:
            sys.exit(f"timed out after 10 minutes: {s}")
        time.sleep(3)
    img = call(job["response_url"])["images"][0]
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    urllib.request.urlretrieve(img["url"], a.out)
    print(img["url"])
    print(f"saved {a.out} in {time.time() - t0:.0f}s", file=sys.stderr)


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        sys.exit(__doc__)
    if sys.argv[1] == "check":
        check(sys.argv[2:])
    elif sys.argv[1] == "models":
        models(" ".join(sys.argv[2:]) or "image")
    else:
        generate(sys.argv[1:])
