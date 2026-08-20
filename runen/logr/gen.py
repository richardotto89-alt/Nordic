# -*- coding: utf-8 -*-
"""Runenkarte LOGR (Younger Futhark) im Stil der SOL-Karte."""
import math, random

W, H = 1080, 1880
rnd = random.Random(20260820)

GOLD      = "#b08f57"
GOLD_DIM  = "#7d6238"
TEXT_WARM = "#a1978a"
SERIF     = "Liberation Serif, FreeSerif, DejaVu Serif, serif"

CX, CY, RAD = 540, 566, 404          # Medaillon

# ------------------------------------------------- Runen (Elder Futhark, Deko)
R = {
 "fehu":     [[(0,-1),(0,1)], [(0,-0.55),(0.5,-1.0)], [(0,-0.05),(0.5,-0.5)]],
 "uruz":     [[(0,1),(0,-1),(0.5,-0.55),(0.5,1)]],
 "thurisaz": [[(0,-1),(0,1)], [(0,-0.55),(0.46,-0.1),(0,0.35)]],
 "ansuz":    [[(0,-1),(0,1)], [(0,-1),(0.5,-0.55)], [(0,-0.4),(0.5,0.05)]],
 "raido":    [[(0,-1),(0,1)], [(0,-1),(0.46,-0.7),(0,-0.3)], [(0,-0.3),(0.46,1)]],
 "kaunaz":   [[(0.45,-1),(0,0),(0.45,1)]],
 "gebo":     [[(-0.45,-1),(0.45,1)], [(0.45,-1),(-0.45,1)]],
 "wunjo":    [[(0,-1),(0,1)], [(0,-1),(0.46,-0.62),(0,-0.24)]],
 "hagalaz":  [[(-0.45,-1),(-0.45,1)], [(0.45,-1),(0.45,1)], [(-0.45,-0.18),(0.45,0.18)]],
 "naudiz":   [[(0,-1),(0,1)], [(-0.45,0.34),(0.45,-0.34)]],
 "isa":      [[(0,-1),(0,1)]],
 "jera":     [[(-0.06,-1),(0.42,-0.62),(-0.06,-0.24)], [(0.06,1),(-0.42,0.62),(0.06,0.24)]],
 "eihwaz":   [[(0,-0.86),(0,0.86)], [(0,-0.86),(0.4,-1.12)], [(0,0.86),(-0.4,1.12)]],
 "perthro":  [[(0.42,-1),(0,-0.62),(0,0.62),(0.42,1)]],
 "algiz":    [[(0,-0.3),(0,1)], [(0,-0.3),(-0.46,-1)], [(0,-0.3),(0.46,-1)]],
 "sowilo":   [[(0.4,-1),(-0.06,-0.36),(0.36,0.2),(-0.1,1)]],
 "tiwaz":    [[(0,-1),(0,1)], [(-0.45,-0.5),(0,-1),(0.45,-0.5)]],
 "berkana":  [[(0,-1),(0,1)], [(0,-1),(0.44,-0.5),(0,0)], [(0,0),(0.44,0.5),(0,1)]],
 "ehwaz":    [[(-0.42,-1),(-0.42,1)], [(0.42,-1),(0.42,1)], [(-0.42,-1),(0,-0.2),(0.42,-1)]],
 "mannaz":   [[(-0.42,-1),(-0.42,1)], [(0.42,-1),(0.42,1)], [(-0.42,-1),(0.42,-0.1)], [(0.42,-1),(-0.42,-0.1)]],
 "laguz":    [[(0,-1),(0,1)], [(0,-0.72),(0.46,-1.02)]],
 "ingwaz":   [[(0,-0.7),(0.4,0),(0,0.7),(-0.4,0),(0,-0.7)]],
 "dagaz":    [[(-0.42,1),(-0.42,-1)], [(0.42,1),(0.42,-1)], [(-0.42,-1),(0.42,1)], [(-0.42,1),(0.42,-1)]],
 "othala":   [[(0,-1),(0.4,-0.4),(0,0.2),(-0.4,-0.4),(0,-1)], [(0,0.2),(0.42,1)], [(0,0.2),(-0.42,1)]],
}

