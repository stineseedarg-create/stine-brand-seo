"""Crea la foto héroe de la ST 9742 RG a partir de la de la ST 9734 (misma familia: LOS CORTOS).
Cambia el número del frente y del lateral, y saca el logo de Agrisure Viptera3 (la 9742 RG no lo lleva)."""
import os, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
H = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(H, '..', 'video_producto_higgsfield', 'referencias', 'bolsa_9734.png')
FONT = os.path.join(H, 'fuentes', 'LeagueGothic.ttf')

def borrar(img, box, oscuro=True, umbral=0.16, dil=7, seed=0):
    x0, y0, x1, y1 = box; pad = 16
    R = img[y0 - pad:y1 + pad, x0 - pad:x1 + pad].astype(np.float32) / 255
    g = R.mean(axis=2)
    if oscuro:
        ref = cv2.GaussianBlur(cv2.dilate(g, np.ones((21, 21), np.uint8)), (0, 0), 4); a = (ref - g) / np.maximum(ref, 1e-3) / 0.45
    else:
        ref = cv2.GaussianBlur(cv2.erode(g, np.ones((11, 11), np.uint8)), (0, 0), 3); a = (g - ref) / 0.35
    m = np.zeros(g.shape, np.uint8); inner = (slice(pad, -pad), slice(pad, -pad))
    m[inner] = (a[inner] > umbral).astype(np.uint8)
    m = cv2.dilate(m, np.ones((dil, dil), np.uint8))
    reg8 = img[y0 - pad:y1 + pad, x0 - pad:x1 + pad].copy()
    fill = cv2.inpaint(reg8, m * 255, 9, cv2.INPAINT_TELEA).astype(np.float32) / 255
    # devolver textura del papel: high-pass de los alrededores
    hp = R - cv2.GaussianBlur(R, (0, 0), 2.0)
    hp_fill = cv2.inpaint(((np.clip(hp * 4 + 0.5, 0, 1)) * 255).astype(np.uint8), m * 255, 9, cv2.INPAINT_NS).astype(np.float32) / 255
    fill = fill + (hp_fill - 0.5) / 4 * 0.0 + np.random.default_rng(seed).normal(0, 0.012, fill.shape).astype(np.float32)
    Ms = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 1.2)[..., None]
    out = img.copy(); out[y0 - pad:y1 + pad, x0 - pad:x1 + pad] = (np.clip(R * (1 - Ms) + fill * Ms, 0, 1) * 255).astype(np.uint8)
    return out

def texto(img, txt, cx, y_top, alto, color, rot=0.0, ancho_max=None, estirar=1.0, textura=True):
    f = ImageFont.truetype(FONT, 400)
    lay = Image.new('L', (3000, 600), 0); ImageDraw.Draw(lay).text((50, 50), txt, font=f, fill=255)
    a = np.asarray(lay).astype(np.float32) / 255; ys, xs = np.nonzero(a > 0.3); a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    w = int(round(a.shape[1] * alto / a.shape[0] * estirar))
    if ancho_max and w > ancho_max: w = ancho_max
    a = cv2.resize(a, (w, alto), interpolation=cv2.INTER_AREA)
    if rot:
        M = cv2.getRotationMatrix2D((w / 2, alto / 2), rot, 1.0); a = cv2.warpAffine(a, M, (w, alto))
    a = cv2.GaussianBlur(a, (0, 0), 0.5)
    x0 = int(round(cx - w / 2)); out = img.astype(np.float32) / 255
    reg = out[y_top:y_top + alto, x0:x0 + w]
    col = np.array(color, np.float32)[None, None, :]
    if textura:   # la tinta toma la textura del papel (pliegues y brillo)
        g = reg.mean(axis=2, keepdims=True); col = col * (0.92 + 0.16 * g / max(g.mean(), 1e-3))
    out[y_top:y_top + alto, x0:x0 + w] = reg * (1 - a[..., None]) + col * a[..., None]
    return (np.clip(out, 0, 1) * 255).astype(np.uint8)

if __name__ == '__main__':
    im = cv2.imread(SRC)
    # tinta del número original (para usar el mismo color)
    r = im[1090:1165, 452:648].astype(np.float32) / 255; g = r.mean(axis=2)
    tinta = np.median(r[g < np.percentile(g, 12)], axis=0)
    im = borrar(im, (444, 1080, 656, 1176), seed=1)            # "ST 9734"
    im = borrar(im, (440, 1188, 660, 1232), seed=2)            # Agrisure Viptera3
    im = texto(im, 'ST 9742 RG', 548, 1088, 81, tinta * 0.85, ancho_max=262)   # mismo alto que el número original, ancho de la etiqueta
    # lateral azul: número en blanco
    lat = im[1229:1255, 262:306].astype(np.float32) / 255; blanco = np.median(lat[lat.mean(axis=2) > np.percentile(lat.mean(axis=2), 85)], axis=0)
    im = borrar(im, (258, 1224, 312, 1259), oscuro=False, umbral=0.25, dil=5, seed=3)
    im = texto(im, 'ST 9742 RG', 291, 1228, 26, blanco, rot=-4, ancho_max=64, textura=False)
    cv2.imwrite(os.path.join(H, 'cuadros', 'bolsa_9742_heroe_941.png'), im)
    cv2.imwrite(os.path.join(H, 'cuadros', '01_9742_heroe.png'), cv2.resize(im, (1080, 1920), interpolation=cv2.INTER_LANCZOS4))
    print('listo', tinta)
