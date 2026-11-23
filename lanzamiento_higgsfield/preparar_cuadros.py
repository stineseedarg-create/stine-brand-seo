"""Arma los cuadros de inicio/fin para Higgsfield a partir de las tomas del set:
   - B: vista frontal + 3 cruces de cinta en perspectiva
   - C: igual que B + las 3 bolsas reales (etiquetas exactas) apoyadas en las cruces
   - referencias de cada bolsa sobre fondo neutro
"""
import os, math, numpy as np, cv2
H = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(H, 'cuadros_para_higgsfield'); os.makedirs(OUT, exist_ok=True)
BAGS = os.path.join(H, '..', 'lanzamiento', 'assets')

im = cv2.imread(os.path.join(H, 'tomas_originales', '03_Vista_frontal_del_set.jpg')).astype(np.float32) / 255
OH, OW = im.shape[:2]
lin = im ** 2.2
YW, YH = 1170.0, 925.0           # base de la pared y horizonte (altura de cámara ~1,5 m)
HC = YW - YH; F = 1000.0; D = F; CX = OW / 2
PXM = HC / 1.5                    # px por metro sobre la pared
yy, xx = np.mgrid[0:OH, 0:OW].astype(np.float32)
fl = yy > YW
ZC = np.where(fl, F * HC / np.maximum(yy - YH, 1e-3), D)
PX = (xx - CX) * ZC / F; PZ = np.where(fl, D - ZC, 0.0)

BASE_Y = 1700.0                   # base de las bolsas / centro de las cruces
zc_b = F * HC / (BASE_Y - YH); BZ = D - zc_b; MAG = F / zc_b
XS = [CX - 300, CX, CX + 300]     # izquierda, centro, derecha (en pantalla)

# cruces de cinta (X), brazos de 0,30 m, cinta de 5 cm
arm, th = 0.16 * PXM, 0.022 * PXM
tape = np.zeros((OH, OW), np.float32)
for x in XS:
    bx = (x - CX) / MAG
    a1 = ((PX - bx) + (PZ - BZ)) / math.sqrt(2); a2 = ((PX - bx) - (PZ - BZ)) / math.sqrt(2)
    m = fl & (((np.abs(a1) < th) & (np.abs(a2) < arm)) | ((np.abs(a2) < th) & (np.abs(a1) < arm)))
    tape = np.maximum(tape, m.astype(np.float32))
tape = cv2.GaussianBlur(tape, (0, 0), 0.8)
lum = lin.mean(axis=2)
lvl = np.clip(cv2.GaussianBlur(lum, (0, 0), 25) * 2.0 + 0.03, 0, 0.6)
grain = 0.92 + 0.08 * np.random.default_rng(1).random((OH, OW)).astype(np.float32)
B = lin * (1 - tape[..., None]) + (lvl * grain * tape)[..., None] * np.array([0.93, 0.97, 1.0], np.float32)
def save(name, a): cv2.imwrite(os.path.join(OUT, name), (np.clip(a, 0, 1) ** (1 / 2.2) * 255).astype(np.uint8))
save('B_vista_frontal_con_cruces.png', B)

# bolsas reales sobre las cruces
C = B.copy(); sh = np.zeros((OH, OW), np.float32)
bag_h = int(round(0.80 * PXM * MAG))      # bolsa de ~80 cm
for x, n in zip(XS, ['9820', '9742', '9734']):
    s = cv2.imread(os.path.join(BAGS, f'bolsa_{n}.png'), cv2.IMREAD_UNCHANGED).astype(np.float32) / 255
    w = int(round(s.shape[1] * bag_h / s.shape[0])); s = cv2.resize(s, (w, bag_h), interpolation=cv2.INTER_AREA)
    rgb = s[..., :3] ** 2.2; a = s[..., 3]
    g = rgb.mean(axis=2, keepdims=True); rgb = (g + (rgb - g) * 0.8) * 0.55 * np.array([0.88, 0.97, 1.05], np.float32)  # luz cálida y baja del set
    x0, y0 = int(x - w / 2), int(BASE_Y - bag_h)
    cv2.ellipse(sh, (int(x), int(BASE_Y)), (int(w * 0.62), 14), 0, 0, 360, 0.7, -1)
    cv2.ellipse(sh, (int(x), int(BASE_Y) + 1), (int(w * 0.5), 4), 0, 0, 360, 1.0, -1)
    C[y0:y0 + bag_h, x0:x0 + w] = rgb * a[..., None] + C[y0:y0 + bag_h, x0:x0 + w] * (1 - a[..., None])
    # reflejo suave en el piso pulido
    r = (rgb * a[..., None])[::-1] * np.clip(1 - np.arange(bag_h) / (bag_h * 0.3), 0, 1)[:, None, None] * 0.14
    y1 = min(OH, int(BASE_Y) + bag_h)
    C[int(BASE_Y):y1, x0:x0 + w] += cv2.GaussianBlur(r, (0, 0), 2.5)[:y1 - int(BASE_Y)]
sh = np.clip(cv2.GaussianBlur(sh, (0, 0), 6), 0, 1)
# la sombra no tapa las bolsas: se aplica antes, solo sobre el piso visible
C = C * (1 - 0.7 * sh[..., None] * (yy > BASE_Y - 3)[..., None]) + 0
save('C_vista_frontal_con_bolsas.png', C)

# referencias de bolsas (fondo gris neutro, para image_references)
for n in ['9820', '9742', '9734']:
    s = cv2.imread(os.path.join(BAGS, f'bolsa_{n}.png'), cv2.IMREAD_UNCHANGED).astype(np.float32) / 255
    h, w = s.shape[:2]; can = np.full((h + 120, w + 120, 3), 0.85, np.float32)
    can[60:60 + h, 60:60 + w] = s[..., :3] * s[..., 3:] + can[60:60 + h, 60:60 + w] * (1 - s[..., 3:])
    cv2.imwrite(os.path.join(OUT, f'ref_bolsa_{n}.png'), (can * 255).astype(np.uint8))
print('bolsa alto px:', bag_h, ' magnificación:', round(MAG, 2))