def rune_d(name, cx, cy, s, rot=0.0):
    a = math.radians(rot); ca, sa = math.cos(a), math.sin(a)
    out = []
    for poly in R[name]:
        pts = []
        for (x, y) in poly:
            X, Y = x * s * 0.9, y * s
            pts.append("%.2f,%.2f" % (cx + X * ca - Y * sa, cy + X * sa + Y * ca))
        out.append("M" + "L".join(pts))
    return "".join(out)

def ring_runes(cx, cy, r, count, size, seq, phase=0.0):
    d = []
    for i in range(count):
        th = phase + 2 * math.pi * i / count
        d.append(rune_d(seq[i % len(seq)], cx + r * math.cos(th), cy + r * math.sin(th),
                        size, math.degrees(th) + 90))
    return "".join(d)

# ------------------------------------------------------------- Flechtwerkringe
def strand(cx, cy, r, amp, k, phase, steps=1600):
    pts = []
    for i in range(steps + 1):
        th = 2 * math.pi * i / steps
        rr = r + amp * math.sin(k * th + phase)
        pts.append("%.2f,%.2f" % (cx + rr * math.cos(th), cy + rr * math.sin(th)))
    return "M" + "L".join(pts) + "Z"

def crossing_arcs(cx, cy, r, amp, k, phase, parity):
    segs = []
    for n in range(0, 2 * k + 2):
        th0 = (n * math.pi - phase) / k
        if th0 > 2 * math.pi + 0.01:
            break
        if n % 2 != parity:
            continue
        d = 0.40 * math.pi / k
        pts = []
        for j in range(25):
            th = th0 - d + 2 * d * j / 24
            rr = r + amp * math.sin(k * th + phase)
            pts.append("%.2f,%.2f" % (cx + rr * math.cos(th), cy + rr * math.sin(th)))
        segs.append("M" + "L".join(pts))
    return "".join(segs)

def knot_ring(cx, cy, r, amp, w, phase=0.0):
    """Zwei gegenlaeufige Straenge; Lobenzahl aus Radius/Amplitude -> echtes Geflecht."""
    k = max(6, int(round(math.pi * r / (2.15 * amp))))
    if k % 2:
        k += 1
    a = strand(cx, cy, r, amp, k, phase)
    b = strand(cx, cy, r, -amp, k, phase)
    g = ['<g fill="none" stroke-linecap="round">']
    def band(p, o=1.0):
        return ('<path d="%s" stroke="#08080a" stroke-width="%.1f" opacity="%.2f"/>'
                '<path d="%s" stroke="url(#carve)" stroke-width="%.1f" opacity="%.2f"/>'
                '<path d="%s" stroke="#0d0d0f" stroke-width="%.1f" opacity="%.2f"/>'
                % (p, w + 8, .95 * o, p, w, o, p, w * 0.30, .5 * o))
    g.append(band(a)); g.append(band(b))
    ov = crossing_arcs(cx, cy, r, amp, k, phase, 0)
    g.append(band(ov))
    g.append('</g>')
    return "".join(g)

# --------------------------------------------------------------------- Ornament
def corner_flourish(x, y, sx, sy):
    p = ["M0,126 C0,70 16,28 58,6 C92,-11 126,6 126,34 C126,58 106,70 88,64 C72,58 70,38 84,30",
         "M20,126 C20,80 34,48 66,28 C94,12 112,24 112,38",
         "M138,0 C184,0 212,18 224,46 C236,70 224,92 204,92 C188,92 180,78 184,64",
         "M138,19 C176,19 198,34 208,56",
         "M56,80 C70,80 79,90 79,102 C79,116 68,126 56,126 C44,126 35,116 35,104",
         "M150,42 C160,52 160,64 152,70"]
    body = "".join('<path d="%s"/>' % q for q in p)
    return ('<g transform="translate(%d,%d) scale(%d,%d)" fill="none" stroke="%s" '
            'stroke-width="2.2" stroke-linecap="round" opacity=".9">%s</g>' % (x, y, sx, sy, GOLD, body))

