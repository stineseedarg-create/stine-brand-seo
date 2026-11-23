"""Video de lanzamiento Green Friday Stine.

Lee config.toml y genera el MP4 (con sonido) y un PNG del cuadro final.
    python3 render.py                 render completo
    python3 render.py --test 2.3,9.5  solo cuadros de prueba en salida/prueba_*.png
"""
import argparse, math, os, subprocess, tomllib, wave
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
from scipy import signal

HERE = os.path.dirname(os.path.abspath(__file__))
def P(p): return p if os.path.isabs(p) else os.path.join(HERE, p)
with open(P('config.toml'), 'rb') as fh:
    C = tomllib.load(fh)

OW, OH = C['salida']['ancho'], C['salida']['alto']
FPS, DUR = C['salida']['fps'], C['salida']['duracion']

def hex_bgr(h):
    h = C['colores'].get(h, h).lstrip('#')
    return np.array([int(h[4:6], 16), int(h[2:4], 16), int(h[0:2], 16)], np.float32) / 255
def sstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0 + 1e-9), 0, 1); return t * t * (3 - 2 * t)
def to_lin(a): return np.clip(a, 0, 1) ** 2.2
def to_srgb(a): return np.clip(a, 0, 1) ** (1 / 2.2)

# ───────────────────────── fondo y geometría ─────────────────────────
bg = cv2.imread(P(C['fondo']['imagen'])).astype(np.float32) / 255
bg = cv2.resize(bg, (OW, OH), interpolation=cv2.INTER_LANCZOS4)
plate = to_lin(bg)
lum = plate.mean(axis=2)
alb = plate / np.maximum(cv2.GaussianBlur(lum, (0, 0), 35), 1e-3)[..., None] * 0.32   # ~albedo
yy, xx = np.mgrid[0:OH, 0:OW].astype(np.float32)
YW, YH, F = C['fondo']['linea_piso'], C['fondo']['horizonte'], C['fondo']['focal']
CX = OW / 2; D = F; HC = YW - YH
isfloor = yy > YW
ZC = np.where(isfloor, F * HC / np.maximum(yy - YH, 1e-3), D)
PX = (xx - CX) * ZC / F
PY = np.where(isfloor, 0.0, HC - (yy - YH))
PZ = np.where(isfloor, D - ZC, 0.0)
def proj(X, Y, Z):
    zc = D - Z; return CX + F * X / zc, YH - F * (Y - HC) / zc

# ───────────────────────── bolsas ─────────────────────────
BC = C['bolsas_comun']
zc_b = F * HC / (BC['base_y'] - YH); BZ = D - zc_b; SC = F / zc_b
BH = BC['alto_px'] / SC
bags = []
for b in C['bolsas']:
    im = cv2.imread(P(b['archivo']), cv2.IMREAD_UNCHANGED).astype(np.float32) / 255
    h = BC['alto_px']; w = int(round(im.shape[1] * h / im.shape[0]))
    im = cv2.resize(im, (w, h), interpolation=cv2.INTER_AREA)
    rgb, a = to_lin(im[..., :3]), im[..., 3]
    rim = cv2.GaussianBlur(np.clip(a - np.roll(a, 5, axis=1), 0, 1), (0, 0), 1.6)        # borde izquierdo
    occl = 1 - 0.35 * np.clip((np.arange(h) - h * 0.92) / (h * 0.08), 0, 1)                 # base apoyada
    bx = (b['x'] - CX) / SC
    gl = rgb.mean(axis=2, keepdims=True); rgb = (gl + (rgb - gl) * 0.82) * 0.80   # integra color/luz con el estudio
    bags.append(dict(rgb=rgb * occl[:, None, None], a=a, rim=rim, x0=int(round(b['x'] - w / 2)),
                     y0=int(BC['base_y'] - h), w=w, h=h, bx=bx, hw=w / 2 / SC, t=b['aparece']))

# cruces de cinta
cr = C['cruces']; tape = np.zeros((OH, OW), np.float32)
for b in bags:
    a1 = ((PX - b['bx']) + (PZ - BZ)) / math.sqrt(2); a2 = ((PX - b['bx']) - (PZ - BZ)) / math.sqrt(2)
    m = isfloor & (((np.abs(a1) < cr['grosor']) & (np.abs(a2) < cr['brazo'])) | ((np.abs(a2) < cr['grosor']) & (np.abs(a1) < cr['brazo'])))
    tape = np.maximum(tape, m.astype(np.float32))
