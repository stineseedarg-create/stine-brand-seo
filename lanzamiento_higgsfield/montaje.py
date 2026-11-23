"""Montaje del lanzamiento Green Friday Stine: tomas de Higgsfield + bolsas reales + flashes + cierre + sonido.
Todo se controla desde config_montaje.toml.
    python3 montaje.py                  video + cuadro final
    python3 montaje.py --test 2.3,10.5  cuadros de prueba en salida/prueba_*.png
"""
import argparse, math, os, subprocess, tomllib, wave
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
from scipy import signal

HERE = os.path.dirname(os.path.abspath(__file__))
def P(p): return p if os.path.isabs(p) else os.path.normpath(os.path.join(HERE, p))
with open(P('config_montaje.toml'), 'rb') as fh:
    C = tomllib.load(fh)
OW, OH = C['salida']['ancho'], C['salida']['alto']
FPS, DUR = C['salida']['fps'], C['salida']['duracion']

def sstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0 + 1e-9), 0, 1); return t * t * (3 - 2 * t)
def hex_bgr(h):
    h = C['colores'].get(h, h).lstrip('#')
    return np.array([int(h[4:6], 16), int(h[2:4], 16), int(h[0:2], 16)], np.float32) / 255
def cover(img):
    h, w = img.shape[:2]; s = max(OW / w, OH / h)
    img = cv2.resize(img, (int(round(w * s)), int(round(h * s))), interpolation=cv2.INTER_AREA if s < 1 else cv2.INTER_CUBIC)
    y0, x0 = (img.shape[0] - OH) // 2, (img.shape[1] - OW) // 2
    return img[y0:y0 + OH, x0:x0 + OW]

# ───────── tomas ─────────
class Toma:
    def __init__(self, d):
        self.d = d; self.cap = None; self.still = None; self.last = (-1, None)
        if d.get('clip') and os.path.exists(P(d['clip'])):
            self.cap = cv2.VideoCapture(P(d['clip'])); self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30
            self.n = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)); print('clip:', d['clip'])
        else:
            self.still = cover(cv2.imread(P(d['foto']))).astype(np.float32) / 255
            print('sin clip, uso foto:', d['foto'])
    def frame(self, t):
        u = t - self.d['inicio'] + self.d.get('desde', 0.0)
        if self.cap is not None:
            i = min(self.n - 1, max(0, int(round(u * self.fps))))
            if i != self.last[0]:
                if i != self.last[0] + 1: self.cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                ok, f = self.cap.read()
                self.last = (i, cover(f).astype(np.float32) / 255 if ok else self.last[1])
            return self.last[1]
        if self.d.get('bolsas'): return self.still          # placa fija: las bolsas tienen que quedar sobre las cruces
        z = 1.0 + 0.012 * u                     # foto de reemplazo: leve deriva
        M = np.float32([[z, 0, OW / 2 * (1 - z)], [0, z, OH / 2 * (1 - z)]])
        return cv2.warpAffine(self.still, M, (OW, OH), borderMode=cv2.BORDER_REFLECT)
TOMAS = [Toma(d) for d in C['tomas']]
def toma_en(t):
    for tm in TOMAS:
        if tm.d['inicio'] <= t < tm.d['fin']: return tm
    return TOMAS[-1]

# ───────── bolsas reales ─────────
BC = C['bolsas_comun']; bags = []
for b in C['bolsas']:
    s = cv2.imread(P(b['archivo']), cv2.IMREAD_UNCHANGED).astype(np.float32) / 255
    h = BC['alto']; w = int(round(s.shape[1] * h / s.shape[0])); s = cv2.resize(s, (w, h), interpolation=cv2.INTER_AREA)
    rgb = s[..., :3] ** 2.2; a = s[..., 3]
    g = rgb.mean(axis=2, keepdims=True); rgb = (g + (rgb - g) * 0.8) * 0.55 * np.array([0.88, 0.97, 1.05], np.float32)
    rgb *= (1 - 0.35 * np.clip((np.arange(h) - h * 0.92) / (h * 0.08), 0, 1))[:, None, None]
    rim = cv2.GaussianBlur(np.clip(a - np.roll(a, 4, axis=1), 0, 1), (0, 0), 1.4)   # borde del lado de la puerta
    bags.append(dict(rgb=rgb, a=a, rim=rim, w=w, h=h, x0=int(b['x'] - w / 2), y0=int(BC['base_y'] - h), t=b['aparece'], x=b['x']))