def valknut(cx, cy, s):
    def tri(ox, oy, sc):
        pts = [(0, -1), (0.87, 0.5), (-0.87, 0.5)]
        return "M" + "L".join("%.1f,%.1f" % (cx + ox + px * sc, cy + oy + py * sc) for px, py in pts) + "Z"
    d = tri(0, -0.30 * s, s * 0.72) + tri(-0.42 * s, 0.30 * s, s * 0.72) + tri(0.42 * s, 0.30 * s, s * 0.72)
    return '<path d="%s" fill="none" stroke="%s" stroke-width="2.6" stroke-linejoin="round"/>' % (d, GOLD)

def vegvisir(cx, cy, r):
    g = ['<g fill="none" stroke="%s" stroke-width="2.1" stroke-linecap="round" opacity=".92">' % GOLD]
    g.append('<circle cx="%d" cy="%d" r="%.1f"/><circle cx="%d" cy="%d" r="%.1f" opacity=".5"/>'
             % (cx, cy, r * 0.30, cx, cy, r * 0.17))
    for i in range(8):
        th = math.pi * i / 4 - math.pi / 2
        c, sn = math.cos(th), math.sin(th)
        n, m = -sn, c
        x0, y0 = cx + c * r * 0.17, cy + sn * r * 0.17
        x1, y1 = cx + c * r, cy + sn * r
        g.append('<path d="M%.1f,%.1f L%.1f,%.1f"/>' % (x0, y0, x1, y1))
        for f, hw in ((0.50, 0.19), (0.72, 0.14)):
            px, py = cx + c * r * f, cy + sn * r * f
            g.append('<path d="M%.1f,%.1f L%.1f,%.1f"/>'
                     % (px - n * r * hw, py - m * r * hw, px + n * r * hw, py + m * r * hw))
        if i % 2 == 0:
            g.append('<path d="M%.1f,%.1f L%.1f,%.1f M%.1f,%.1f L%.1f,%.1f"/>'
                     % (x1, y1, x1 - c * r * .24 + n * r * .20, y1 - sn * r * .24 + m * r * .20,
                        x1, y1, x1 - c * r * .24 - n * r * .20, y1 - sn * r * .24 - m * r * .20))
        else:
            g.append('<path d="M%.1f,%.1f L%.1f,%.1f"/>'
                     % (x1 - n * r * .16, y1 - m * r * .16, x1 + n * r * .16, y1 + m * r * .16))
            g.append('<circle cx="%.1f" cy="%.1f" r="3.4"/>' % (x1 + c * r * .09, y1 + sn * r * .09))
    g.append('</g>')
    return "".join(g)

# ------------------------------------------------------------------ Landschaft
def ridgeline(y0, amp, seed, rough=0.58, depth=8):
    """Mittelpunktverschiebung -> natuerliche Bergkette."""
    r2 = random.Random(seed)
    pts = [(-80.0, y0 + r2.uniform(-amp, amp) * .4), (W + 80.0, y0 + r2.uniform(-amp, amp) * .4)]
    a = amp
    for _ in range(depth):
        new = [pts[0]]
        for i in range(len(pts) - 1):
            x0, ya = pts[i]; x1, yb = pts[i + 1]
            new.append(((x0 + x1) / 2, (ya + yb) / 2 + r2.uniform(-a, a)))
            new.append(pts[i + 1])
        pts = new
        a *= rough
    return pts