tape = cv2.GaussianBlur(tape, (0, 0), 0.7)
tape_lvl = cv2.GaussianBlur(lum, (0, 0), 20) * 2.4 + 0.05
grain = 0.93 + 0.07 * np.random.default_rng(1).random((OH, OW)).astype(np.float32)
plate = plate * (1 - tape[..., None]) + (np.clip(tape_lvl * grain, 0, 0.9) * tape)[..., None] * np.array([0.97, 0.99, 1.0], np.float32)
alb = alb * (1 - tape[..., None]) + 0.75 * tape[..., None]

# ───────────────────────── luz de la puerta ─────────────────────────
PU = C['puerta']
Ld = np.array([1.0, -0.30, 0.10]); Ld /= np.linalg.norm(Ld)
XL, DZ0, DZW, DY1 = -700.0, 40.0, 170.0, 560.0
DOORC = hex_bgr(PU['color'])
def door_lit(Px, Py, Pz, w, soft=0.05):
    s = (Px - XL) / Ld[0]; qy = Py - s * Ld[1]; qz = Pz - s * Ld[2]
    ww = 1.0 + soft * np.maximum(s, 0)
    return (sstep(-ww, ww, qy) * (1 - sstep(DY1 - ww, DY1 + ww, qy)) *
            sstep(DZ0 - ww, DZ0 + ww, qz) * (1 - sstep(DZ0 + w - ww, DZ0 + w + ww, qz)) * (s > 0))
DOOR_FALL = np.clip(1.5 - 1.1 * ((PX - XL) / Ld[0]) / 1500.0, 0.35, 1.5)   # más fuerte cerca de la puerta
def door_w(t): return DZW * float(sstep(PU['inicio'], PU['inicio'] + PU['apertura'], t)) ** 0.8
floor_hp = np.clip((lum - cv2.GaussianBlur(lum, (0, 0), 2.5)) / (cv2.GaussianBlur(lum, (0, 0), 2.5) + 1e-3), -0.6, 0.6)

def bag_shadow(active):
    m = np.zeros((OH, OW), np.uint8); k = -1.0 / Ld[1]
    for b, on in zip(bags, active):
        if not on: continue
        d = b['hw'] * 0.45; pts = []
        for X in (b['bx'] - b['hw'], b['bx'] + b['hw']):
            for Z in (BZ - d, BZ + d):
                for Y in (0.0, BH):
                    Xs, Zs = X + Y * k * Ld[0], min(Z + Y * k * Ld[2], D - 30)
                    pts.append(proj(Xs, 0, Zs))
        cv2.fillPoly(m, [cv2.convexHull(np.int32(pts))], 1)
    return cv2.GaussianBlur(m.astype(np.float32), (0, 0), 6)
def contact(active):
    m = np.zeros((OH, OW), np.float32)
    for b, on in zip(bags, active):
        if not on: continue
        xc = b['x0'] + b['w'] / 2; yb = BC['base_y']
        cv2.ellipse(m, (int(xc), int(yb)), (int(b['w'] * 0.60), 20), 0, 0, 360, 0.65, -1)
        cv2.ellipse(m, (int(xc), int(yb) + 2), (int(b['w'] * 0.50), 5), 0, 0, 360, 1.0, -1)
    return np.clip(cv2.GaussianBlur(m, (0, 0), 8), 0, 1)
def reflection(active):
    r = np.zeros((OH, OW, 3), np.float32)
    for b, on in zip(bags, active):
        if not on: continue
        fl = (b['rgb'] * b['a'][..., None])[::-1]
        fade = np.clip(1 - np.arange(b['h']) / (b['h'] * 0.30), 0, 1)[:, None, None] * 0.16
        fl = cv2.GaussianBlur(fl * fade, (0, 0), 3)
        y0 = BC['base_y']; y1 = min(OH, y0 + b['h']); x0, x1 = max(0, b['x0']), min(OW, b['x0'] + b['w'])
        r[y0:y1, x0:x1] += fl[:y1 - y0, x0 - b['x0']:x1 - b['x0']]
    return r

