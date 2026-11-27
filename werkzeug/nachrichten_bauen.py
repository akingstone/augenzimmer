"""Nachrichten-Video fürs Augenzimmer: Clips + Senderlogo + Bauchbinde + Laufband.
Aufruf: python3 news.py segments.json ausgabe.mp4
"""
import json, sys, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1280, 720, 30
F = '/usr/share/fonts/opentype/inter/'
def font(name, size): return ImageFont.truetype(F + name, size)
fB = font('Inter-Bold.otf', 34); fS = font('Inter-SemiBold.otf', 22); fT = font('Inter-SemiBold.otf', 24)
fL = font('Inter-Black.otf', 26); fLive = font('Inter-Bold.otf', 18); fTag = font('Inter-Black.otf', 20)

RED = (200, 16, 30); NAVY = (12, 24, 52); WHITE = (255, 255, 255); INK = (15, 18, 28)
SENDER = 'INNENWELT 24'
TICKER_H = 44; LT_Y = H - TICKER_H - 150

def overlay(headline, sub, tag, credit=None):
    o = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(o)
    # sender bug top left
    d.rectangle([36, 30, 36 + d.textlength(SENDER, font=fL) + 28, 72], fill=NAVY + (235,))
    d.text((50, 36), SENDER, font=fL, fill=WHITE)
    x = 36 + d.textlength(SENDER, font=fL) + 28
    d.rectangle([x, 30, x + 64, 72], fill=RED + (255,)); d.text((x + 12, 41), 'LIVE', font=fLive, fill=WHITE)
    # lower third
    tw = d.textlength(tag, font=fTag) + 28
    d.rectangle([60, LT_Y, 60 + tw, LT_Y + 34], fill=RED + (255,))
    d.text((74, LT_Y + 6), tag, font=fTag, fill=WHITE)
    hw = max(d.textlength(headline, font=fB), d.textlength(sub, font=fS)) + 48
    d.rectangle([60, LT_Y + 34, 60 + hw, LT_Y + 34 + 56], fill=(250, 250, 250, 245))
    d.text((84, LT_Y + 40), headline, font=fB, fill=INK)
    d.rectangle([60, LT_Y + 90, 60 + hw, LT_Y + 90 + 34], fill=NAVY + (235,))
    d.text((84, LT_Y + 95), sub, font=fS, fill=WHITE)
    if credit:
        fc = font('Inter-Medium.otf', 15); cw = d.textlength(credit, font=fc)
        d.rectangle([W - cw - 46, 32, W - 30, 56], fill=(0, 0, 0, 140)); d.text((W - cw - 38, 35), credit, font=fc, fill=(235, 235, 235))
    return np.asarray(o).astype(np.float32)

def ticker_strip(items):
    txt = '   +++   '.join(items) + '   +++   '
    tmp = ImageDraw.Draw(Image.new('L', (1, 1)))
    tw = int(tmp.textlength(txt, font=fT)) + 1
    s = Image.new('RGB', (tw, TICKER_H), NAVY); ImageDraw.Draw(s).text((0, 9), txt, font=fT, fill=WHITE)
    return np.asarray(s)

def anchor_frames(seg, n):
    """Gemalte Sprecherin aus dem Gedankenaufzug im Studio, spricht (Mund) und blinzelt."""
    import cv2, math
    tv = cv2.cvtColor(cv2.imread(seg['file']), cv2.COLOR_BGR2RGB)
    tv = cv2.bilateralFilter(tv, 7, 30, 7)
    th, tw = tv.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W]
    bg = np.zeros((H, W, 3), np.float32)
    g = np.clip(1 - np.hypot((xx - 820) / 900, (yy - 300) / 600), 0, 1)[..., None]
    bg[:] = np.array([10, 22, 52]) * (1 - g) + np.array([38, 78, 150]) * g
    for k in range(-6, 14):   # Studio-Linien
        x = 120 * k + 40; cv2.line(bg, (x, 0), (x - 260, H), (60, 100, 170), 1, cv2.LINE_AA)
    rng = np.random.default_rng(3)
    mouth_h = 0.0
    SKIN = tuple(int(v) for v in tv[205:210, 505:510].reshape(-1, 3).mean(0))
    for i in range(n):
        t = i / FPS
        f = tv.copy()
        # Mund: Sprechbewegung
        target = 0 if (int(t * 4) % 7 == 6) else rng.uniform(2, 11)
        mouth_h += (target - mouth_h) * 0.5
        cv2.ellipse(f, (526, 220), (17, 9), 0, 0, 360, SKIN, -1, cv2.LINE_AA)
        cv2.ellipse(f, (526, 220), (12, max(2, int(mouth_h / 2 + 2))), 0, 0, 360, (45, 28, 32), -1, cv2.LINE_AA)
        # Blinzeln
        if (t % 3.2) < 0.13:
            for (ex, ey) in [(496, 166), (548, 161)]:
                cv2.ellipse(f, (ex, ey), (15, 8), 0, 0, 360, SKIN, -1, cv2.LINE_AA)
                cv2.line(f, (ex - 13, ey + 2), (ex + 13, ey + 2), (40, 30, 30), 3, cv2.LINE_AA)
        z = 1.0 + 0.06 * t / (n / FPS)
        hh = int(560 * z); ww = int(tw * hh / th)
        fs = cv2.resize(f, (ww, hh), interpolation=cv2.INTER_CUBIC)
        out = bg.copy(); x0 = W - ww - 90 + int(40 * (z - 1) / 0.06); y0 = (H - hh) // 2 - 30
        x0 = max(0, min(W - ww, x0)); y0 = max(0, y0)
        out[y0:y0 + hh, x0:x0 + ww] = fs[:H - y0, :W - x0]
        cv2.rectangle(out, (x0, y0), (x0 + ww, y0 + hh), (230, 230, 235), 3)
        yield out

