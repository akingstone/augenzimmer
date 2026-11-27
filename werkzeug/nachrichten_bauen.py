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