# neblina (ray-marching a baja resolución)
VW, VH = 135, 240
vy_, vx_ = np.mgrid[0:VH, 0:VW].astype(np.float32)
vxs, vys = (vx_ + 0.5) * OW / VW, (vy_ + 0.5) * OH / VH
vfl = vys > YW; vZc = np.where(vfl, F * HC / np.maximum(vys - YH, 1e-3), D)
vPX = (vxs - CX) * vZc / F; vPY = np.where(vfl, 0.0, HC - (vys - YH)); vPZ = np.where(vfl, D - vZc, 0.0)
CAM = np.array([0.0, HC, D])
HAZE = cv2.GaussianBlur(np.random.default_rng(9).random((96, 54)).astype(np.float32), (0, 0), 3)
HAZE = (HAZE - HAZE.min()) / (HAZE.max() - HAZE.min())
_vol_cache = {}
def volume(w):
    key = round(w, 1)
    if key in _vol_cache: return _vol_cache[key]
    acc = np.zeros((VH, VW), np.float32); NS = 34
    for i in range(NS):
        t = (i + 0.5) / NS
        mx, my, mz = CAM[0] + t * (vPX - CAM[0]), CAM[1] + t * (vPY - CAM[1]), CAM[2] + t * (vPZ - CAM[2])
        lit = door_lit(mx, my, mz, w, soft=0.06)
        ss = (mx - XL) / Ld[0]; qy = my - ss * Ld[1]; qz = mz - ss * Ld[2]
        streak = 0.5 + 0.5 * (0.45 * np.sin(qy / 11.0 + 1.3 * np.sin(qz / 23.0)) + 0.35 * np.sin(qy / 4.7 + qz / 9.0 + 2.0) + 0.2 * np.sin(qz / 6.1 - qy / 31.0))
        dx, dy, dz = CAM[0] - mx, CAM[1] - my, CAM[2] - mz; dn = np.sqrt(dx * dx + dy * dy + dz * dz) + 1e-3
        cos = (dx * Ld[0] + dy * Ld[1] + dz * Ld[2]) / dn; g = 0.55
        acc += lit * (0.35 + 0.95 * streak ** 1.6) * (1 - g * g) / (1 + g * g - 2 * g * cos) ** 1.5
    seg = np.sqrt((vPX - CAM[0]) ** 2 + (vPY - CAM[1]) ** 2 + (vPZ - CAM[2]) ** 2)
    v = cv2.resize(cv2.GaussianBlur(acc / NS * seg / 700.0, (0, 0), 1.3), (OW, OH), interpolation=cv2.INTER_CUBIC)
    _vol_cache[key] = v; return v
rng = np.random.default_rng(5); ND = 1100
dust = np.stack([rng.uniform(-700, 520, ND), rng.uniform(5, 560, ND), rng.uniform(10, 520, ND)], 1)
dph = rng.uniform(0, 6.28, ND); dsz = rng.uniform(0.5, 1.5, ND)

# ───────────────────────── flashes y cámara ─────────────────────────
FLASH_T = sorted([b['t'] for b in bags] + list(C['flashes']['rafaga']))
def flash(t):
    v = 0.0
    for ft in FLASH_T:
        d = t - ft
        if 0 <= d < 0.2: v = max(v, math.exp(-d / 0.035))
    return v * C['flashes']['intensidad']
CA = C['camara']
def zoom(t): return 1.0 + (CA['zoom_max'] - 1) * float(sstep(CA['zoom_desde'], CA['zoom_hasta'], t))

