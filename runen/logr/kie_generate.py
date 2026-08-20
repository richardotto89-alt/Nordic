#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Runenkarte über die kie.ai-API erzeugen (4o Image API = ChatGPT-Bildeditor).

Voraussetzung:  export KIE_API_KEY="dein_key_von_https://kie.ai/api-key"

Beispiele:
    # Text-zu-Bild (ohne Referenzbild)
    python3 kie_generate.py

    # Bild-Editor-Modus: SOL-Karte als Stilreferenz mitgeben
    python3 kie_generate.py --ref ../../SOL.png --ref logr_rune.png

    # eigener Prompt
    python3 kie_generate.py --prompt-file mein_prompt.txt --n 2
"""
import argparse, base64, json, os, sys, time, urllib.request, urllib.error, pathlib

API      = "https://api.kie.ai"
UPLOAD   = "https://kieai.redpandaai.co/api/file-base64-upload"
MIME     = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}

PROMPT = """Ultra-detailed dark Nordic oracle/tarot card poster, vertical format, museum print quality.

CENTER: a huge circular medallion carved from weathered black granite, standing in relief.
Concentric rings: an outer ring of carved runic inscription, inside it several rings of dense
interlaced Viking/Celtic knotwork, deeply chiselled, rough stone texture, cold rim light.

THE RUNE: in the exact center, ONE single rune carved from pale cracked white stone, raised and
beveled with a deep drop shadow, softly glowing. The rune is the Younger Futhark rune "Logr":
a straight vertical stave with exactly ONE short diagonal branch that leaves the stave near its
top and rises upward to the RIGHT, at about 40 degrees, roughly one third the length of the stave.
Nothing else: no crossbars, no second branch, no mirrored strokes.

TYPOGRAPHY below the medallion, centered, engraved pale stone serif capitals:
"LOGR"
underneath, smaller, wide letter-spaced capitals with a thin rule on each side: "WATER"
underneath, three lines of small warm-grey serif text in German:
"Steht fuer das Wasser, den Fluss und die Lebenskraft."
"Sie lehrt, der Stroemung zu vertrauen, und schenkt"
"Intuition, Reinigung und tiefe innere Klarheit."

LOWER THIRD: photorealistic moonlit Nordic landscape - a black fjord lake, steep mountains,
a waterfall in the distance, dense black pine forest, a white wolf standing on a rock outcrop in
the foreground, alert, looking to the right; dramatic storm clouds, faint moon glow on the water.

FRAME: thin ornate gold border with filigree knotwork corners, a gold Valknut symbol centered at
the very top, vertical columns of small gold rune marks along the left and right edges, a gold
Vegvisir compass symbol carved on the rock at the bottom center.

STYLE: monochrome black and silver palette with warm gold accents, cinematic chiaroscuro,
high contrast, deep blacks, fine film grain, hyper detailed, 8k."""


def post(url, payload, key):
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode(),
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.loads(r.read().decode())


def get(url, key):
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + key})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode())


def upload(path, key):
    """Lokale Datei hochladen -> oeffentliche URL (24 h gueltig)."""
    p = pathlib.Path(path)
    mime = MIME.get(p.suffix.lower(), "image/png")
    data = base64.b64encode(p.read_bytes()).decode()
    res = post(UPLOAD, {"base64Data": "data:%s;base64,%s" % (mime, data),
                        "uploadPath": "images/runen", "fileName": p.name}, key)
    if res.get("code") != 200:
        sys.exit("Upload fehlgeschlagen (%s): %s" % (res.get("code"), res.get("msg")))
    url = res["data"]["downloadUrl"]
    print("  hochgeladen: %s -> %s" % (p.name, url))
    return url


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--key", default=os.environ.get("KIE_API_KEY"))
    ap.add_argument("--prompt-file")
    ap.add_argument("--ref", action="append", default=[],
                    help="lokale Datei oder URL als Stil-/Bildreferenz (max. 5)")
    ap.add_argument("--size", default="2:3", choices=["1:1", "3:2", "2:3"])
    ap.add_argument("--n", type=int, default=1, help="Anzahl Varianten")
    ap.add_argument("--out", default="kie_logr")
    a = ap.parse_args()

    if not a.key:
        sys.exit("Kein API-Key. Bitte 'export KIE_API_KEY=...' setzen (https://kie.ai/api-key).")

    prompt = pathlib.Path(a.prompt_file).read_text() if a.prompt_file else PROMPT

    files = []
    for r in a.ref[:5]:
        files.append(r if r.startswith("http") else upload(r, a.key))

    body = {"prompt": prompt, "size": a.size, "nVariants": a.n}
    if files:
        body["filesUrl"] = files

    res = post(API + "/api/v1/gpt4o-image/generate", body, a.key)
    if res.get("code") != 200:
        sys.exit("Start fehlgeschlagen (%s): %s" % (res.get("code"), res.get("msg")))
    task = res["data"]["taskId"]
    print("Task:", task)

    for i in range(180):
        time.sleep(5)
        info = get(API + "/api/v1/gpt4o-image/record-info?taskId=" + task, a.key)
        d = info.get("data") or {}
        st = d.get("status") or d.get("successFlag")
        print("  [%3ds] %s" % (i * 5, st))
        if st == "SUCCESS":
            urls = (d.get("response") or {}).get("resultUrls") or d.get("resultUrls") or []
            if isinstance(urls, str):
                urls = json.loads(urls)
            for n, u in enumerate(urls):
                name = "%s_%d.png" % (a.out, n + 1) if len(urls) > 1 else a.out + ".png"
                urllib.request.urlretrieve(u, name)
                print("gespeichert:", name, "<-", u)
            return
        if st in ("GENERATE_FAILED", "CREATE_TASK_FAILED"):
            sys.exit("Generierung fehlgeschlagen: %s" % (d.get("errorMessage") or info.get("msg")))
    sys.exit("Timeout beim Warten auf das Ergebnis.")


if __name__ == "__main__":
    main()