def mountain(y0, amp, seed, fill, snow=None, rough=0.58):
    pts = ridgeline(y0, amp, seed, rough)
    body = "M" + "L".join("%.1f,%.1f" % p for p in pts) + "L%d,%d L-80,%d Z" % (W + 80, H, H)
    out = '<path d="%s" fill="%s"/>' % (body, fill)
    if snow:
        line = "M" + "L".join("%.1f,%.1f" % p for p in pts)
        out += '<path d="%s" fill="none" stroke="%s" stroke-width="2.2" opacity=".5"/>' % (line, snow)
    return out

def pine(x, base, h, w, fill, op=1.0):
    d = ["M%.1f,%.1f" % (x - w * .10, base)]
    L = 7
    for i in range(L):
        t = i / (L - 1.0); yy = base - h * (.12 + .88 * t); ww = w * (1 - .85 * t)
        d.append("L%.1f,%.1f L%.1f,%.1f L%.1f,%.1f"
                 % (x - ww, yy + h * .06, x - ww * .42, yy + h * .02, x - ww * .72, yy - h * .03))
    d.append("L%.1f,%.1f" % (x, base - h))
    for i in range(L - 1, -1, -1):
        t = i / (L - 1.0); yy = base - h * (.12 + .88 * t); ww = w * (1 - .85 * t)
        d.append("L%.1f,%.1f L%.1f,%.1f L%.1f,%.1f"
                 % (x + ww * .72, yy - h * .03, x + ww * .42, yy + h * .02, x + ww, yy + h * .06))
    d.append("L%.1f,%.1f Z" % (x + w * .10, base))
    return '<path d="%s" fill="%s" opacity="%.2f"/>' % ("".join(d), fill, op)

# --------------------------------------------------------------------- Aufbau
s = []; add = s.append
add('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">' % (W, H, W, H))