# ───────────────────────── render de escena ─────────────────────────
def scene(t):
    """Devuelve fondo (lineal) y capa de bolsas (lineal + alfa), ya con zoom."""
    w = door_w(t); fl = flash(t)
    active = [t >= b['t'] for b in bags]
    op = w / DZW
    img = plate * (0.9 + 0.1 * op)          # el cuarto se aclara un poco al entrar la luz
    if w > 0.5:
        dl = door_lit(PX, PY, PZ, w) * isfloor * (1 + 0.8 * floor_hp) * (1 - 0.85 * bag_shadow(active)) * DOOR_FALL
        img += alb * (dl * PU['intensidad'] * 2.0)[..., None] * DOORC
    img += reflection(active)
    img *= (1 - 0.7 * contact(active))[..., None]
    if fl > 0:
        img += alb * (fl * 0.9 * np.minimum(F / ZC, 1.6))[..., None]
    if w > 0.5:
        nz = np.roll(cv2.resize(HAZE, (OW, OH), interpolation=cv2.INTER_CUBIC), int(t * 14), axis=1)
        img += (volume(w) * PU['neblina'] * 1.5 * (0.6 + 0.8 * nz))[..., None] * DOORC
        p = dust + np.stack([5 * np.sin(0.3 * t + dph), 3 * np.sin(0.25 * t + 2 * dph) + 2 * t, 4 * np.cos(0.33 * t + dph)], 1)
        lit = door_lit(p[:, 0], p[:, 1], p[:, 2], w, soft=0.06)
        zc = D - p[:, 2]; px = CX + F * p[:, 0] / zc; py = YH - F * (p[:, 1] - HC) / zc
        lay = np.zeros((OH, OW), np.float32)
        for i in np.nonzero(lit > 0.05)[0]:
            if 0 <= px[i] < OW and 0 <= py[i] < OH:
                cv2.circle(lay, (int(px[i]), int(py[i])), max(1, int(dsz[i] * F / zc[i])), float(lit[i] * (0.6 + 0.4 * math.sin(3 * t + 5 * dph[i]))), -1, cv2.LINE_AA)
        img += (cv2.GaussianBlur(lay, (0, 0), 0.7) * PU['polvo'])[..., None] * DOORC
    # bolsas
    bl = np.zeros((OH, OW, 3), np.float32); ba = np.zeros((OH, OW), np.float32)
    for b, on in zip(bags, active):
        if not on: continue
        col = b['rgb']
        if w > 0.5:
            dlv = float(door_lit(b['bx'] - b['hw'], BH * 0.45, BZ, w))
            col = col + (b['rim'] * dlv * PU['intensidad'] * 1.6)[..., None] * DOORC + b['rgb'] * dlv * PU['intensidad'] * 0.15 * DOORC
        if fl > 0: col = col + b['rgb'] * fl * 1.5
        dy = -8 if 0 <= t - b['t'] < 1.5 / FPS else 0          # golpecito stop-motion al aparecer
        y0, x0 = b['y0'] + dy, b['x0']
        ys0, ys1, xs0, xs1 = max(0, y0), min(OH, y0 + b['h']), max(0, x0), min(OW, x0 + b['w'])
        bl[ys0:ys1, xs0:xs1] = col[ys0 - y0:ys1 - y0, xs0 - x0:xs1 - x0]
        ba[ys0:ys1, xs0:xs1] = b['a'][ys0 - y0:ys1 - y0, xs0 - x0:xs1 - x0]
    z = zoom(t); M = np.float32([[z, 0, CX - z * CX], [0, z, CA['centro_y'] - z * CA['centro_y']]])
    warp = lambda a: cv2.warpAffine(a, M, (OW, OH), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    return warp(img), warp(bl), warp(ba), fl

def tone(x, fl=0.0):
    k = 0.78; y = np.where(x < k, x, k + (1 - k) * (1 - np.exp(-(x - k) / (1 - k))))
    s = to_srgb(y); hi = np.clip(s - 0.7, 0, None)
    return np.clip(s + cv2.GaussianBlur(hi, (0, 0), 18) * (0.25 + 0.35 * fl), 0, 1)

# ───────────────────────── cierre ─────────────────────────
FONTS = {'titulo': P(C['tipografia']['titulo']), 'fina': P(C['tipografia']['fina'])}
def text_layer(tx):
    lay = Image.new('L', (OW, OH), 0); d = ImageDraw.Draw(lay)
    fo = ImageFont.truetype(FONTS[tx['fuente']], tx['tamano'])
    if tx['fuente'] == 'fina': fo.set_variation_by_name(tx.get('peso', 'Regular'))
    s = tx['texto']; tr = tx.get('espaciado', 0.0) * tx['tamano']
    ws = [fo.getlength(c) for c in s]; tot = sum(ws) + tr * (len(s) - 1)
    if tot > OW - 80: print(f"AVISO: '{s}' mide {tot:.0f}px, se sale de los márgenes")
    x = (OW - tot) / 2
    for c, wc in zip(s, ws):
        d.text((x, tx['y']), c, font=fo, fill=255, anchor='ls'); x += wc + tr
    return np.asarray(lay).astype(np.float32) / 255
TEXTS = [(text_layer(tx), hex_bgr(tx['color']), tx['aparece']) for tx in C['textos']]
IMAGES = []
for im in C['imagenes']:
    a = cv2.imread(P(im['archivo']), cv2.IMREAD_UNCHANGED).astype(np.float32) / 255
    h = int(round(a.shape[0] * im['ancho'] / a.shape[1])); a = cv2.resize(a, (im['ancho'], h), interpolation=cv2.INTER_AREA)
    rgb, al = a[..., :3], a[..., 3]
    if im.get('oscuro_a_blanco'): rgb = np.where((rgb.mean(axis=2) < 0.3)[..., None], 0.97, rgb)
    IMAGES.append((rgb, al, int(OW / 2 - im['ancho'] / 2), im['y'], im['aparece']))
CI = C['cierre']; FADE = 0.35
def frame(t):
    img, bl, ba, fl = scene(t)
    k = float(sstep(CI['inicio'], CI['inicio'] + 0.6, t))
    if k > 0:
        img = cv2.GaussianBlur(img, (0, 0), 0.5 + CI['desenfoque'] * k)
        grad = np.clip(1.05 - (yy - 150) / 1300, 0.45, 1)[..., None]
        img = img * (1 - CI['oscurecer'] * k * grad)
        bl = bl * (1 - 0.34 * k)
    lin = bl * ba[..., None] + img * (1 - ba[..., None])
    y = tone(lin, fl)
    g = np.random.default_rng(int(t * FPS)).normal(0, 0.006, y.shape).astype(np.float32)
    y = np.clip(y + g, 0, 1)
    for L_, col, t0 in TEXTS:
        kk = float(sstep(t0, t0 + FADE, t))
        if kk <= 0: continue
        L_ = np.roll(L_, int(round((1 - kk) * 14)), axis=0)
        sh = cv2.GaussianBlur(L_, (0, 0), 7)[..., None]
        y = y * (1 - 0.45 * kk * sh)
        y = y * (1 - kk * L_[..., None]) + kk * L_[..., None] * col
    for rgb, al, x0, y0, t0 in IMAGES:
        kk = float(sstep(t0, t0 + FADE, t))
        if kk <= 0: continue
        s = 1.05 - 0.05 * kk; h, w = al.shape
        M = np.float32([[s, 0, x0 + w / 2 - s * w / 2], [0, s, y0 + h / 2 - s * h / 2]])
        A = cv2.warpAffine(al, M, (OW, OH)) * kk; R = cv2.warpAffine(rgb, M, (OW, OH))
        y = y * (1 - A[..., None]) + R * A[..., None]
    return (np.clip(y, 0, 1) * 255).astype(np.uint8)

# ───────────────────────── sonido ─────────────────────────
SR = 48000
def place(buf, snd, t, gain=1.0):
    i = int(t * SR); j = min(len(buf), i + len(snd))
    if 0 <= i < len(buf): buf[i:j] += snd[:j - i] * gain
def bp(x, lo, hi, order=2): return signal.sosfilt(signal.butter(order, [lo, hi], 'band', fs=SR, output='sos'), x)
def lp(x, fc, order=2): return signal.sosfilt(signal.butter(order, fc, 'low', fs=SR, output='sos'), x)
def env(n, a, d):
    t = np.arange(n) / SR; return (1 - np.exp(-t / max(a, 1e-4))) * np.exp(-t / d)
def shutter(r):
    n = int(0.12 * SR); s = np.zeros(n)
    for t0, g in ((0.0, 1.0), (0.048, 0.7)):
        m = int(0.012 * SR); c = bp(r.normal(0, 1, m), 2500, 9000) * env(m, 0.0002, 0.0025)
        body = np.sin(2 * np.pi * 950 * np.arange(m) / SR) * env(m, 0.0003, 0.004) * 0.4
        i = int(t0 * SR); s[i:i + m] += (c + body) * g
    return s
def thump(r):
    n = int(0.35 * SR); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * (85 * t - 30 * t * t / 0.35 * 0.5)) * env(n, 0.002, 0.11)
    s += lp(r.normal(0, 1, n), 600) * env(n, 0.0005, 0.02) * 0.6
    return s
