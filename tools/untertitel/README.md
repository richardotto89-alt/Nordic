# Intro-Video: Block unter dem Titel neu setzen

Entfernt im 18-Sekunden-Intro (1080x1920, 30 fps) alles unterhalb von
"NORDISCHE URKRAFT" — goldene Trennlinie, Untertitelzeile und "HAMR" — und
setzt stattdessen eine einzelne Zeile in der Titelschrift darunter.

    python3 render.py <quell.mp4> <ziel.mp4> "COMING SOON"

Die alten Elemente werden pixelgenau herausgerechnet (Inpainting entlang
`mask_all.npy`), nicht überdeckt. Die neue Zeile übernimmt Farbe (242/235/227)
und Einblendkurve der ehemaligen Untertitelzeile und wird von der Schlussblende
korrekt mit ausgeblendet.

Layout: Versalhöhe 62 px, Laufweite 0.20 em, zentriert auf x=540, Mitte y=1291.
Diese Werte stehen oben in `render.py`.

## Schrift

Die Titelschrift ist **Norse** von Joël Carrouché (kostenlos, auch kommerziell
nutzbar). Sie liegt hier **nicht** bei — die Lizenz untersagt das Weitergeben
der Datei. Vor dem Rendern einmal von https://www.dafont.com/norse.font laden
und `Norse.otf` nach `nf/Norse.otf` neben dieses Skript legen.

## Voraussetzungen

`ffmpeg` sowie `python3` mit `numpy`, `opencv-python-headless`, `pillow`.

## Dateien

- `mask_all.npy` — Maske der entfernten Elemente, Bildband y 1150..1440
- `Scurve.npy` — gemessene Deckkraft der Originalzeile je Frame (420..539)

Gilt nur für dieses eine Quellvideo: Maske und Kurve sind daraus gemessen.