add('<defs>')
add('''
<filter id="clouds" x="-10%" y="-10%" width="120%" height="120%">
  <feTurbulence type="fractalNoise" baseFrequency="0.0020 0.0052" numOctaves="6" seed="11" result="t"/>
  <feColorMatrix in="t" type="matrix" values="0 0 0 0 0.63  0 0 0 0 0.64  0 0 0 0 0.68  0.95 0.35 0 0 -0.30"/>
</filter>
<filter id="clouds2" x="-10%" y="-10%" width="120%" height="120%">
  <feTurbulence type="fractalNoise" baseFrequency="0.0065 0.0125" numOctaves="5" seed="29" result="t"/>
  <feColorMatrix in="t" type="matrix" values="0 0 0 0 0.58  0 0 0 0 0.60  0 0 0 0 0.66  1.15 0.25 0 0 -0.58"/>
</filter>
<filter id="grain"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="5" result="t"/>
  <feColorMatrix in="t" type="saturate" values="0"/></filter>
<filter id="stonetex" x="-5%" y="-5%" width="110%" height="110%">
  <feTurbulence type="fractalNoise" baseFrequency="0.045" numOctaves="5" seed="3" result="t"/>
  <feColorMatrix in="t" type="matrix" values="0 0 0 0 0.44  0 0 0 0 0.44  0 0 0 0 0.46  0.85 0 0 0 -0.20"/>
</filter>
<filter id="runetex" x="-5%" y="-5%" width="110%" height="110%">
  <feTurbulence type="fractalNoise" baseFrequency="0.09" numOctaves="4" seed="17" result="t"/>
  <feColorMatrix in="t" type="matrix" values="0 0 0 0 0.35  0 0 0 0 0.34  0 0 0 0 0.32  0.9 0 0 0 -0.28"/>
</filter>
<filter id="softglow" x="-150%" y="-150%" width="400%" height="400%"><feGaussianBlur stdDeviation="30"/></filter>
<filter id="deep" x="-40%" y="-40%" width="180%" height="180%">
  <feDropShadow dx="0" dy="9" stdDeviation="12" flood-color="#000" flood-opacity="0.9"/></filter>
<filter id="discshadow" x="-30%" y="-30%" width="160%" height="160%">
  <feDropShadow dx="0" dy="10" stdDeviation="18" flood-color="#000" flood-opacity="0.85"/></filter>
<radialGradient id="vign" cx="50%" cy="40%" r="76%">
  <stop offset="0%" stop-color="#000" stop-opacity="0"/><stop offset="55%" stop-color="#000" stop-opacity=".32"/>
  <stop offset="100%" stop-color="#000" stop-opacity=".95"/></radialGradient>
<radialGradient id="disc" cx="34%" cy="26%" r="84%">
  <stop offset="0%" stop-color="#3c3c40"/><stop offset="40%" stop-color="#242427"/>
  <stop offset="76%" stop-color="#141416"/><stop offset="100%" stop-color="#0a0a0c"/></radialGradient>
<linearGradient id="carve" x1="0" y1="0" x2="0.35" y2="1">
  <stop offset="0%" stop-color="#5e5e63"/><stop offset="45%" stop-color="#3d3d41"/>
  <stop offset="100%" stop-color="#212124"/></linearGradient>
<linearGradient id="runestone" gradientUnits="userSpaceOnUse" x1="{RX1}" y1="{RY1}" x2="{RX2}" y2="{RY2}">
  <stop offset="0%" stop-color="#f4f1ec"/><stop offset="30%" stop-color="#d7d2c9"/>
  <stop offset="62%" stop-color="#b3ada3"/><stop offset="100%" stop-color="#e2ded6"/></linearGradient>
<linearGradient id="titlegrad" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0%" stop-color="#f2eee7"/><stop offset="58%" stop-color="#cdc8be"/>
  <stop offset="100%" stop-color="#98928a"/></linearGradient>
<linearGradient id="water" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0%" stop-color="#343941"/><stop offset="30%" stop-color="#1e2228"/>
  <stop offset="100%" stop-color="#0f1114"/></linearGradient>
<linearGradient id="haze" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0%" stop-color="#20242b" stop-opacity="0"/>
  <stop offset="100%" stop-color="#12151a" stop-opacity=".8"/></linearGradient>
<linearGradient id="botfade" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#000" stop-opacity="0"/><stop offset="55%" stop-color="#000" stop-opacity=".18"/><stop offset="100%" stop-color="#000" stop-opacity=".72"/></linearGradient>
<radialGradient id="moon" cx="50%" cy="50%" r="50%">
  <stop offset="0%" stop-color="#fdf8ea" stop-opacity=".9"/>
  <stop offset="30%" stop-color="#ecdfc2" stop-opacity=".38"/>
  <stop offset="100%" stop-color="#ecdfc2" stop-opacity="0"/></radialGradient>
<clipPath id="discclip"><circle cx="{CX}" cy="{CY}" r="{RAD}"/></clipPath>
'''.format(RX1=CX-200, RY1=CY-240, RX2=CX+180, RY2=CY+240, CX=CX, CY=CY, RAD=RAD))

# Rune-Geometrie (Younger Futhark: Lögr = Stab + Zweig nach rechts oben)
SX, SY = CX - 52, CY
HALF, TW = 236, 34
JY = SY - HALF + 78                       # Ansatz des Zweiges
TIPX, TIPY = SX + 176, SY - HALF - 14     # Zweigspitze
ang = math.atan2(TIPY - JY, TIPX - SX)
nx, ny = -math.sin(ang) * TW / 2, math.cos(ang) * TW / 2
rune_path = ("M%.1f,%.1f L%.1f,%.1f L%.1f,%.1f L%.1f,%.1f Z "
             "M%.1f,%.1f L%.1f,%.1f L%.1f,%.1f L%.1f,%.1f Z"
             % (SX - TW / 2, SY - HALF, SX + TW / 2, SY - HALF, SX + TW / 2, SY + HALF, SX - TW / 2, SY + HALF,
                SX - nx, JY - ny, TIPX - nx, TIPY - ny, TIPX + nx, TIPY + ny, SX + nx, JY + ny))
add('<clipPath id="runeclip"><path d="%s"/></clipPath>' % rune_path)
add('</defs>')