def bag_layers(t):
    bl = np.zeros((OH, OW, 3), np.float32); ba = np.zeros((OH, OW), np.float32)
    ground = np.zeros((OH, OW), np.float32); refl = np.zeros((OH, OW, 3), np.float32)
    for b in bags:
        if t < b['t']: continue
        dy = -8 if t - b['t'] < 1.5 / FPS else 0
        y0, x0, h, w = b['y0'] + dy, b['x0'], b['h'], b['w']
        col = b['rgb'] + (b['rim'] * 0.25)[..., None] * np.array([0.65, 0.85, 1.0], np.float32)
        bl[y0:y0 + h, x0:x0 + w] = col; ba[y0:y0 + h, x0:x0 + w] = b['a']
        yb = int(BC['base_y'])
        cv2.ellipse(ground, (int(b['x']), yb), (int(w * 0.62), 14), 0, 0, 360, 0.7, -1)
        cv2.ellipse(ground, (int(b['x']), yb + 1), (int(w * 0.5), 4), 0, 0, 360, 1.0, -1)
        cv2.ellipse(ground, (int(b['x'] + w * 0.55), yb - 2), (int(w * 0.75), 10), 0, 0, 360, 0.35, -1)   # sombra por la luz de la puerta (hacia la derecha)
        r = (b['rgb'] * b['a'][..., None])[::-1] * np.clip(1 - np.arange(h) / (h * 0.3), 0, 1)[:, None, None] * 0.14
        y1 = min(OH, yb + h); refl[yb:y1, x0:x0 + w] += r[:y1 - yb]
    return bl, ba, np.clip(cv2.GaussianBlur(ground, (0, 0), 6), 0, 1), cv2.GaussianBlur(refl, (0, 0), 2.5)

FLASH_T = sorted([b['t'] for b in bags] + list(C['flashes']['rafaga']))
def flash(t):
    v = 0.0
    for ft in FLASH_T:
        d = t - ft
        if 0 <= d < 0.2: v = max(v, math.exp(-d / 0.035))
    return v * C['flashes']['intensidad']
CA = C['camara']
def zoom(t): return 1.0 + (CA['zoom_max'] - 1) * float(sstep(CA['zoom_desde'], CA['zoom_hasta'], t))

# ───────── cierre ─────────
FONTS = {'titulo': P(C['tipografia']['titulo']), 'fina': P(C['tipografia']['fina'])}
def text_layer(tx):
    lay = Image.new('L', (OW, OH), 0); d = ImageDraw.Draw(lay)
    fo = ImageFont.truetype(FONTS[tx['fuente']], tx['tamano'])
    if tx.get('peso'):
        try: fo.set_variation_by_name(tx['peso'])
        except Exception: pass
    s = tx['texto']; tr = tx.get('espaciado', 0.0) * tx['tamano']
    ws = [fo.getlength(c) for c in s]; tot = sum(ws) + tr * (len(s) - 1)
    if tot > OW - 80: print(f"AVISO: '{s}' mide {tot:.0f}px y se sale de los márgenes")
    x = (OW - tot) / 2
    for c, wc in zip(s, ws):
        d.text((x, tx['y']), c, font=fo, fill=255, anchor='ls'); x += wc + tr
    return np.asarray(lay).astype(np.float32) / 255
TEXTS = [(text_layer(tx), hex_bgr(tx['color']), tx['aparece']) for tx in C['textos']]
CI = C['cierre']