def creak(r, dur):
    n = int(dur * SR); rate = 45 + 70 * np.abs(np.cumsum(r.normal(0, 0.02, n)) % 2 - 1) + 30 * np.sin(np.linspace(0, 5, n))
    ph = np.cumsum(rate / SR); imp = (np.diff(np.floor(ph), prepend=0) > 0).astype(float) * (0.5 + 0.5 * r.random(n))
    s = sum(bp(imp, fc * 0.93, fc * 1.07) * g for fc, g in ((620, 1.0), (1180, 0.8), (2300, 0.45), (3400, 0.2)))
    e = sstep(0, 0.08, np.arange(n) / SR) * (1 - sstep(dur - 0.3, dur, np.arange(n) / SR)) * (0.6 + 0.4 * np.sin(np.linspace(0, 9, n)) ** 2)
    return s * e
def latch(r):
    m = int(0.03 * SR); return bp(r.normal(0, 1, m), 1500, 6000) * env(m, 0.0002, 0.004) + np.sin(2 * np.pi * 140 * np.arange(m) / SR) * env(m, 0.001, 0.012) * 0.5
def music(dur, start):
    n = int((dur - start) * SR); t = np.arange(n) / SR
    notes = [110.0, 164.81, 196.0, 246.94, 261.63, 329.63]   # La menor con 9na
    s = np.zeros(n)
    for f0 in notes:
        for det in (-0.12, 0.0, 0.11):
            ph = 2 * np.pi * f0 * (1 + det / 100) * t
            s += signal.sawtooth(ph) * (0.5 if f0 > 200 else 0.8)
    s = lp(s, 1400, 2) * sstep(0, 1.4, t) * (1 - sstep(len(t) / SR - 0.6, len(t) / SR, t))
    sub = np.sin(2 * np.pi * 55 * t) * env(n, 0.005, 0.9) * 1.2                  # golpe grave al entrar
    return (s / 12 + sub * 0.5)
