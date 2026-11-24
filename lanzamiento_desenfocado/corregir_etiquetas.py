"""Corrige dos errores de texto que dejó la IA en las etiquetas:
   - 3_en_fila: la bolsa del centro dice "LOS COTTSOS" -> "LOS CORTOS" (copiado de la bolsa 9734 de la misma foto)
   - 4_sesion: la bolsa ST 9734 no tiene "LOS CORTOS" -> se copia de la bolsa central de la misma foto
"""
import os, sys, numpy as np, cv2
H = os.path.dirname(os.path.abspath(__file__))
def ink(img, box, pad=12):
    x0, y0, x1, y1 = box
    R = img[y0 - pad:y1 + pad, x0 - pad:x1 + pad].astype(np.float32) / 255
    g = R.mean(axis=2); paper = cv2.GaussianBlur(cv2.dilate(g, np.ones((7, 7), np.uint8)), (0, 0), 3)
    a = np.clip((paper - g) / np.maximum(paper, 1e-3) / 0.45, 0, 1)
    return R[pad:-pad, pad:-pad], a[pad:-pad, pad:-pad]
def bbox(a, thr=0.35):
    ys, xs = np.nonzero(a > thr); return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
def transplant(img, src_box, dst_box, erase_box=None, scale=None, dst_center=None):
    out = img.astype(np.float32) / 255
    if erase_box is not None:                     # borrar texto equivocado
        x0, y0, x1, y1 = erase_box; _, a = ink(img, erase_box)
        m = np.zeros(img.shape[:2], np.uint8); m[y0:y1, x0:x1] = (cv2.dilate((a > 0.15).astype(np.uint8), np.ones((5, 5), np.uint8)) * 255)
        out = cv2.inpaint((out * 255).astype(np.uint8), m, 5, cv2.INPAINT_TELEA).astype(np.float32) / 255
    r, a = ink(img, src_box); bx0, by0, bx1, by1 = bbox(a)
    a = a[by0:by1, bx0:bx1]; col = r[by0:by1, bx0:bx1]
    inkc = np.median(col[a > 0.7], axis=0)
    if scale is None:
        _, ad = ink(img, dst_box); dx0, dy0, dx1, dy1 = bbox(ad); scale = (dy1 - dy0) / (by1 - by0)
        dst_center = (dst_box[0] + (dx0 + dx1) / 2, dst_box[1] + (dy0 + dy1) / 2)
    a = cv2.resize(a, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    a = cv2.GaussianBlur(np.clip(a, 0, 1), (0, 0), 0.5)
    h, w = a.shape; x0 = int(round(dst_center[0] - w / 2)); y0 = int(round(dst_center[1] - h / 2))
    reg = out[y0:y0 + h, x0:x0 + w]
    out[y0:y0 + h, x0:x0 + w] = reg * (1 - a[..., None]) + inkc * a[..., None]
    return (np.clip(out, 0, 1) * 255).astype(np.uint8)

def fix(path_in, path_out, src_box, dst_center, scale, erase_box=None):
    im = cv2.imread(path_in)
    out = im.astype(np.float32) / 255
    if erase_box is not None:
        x0, y0, x1, y1 = erase_box; _, a = ink(im, erase_box)
        m = np.zeros(im.shape[:2], np.uint8); m[y0:y1, x0:x1] = cv2.dilate((a > 0.12).astype(np.uint8), np.ones((5, 5), np.uint8)) * 255
        out = cv2.inpaint(im, m, 4, cv2.INPAINT_TELEA).astype(np.float32) / 255
        # grano del papel para que no quede liso
        sm = np.zeros(im.shape[:2], np.float32); sm[y0:y1, x0:x1] = 1; sm = cv2.GaussianBlur(sm, (0, 0), 2)[..., None]
        out = out + np.random.default_rng(2).normal(0, 0.012, out.shape) * sm
    r, a = ink(im, src_box); bx0, by0, bx1, by1 = bbox(a, 0.3)
    a = a[by0:by1, bx0:bx1]; inkc = np.median(r[by0:by1, bx0:bx1][a > 0.6], axis=0)
    a = np.clip((a - 0.22) / 0.6, 0, 1)            # sin fondo: solo la tinta
    a = np.clip(cv2.resize(a, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC), 0, 1)
    h, w = a.shape; x0 = int(round(dst_center[0] - w / 2)); y0 = int(round(dst_center[1] - h / 2))
    reg = out[y0:y0 + h, x0:x0 + w]; out[y0:y0 + h, x0:x0 + w] = reg * (1 - a[..., None]) + inkc * a[..., None]
    cv2.imwrite(path_out, (np.clip(out, 0, 1) * 255).astype(np.uint8))

if __name__ == '__main__':
    F = lambda n: os.path.join(H, 'fotos', n)
    # 3_en_fila: borrar "LOS COTTSOS" de la bolsa central y escribir "LOS CORTOS" (de la bolsa ST 9734)
    fix(F('3_en_fila.png'), F('3_en_fila_corregida.png'), src_box=(657, 1023, 712, 1036),
        dst_center=(482.5, 1072.5), scale=1.16, erase_box=(446, 1065, 519, 1081))
    # 4_sesion: agregar "LOS CORTOS" a la bolsa ST 9734 (copiado de la bolsa central)
    fix(F('4_sesion.png'), F('4_sesion_corregida.png'), src_box=(447, 1013, 512, 1027),
        dst_center=(705, 1020), scale=1.0)
    print('listo')