def clip_frames(seg, n):
    """Frames eines Clips (Video oder Standbild mit langsamem Zoom) als RGB-Arrays 1280x720."""
    src = seg.get('file')
    if seg.get('still'):
        im = Image.open(src).convert('RGB')
        r = max(W / im.width, H / im.height) * 1.12
        im = im.resize((int(im.width * r), int(im.height * r)), Image.LANCZOS)
        a = np.asarray(im)
        for i in range(n):
            t = i / max(n - 1, 1); z = 1.0 + 0.10 * t           # langsamer Zoom
            cw, ch = int(im.width / z), int(im.height / z)
            x0 = (im.width - cw) // 2; y0 = (im.height - ch) // 2
            yield np.asarray(Image.fromarray(a[y0:y0 + ch, x0:x0 + cw]).resize((W, H), Image.BILINEAR))
        return
    if seg.get('anchor'):
        yield from anchor_frames(seg, n)
        return
    if seg.get('placeholder'):
        for i in range(n):
            im = Image.new('RGB', (W, H), tuple(seg['placeholder'])); d = ImageDraw.Draw(im)
            d.text((W // 2 - 260, H // 2 - 120), seg['label'], font=fB, fill=WHITE)
            yield np.asarray(im)
        return
    vf = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS}"
    if seg.get('zoom'):
        z = seg['zoom']; vf = f"scale={int(W*z)}:{int(H*z)},crop={W}:{H}:{int(W*z)-W}:{int(H*z)-H},fps={FPS}"
    if seg.get('speed'): vf = f"setpts=PTS/{seg['speed']}," + vf
    p = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-ss', str(seg.get('start', 0)), '-i', src, '-t',
                          str(seg['dur'] * seg.get('speed', 1) + 1), '-vf', vf, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                         stdout=subprocess.PIPE)
    last = None
    for i in range(n):
        b = p.stdout.read(W * H * 3)
        if len(b) == W * H * 3: last = np.frombuffer(b, np.uint8).reshape(H, W, 3)
        yield last
    p.kill()

def main(cfg_path, out):
    cfg = json.load(open(cfg_path, encoding='utf-8'))
    strip = ticker_strip(cfg['ticker']); sw = strip.shape[1]
    total = sum(int(s['dur'] * FPS) for s in cfg['segments'])
    speed = sw * max(1, round(total * 3 / sw)) / total   # ~3 px/Frame, nahtlose Schleife
    enc = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                            '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '23',
                            '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '-an', out], stdin=subprocess.PIPE)
    k = 0
    for seg in cfg['segments']:
        n = int(seg['dur'] * FPS)
        ov = overlay(seg['headline'], seg['sub'], seg.get('tag', 'EILMELDUNG'), seg.get('credit')); a = ov[..., 3:] / 255
        for i, fr in enumerate(clip_frames(seg, n)):
            f = fr.astype(np.float32)
            if i < 6: f *= (i + 1) / 7                       # kurzer Schnitt-Blitz aus Schwarz
            f = f * (1 - a) + ov[..., :3] * a
            off = int(k * speed) % sw                           # Laufband (nahtlos, da Schleife)
            row = np.concatenate([strip, strip], 1)[:, off:off + W]
            f[H - TICKER_H:] = row
            f[H - TICKER_H - 3:H - TICKER_H] = RED
            enc.stdin.write(np.clip(f, 0, 255).astype(np.uint8).tobytes()); k += 1
    enc.stdin.close(); enc.wait()
    print('frames', k, 'sekunden', k / FPS, 'ticker-px', sw, 'umlaeufe', k * speed / sw)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