def soundtrack():
    S_ = C['sonido']; r = np.random.default_rng(3); n = int(DUR * SR)
    buf = np.zeros(n)
    room = lp(r.normal(0, 1, n), 400) * 0.012
    air = bp(r.normal(0, 1, n), 250, 2500) * 0.02 * np.array([door_w(i / SR) / DZW for i in range(0, n, 480)]).repeat(480)[:n]
    buf += room + air
    if S_.get('puerta'):
        place(buf, latch(r), PU['inicio'] + 0.02, 0.6)
        place(buf, creak(r, PU['apertura'] * 0.85), PU['inicio'] + 0.12, 0.35)
    if S_.get('disparos'):
        for b in bags:
            place(buf, shutter(r), b['t'] - 0.01, 0.55); place(buf, thump(r), b['t'], 0.9)
        for ft in C['flashes']['rafaga']:
            place(buf, shutter(r), ft - 0.01, 0.45)
    if S_.get('musica'):
        place(buf, music(DUR, CI['inicio']), CI['inicio'], S_.get('volumen_musica', 0.5))
    buf = buf / (np.abs(buf).max() + 1e-9) * 0.89
    fade = np.ones(n); fade[-int(0.25 * SR):] = np.linspace(1, 0, int(0.25 * SR)); buf *= fade
    return buf

# ───────────────────────── main ─────────────────────────
if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--test'); a = ap.parse_args()
    os.makedirs(P('salida'), exist_ok=True)
    if a.test:
        for t in [float(x) for x in a.test.split(',')]:
            cv2.imwrite(P(f'salida/prueba_{t:05.2f}.png'), frame(t))
        raise SystemExit
    vid = P(C['salida']['video']); tmp = vid + '.tmp.mp4'
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{OW}x{OH}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', tmp], stdin=subprocess.PIPE)
    N = int(round(FPS * DUR)); last = None
    for i in range(N):
        last = frame(i / FPS); p.stdin.write(last.tobytes())
    p.stdin.close(); p.wait()
    cv2.imwrite(P(C['salida']['cuadro_final']), last)
    if C['sonido'].get('activado'):
        wav = vid + '.wav'; s = (soundtrack() * 32767).astype(np.int16)
        with wave.open(wav, 'wb') as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(s.tobytes())
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-i', wav, '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
                        '-shortest', '-movflags', '+faststart', vid], check=True)
        os.remove(wav)
    else:
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-c', 'copy', '-movflags', '+faststart', vid], check=True)
    os.remove(tmp)
    print('listo:', vid)