# --------------------------------------------------------------- Hintergrund
add('<rect width="%d" height="%d" fill="#08080b"/>' % (W, H))
add('<rect width="%d" height="%d" filter="url(#clouds)" opacity=".60"/>' % (W, H))
add('<rect width="%d" height="%d" filter="url(#clouds2)" opacity=".30"/>' % (W, H))
add('<ellipse cx="812" cy="1266" rx="170" ry="130" fill="url(#moon)"/>')
add('<rect width="%d" height="%d" fill="url(#vign)"/>' % (W, H))

# ---------------------------------------------------------------- Landschaft
HZ = 1408
add('<g>')
add(mountain(HZ - 178, 120, 501, "#1c2027", "#333a45", rough=.55))
add('<rect x="0" y="%d" width="%d" height="240" fill="url(#haze)" opacity=".55"/>' % (HZ - 240, W))
add(mountain(HZ - 96, 108, 733, "#141821", "#2a313b", rough=.56))
add('<rect x="0" y="%d" width="%d" height="180" fill="url(#haze)" opacity=".45"/>' % (HZ - 170, W))
# Fjord
add('<rect x="0" y="%d" width="%d" height="150" fill="url(#water)"/>' % (HZ, W))
add('<ellipse cx="812" cy="%d" rx="105" ry="40" fill="#ecdfc2" opacity=".13" filter="url(#softglow)"/>' % (HZ + 26))
for i in range(30):
    yy = HZ + 4 + i * 4.8
    ww = 100 + rnd.random() * 320
    xx = 520 + (rnd.random() - .5) * 700
    add('<rect x="%.0f" y="%.1f" width="%.0f" height="1.5" fill="#c9d2dc" opacity="%.2f"/>'
        % (xx - ww / 2, yy, ww, .04 + .18 * rnd.random()))
# nahe Ketten
add(mountain(HZ + 68, 150, 97, "#0f1216", "#242a33", rough=.60))
add('<rect x="0" y="%d" width="%d" height="200" fill="url(#haze)" opacity=".35"/>' % (HZ, W))
add(mountain(HZ + 232, 130, 313, "#08090c", None, rough=.62))
add('</g>')
# Nadelwald
for _ in range(18):
    add(pine(rnd.uniform(-10, 330), HZ + 250 + rnd.uniform(-40, 80), rnd.uniform(105, 190),
             rnd.uniform(24, 42), "#0a0c0e", .95))
for _ in range(18):
    add(pine(rnd.uniform(750, 1090), HZ + 250 + rnd.uniform(-40, 80), rnd.uniform(105, 190),
             rnd.uniform(24, 42), "#0a0c0e", .95))
for _ in range(12):
    add(pine(rnd.uniform(-20, 1100), HZ + 430 + rnd.uniform(0, 90), rnd.uniform(150, 260),
             rnd.uniform(32, 54), "#050608", .98))
# Felsen
rock = [(228, H + 40), (312, 1712), (378, 1666), (452, 1636), (540, 1626),
        (632, 1640), (716, 1676), (792, 1726), (866, H + 40)]
add('<path d="M%s Z" fill="#090a0c"/>' % "L".join("%.1f,%.1f" % p for p in rock))
add('<path d="M312,1712 C392,1656 470,1632 540,1626 C632,1632 712,1668 792,1726" fill="none" '
    'stroke="#2b3037" stroke-width="2.2" opacity=".6"/>')
add('<path d="M400,1690 C470,1660 610,1662 700,1700" fill="none" stroke="#1c2025" stroke-width="1.6" opacity=".5"/>')

# ---------------------------------------------------------------- Medaillon
add('<g filter="url(#discshadow)"><circle cx="%d" cy="%d" r="%d" fill="url(#disc)"/></g>' % (CX, CY, RAD))
add('<g clip-path="url(#discclip)"><rect x="%d" y="%d" width="%d" height="%d" filter="url(#stonetex)" '
    'opacity=".40" style="mix-blend-mode:overlay"/></g>' % (CX - RAD, CY - RAD, RAD * 2, RAD * 2))
