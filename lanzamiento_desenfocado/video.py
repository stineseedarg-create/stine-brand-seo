"""Lanzamiento Green Friday Stine – estilo desenfocado (como la referencia de EMESTUDIOS).
Todo se controla desde config.toml.
    python3 video.py                 video + cuadro final
    python3 video.py --test 1.0,5.0  cuadros de prueba en salida/prueba_*.png
    python3 video.py --sin-texto     versión sin sobreimpresos (archivos con sufijo -sin-texto)
"""
import argparse, math, os, subprocess, tomllib, wave
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
def P(p): return p if os.path.isabs(p) else os.path.join(HERE, p)
with open(P('config.toml'), 'rb') as fh:
    C = tomllib.load(fh)
OW, OH, FPS = C['salida']['ancho'], C['salida']['alto'], C['salida']['fps']
TOMAS = C['tomas']; DUR = TOMAS[-1]['fin']; E = C['efecto']

def sstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0 + 1e-9), 0, 1); return t * t * (3 - 2 * t)
def ease(x): x = min(max(x, 0.0), 1.0); return x * x * (3 - 2 * x)
def hex_bgr(h):
    h = h.lstrip('#'); return np.array([int(h[4:6], 16), int(h[2:4], 16), int(h[0:2], 16)], np.float32) / 255

FOTOS = {}
def foto(p):
    if p not in FOTOS: FOTOS[p] = (cv2.imread(P(p)).astype(np.float32) / 255) ** 2.2
    return FOTOS[p]

def disc(r):
    r = max(1, int(round(r))); k = np.zeros((2 * r + 1, 2 * r + 1), np.float32)
    cv2.circle(k, (r, r), r, 1.0, -1, cv2.LINE_AA); return k / k.sum()
