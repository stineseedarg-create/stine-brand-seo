# Video de lanzamiento – Green Friday Stine

- `config.toml`: todos los textos, tiempos, posiciones, colores y sonido. Es lo único que hace falta editar.
- `render.py`: genera el video.
- `assets/`: el fondo (`estudio_vacio.png`), las bolsas recortadas, la marca GREEN/BLACK FRIDAY, el logo y las fuentes.
- `salida/`: el MP4 final (1080x1920, 30 fps, con sonido) y el PNG del último cuadro.

## Cómo volver a generarlo

Render completo, unos 10 minutos:

```bash
python3 render.py
```

Solo algunos cuadros de prueba, que quedan en `salida/prueba_*.png`:

```bash
python3 render.py --test 2.3,9.5,12.9
```

Necesita Python 3.11 o superior con numpy, opencv-python, pillow y scipy, y además ffmpeg.

## Fuentes

Las fuentes son Anton (títulos) y Montserrat (líneas chicas), las dos con licencia SIL Open Font License.

## Sonido

Todo el sonido está sintetizado: puerta, disparos, golpes y música. Sirve como guía de ritmo. Para la versión final conviene reemplazarlo por efectos y música de una librería con licencia.
