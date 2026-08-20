# Runenkarte LOGR (ᛚ)

Karte zur Rune **Lögr** (Wasser / Fluss / Lebenskraft) im Stil der SOL-Karte.

## Dateien

| Datei | Inhalt |
|---|---|
| `logr.png` | fertige Karte, 1080 × 1880 px |
| `logr.svg` | dieselbe Karte als Vektor (frei skalierbar, Text editierbar) |
| `gen.py` | Generator für SVG + HTML (Layout, Flechtwerk, Runenring, Landschaft) |
| `kie_generate.py` | Anbindung an die kie.ai-API (4o Image API = ChatGPT-Bildeditor) |

## Vektorkarte neu bauen

```bash
python3 gen.py
/opt/pw-browsers/chromium-1194/chrome-linux/chrome --headless --no-sandbox \
  --window-size=1080,1880 --screenshot=logr.png file://$PWD/logr.html
```

## Foto-Version über kie.ai

```bash
export KIE_API_KEY="..."          # von https://kie.ai/api-key
python3 kie_generate.py                       # rein aus dem Prompt
python3 kie_generate.py --ref ../../sol.png   # SOL-Karte als Stilreferenz
```

Der Prompt steckt in `kie_generate.py` (Konstante `PROMPT`) und beschreibt
Steinmedaillon, Runenform, Typografie, Landschaft und Goldrahmen.

## Runenform

Lögr im jüngeren Futhark: senkrechter Stab, **ein** kurzer Zweig, der knapp
unter der Spitze ansetzt und nach rechts oben führt — keine Querbalken,
kein zweiter Zweig.