add('<circle cx="%d" cy="%d" r="%d" fill="none" stroke="#000" stroke-width="7" opacity=".75"/>' % (CX, CY, RAD))
add('<circle cx="%d" cy="%d" r="%d" fill="none" stroke="#4c4c51" stroke-width="1.6" opacity=".45"/>' % (CX, CY, RAD - 6))

seq = ["laguz", "ansuz", "gebo", "uruz", "raido", "isa", "sowilo", "tiwaz", "berkana", "mannaz",
       "algiz", "fehu", "wunjo", "othala", "jera", "naudiz", "ehwaz", "thurisaz", "dagaz",
       "perthro", "kaunaz", "hagalaz", "ingwaz", "eihwaz"]
add('<circle cx="%d" cy="%d" r="%d" fill="none" stroke="#3b3b40" stroke-width="1.4" opacity=".6"/>' % (CX, CY, RAD - 20))
add('<circle cx="%d" cy="%d" r="%d" fill="none" stroke="#3b3b40" stroke-width="1.4" opacity=".6"/>' % (CX, CY, RAD - 92))
rd = ring_runes(CX, CY, RAD - 56, 32, 24, seq, phase=-math.pi / 2)
add('<g fill="none" stroke-linecap="round">')
add('<path d="%s" stroke="#000" stroke-width="9.5" opacity=".85"/>' % rd)
add('<path d="%s" stroke="url(#carve)" stroke-width="5"/>' % rd)
add('</g>')
add(knot_ring(CX, CY, RAD - 140, 40, 12))
add('<circle cx="%d" cy="%d" r="%d" fill="none" stroke="#37373b" stroke-width="1.3" opacity=".55"/>' % (CX, CY, RAD - 192))
add(knot_ring(CX, CY, RAD - 244, 36, 11, phase=0.7))
add('<circle cx="%d" cy="%d" r="%d" fill="none" stroke="#37373b" stroke-width="1.3" opacity=".55"/>' % (CX, CY, RAD - 292))

# ------------------------------------------------------------- Rune "Lögr" ᛚ
add('<g filter="url(#deep)">')
add('<path d="%s" fill="#141416" transform="translate(6,9)" opacity=".9"/>' % rune_path)   # Tiefe
add('<path d="%s" fill="url(#runestone)"/>' % rune_path)
add('</g>')
add('<g clip-path="url(#runeclip)">')
add('<rect x="%d" y="%d" width="500" height="560" filter="url(#runetex)" opacity=".45" '
    'style="mix-blend-mode:multiply"/>' % (SX - 120, SY - HALF - 40))
add('<g stroke="#8b867e" stroke-width="1.6" opacity=".7" fill="none">')
for i in range(13):
    yy = SY - HALF + 22 + i * 36
    add('<path d="M%.0f,%.0f L%.0f,%.0f"/>' % (SX - TW, yy, SX + TW, yy + rnd.uniform(-5, 5)))
for i in range(5):
    t = .16 + i * .18
    x1 = SX + (TIPX - SX) * t; y1 = JY + (TIPY - JY) * t
    add('<path d="M%.0f,%.0f L%.0f,%.0f"/>' % (x1 - 16, y1 - 13, x1 + 16, y1 + 13))
add('</g>')
add('<path d="M%.0f,%.0f L%.0f,%.0f" stroke="#ffffff" stroke-width="4" opacity=".45"/>'
    % (SX - TW / 2 + 2, SY - HALF, SX - TW / 2 + 2, SY + HALF))
add('<path d="M%.0f,%.0f L%.0f,%.0f" stroke="#1a1a1c" stroke-width="5" opacity=".45"/>'
    % (SX + TW / 2 - 2, SY - HALF, SX + TW / 2 - 2, SY + HALF))
add('</g>')

