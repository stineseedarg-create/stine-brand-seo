"""Prepara los cuadros de inicio para Higgsfield:
   - corrige "LOS CORTOS" -> "LOS PETISOS" en la bolsa ST 9820 CL (la IA puso la familia equivocada)
   - separa las 4 tomas de la grilla y las lleva a 1080x1920
"""
import os, numpy as np, cv2
H = os.path.dirname(os.path.abspath(__file__))
R = lambda n: os.path.join(H, 'referencias', n)
O = lambda n: os.path.join(H, 'cuadros_inicio', n)

def ink(img, box, pad=14):
    x0, y0, x1, y1 = box
    Rg = img[y0 - pad:y1 + pad, x0 - pad:x1 + pad].astype(np.float32) / 255
    g = Rg.mean(axis=2)
    paper = cv2.GaussianBlur(cv2.dilate(g, np.ones((11, 11), np.uint8)), (0, 0), 3)
    a = np.clip((paper - g) / np.maximum(paper, 1e-3) / 0.45, 0, 1)
    return Rg[pad:-pad, pad:-pad], a[pad:-pad, pad:-pad]

def reemplazar(img, dst_box, src_alpha, seed):
    x0, y0, x1, y1 = dst_box
    r, a = ink(img, dst_box)
    rr = r; blue = rr[..., 0] > rr[..., 2] + 0.10
    tinta = (a > 0.16) & ~blue
    col = np.median(r[tinta & (a > 0.6)], axis=0)
    m = cv2.dilate(tinta.astype(np.uint8), np.ones((5, 5), np.uint8))
    pad = 16; X0, Y0, X1, Y1 = x0 - pad, y0 - pad, x1 + pad, y1 + pad
    reg8 = img[Y0:Y1, X0:X1].copy()
    M = np.zeros(reg8.shape[:2], np.uint8); M[pad:-pad, pad:-pad] = m
    rg = reg8.astype(np.int32); azul = cv2.dilate(((rg[..., 0] > rg[..., 2] + 25) & (rg[..., 0] > 50)).astype(np.uint8), np.ones((5, 5), np.uint8))
    fill = cv2.inpaint(reg8, np.maximum(M, azul) * 255, 6, cv2.INPAINT_TELEA).astype(np.float32) / 255
    fill = cv2.GaussianBlur(fill, (0, 0), 1.2) + np.random.default_rng(seed).normal(0, 0.010, fill.shape).astype(np.float32)
    Ms = cv2.GaussianBlur(M.astype(np.float32), (0, 0), 1.0)[..., None]
    reg = reg8.astype(np.float32) / 255 * (1 - Ms) + fill * Ms
    # texto nuevo, ajustado al alto/ancho del texto viejo
    ys, xs = np.nonzero(a > 0.35); tx0, tx1, ty0, ty1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    A = cv2.resize(src_alpha, (tx1 - tx0, ty1 - ty0), interpolation=cv2.INTER_AREA)
    A = np.clip(A * 1.15, 0, 1)[..., None]
    sl = (slice(pad + ty0, pad + ty1), slice(pad + tx0, pad + tx1))
    reg[sl] = reg[sl] * (1 - A) + col * A
    out = img.copy(); out[Y0:Y1, X0:X1] = (np.clip(reg, 0, 1) * 255).astype(np.uint8)
    return out

if __name__ == '__main__':
    # "LOS PETISOS" en una tipografía de marcador parecida a la de la bolsa, renderizado nítido
    from PIL import Image, ImageDraw, ImageFont
    f = ImageFont.truetype(os.path.join(H, 'fuentes', 'PermanentMarker.ttf'), 120)
    lay = Image.new('L', (1400, 220), 0); ImageDraw.Draw(lay).text((20, 30), 'LOS PETISOS', font=f, fill=255)
    sa = np.asarray(lay).astype(np.float32) / 255
    sh = 0.22; hh, ww = sa.shape                      # inclinación como la letra de la bolsa
    sa = cv2.warpAffine(sa, np.float32([[1, -sh, sh * hh], [0, 1, 0]]), (int(ww + sh * hh) + 2, hh))
    ys, xs = np.nonzero(sa > 0.35); sa = sa[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    im = cv2.imread(R('bolsa_9820_4_tomas.png'))
    im = reemplazar(im, (184, 549, 293, 570), sa, 1)     # toma 1 (frente)
    im = reemplazar(im, (759, 546, 826, 564), sa, 2)     # toma 2 (3/4)
    cv2.imwrite(R('bolsa_9820_4_tomas_corregida.png'), im)
    paneles = {'02_9820_frente': (0, 0, 472, 834), '03_9820_tres_cuartos': (476, 0, 941, 834),
               '04_9820_detalle_cierre': (0, 837, 472, 1672), '05_9820_detalle_lateral': (476, 837, 941, 1672)}
    for n, (x0, y0, x1, y1) in paneles.items():
        p = im[y0:y1, x0:x1]
        p = cv2.resize(p, (1080, 1920), interpolation=cv2.INTER_LANCZOS4)
        cv2.imwrite(O(n + '.png'), p)
    b = cv2.imread(R('bolsa_9734.png'))
    cv2.imwrite(O('01_9734_heroe.png'), cv2.resize(b, (1080, 1920), interpolation=cv2.INTER_LANCZOS4))
    print('listo')
