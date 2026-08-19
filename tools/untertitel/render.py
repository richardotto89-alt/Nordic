import numpy as np, cv2, subprocess, sys, os
from PIL import Image, ImageDraw, ImageFont

# usage: python3 render.py <quell.mp4> <ziel.mp4> ["Segment links"] ["Segment rechts"]
V    = sys.argv[1]
OUT  = sys.argv[2]
SEG1 = sys.argv[3] if len(sys.argv) > 3 else "Nordische Urkraft"
SEG2 = sys.argv[4] if len(sys.argv) > 4 else "coming soon"
HERE = os.path.dirname(os.path.abspath(__file__))

W,H,FPS,N = 1080,1920,30,540
BY0,BY1 = 1180,1320                 # band we operate on
mask_d = np.load(os.path.join(HERE,'mask_d.npy'))      # dilated glyph mask, band coords
S      = np.load(os.path.join(HERE,'Scurve.npy'))      # S(f) for f=420..539
SREF   = S.max()
F0, F1 = 430, 539                   # frames to process

def k(f):
    if f < 420 or f > 539: return 0.0
    return float(np.clip(S[f-420]/SREF, 0.0, 1.0))

# --- build alpha map of the new subtitle -------------------------------------
FONT   = os.path.join(HERE,'EagleLake.ttf')
SIZE   = 28
SS     = 4                          # supersampling
BASE   = 1274                       # baseline (abs y)
CX     = 541                        # line centre x
GAP    = 39                         # gap between the two segments
COLOR  = np.array([245.,238.,234.]) # text colour at full opacity

f4 = ImageFont.truetype(FONT, SIZE*SS)
def ink_w(txt):
    b = f4.getbbox(txt)
    return b[2]-b[0], b[0]
w1,lb1 = ink_w(SEG1); w2,lb2 = ink_w(SEG2)
total = w1 + GAP*SS + w2
x1 = CX*SS - total//2
x2 = x1 + w1 + GAP*SS

canvas = Image.new('L', (W*SS, (BY1-BY0)*SS), 0)
dr = ImageDraw.Draw(canvas)
by = (BASE-BY0)*SS
dr.text((x1-lb1, by), SEG1, font=f4, fill=255, anchor='ls')
dr.text((x2-lb2, by), SEG2, font=f4, fill=255, anchor='ls')
alpha = np.array(canvas.resize((W, BY1-BY0), Image.LANCZOS)).astype(np.float32)/255.0
alpha = np.clip(alpha,0,1)[...,None]
ys,xs = np.nonzero(alpha[...,0]>0.15)
print(f"new text ink: x {xs.min()}..{xs.max()} (w {xs.max()-xs.min()+1})  y {BY0+ys.min()}..{BY0+ys.max()}", flush=True)

# --- transcode ---------------------------------------------------------------
dec = subprocess.Popen(["ffmpeg","-v","error","-i",V,"-f","rawvideo","-pix_fmt","rgb24","-"],
                       stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg","-v","error","-y",
    "-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-",
    "-i",V,"-map","0:v:0","-map","1:a:0",
    "-c:v","libx264","-preset","slow","-crf","17","-pix_fmt","yuv420p",
    "-color_primaries","bt709","-color_trc","bt709","-colorspace","bt709",
    "-c:a","copy","-movflags","+faststart", OUT], stdin=subprocess.PIPE)

for f in range(N):
    buf = dec.stdout.read(W*H*3)
    if len(buf) < W*H*3: break
    frame = np.frombuffer(buf, np.uint8).reshape(H,W,3)
    if F0 <= f <= F1 and k(f) > 0.002:
        band = frame[BY0:BY1].copy()
        bg   = cv2.inpaint(band, mask_d, 6, cv2.INPAINT_TELEA).astype(np.float32)
        kk   = k(f)
        g    = kk if f <= 504 else 1.0     # fade-in of the overlay
        d    = 1.0 if f <= 504 else kk     # global fade to black
        a    = alpha*g
        out  = bg*(1.0-a) + (COLOR*d)*a
        frame = frame.copy()
        frame[BY0:BY1] = np.clip(out+0.5,0,255).astype(np.uint8)
    enc.stdin.write(frame.tobytes())
enc.stdin.close(); enc.wait(); dec.wait()
print("done ->", OUT)