def lens_blur(img, r):
    """Desenfoque tipo lente (bokeh): las luces se abren en discos."""
    if r < 0.8: return img
    s = 0.5; sm = cv2.resize(img, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
    sm = cv2.filter2D(sm, -1, disc(r * s), borderType=cv2.BORDER_REFLECT)
    return cv2.resize(sm, (OW, OH), interpolation=cv2.INTER_LINEAR)
def motion_blur(img, L, direction=1):
    if L < 2: return img
    L = int(L); k = np.zeros((1, L), np.float32); k[0] = np.linspace(0.4, 1.0, L)[::direction]; k /= k.sum()
    s = 0.5; sm = cv2.resize(img, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
    sm = cv2.filter2D(sm, -1, cv2.resize(k, (max(2, int(L * s)), 1)) / cv2.resize(k, (max(2, int(L * s)), 1)).sum(), borderType=cv2.BORDER_REFLECT)
    return cv2.resize(sm, (OW, OH), interpolation=cv2.INTER_LINEAR)

def toma_en(t):
    for i, s in enumerate(TOMAS):
        if s['inicio'] <= t < s['fin']: return i, s
    return len(TOMAS) - 1, TOMAS[-1]

rng_shake = np.random.default_rng(4)
SHK = np.cumsum(rng_shake.normal(0, 1, (int(DUR * FPS) + 10, 2)), axis=0)
SHK = cv2.GaussianBlur(SHK.astype(np.float32), (1, 0), sigmaX=0.1, sigmaY=6)
SHK = (SHK - SHK.mean(axis=0)) / (SHK.std(axis=0) + 1e-6)

def plano(s, t):
    src = foto(s['foto']); h, w = src.shape[:2]
    u = (t - s['inicio']) / (s['fin'] - s['inicio']); k = ease(u)
    z = s['zoom'][0] + (s['zoom'][1] - s['zoom'][0]) * k
    cx = s['centro'][0][0] + (s['centro'][1][0] - s['centro'][0][0]) * k
    cy = s['centro'][0][1] + (s['centro'][1][1] - s['centro'][0][1]) * k
    sc = max(OW / w, OH / h) * z
    fi = min(len(SHK) - 1, int(t * FPS)); jx, jy = SHK[fi] * E['temblor']
    # mantener el encuadre dentro de la foto
    half_w, half_h = OW / 2 / sc, OH / 2 / sc
    cx = min(max(cx, half_w), w - half_w); cy = min(max(cy, half_h), h - half_h)
    M = np.float32([[sc, 0, OW / 2 - sc * cx + jx], [0, sc, OH / 2 - sc * cy + jy]])
    return cv2.warpAffine(src, M, (OW, OH), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)

LEAK = hex_bgr(E['luz_color'])
yy, xx = np.mgrid[0:OH, 0:OW].astype(np.float32)
VIG = 1 - E['vineta'] * np.clip(((xx - OW / 2) / (OW * 0.75)) ** 2 + ((yy - OH / 2) / (OH * 0.72)) ** 2, 0, 1)
LEAKMAP = np.clip(1.2 - (xx / OW) * 0.9 - np.abs(yy / OH - 0.4) * 0.8, 0, 1) ** 1.5

def frame_lin(t):
    i, s = toma_en(t); dur = s['fin'] - s['inicio']; u = t - s['inicio']
    img = plano(s, t)
    blur = 0.0; mb = 0.0; mdir = 1
    if s.get('entrada') == 'enfoque':
        blur = max(blur, E['desenfoque_max'] * (1 - float(sstep(0, E['duracion_foco'], u))) ** 1.4)
    if s.get('entrada') == 'barrido':
        mb = max(mb, E['barrido_px'] * (1 - float(sstep(0, 0.16, u)))); mdir = -1
    so = s.get('salida', 'corte'); ko = float(sstep(dur - E['duracion_salida'], dur, u))
    if so == 'desenfoque': blur = max(blur, E['desenfoque_max'] * ko ** 1.3)
    if so == 'barrido': mb = max(mb, E['barrido_px'] * float(sstep(dur - 0.16, dur, u)))
    if so == 'luz': blur = max(blur, E['desenfoque_max'] * 0.5 * ko)
    img = lens_blur(img, blur)
    img = motion_blur(img, mb, mdir)
    # flashes de la sesión
    fl = 0.0
    for ft in s.get('flashes', []):
        d = t - ft
        if 0 <= d < 0.22: fl = max(fl, math.exp(-d / 0.04))
    img = img * (1 + 1.4 * fl) + 0.04 * fl
    # destello de luz cálida en el corte
    lk = 0.0
    if so == 'luz': lk = max(lk, float(sstep(dur - 0.22, dur, u)))
    if i > 0 and TOMAS[i - 1].get('salida') == 'luz': lk = max(lk, 1 - float(sstep(0, 0.25, u)))
    if lk > 0:
        img = 1 - (1 - img) * (1 - (lk * (0.35 + 0.75 * LEAKMAP))[..., None] * LEAK)
    return img

def film(img, t):
    hi = np.clip(img - 0.5, 0, None)
    img = img + cv2.GaussianBlur(hi, (0, 0), 22) * E['halo'] * np.array([0.7, 0.85, 1.0], np.float32)
    img = img * VIG[..., None]
    y = np.clip(img, 0, None); y = y / (1 + 0.25 * y)                 # hombro suave
    y = np.clip(y * 1.12, 0, 1) ** (1 / 2.2)
    g = np.random.default_rng(int(t * FPS) + 7).normal(0, 1, (OH // 2, OW // 2)).astype(np.float32)
    g = cv2.resize(cv2.GaussianBlur(g, (0, 0), 0.6), (OW, OH), interpolation=cv2.INTER_LINEAR)
    return np.clip(y + g[..., None] * E['grano'] * (0.6 + 0.4 * (1 - y)), 0, 1)

# texto fijo (como la referencia)
TX = C['texto']
def text_layer():
    lay = Image.new('L', (OW, OH), 0); d = ImageDraw.Draw(lay)
    m = TX['margen']; avail = OW - 2 * m
    size = 200
    while True:
        f = ImageFont.truetype(P(TX['fuente_titulo']), size); bb = d.textbbox((0, 0), TX['titulo'], font=f)
        if bb[2] - bb[0] <= avail or size < 20: break
        size -= 2
    bb = d.textbbox((0, 0), TX['titulo'], font=f)
    d.text((m - bb[0] + (avail - (bb[2] - bb[0])) / 2, TX['y_titulo']), TX['titulo'], font=f, fill=255, anchor='ls')
    fc = ImageFont.truetype(P(TX['fuente_chica']), TX['tamano_chico']); yb = TX['y_titulo'] + int(TX['tamano_chico'] * 1.35)
    d.text((m, yb), TX['izquierda'], font=fc, fill=255, anchor='ls')
    d.text((OW - m, yb), TX['derecha'], font=fc, fill=255, anchor='rs')
    return np.asarray(lay).astype(np.float32) / 255
TL = text_layer(); TCOL = hex_bgr(TX['color'])
TSH = cv2.GaussianBlur(TL, (0, 0), 10)

SIN_TEXTO = False
def frame(t):
    y = film(frame_lin(t), t)
    k = 0.0 if SIN_TEXTO else float(sstep(TX['aparece'], TX['aparece'] + 0.3, t))
    if k > 0:
        y = y * (1 - 0.30 * k * TSH[..., None])
        y = y * (1 - k * TL[..., None]) + k * TL[..., None] * TCOL
    return (np.clip(y, 0, 1) * 255).astype(np.uint8)

def soundtrack():
    from scipy import signal
    SR = 48000; n = int(DUR * SR); buf = np.zeros(n); r = np.random.default_rng(3)
    def bp(x, lo, hi): return signal.sosfilt(signal.butter(2, [lo, hi], 'band', fs=SR, output='sos'), x)
    for s in TOMAS:
        for ft in s.get('flashes', []):
            for t0, g in ((0.0, 1.0), (0.048, 0.7)):
                m = int(0.012 * SR); c = bp(r.normal(0, 1, m), 2500, 9000) * np.exp(-np.arange(m) / SR / 0.0025)
                i = int((ft + t0) * SR); buf[i:i + m] += c * g
    return buf / (np.abs(buf).max() + 1e-9) * 0.8, SR

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--test'); ap.add_argument('--sin-texto', action='store_true'); a = ap.parse_args()
    os.makedirs(P('salida'), exist_ok=True)
    SIN_TEXTO = a.sin_texto
    suf = '-sin-texto' if SIN_TEXTO else ''
    C['salida']['video'] = C['salida']['video'].replace('.mp4', suf + '.mp4'); C['salida']['cuadro_final'] = C['salida']['cuadro_final'].replace('.png', suf + '.png')
    if a.test:
        for t in [float(x) for x in a.test.split(',')]: cv2.imwrite(P(f'salida/prueba_{t:05.2f}.png'), frame(t))
        raise SystemExit
    vid = P(C['salida']['video']); tmp = vid + '.tmp.mp4'
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{OW}x{OH}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p', tmp], stdin=subprocess.PIPE)
    last = None
    for i in range(int(round(FPS * DUR))):
        last = frame(i / FPS); p.stdin.write(last.tobytes())
    p.stdin.close(); p.wait()
    cv2.imwrite(P(C['salida']['cuadro_final']), last)
    if C['sonido'].get('disparos'):
        buf, SR = soundtrack(); wav = vid + '.wav'
        with wave.open(wav, 'wb') as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((buf * 32767).astype(np.int16).tobytes())
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-i', wav, '-c:v', 'copy', '-c:a', 'aac', '-shortest', '-movflags', '+faststart', vid], check=True)
        os.remove(wav)
    else:
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-c', 'copy', '-movflags', '+faststart', vid], check=True)
    os.remove(tmp); print('listo:', vid)
