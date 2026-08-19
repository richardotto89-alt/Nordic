# Untertitel im Intro-Video austauschen

Ersetzt die Untertitelzeile über `HAMR` im 18-Sekunden-Intro (1080x1920, 30 fps).
Die alte Zeile wird pixelgenau entfernt (Inpainting der Glyphenmaske), die neue
in Eagle Lake gesetzt — gleiche Position, Farbe, Ein- und Ausblendung.

    python3 render.py <quell.mp4> <ziel.mp4> "Nordische Urkraft" "coming soon"

Die beiden Textsegmente stehen mit 39 px Abstand nebeneinander und werden
gemeinsam auf x=541 zentriert, Grundlinie y=1274.

Voraussetzungen: `ffmpeg`, `python3` mit `numpy`, `opencv-python-headless`, `pillow`.

Dateien:
- `mask_d.npy`  – Maske der alten Glyphen (Bildband y 1180..1320)
- `Scurve.npy`  – gemessene Deckkraft der Originalzeile je Frame (420..539)
- `EagleLake.ttf` – Schrift (SIL Open Font License)

Gilt nur für dieses eine Quellvideo: Maske und Kurve sind daraus gemessen.
