"""Video animado por bolsa (Stine Green Friday): cortes al ritmo, zooms de golpe, barridos,
flashes de foto con congelado (como una sesión de fotos) y look de película.
    python3 animado.py bolsas/9734.toml                 render completo (video + cuadro final)
    python3 animado.py bolsas/9734.toml --test 1.0,2.3  cuadros de prueba
Cada toma puede usar un clip de Higgsfield ("clip") o una foto ("foto") con movimiento de cámara.
"""
import argparse, math, os, subprocess, tomllib, wave
import numpy as np, cv2
from scipy import signal

HERE = os.path.dirname(os.path.abspath(__file__))
def P(p): return p if os.path.isabs(p) else os.path.normpath(os.path.join(HERE, p))
ap = argparse.ArgumentParser(); ap.add_argument('config'); ap.add_argument('--test'); A = ap.parse_args()
with open(P(A.config), 'rb') as fh: C = tomllib.load(fh)
G = C.get('general', {})
OW, OH, FPS = G.get('ancho', 1080), G.get('alto', 1920), G.get('fps', 30)
TOMAS = C['tomas']; DUR = TOMAS[-1]['fin']; E = C.get('efecto', {})
def e(k, d): return E.get(k, d)

def sstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0 + 1e-9), 0, 1); return t * t * (3 - 2 * t)
def curva(u, tipo):
    u = min(max(u, 0.0), 1.0)
    if tipo == 'snap': return 1 - (1 - u) ** 4            # golpe rápido y frena
    if tipo == 'lineal': return u
    if tipo == 'acelera': return u ** 2.2
    return u * u * (3 - 2 * u)

FOTOS = {}
def foto(p):
    if p not in FOTOS: FOTOS[p] = (cv2.imread(P(p)).astype(np.float32) / 255) ** 2.2
    return FOTOS[p]
CAPS = {}
def clip_frame(s, t):
    p = s.get('clip')
    if not p or not os.path.exists(P(p)): return None
    if p not in CAPS:
        cap = cv2.VideoCapture(P(p)); CAPS[p] = [cap, cap.get(cv2.CAP_PROP_FPS) or 24, int(cap.get(cv2.CAP_PROP_FRAME_COUNT)), -1, None]
    c = CAPS[p]; i = min(c[2] - 1, max(0, int((t - s['inicio'] + s.get('desde', 0.0)) * c[1])))
    if i != c[3]:
        c[0].set(cv2.CAP_PROP_POS_FRAMES, i); ok, f = c[0].read()
        if ok:
            h, w = f.shape[:2]; sc = max(OW / w, OH / h); f = cv2.resize(f, (int(round(w * sc)), int(round(h * sc))), interpolation=cv2.INTER_CUBIC)
            y0, x0 = (f.shape[0] - OH) // 2, (f.shape[1] - OW) // 2; c[4] = (f[y0:y0 + OH, x0:x0 + OW].astype(np.float32) / 255) ** 2.2
        c[3] = i
    return c[4]

def disc(r):
    r = max(1, int(round(r))); k = np.zeros((2 * r + 1, 2 * r + 1), np.float32)
    cv2.circle(k, (r, r), r, 1.0, -1, cv2.LINE_AA); return k / k.sum()
