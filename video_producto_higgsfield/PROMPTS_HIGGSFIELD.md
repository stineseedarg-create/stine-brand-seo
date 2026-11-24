# Video de producto Stine: tomas para Higgsfield

No pude abrir el pin de Pinterest. Para armar este plan usé tus dos imágenes: la bolsa héroe y la grilla de 4 tomas (frente, 3/4, detalle del cierre y detalle del lateral). Si querés que copie el ritmo exacto de la referencia, subí el video como archivo.

## Configuración para todas las tomas

- **Modelo:** Cinema Studio Video 3.0. Alternativa: Seedance 2.0 (std).
- **Formato:** 9:16, 1080p, 5 s.
- **Audio:** desactivado. La música se pone al final.
- **start_image:** el cuadro de `cuadros_inicio/` que indica cada toma.
- **Nombre de salida:** guardá cada MP4 en `clips/` con el nombre indicado.

Agregá esta frase al final de todos los prompts:

```
The printed labels on the bag stay exactly the same, no new text, no letters changing.
```

---

### 1 · Héroe ST 9734 → `clips/01_9734_heroe.mp4`

**start_image:** `cuadros_inicio/01_9734_heroe.png`

```
Premium product commercial. Very slow cinematic push-in toward the kraft-paper seed bag standing on a dark polished concrete floor. A warm diagonal sunbeam slowly sweeps across the textured wall behind it, dust particles floating in the light, soft reflection on the floor. Shallow depth of field, moody golden light, 35mm film look.
```

### 2 · ST 9820 CL de frente → `clips/02_9820_frente.mp4`

**start_image:** `cuadros_inicio/02_9820_frente.png`

```
Premium product commercial. The camera slowly dollies in toward the front of the kraft-paper seed bag, centered. Warm top light gently flickers as if a cloud passes, highlights glide over the paper texture. Dark studio, polished concrete floor, shallow depth of field.
```

### 3 · Giro a tres cuartos → `clips/03_9820_tres_cuartos.mp4`

**start_image:** `cuadros_inicio/03_9820_tres_cuartos.png`

```
Premium product commercial. Smooth slow orbit of the camera around the seed bag from left to right, revealing the blue side panel with the white STINE logo. Warm rim light from above, dark background, soft floor reflection, cinematic.
```

### 4 · Detalle del cierre cosido → `clips/04_9820_detalle_cierre.mp4`

**start_image:** `cuadros_inicio/04_9820_detalle_cierre.png`

```
Macro product shot. The camera slowly slides sideways along the stitched folded top of the kraft-paper bag, very shallow depth of field, focus gliding across the paper texture and the seam stitches, warm light from above.
```

### 5 · Detalle del lateral → `clips/05_9820_detalle_lateral.mp4`

**start_image:** `cuadros_inicio/05_9820_detalle_lateral.png`

```
Macro product shot of the blue side panel of the seed bag. Slow tilt up from the bottom label to the white STINE logo, rack focus, warm light, dark polished concrete floor.
```

---

## Después de generar

1. Revisá en cada clip que las etiquetas no hayan cambiado: ST 9734, ST 9820 CL, "LOS PETISOS" en la 9820 y Agrisure Viptera3. La IA suele deformar letras, sobre todo en los giros (toma 3).
2. Copiá los MP4 en `clips/`.
3. Corré `python3 montaje.py`, o pasámelos y lo corro yo. El montaje une las tomas con entradas en foco, barridos y destellos de luz cálida, como en el video anterior.

Los cortes, los tiempos y desde qué segundo se usa cada clip se cambian en `config.toml`.