def frame(t):
    tm = toma_en(t)
    bg = tm.frame(t) ** 2.2
    fl = flash(t)
    use_bags = tm.d.get('bolsas', False)
    if use_bags:
        bl, ba, ground, refl = bag_layers(t)
        bg = bg * (1 - 0.7 * ground[..., None]) + refl
    else:
        bl = np.zeros_like(bg); ba = np.zeros((OH, OW), np.float32)
    if fl > 0:
        bg = bg + bg * fl * 0.9 + fl * 0.03; bl = bl + bl * fl * 1.6
    if use_bags:
        z = zoom(t); M = np.float32([[z, 0, OW / 2 * (1 - z)], [0, z, CA['centro_y'] * (1 - z)]])
        wa = lambda a: cv2.warpAffine(a, M, (OW, OH), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        bg, bl, ba = wa(bg), wa(bl), wa(ba)
    k = float(sstep(CI['inicio'], CI['inicio'] + 0.6, t))
    if k > 0:
        bg = cv2.GaussianBlur(bg, (0, 0), 0.5 + CI['desenfoque'] * k)
        grad = np.clip(1.05 - (np.arange(OH, dtype=np.float32)[:, None, None] - 150) / 1500, 0.45, 1)
        bg = bg * (1 - CI['oscurecer'] * k * grad); bl = bl * (1 - 0.25 * k)
    lin = bl * ba[..., None] + bg * (1 - ba[..., None])
    kk_ = 0.8; lin = np.where(lin < kk_, lin, kk_ + (1 - kk_) * (1 - np.exp(-(lin - kk_) / (1 - kk_))))
    y = np.clip(lin, 0, 1) ** (1 / 2.2)
    for L_, col, t0 in TEXTS:
        kk = float(sstep(t0, t0 + 0.35, t))
        if kk <= 0: continue
        L_ = np.roll(L_, int(round((1 - kk) * 14)), axis=0)
        y = y * (1 - 0.45 * kk * cv2.GaussianBlur(L_, (0, 0), 7)[..., None])
        y = y * (1 - kk * L_[..., None]) + kk * L_[..., None] * col
    return (np.clip(y, 0, 1) * 255).astype(np.uint8)

# ───────── sonido (sintetizado; se puede reemplazar por un archivo) ─────────
SR = 48000
def place(buf, snd, t, gain=1.0):
    i = int(t * SR); j = min(len(buf), i + len(snd))
    if 0 <= i < len(buf): buf[i:j] += snd[:j - i] * gain
def bp(x, lo, hi): return signal.sosfilt(signal.butter(2, [lo, hi], 'band', fs=SR, output='sos'), x)
def lp(x, fc): return signal.sosfilt(signal.butter(2, fc, 'low', fs=SR, output='sos'), x)
def env(n, a, d):
    t = np.arange(n) / SR; return (1 - np.exp(-t / max(a, 1e-4))) * np.exp(-t / d)
def shutter(r):
    s = np.zeros(int(0.12 * SR))
    for t0, g in ((0.0, 1.0), (0.048, 0.7)):
        m = int(0.012 * SR); c = bp(r.normal(0, 1, m), 2500, 9000) * env(m, 0.0002, 0.0025)
        c += np.sin(2 * np.pi * 950 * np.arange(m) / SR) * env(m, 0.0003, 0.004) * 0.4
        i = int(t0 * SR); s[i:i + m] += c * g
    return s
def thump(r):
    n = int(0.35 * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * (85 * t - 21 * t * t)) * env(n, 0.002, 0.11) + lp(r.normal(0, 1, n), 600) * env(n, 0.0005, 0.02) * 0.6
def creak(r, dur):
    n = int(dur * SR); rate = 45 + 70 * np.abs(np.cumsum(r.normal(0, 0.02, n)) % 2 - 1) + 30 * np.sin(np.linspace(0, 5, n))
    imp = (np.diff(np.floor(np.cumsum(rate / SR)), prepend=0) > 0) * (0.5 + 0.5 * r.random(n))
    s = sum(bp(imp, fc * 0.93, fc * 1.07) * g for fc, g in ((620, 1.0), (1180, 0.8), (2300, 0.45), (3400, 0.2)))
    tt = np.arange(n) / SR
    return s * sstep(0, 0.08, tt) * (1 - sstep(dur - 0.3, dur, tt)) * (0.6 + 0.4 * np.sin(np.linspace(0, 9, n)) ** 2)
def music(n):
    t = np.arange(n) / SR; s = np.zeros(n)
    for f0 in (110.0, 164.81, 196.0, 246.94, 261.63, 329.63):
        for det in (-0.12, 0.0, 0.11):
            s += signal.sawtooth(2 * np.pi * f0 * (1 + det / 100) * t) * (0.5 if f0 > 200 else 0.8)
    s = lp(s, 1400) * sstep(0, 1.4, t) * (1 - sstep(n / SR - 0.6, n / SR, t))
    return s / 12 + np.sin(2 * np.pi * 55 * t) * env(n, 0.005, 0.9) * 0.6
def soundtrack():
    S_ = C['sonido']; n = int(DUR * SR)
    if S_.get('archivo'):
        out = subprocess.run(['ffmpeg', '-v', 'error', '-i', P(S_['archivo']), '-f', 's16le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True, check=True).stdout
        a = np.frombuffer(out, np.int16).astype(np.float64) / 32768; buf = np.zeros(n); buf[:min(n, len(a))] = a[:n]; return buf
    r = np.random.default_rng(3); buf = lp(r.normal(0, 1, n), 400) * 0.012
    door_open = np.clip(np.arange(n) / SR / 1.4, 0, 1)
    buf += bp(r.normal(0, 1, n), 250, 2500) * 0.02 * door_open
    if S_.get('puerta'):
        m = int(0.03 * SR); place(buf, bp(r.normal(0, 1, m), 1500, 6000) * env(m, 0.0002, 0.004), 0.02, 0.6)
        place(buf, creak(r, 1.3), 0.12, 0.35)
    if S_.get('disparos'):
        for b in bags: place(buf, shutter(r), b['t'] - 0.01, 0.55); place(buf, thump(r), b['t'], 0.9)
        for ft in C['flashes']['rafaga']: place(buf, shutter(r), ft - 0.01, 0.45)
    if S_.get('musica'):
        place(buf, music(int((DUR - CI['inicio']) * SR)), CI['inicio'], S_.get('volumen_musica', 0.5))
    buf = buf / (np.abs(buf).max() + 1e-9) * 0.89
    buf[-int(0.25 * SR):] *= np.linspace(1, 0, int(0.25 * SR)); return buf

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--test'); a = ap.parse_args()
    os.makedirs(P('salida'), exist_ok=True)
    if a.test:
        for t in [float(x) for x in a.test.split(',')]: cv2.imwrite(P(f'salida/prueba_{t:05.2f}.png'), frame(t))
        raise SystemExit
    vid = P(C['salida']['video']); tmp = vid + '.tmp.mp4'
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{OW}x{OH}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', tmp], stdin=subprocess.PIPE)
    last = None
    for i in range(int(round(FPS * DUR))):
        last = frame(i / FPS); p.stdin.write(last.tobytes())
    p.stdin.close(); p.wait()
    cv2.imwrite(P(C['salida']['cuadro_final']), last)
    if C['sonido'].get('activado'):
        wav = vid + '.wav'
        with wave.open(wav, 'wb') as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((soundtrack() * 32767).astype(np.int16).tobytes())
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-i', wav, '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', vid], check=True)
        os.remove(wav)
    else:
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-c', 'copy', '-movflags', '+faststart', vid], check=True)
    os.remove(tmp); print('listo:', vid)
