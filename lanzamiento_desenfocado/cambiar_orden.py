"""Cambia el orden de las bolsas: ST 9742 RG a la izquierda y ST 9820 CL al centro.
Las bolsas son iguales salvo el bloque impreso debajo de "SEMILLA MAÍZ HÍBRIDO"
(familia, número y logo de Viptera3), así que se intercambia ese bloque.
Como fuente se usan los bloques limpios de la foto 4 (sin errores de la IA).
"""
import os, numpy as np, cv2
H = os.path.dirname(os.path.abspath(__file__))
F = lambda n: os.path.join(H, 'fotos', n)
R_ALTO = 0.66      # alto del bloque, relativo al ancho de "SEMILLA MAÍZ HÍBRIDO"
GAP = 0.02

def semilla(img, rough):
    """Caja de la línea azul "SEMILLA MAÍZ HÍBRIDO" dentro de una zona aproximada."""
    x0, y0, x1, y1 = rough; r = img[y0:y1, x0:x1].astype(np.int32)
    b, g, rr = r[..., 0], r[..., 1], r[..., 2]
    blue = ((b > rr + 30) & (b > g + 12) & (b > 55)).astype(np.uint8)
    blue = cv2.morphologyEx(blue, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
    ys, xs = np.nonzero(blue)
    return x0 + xs.min(), y0 + ys.min(), x0 + xs.max() + 1, y0 + ys.max() + 1

def bloque(spec):
    """spec = (x izquierda, x derecha, y base) de la línea "SEMILLA MAÍZ HÍBRIDO"."""
    sx0, sx1, sy1 = spec; W = sx1 - sx0
    return (int(sx0 - GAP * W), int(sy1 + GAP * W), int(sx1 + GAP * W), int(sy1 + R_ALTO * W))

def ink(img, box, pad=14):
    x0, y0, x1, y1 = box
    R = img[y0 - pad:y1 + pad, x0 - pad:x1 + pad].astype(np.float32) / 255
    g = R.mean(axis=2)
    paper = cv2.GaussianBlur(cv2.dilate(g, np.ones((15, 15), np.uint8)), (0, 0), 4)
    a = np.clip((paper - g) / np.maximum(paper, 1e-3) / 0.45, 0, 1)
    return R[pad:-pad, pad:-pad], a[pad:-pad, pad:-pad]

def pegar(img, dst_box, src_alpha, seed):
    x0, y0, x1, y1 = dst_box
    r, a = ink(img, dst_box)
    rr = r.astype(np.float32); blue = (rr[..., 0] > rr[..., 2] + 0.10)          # no tocar la franja azul
    tinta = (a > 0.16) & ~blue
    col = np.median(r[tinta & (a > 0.6)], axis=0) if (tinta & (a > 0.6)).sum() > 20 else np.array([0.12, 0.13, 0.16], np.float32)
    m = cv2.dilate(tinta.astype(np.uint8), np.ones((7, 7), np.uint8))
    # borrar solo la tinta vieja (inpaint) y devolverle el grano al papel
    pad = 20; X0, Y0, X1, Y1 = x0 - pad, y0 - pad, x1 + pad, y1 + pad
    reg8 = img[Y0:Y1, X0:X1].copy()
    M = np.zeros(reg8.shape[:2], np.uint8); M[pad:-pad, pad:-pad] = m
    rg = reg8.astype(np.int32); azul = ((rg[..., 0] > rg[..., 2] + 25) & (rg[..., 0] > 50)).astype(np.uint8)
    azul = cv2.dilate(azul, np.ones((5, 5), np.uint8))          # el texto azul no se usa como fuente del relleno
    fill = cv2.inpaint(reg8, np.maximum(M, azul) * 255, 7, cv2.INPAINT_TELEA).astype(np.float32) / 255
    fill = cv2.GaussianBlur(fill, (0, 0), 1.5) + np.random.default_rng(seed).normal(0, 0.010, fill.shape).astype(np.float32)
    Ms = cv2.GaussianBlur(M.astype(np.float32), (0, 0), 1.2)[..., None]
    reg = reg8.astype(np.float32) / 255 * (1 - Ms) + fill * Ms
    A = cv2.resize(src_alpha, (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA)
    A = np.clip((A - 0.28) / 0.5, 0, 1)[..., None]
    reg[pad:-pad, pad:-pad] = reg[pad:-pad, pad:-pad] * (1 - A) + col * A
    out = img.copy(); out[Y0:Y1, X0:X1] = (np.clip(reg, 0, 1) * 255).astype(np.uint8)
    return out

def suavizar_reflejo(img, rect):
    """El piso refleja el número viejo espejado: lo desenfocamos para que no se lea
    (se conservan las vetas finas del piso)."""
    x0, y0, x1, y1 = rect; p = 24
    X0, Y0, X1, Y1 = max(0, x0 - p), max(0, y0 - p), min(img.shape[1], x1 + p), min(img.shape[0], y1 + p)
    R = img[Y0:Y1, X0:X1].astype(np.float32) / 255
    base = cv2.GaussianBlur(R, (0, 0), sigmaX=7, sigmaY=11)
    fino = R - cv2.GaussianBlur(R, (0, 0), 1.0)
    M = np.zeros(R.shape[:2], np.float32); M[y0 - Y0:y1 - Y0, x0 - X0:x1 - X0] = 1
    M = cv2.GaussianBlur(M, (0, 0), 9)[..., None]
    out = img.copy(); out[Y0:Y1, X0:X1] = (np.clip(R * (1 - M) + (base + fino) * M, 0, 1) * 255).astype(np.uint8)
    return out

# zonas del piso donde se lee el reflejo del número de la bolsa (izquierda, centro)
REFLEJOS = {
    '2_llegan.png':            [(205, 1100, 300, 1150), (395, 1170, 500, 1240)],
    '3_en_fila_corregida.png': [(235, 1190, 370, 1240), (415, 1240, 540, 1292)],
    '4_sesion_corregida.png':  [(175, 1262, 335, 1360), (400, 1262, 565, 1360)],
}

# línea "SEMILLA MAÍZ HÍBRIDO" de cada bolsa: (x izq, x der, y base) — izquierda, centro
SPEC = {
    '2_llegan.png':            ((211, 303, 965), (390, 506, 1025)),
    '3_en_fila_corregida.png': ((223, 346, 1027), (408, 562, 1063)),
    '4_sesion_corregida.png':  ((181, 326, 1008), (408, 557, 1008)),
}

if __name__ == '__main__':
    ref = cv2.imread(F('4_sesion_corregida.png'))
    l_ref, c_ref = SPEC['4_sesion_corregida.png']
    alfa_9820 = ink(ref, bloque(l_ref))[1]      # LOS PETISOS / ST 9820 CL / Viptera3
    alfa_9742 = ink(ref, bloque(c_ref))[1]      # LOS CORTOS / ST 9742 RG
    for n, (sl, sc) in SPEC.items():
        orig = cv2.imread(F(n)); print(n)
        im = pegar(orig, bloque(sl), alfa_9742, 1)
        im = pegar(im, bloque(sc), alfa_9820, 2)
        for rect in REFLEJOS[n]: im = suavizar_reflejo(im, rect)
        cv2.imwrite(F(n.replace('.png', '').replace('_corregida', '') + '_orden.png'), im)
    print('listo')