# --------------------------------------------------------------- Typographie
add('<text x="%d" y="1006" text-anchor="middle" font-family="%s" font-size="94" letter-spacing="15" '
    'fill="url(#titlegrad)">LOGR</text>' % (CX, SERIF))
add('<g opacity=".88">')
add('<text x="%d" y="1054" text-anchor="middle" font-family="%s" font-size="31" letter-spacing="8" '
    'fill="%s">WATER</text>' % (CX, SERIF, TEXT_WARM))
add('<path d="M%d,1045 L%d,1045 M%d,1045 L%d,1045" stroke="%s" stroke-width="1.6"/>'
    % (CX - 132, CX - 82, CX + 82, CX + 132, TEXT_WARM))
add('<circle cx="%d" cy="1045" r="2.6" fill="%s"/><circle cx="%d" cy="1045" r="2.6" fill="%s"/>'
    % (CX - 74, TEXT_WARM, CX + 74, TEXT_WARM))
add('</g>')
for i, ln in enumerate(["Steht für das Wasser, den Fluss und die Lebenskraft.",
                        "Sie lehrt, der Strömung zu vertrauen, und schenkt",
                        "Intuition, Reinigung und tiefe innere Klarheit."]):
    add('<text x="%d" y="%d" text-anchor="middle" font-family="%s" font-size="27" fill="%s" '
        'opacity=".92">%s</text>' % (CX, 1114 + i * 38, SERIF, TEXT_WARM, ln))

add(vegvisir(540, 1768, 62))

# -------------------------------------------------------------------- Rahmen
add('<rect x="26" y="26" width="%d" height="%d" fill="none" stroke="%s" stroke-width="2.2" opacity=".9"/>'
    % (W - 52, H - 52, GOLD))
add('<rect x="36" y="36" width="%d" height="%d" fill="none" stroke="%s" stroke-width="1" opacity=".55"/>'
    % (W - 72, H - 72, GOLD_DIM))
for cx_, cy_, ax, ay in ((46, 46, 1, 1), (W - 46, 46, -1, 1), (46, H - 46, 1, -1), (W - 46, H - 46, -1, -1)):
    add(corner_flourish(cx_, cy_, ax, ay))

col = ["hagalaz", "isa", "naudiz", "algiz", "sowilo", "isa", "tiwaz", "laguz", "isa", "gebo", "naudiz", "isa"]
for side in (0, 1):
    x = 58 if side == 0 else W - 58
    yy, i = 236, 0
    while yy < H - 236:
        add('<path d="%s" fill="none" stroke="%s" stroke-width="2" stroke-linecap="round" opacity=".72"/>'
            % (rune_d(col[i % len(col)], x, yy, 15), GOLD))
        yy += 52; i += 1

add(valknut(540, 86, 46))
add('<g stroke="%s" stroke-width="1.5" opacity=".7" fill="none">' % GOLD)
add('<path d="M330,126 L462,126 M618,126 L750,126"/>')
add('<path d="M470,126 l8,-8 8,8 -8,8 z M602,126 l8,-8 8,8 -8,8 z" fill="%s"/>' % GOLD)
add('<path d="M356,118 L356,134 M724,118 L724,134" opacity=".8"/></g>')

add('<rect x="0" y="1180" width="%d" height="700" fill="url(#botfade)"/>' % W)
add('<rect width="%d" height="%d" filter="url(#grain)" opacity=".05" style="mix-blend-mode:overlay"/>' % (W, H))
add('</svg>')

svg = "\n".join(s)
base = "/tmp/claude-0/-home-user-Nordic/10724e7a-916a-5c02-8e30-b21cbe97cd2d/scratchpad/logr/"
open(base + "logr.svg", "w").write(svg)
open(base + "logr.html", "w").write(
    "<!doctype html><meta charset='utf-8'><style>html,body{margin:0;padding:0;background:#000;"
    "overflow:hidden}svg{display:block}</style>" + svg)
print("ok")
