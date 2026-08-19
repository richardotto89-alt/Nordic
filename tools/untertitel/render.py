import numpy as np, cv2, subprocess, sys, os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
V    = sys.argv[1]
OUT  = sys.argv[2]
TXT  = sys.argv[3] if len(sys.argv) > 3 else "COMING SOON"

W,H,FPS,N = 1080,1920,30,540
BY0,BY1   = 1150,1440                       # band containing line + subtitle + HAMR
MASK  = np.load(os.path.join(HERE,'mask_all.npy'))   # everything below the title
S     = np.load(os.path.join(HERE,'Scurve.npy'))     # opacity of the original subtitle, f=420..539
SREF  = S.max()
CAPH, TRACK, CY = 62, 0.20, 1291            # cap height / letter-spacing / vertical centre
COLOR = np.array([242.,235.,227.])          # same cream as the title
FONT  = os.path.join(HERE,'nf','Norse.otf')
SS    = 4

def k(f):
    if f < 420 or f > 539: return 0.0
    return float(np.clip(S[f-420]/SREF, 0.0, 1.0))
def ramp(f):                                # fade the inpainting in before anything appears
    return float(np.clip((f-428)/6.0, 0.0, 1.0))

# ---- alpha map of the new line ---------------------------------------------
lo,hi = 10,400
for _ in range(30):                          # font size that yields CAPH
    m = (lo+hi)/2
    t = Image.new('L',(2000,900),0); ImageDraw.Draw(t).text((200,300),"C",
        font=ImageFont.truetype(FONT,int(m*SS)), fill=255)
    a = np.array(t); ys,xs = np.nonzero(a>90)
    if (ys.max()-ys.min()+1)/SS < CAPH: lo = m
    else: hi = m
size = int(lo*SS)
f4   = ImageFont.truetype(FONT, size)
W4,H4 = W*SS, 400*SS
t  = Image.new('L',(W4,H4),0); dd = ImageDraw.Draw(t)
adv = [dd.textlength(c,font=f4)+TRACK*size for c in TXT]
x = (W4-(sum(adv)-TRACK*size))/2
for c,a_ in zip(TXT,adv):
    dd.text((x,H4/2), c, font=f4, fill=255, anchor='lm'); x += a_
arr = np.array(t); ys,xs = np.nonzero(arr>60)
arr = np.roll(arr, int(round(W4/2-(xs.min()+xs.max())/2)), axis=1)
alpha = np.clip(np.array(Image.fromarray(arr).resize((W,400),Image.LANCZOS)).astype(np.float32)/255.,0,1)
ay,ax = np.nonzero(alpha>0.15)
TY = int(CY-(ay.min()+ay.max())/2)           # absolute y of the alpha canvas
print(f"'{TXT}': ink x {ax.min()}..{ax.max()} (w {ax.max()-ax.min()+1}), "
      f"y {TY+ay.min()}..{TY+ay.max()} (cap {ay.max()-ay.min()+1})", flush=True)
alpha = alpha[...,None]

# ---- transcode --------------------------------------------------------------
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
    r = ramp(f)
    if r > 0:
        frame = frame.copy()
        band  = frame[BY0:BY1]
        clean = cv2.inpaint(band, MASK, 7, cv2.INPAINT_TELEA).astype(np.float32)
        frame[BY0:BY1] = np.clip(band.astype(np.float32)*(1-r) + clean*r + 0.5,0,255).astype(np.uint8)
        kk = k(f)
        if kk > 0.002:
            g = kk if f <= 504 else 1.0      # fade-in of the new line
            d = 1.0 if f <= 504 else kk      # global fade to black
            a = alpha*g
            reg = frame[TY:TY+400].astype(np.float32)
            frame[TY:TY+400] = np.clip(reg*(1-a) + (COLOR*d)*a + 0.5,0,255).astype(np.uint8)
    enc.stdin.write(frame.tobytes())
enc.stdin.close(); enc.wait(); dec.wait()
print("done ->", OUT)
