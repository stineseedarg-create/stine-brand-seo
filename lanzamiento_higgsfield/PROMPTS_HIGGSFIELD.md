# Lanzamiento Green Friday Stine: tomas para Higgsfield

## Cómo se reparte el trabajo

- **Higgsfield genera lo que tiene que verse filmado:** la puerta, la luz, la neblina y el polvo.
- **Las bolsas se agregan en el montaje.** Se usan los recortes reales de las tres bolsas, que aparecen con flash en estilo stop-motion. Así las etiquetas quedan exactas: ST 9820 CL, ST 9742 RG sin Viptera3 y ST 9734. Si se generan con IA, el texto de las bolsas se deforma.
- **En el montaje también van** los flashes, el acercamiento, el cierre con los textos y el sonido. Todo se ajusta en `config_montaje.toml`.

Solo hay que generar **dos clips**. Los MP4 van en `clips/` con estos nombres exactos.

En las dos tomas conviene desactivar el audio generado, porque el sonido lo pone el montaje.

---

### Toma A: la puerta se abre (0 a 2 s del video) → `clips/A_puerta.mp4`

- **Modelo:** Cinema Studio Video 3.0. Alternativa: Seedance 2.0.
- **Formato:** 9:16, 1080p, 5 s. Del clip se usan los primeros 2 s.
- **start_image:** `tomas_originales/05_Detalle_puerta_lateral.jpg`
- **Audio:** desactivado.

**Prompt:**

```
Locked-off static camera, no camera movement. Dark, empty concrete photo studio. In the first second the dark metal door on the left wall swings open, and warm golden daylight floods in through the doorway from behind it, backlighting a soft haze. Visible light rays and slow floating dust particles drift in the beam. A soft warm wedge of light spreads across the polished concrete floor. This door light is softer than the existing diagonal skylight beam, which stays exactly as it is. No people, no objects, no text.
```

---

### Toma B: el set (placa para las bolsas y el cierre, de 2 a 13 s) → `clips/B_set.mp4`

- **Modelo:** Cinema Studio Video 3.0. Alternativa: Seedance 2.0 en modo std.
- **Formato:** 9:16, 1080p, **12 s**.
- **start_image:** `cuadros_para_higgsfield/B_vista_frontal_con_cruces.png`. Ya tiene las tres cruces de cinta en perspectiva.
- **Audio:** desactivado.

**Prompt:**

```
Locked-off static tripod shot, absolutely no camera movement, no zoom. Empty concrete photo studio exactly as in the image. The door on the left wall is open and soft warm daylight comes through it, forming a gentle wedge of light on the floor from the left. Dust particles drift slowly through the diagonal skylight beam and through the door light; thin haze moves subtly. The three white tape X marks on the floor stay exactly in place, unchanged. Nothing else happens. No people, no objects, no text.
```

**Importante: la cámara tiene que quedar quieta.** Las bolsas se pegan sobre las cruces, así que si el clip trae movimiento de cámara, las bolsas "flotan". Si Higgsfield mueve la cámara igual, regenerá la toma o avisame y estabilizo el clip.

Si la puerta se abre durante el primer segundo, no hay problema: el montaje saltea ese tramo (`desde = 1.0`).

---

### Toma C (opcional): acercamiento con las bolsas, hecho por IA

Solo para probar. Por defecto el acercamiento se hace en el montaje.

- **Modelo:** Seedance 2.0 (std, 1080p, 9:16, 5 s).
- **start_image:** `cuadros_para_higgsfield/C_vista_frontal_con_bolsas.png`
- **image_references:** `ref_bolsa_9820.png`, `ref_bolsa_9742.png`, `ref_bolsa_9734.png`

**Prompt:**

```
Slow cinematic push-in toward the three kraft-paper seed bags standing on the tape marks. Off-camera photographer flashes pop several times like a fashion shoot, briefly lighting the bags. The bags do not move and their printed labels stay exactly the same. Dust in the light beams. No people, no text added.
```

**Riesgo:** la IA tiende a cambiar letras de las etiquetas (por ejemplo, "ST 9742 RG" o el logo de Viptera3). Revisalas cuadro por cuadro antes de usar esta toma.

---

## Después de generar

1. Copiá los MP4 a `clips/` como `A_puerta.mp4` y `B_set.mp4`.
2. Corré `python3 montaje.py`, o pasámelos y lo corro yo.
3. Salen `salida/lanzamiento-green-friday-9x16.mp4` y `salida/lanzamiento-cuadro-final.png`.