def lens_blur(img, r):
    if r < 0.8: return img
    sm = cv2.resize(img, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
    sm = cv2.filter2D(sm, -1, disc(r * 0.5), borderType=cv2.BORDER_REFLECT)
    return cv2.resize(sm, (OW, OH), interpolation=cv2.INTER_LINEAR)
def dir_blur(img, L, ang):
    if L < 2: return img
    n = max(3, int(L * 0.5)); k = np.zeros((n, n), np.float32)
    c = n // 2; dx, dy = math.cos(ang), math.sin(ang)
    for i in range(n):
        x = int(round(c + (i - c) * dx)); y = int(round(c + (i - c) * dy)); k[min(max(y, 0), n - 1), min(max(x, 0), n - 1)] = 1
    k /= k.sum()
    sm = cv2.resize(img, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
    sm = cv2.filter2D(sm, -1, k, borderType=cv2.BORDER_REFLECT)
    return cv2.resize(sm, (OW, OH), interpolation=cv2.INTER_LINEAR)

def toma_en(t):
    for i, s in enumerate(TOMAS):
        if s['inicio'] <= t < s['fin']: return i, s
    return len(TOMAS) - 1, TOMAS[-1]

rng = np.random.default_rng(4)
SHK = cv2.GaussianBlur(np.cumsum(rng.normal(0, 1, (int(DUR * FPS) + 20, 2)), axis=0).astype(np.float32), (1, 0), sigmaX=0.1, sigmaY=5)
SHK = (SHK - SHK.mean(axis=0)) / (SHK.std(axis=0) + 1e-6)
WHIP = {'whip_izq': math.pi, 'whip_der': 0.0, 'whip_arriba': -math.pi / 2, 'whip_abajo': math.pi / 2}

# flashes: [t, "flash"] o [t, "foto"] (flash + cuadro congelado)
FL = sorted([(float(f[0]), f[1]) for f in C.get('flashes', [])])
FREEZE = e('congelado', 0.14)
def t_escena(t):
    for ft, tp in FL:
        if tp == 'foto' and ft <= t < ft + FREEZE: return ft
    return t
def flash_val(t):
    v = 0.0
    for ft, tp in FL:
        d = t - ft
        if 0 <= d < 0.25: v = max(v, math.exp(-d / (0.05 if tp == 'foto' else 0.035)) * (1.0 if tp == 'foto' else 0.75))
    return v
def punch(t):
    v = 0.0
    for ft, tp in FL:
        d = t - ft
        if tp == 'foto' and 0 <= d < FREEZE + 0.15: v = max(v, math.exp(-max(0, d - FREEZE) / 0.06))
    return v

def plano(s, t):
    cf = clip_frame(s, t)
    u = (t - s['inicio']) / (s['fin'] - s['inicio']); k = curva(u, s.get('curva', 'suave'))
    z = s.get('zoom', [1, 1]); z = z[0] + (z[1] - z[0]) * k
    c0, c1 = s.get('centro', [[OW / 2, OH / 2], [OW / 2, OH / 2]])
    cx, cy = c0[0] + (c1[0] - c0[0]) * k, c0[1] + (c1[1] - c0[1]) * k
    rot = s.get('giro', [0, 0]); rot = rot[0] + (rot[1] - rot[0]) * k
    z *= 1 + 0.035 * punch(t)
    fi = min(len(SHK) - 1, int(t * FPS)); u0 = t - s['inicio']
    imp = math.exp(-u0 / 0.12) * e('golpe_corte', 10)               # sacudón al cortar
    jx, jy = SHK[fi] * (e('temblor', 1.5) + imp)
    if cf is not None:
        src = cf; h, w = OH, OW; cx = cx * w / OW if 'clip' in s else cx
    else:
        src = foto(s['foto']); h, w = src.shape[:2]
    sc = max(OW / w, OH / h) * z
    hw, hh = OW / 2 / sc, OH / 2 / sc
    cx = min(max(cx, hw), w - hw); cy = min(max(cy, hh), h - hh)
    M = cv2.getRotationMatrix2D((cx, cy), rot, sc)
    M[0, 2] += OW / 2 - cx + jx; M[1, 2] += OH / 2 - cy + jy
    return cv2.warpAffine(src, M, (OW, OH), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)

yy, xx = np.mgrid[0:OH, 0:OW].astype(np.float32)
VIG = 1 - e('vineta', 0.3) * np.clip(((xx - OW / 2) / (OW * 0.75)) ** 2 + ((yy - OH / 2) / (OH * 0.72)) ** 2, 0, 1)

def frame(t):
    ts = t_escena(t)
    i, s = toma_en(ts); dur = s['fin'] - s['inicio']; u = ts - s['inicio']
    img = plano(s, ts)
    ent = s.get('entrada', 'corte'); sal = TOMAS[i + 1].get('entrada', 'corte') if i + 1 < len(TOMAS) else 'corte'
    blur = 0.0
    if ent == 'enfoque': blur = e('desenfoque_max', 28) * (1 - float(sstep(0, e('duracion_foco', 0.3), u))) ** 1.4
    if ent in WHIP:
        k = 1 - float(sstep(0, 0.12, u))
        img = np.roll(img, int(-k * 140 * math.cos(WHIP[ent])), axis=1) if 'izq' in ent or 'der' in ent else np.roll(img, int(-k * 140 * math.sin(WHIP[ent])), axis=0)
        img = dir_blur(img, k * e('barrido_px', 160), WHIP[ent])
    if sal in WHIP:
        k = float(sstep(dur - 0.08, dur, u))
        img = dir_blur(img, k * e('barrido_px', 160), WHIP[sal])
    if sal == 'enfoque': blur = max(blur, e('desenfoque_max', 28) * 0.6 * float(sstep(dur - 0.12, dur, u)))
    img = lens_blur(img, blur)
    fl = flash_val(t)
    if fl > 0:
        g = img.mean(axis=2, keepdims=True); img = img * (1 - 0.25 * fl) + g * 0.25 * fl     # el flash lava un poco el color
        img = img * (1 + 2.6 * fl) + 0.10 * fl
    if ent == 'flash': img = img + 1.4 * (1 - float(sstep(0, 0.12, u)))
    # look
    hi = np.clip(img - 0.5, 0, None)
    img = img + cv2.GaussianBlur(hi, (0, 0), 22) * (e('halo', 0.3) + 0.5 * fl) * np.array([0.75, 0.88, 1.0], np.float32)
    img = img * VIG[..., None]
    y = np.clip(img, 0, None); y = y / (1 + 0.22 * y)
    y = np.clip(y * 1.12, 0, 1) ** (1 / 2.2)
    gr = np.random.default_rng(int(t * FPS) + 7).normal(0, 1, (OH // 2, OW // 2)).astype(np.float32)
    y = np.clip(y + cv2.resize(gr, (OW, OH))[..., None] * e('grano', 0.03), 0, 1)
    fo = e('fundido_final', 0.35)
    if t > DUR - fo: y = y * (1 - float(sstep(DUR - fo, DUR, t)))
    return (np.clip(y, 0, 1) * 255).astype(np.uint8)

# ───────── sonido (disparos de cámara, barridos y golpes; la música va aparte) ─────────
SR = 48000
def bp(x, lo, hi): return signal.sosfilt(signal.butter(2, [lo, hi], 'band', fs=SR, output='sos'), x)
def lp(x, fc): return signal.sosfilt(signal.butter(2, fc, 'low', fs=SR, output='sos'), x)
def env(n, a, d):
    t = np.arange(n) / SR; return (1 - np.exp(-t / max(a, 1e-4))) * np.exp(-t / d)
def place(buf, snd, t, g=1.0):
    i = int(t * SR); j = min(len(buf), i + len(snd))
    if 0 <= i < len(buf): buf[i:j] += snd[:j - i] * g
def shutter(r, fuerte=False):
    s = np.zeros(int(0.2 * SR))
    for t0, g in ((0.0, 1.0), (0.05, 0.75)):
        m = int(0.014 * SR); c = bp(r.normal(0, 1, m), 2200, 9000) * env(m, 0.0002, 0.003)
        c += np.sin(2 * np.pi * 900 * np.arange(m) / SR) * env(m, 0.0003, 0.004) * 0.5
        i = int(t0 * SR); s[i:i + m] += c * g
    if fuerte:   # zumbido de recarga del flash
        n = int(0.16 * SR); tt = np.arange(n) / SR
        s[int(0.04 * SR):int(0.04 * SR) + n] += np.sin(2 * np.pi * (2400 + 4000 * tt) * tt) * env(n, 0.01, 0.06) * 0.08
    return s
def whoosh(r):
    n = int(0.22 * SR); t = np.arange(n) / SR; x = r.normal(0, 1, n)
    return bp(x, 400, 3500) * np.sin(np.pi * t / t[-1]) ** 2 * 0.6
def thump(r):
    n = int(0.3 * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * (70 * t - 15 * t * t)) * env(n, 0.002, 0.09) + lp(r.normal(0, 1, n), 500) * env(n, 0.0005, 0.015) * 0.5
def soundtrack():
    S = C.get('sonido', {}); n = int(DUR * SR); r = np.random.default_rng(3); buf = lp(r.normal(0, 1, n), 300) * 0.006
    for ft, tp in FL: place(buf, shutter(r, tp == 'foto'), ft - 0.005, 0.7 if tp == 'foto' else 0.45)
    for s in TOMAS[1:]:
        if s.get('entrada') in WHIP: place(buf, whoosh(r), s['inicio'] - 0.11, 0.5)
        if s.get('curva') == 'snap': place(buf, thump(r), s['inicio'], 0.55)
    if S.get('musica'):
        out = subprocess.run(['ffmpeg', '-v', 'error', '-i', P(S['musica']), '-f', 's16le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True, check=True).stdout
        m = np.frombuffer(out, np.int16).astype(np.float64) / 32768; buf[:min(n, len(m))] += m[:n] * S.get('volumen_musica', 0.6)
    buf = buf / (np.abs(buf).max() + 1e-9) * 0.89
    buf[-int(0.3 * SR):] *= np.linspace(1, 0, int(0.3 * SR)); return buf

if __name__ == '__main__':
    os.makedirs(P('salida'), exist_ok=True)
    name = os.path.splitext(os.path.basename(A.config))[0]
    if A.test:
        for t in [float(x) for x in A.test.split(',')]: cv2.imwrite(P(f'salida/prueba_{name}_{t:05.2f}.png'), frame(t))
        raise SystemExit
    vid = P(G.get('video', f'salida/stine-{name}-9x16.mp4')); tmp = vid + '.tmp.mp4'
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{OW}x{OH}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'slow', '-crf', '21', '-maxrate', '16M', '-bufsize', '32M', '-pix_fmt', 'yuv420p', tmp], stdin=subprocess.PIPE)
    N = int(round(FPS * DUR)); best = None
    for i in range(N):
        f = frame(i / FPS); p.stdin.write(f.tobytes())
        if i == int(N * 0.9): best = f
    p.stdin.close(); p.wait()
    cv2.imwrite(vid.replace('.mp4', '-cuadro.png'), best)
    wav = vid + '.wav'
    with wave.open(wav, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((soundtrack() * 32767).astype(np.int16).tobytes())
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-i', wav, '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', vid], check=True)
    os.remove(wav); os.remove(tmp); print('listo:', vid)
